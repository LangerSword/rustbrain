#!/usr/bin/env python3
"""rustbrain gaps: the routing-gap report, in three tiers, with scope on every count.

Tier 1 ACTIVE     the label's team exists and is active
Tier 2 SUCCESSOR  the label's team is archived and has a curated successor edge
Tier 3 TRUE_GAP   archived with no successor, or no team file at all

Every count below carries its numerator, its denominator and its scope, because a
bare total is the failure mode this project already made once.

Usage:  python3 cmd/gaps.py [--json]
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "scripts"))
from load_graph import Resp, GRAPH  # noqa: E402

# EDGE DIRECTIONS:
#   (Team)-[:SUCCEEDED_BY]->(Team)   archived team points AT its active successor
#   (Team)-[:GOVERNED]->(RFC)        team points AT rfc
# Label load is read from RFC.team_labels, so a label with NO team file still counts.
TIERS_CYPHER = """
MATCH (r:RFC) UNWIND r.team_labels AS label
WITH label, count(DISTINCT r) AS rfcs
OPTIONAL MATCH (t:Team {slug: label})
OPTIONAL MATCH (t)-[:SUCCEEDED_BY]->(succ:Team)
WITH label, rfcs, t, succ,
     CASE WHEN t IS NULL THEN 'TRUE_GAP'
          WHEN t.status = 'active' THEN 'ACTIVE'
          WHEN succ IS NOT NULL THEN 'SUCCESSOR'
          ELSE 'TRUE_GAP' END AS tier
RETURN tier, label, rfcs, coalesce(t.status, 'NO_TEAM_FILE') AS status,
       coalesce(succ.slug, '') AS successor
ORDER BY tier, rfcs DESC
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    conn = Resp()
    rows = conn.q(GRAPH, TIERS_CYPHER).rows
    total_rfcs = int(conn.q(GRAPH, "MATCH (r:RFC) RETURN count(r)").rows[0][0])
    labels_total = len(rows)
    tiers = {}
    for tier, label, rfcs, status, succ in rows:
        tiers.setdefault(tier, []).append(
            {"label": label, "rfcs": int(rfcs), "status": status, "successor": succ})

    # An RFC can carry more than one label, so label loads are NOT disjoint. The
    # distinct-RFC count per tier is therefore computed separately.
    per_tier = {}
    for name, q in (
        ("ACTIVE",
         "MATCH (r:RFC) UNWIND r.team_labels AS l MATCH (t:Team {slug:l}) "
         "WHERE t.status='active' RETURN count(DISTINCT r)"),
        ("SUCCESSOR",
         "MATCH (r:RFC) UNWIND r.team_labels AS l MATCH (t:Team {slug:l})-[:SUCCEEDED_BY]->(:Team) "
         "RETURN count(DISTINCT r)"),
        ("TRUE_GAP",
         "MATCH (r:RFC) UNWIND r.team_labels AS l "
         "OPTIONAL MATCH (t:Team {slug:l}) "
         "WITH r, l, t WHERE t IS NULL OR (t.status<>'active' AND NOT (t)-[:SUCCEEDED_BY]->(:Team)) "
         "RETURN count(DISTINCT r)"),
    ):
        per_tier[name] = int(conn.q(GRAPH, q).rows[0][0])

    out = {"scope": "all merged RFC PRs in rust-lang/rfcs, 2026-10-16 pins",
           "rfc_total": total_rfcs, "labels_total": labels_total,
           "tiers": tiers, "distinct_rfcs_per_tier": per_tier,
           "note": ("A single RFC can carry labels in more than one tier, so "
                    "distinct_rfcs_per_tier does not sum to rfc_total.")}

    if args.json:
        print(json.dumps(out, indent=1))
        return 0

    W = 74
    print("ROUTING GAP REPORT")
    print("=" * W)
    print("Scope: all merged RFC PRs in rust-lang/rfcs at the pinned SHA")
    print("       (see PINS.md). Labels come from RFC.team_labels, so a label with")
    print("       no team file still appears below.")
    print("Denominators: %d merged RFCs, %d distinct T-* labels in use."
          % (total_rfcs, labels_total))
    print()

    for tier in ("ACTIVE", "SUCCESSOR", "TRUE_GAP"):
        items = tiers.get(tier, [])
        if tier == "ACTIVE":
            print("TIER 1: ACTIVE (%d labels, %d distinct RFCs)"
                  % (len(items), per_tier["ACTIVE"]))
            print("  The label's team exists and is active. No action needed.")
        elif tier == "SUCCESSOR":
            print("\nTIER 2: ARCHIVED WITH A NAMED SUCCESSOR (%d labels, %d distinct RFCs)"
                  % (len(items), per_tier["SUCCESSOR"]))
            print("  Actionable: the route is real, it just has to follow one hop.")
        else:
            print("\nTIER 3: TRUE GAP (%d labels, %d distinct RFCs)"
                  % (len(items), per_tier["TRUE_GAP"]))
            print("  Actionable: create the team, or stop using the label.")
        print("  %-26s %-6s %-14s %s" % ("label", "rfcs", "status", "successor"))
        for it in items:
            print("  %-26s %-6d %-14s %s"
                  % (it["label"], it["rfcs"], it["status"], it["successor"] or "-"))
        print("  %-26s %-6d   (%d of %d RFCs carry at least one label in this tier)"
              % ("SUBTOTAL", sum(i["rfcs"] for i in items),
                 per_tier[tier], total_rfcs))
        print()

    print("=" * W)
    print("Per-label RFC loads overlap: one RFC can carry several labels, so the")
    print("SUBTOTAL column sums to more than the RFC total. The distinct-RFC")
    print("figures above are the ones to quote.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
