#!/usr/bin/env python3
"""rustbrain route: given an RFC PR number or a set of T-* labels, say who reviews it.

Output: the owning team chain (with the successor hop shown), the current members
with their role, each person's authored RFC count and latest date, sorted by LATEST
DATE first, then a routing-gap flag when a label has no active team.

No LLM anywhere in this path.

Usage:
  python3 cmd/route.py 3485                route by PR number
  python3 cmd/route.py T-libs-api T-core   route by labels
  python3 cmd/route.py 3485 --json         machine-readable output
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "scripts"))
from load_graph import Resp, GRAPH  # noqa: E402

# EDGE DIRECTIONS, pinned:
#   (Person)-[:MEMBER|LEAD]->(Team)     person points AT team
#   (Person)-[:AUTHORED]->(RFC)         person points AT rfc
#   (Team)-[:GOVERNED]->(RFC)           team points AT rfc
#   (Team)-[:SUCCEEDED_BY]->(Team)      archived points AT active successor
# Role comes from the collected relationship TYPES, not from a pattern expression:
# on this build a pattern expression inside CASE is always truthy and labels every
# member as a lead. Measured 2026-10-19, module ver 42201.
ROUTE_CYPHER = """
MATCH (labelled:Team {slug: $slug})
MATCH (labelled)-[:SUCCEEDED_BY*0..3]->(owner:Team)
WHERE owner.status = 'active'
MATCH (owner)<-[r:LEAD|MEMBER]-(p:Person)
OPTIONAL MATCH (p)-[:AUTHORED]->(authored:RFC)
WITH owner, p, collect(DISTINCT type(r)) AS kinds,
     count(DISTINCT authored) AS authored_count, max(authored.created) AS latest
RETURN owner.slug AS owner, p.handle AS handle,
       CASE WHEN 'LEAD' IN kinds THEN 'lead' ELSE 'member' END AS role,
       authored_count AS authored, coalesce(latest, '') AS latest
ORDER BY latest DESC, authored DESC, handle
"""

NAIVE_CYPHER = """
MATCH (labelled:Team {slug: $slug})
MATCH (labelled)<-[r:LEAD|MEMBER]-(p:Person)
OPTIONAL MATCH (p)-[:AUTHORED]->(authored:RFC)
WITH labelled, p, collect(DISTINCT type(r)) AS kinds,
     count(DISTINCT authored) AS authored_count, max(authored.created) AS latest
RETURN labelled.slug AS owner, p.handle AS handle,
       CASE WHEN 'LEAD' IN kinds THEN 'lead' ELSE 'member' END AS role,
       authored_count AS authored, coalesce(latest, '') AS latest
ORDER BY latest DESC, authored DESC, handle
"""
# The naive twin above is deliberately NOT a fallback: it exists so the demo can
# show the dead end (an archived team with an empty roster) next to the real route.
# Same directions as ROUTE_CYPHER, just with the successor walk removed.

CHAIN_CYPHER = """
MATCH (labelled:Team {slug: $slug})
OPTIONAL MATCH path = (labelled)-[:SUCCEEDED_BY*1..3]->(owner:Team)
RETURN labelled.slug AS labelled, labelled.status AS status,
       CASE WHEN owner IS NULL THEN labelled.slug ELSE owner.slug END AS final_team,
       CASE WHEN owner IS NULL THEN 'ACTIVE' ELSE 'SUCCESSOR' END AS tier,
       size(coalesce(relationships(path), [])) AS hops
"""

LABEL_TIER_CYPHER = """
MATCH (r:RFC) UNWIND r.team_labels AS label
WITH label, count(DISTINCT r) AS rfcs
OPTIONAL MATCH (t:Team {slug: label})
OPTIONAL MATCH (t)-[:SUCCEEDED_BY]->(succ:Team)
RETURN label, rfcs,
       coalesce(t.status, 'NO_TEAM_FILE') AS status,
       CASE WHEN t IS NULL THEN 'TRUE_GAP'
            WHEN t.status = 'active' THEN 'ACTIVE'
            WHEN succ IS NOT NULL THEN 'SUCCESSOR'
            ELSE 'TRUE_GAP' END AS tier,
       coalesce(succ.slug, '') AS successor
"""


def parse_list_prop(v):
    """A list property comes back from the wire as a bracketed STRING such as
    '[lang, libs-api]'. Iterating it directly walks characters, which routed every
    RFC to a one-letter team. Measured 2026-10-19 on module ver 42201."""
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v]
    s = str(v).strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    return [x.strip() for x in s.split(",") if x.strip()]


def slugs_from_pr(conn, pr):
    rows = conn.q(GRAPH, "MATCH (r:RFC {num:%d}) RETURN r.team_labels, r.title, r.outcome" % pr).rows
    if not rows:
        return None
    labels = parse_list_prop(rows[0][0])
    return labels, rows[0][1], rows[0][2]


def route_label(conn, slug, naive=False):
    chain = conn.q(GRAPH, CHAIN_CYPHER.replace("$slug", "'%s'" % slug)).rows
    q = NAIVE_CYPHER if naive else ROUTE_CYPHER
    people = conn.q(GRAPH, q.replace("$slug", "'%s'" % slug)).rows
    return chain, people


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="+", help="an RFC PR number, or one or more T-* labels")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--naive", action="store_true",
                    help="skip the successor walk: look up only the team the label names "
                         "(the demo contrast; the default route follows recorded successors)")
    args = ap.parse_args()

    conn = Resp()
    out = {"input": args.targets, "labels": []}

    for target in args.targets:
        if target.isdigit():
            got = slugs_from_pr(conn, int(target))
            if got is None:
                out["labels"].append({"label": "RFC %s" % target, "tier": "NOT FOUND",
                                      "rfcs": 0, "people": []})
                continue
            labels, title, outcome = got
            for l in labels:
                chain, people = route_label(conn, l, naive=args.naive)
                out["labels"].append({"label": "T-" + l, "from_pr": int(target),
                                      "pr_title": title, "pr_outcome": outcome,
                                      "rfcs": None,
                                      "tier": chain[0][3] if chain else "TRUE_GAP",
                                      "chain": chain, "people": people})
            if not labels:
                out["labels"].append({"label": "RFC %s" % target, "tier": "NO_TEAM_LABEL",
                                      "people": []})
        else:
            slug = target[2:].lower() if target.lower().startswith("t-") else target.lower()
            chain, people = route_label(conn, slug, naive=args.naive)
            tier_row = conn.q(GRAPH, LABEL_TIER_CYPHER).rows
            rfcs = next((r[1] for r in tier_row if r[0] == slug), 0)
            out["labels"].append({"label": "T-" + slug, "rfcs": rfcs,
                                  "tier": chain[0][3] if chain else "TRUE_GAP",
                                  "chain": chain, "people": people})

    if args.json:
        print(json.dumps(out, indent=1))
        return 0

    for blk in out["labels"]:
        print("=" * 72)
        head = blk["label"]
        if blk.get("from_pr"):
            head += "  (RFC #%s: %s)" % (blk["from_pr"], (blk.get("pr_title") or "")[:58])
        print(head)
        if blk.get("rfcs") is not None:
            print("  merged RFCs carrying this label: %s" % blk["rfcs"])
        chain = blk.get("chain") or []
        if chain:
            c = chain[0]
            if args.naive and c[2] != c[0]:
                print("  route: %s (%s), successor hop not taken   [--naive]" % (c[0], c[1]))
                print("  naive lookup: %d current members on %s. This is the dead end the graph exists to fix."
                      % (len(blk.get("people") or []), c[0]))
                continue
            if c[2] != c[0]:
                print("  route: %s (%s) --SUCCEEDED_BY--> %s   [tier %s, %s hop(s)]"
                      % (c[0], c[1], c[2], c[3], c[4]))
            else:
                print("  route: %s (%s), no successor hop needed   [tier %s]"
                      % (c[0], c[1], c[3]))
        people = blk.get("people") or []
        if blk["tier"] in ("TRUE_GAP", "NOT FOUND", "NO_TEAM_LABEL"):
            print("  ROUTING GAP: %s." % blk["tier"])
            print("  There is no active team for this label, so there is nobody to route to.")
            if people:
                print("  (%d rows returned anyway, which should not happen)" % len(people))
        elif not people:
            print("  ROUTING GAP: team exists but has 0 current members.")
        else:
            print("  %d current members, sorted by latest authored RFC:" % len(people))
            print("    %-22s %-8s %-10s %s" % ("handle", "role", "authored", "latest"))
            for _owner, handle, role, count, latest in people:
                print("    %-22s %-8s %-10s %s" % (handle, role, count, latest or "-"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
