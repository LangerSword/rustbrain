#!/usr/bin/env python3
"""Export the site's static data from the committed snapshot. Deterministic.

Reads data/snapshot.json (and data/rfcs_merged.json for the widened-scope
figure) and writes site/data.json. The site never calls a server and never
reads the graph at runtime: everything the pages show is precomputed here and
asserted against the snapshot by scripts/assert_site_numbers.py in CI.

Run:  python3 scripts/export_site_data.py            write site/data.json
      python3 scripts/export_site_data.py --check    exit 1 if the file would change
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_snapshot import PIN_META  # noqa: E402

OUT = os.path.join(HERE, "site", "data.json")


def load():
    snap = json.load(open(os.path.join(DATA, "snapshot.json")))
    raw = json.load(open(os.path.join(DATA, "rfcs_merged.json")))
    return snap, raw


def label_tier(snap, label):
    succ = {e["from"]: e for e in snap["successor_map"]["edges"]}
    t = snap["teams"].get(label)
    if t is None:
        return "TRUE_GAP", None
    if t["status"] == "active":
        return "ACTIVE", None
    if label in succ:
        return "SUCCESSOR", succ[label]
    return "TRUE_GAP", None


def reviewers_for(snap, owner_slug):
    """Same result as the graph route: leads and members of the owner, with
    authored counts and latest RFC dates, sorted latest desc then authored desc."""
    t = snap["teams"][owner_slug]
    authored = {}
    latest = {}
    for r in snap["rfcs"]:
        a = r["author"]
        authored[a] = authored.get(a, 0) + 1
        if (r["created"] or "") > latest.get(a, ""):
            latest[a] = r["created"] or ""
    leads = set(t["leads"])
    people = sorted({h for h, _r in t["members"]} | leads)
    rows = [{"handle": h, "role": "lead" if h in leads else "member",
             "authored": authored.get(h, 0), "latest": latest.get(h, "")} for h in people]
    rows.sort(key=lambda x: x["handle"])
    rows.sort(key=lambda x: x["authored"], reverse=True)
    rows.sort(key=lambda x: x["latest"], reverse=True)  # '' sorts last under reverse
    return rows


def build():
    snap, raw = load()
    teams, rfcs = snap["teams"], snap["rfcs"]
    succ_edges = snap["successor_map"]["edges"]

    # hero: RFC 1892 routed by its labels, with T-libs-api's successor hop
    rfc = next(r for r in rfcs if r["num"] == 1892)
    hero_label = "libs-api"
    tier, edge = label_tier(snap, hero_label)
    owner = edge["to"] if edge else hero_label
    reviewers = reviewers_for(snap, owner)

    # gap tiers with distinct-RFC counts per tier
    labels = sorted({l for r in rfcs for l in r["team_labels"]})
    tiers = {"ACTIVE": [], "SUCCESSOR": [], "TRUE_GAP": []}
    for l in labels:
        t, e = label_tier(snap, l)
        tiers[t].append({"label": l,
                         "rfcs": sum(1 for r in rfcs if l in r["team_labels"]),
                         "status": teams[l]["status"] if l in teams else "NO_TEAM_FILE",
                         "successor": e["to"] if e else ""})
    for t in tiers:
        tiers[t].sort(key=lambda x: (-x["rfcs"], x["label"]))
    distinct = {}
    for t, q in (("ACTIVE", lambda l: l in teams and teams[l]["status"] == "active"),
                 ("SUCCESSOR", lambda l: t_of(snap, l)[0] == "SUCCESSOR"),
                 ("TRUE_GAP", lambda l: t_of(snap, l)[0] == "TRUE_GAP")):
        distinct[t] = sum(1 for r in rfcs if any(q(l) for l in r["team_labels"]))

    # coverage figures, same definitions as scripts/verify_readme_numbers.py
    active = {s for s, t in teams.items() if t["status"] == "active"}
    to_active = [l for l in labels if l in active]
    to_any = [l for l in labels if l in teams]
    act_file = [r for r in rfcs if any(l in active for l in r["team_labels"])]
    any_file = [r for r in rfcs if any(l in teams for l in r["team_labels"])]
    no_label = [r for r in rfcs if not r["team_labels"]]
    docs = sum(1 for r in rfcs if r.get("document"))
    idx = json.load(open(os.path.join(DATA, "rfcs_text_index.json")))
    authors = {r["author"] for r in rfcs}
    on_team = {a for a in authors if snap["people"].get(a, {}).get("on_active_team")}
    others = {r["user"] for r in raw}
    others_team = {a for a in others if snap["people"].get(a, {}).get("on_active_team")}
    no_member = [r for r in rfcs if (r["author"] not in snap["people"]
                                     or not snap["people"][r["author"]]["on_active_team"])
                 and not snap["people"].get(r["author"], {}).get("alumni_of")]
    not_on_active = [r for r in rfcs if not snap["people"].get(r["author"], {}).get("on_active_team")]
    def pct(a, b):
        return round(100.0 * a / b, 1) if b else None
    coverage = [
        ["labels resolving to an active team", pct(len(to_active), len(labels)), len(to_active), len(labels), "slug matches an active team file"],
        ["labels resolving to any team file", pct(len(to_any), len(labels)), len(to_any), len(labels), "includes archived files"],
        ["RFCs with a label resolving to an active team", pct(len(act_file), len(rfcs)), len(act_file), len(rfcs), "routable with no successor hop"],
        ["RFCs with a label resolving to any team file", pct(len(any_file), len(rfcs)), len(any_file), len(rfcs), "routable after a successor hop where one exists"],
        ["RFCs carrying no team label at all", pct(len(no_label), len(rfcs)), len(no_label), len(rfcs), "cannot be routed by label"],
        ["numbered RFC files joining to a merged RFC", pct(docs, len(idx)), docs, len(idx), "document layer; denominator is numbered files in the pinned tree"],
        ["authors on an active team (RFC corpus)", pct(len(on_team), len(authors)), len(on_team), len(authors), "over the 761 merged RFCs"],
        ["authors on an active team (all merged PRs)", pct(len(others_team), len(others)), len(others_team), len(others), "widened scope, includes not-rfc PRs"],
        ["RFCs whose author was never on a team and has no alumni record", pct(len(no_member), len(rfcs)), len(no_member), len(rfcs), "no current membership, no alumni entry"],
        ["the same, restricted to outcome merge", pct(sum(1 for r in no_member if r["outcome"] == "merge"), len(rfcs)),
         sum(1 for r in no_member if r["outcome"] == "merge"), len(rfcs), "the decisions subset"],
    ]

    out = {
        "generated_from": {"content_sha256": snap["content_sha256"], "pins": PIN_META},
        "counts": snap["counts"],
        "hero": {
            "rfc": rfc["num"], "rfc_title": rfc["title"], "rfc_labels": rfc["team_labels"],
            "label": hero_label, "tier": tier,
            "edge": edge,           # from/to/rfc/source/quote for libs-api -> libs
            "reviewers": reviewers,  # 37 rows, latest desc then authored desc
        },
        "graph": {
            "chain": [{"slug": "libs-api", "status": "archived"},
                      {"slug": "libs", "status": "active"}],
            "edge": edge,
            "roster": reviewers[:6],
            "gap": {"label": "dev-tools", "rfcs": tiers["TRUE_GAP"][0]["rfcs"] if tiers["TRUE_GAP"] else 0},
        },
        "gaps": {"tiers": tiers, "distinct": distinct, "rfc_total": len(rfcs), "labels_total": len(labels)},
        "coverage": coverage,
        "successor_map": {"edges": succ_edges, "unmapped": snap["successor_map"]["unmapped"]},
        "bugs": {"not_on_active_rfcs": len(not_on_active), "no_team_file_rfcs": len(no_member),
                 "merge_subset_rfcs": sum(1 for r in no_member if r["outcome"] == "merge"),
                 "archived_team_files": snap["counts"]["teams_archived"],
                 "labels": len(labels), "active_labels": len(to_active),
                 "successor_rfcs": distinct["SUCCESSOR"], "gap_rfcs": distinct["TRUE_GAP"]},
        "module": {"ver": "42201", "redis": "8.10.2"},
    }
    return out


def t_of(snap, label):
    return label_tier(snap, label)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    out = build()
    body = json.dumps(out, sort_keys=True, indent=1, ensure_ascii=True) + "\n"
    if args.check:
        if not os.path.exists(OUT) or open(OUT).read() != body:
            print("FAIL: site/data.json is stale or missing; run scripts/export_site_data.py")
            return 1
        print("PASS: site/data.json is byte-identical to a fresh export")
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", OUT, len(body), "bytes")
    print("hero reviewers:", len(out["hero"]["reviewers"]))
    print("tier distinct:", out["gaps"]["distinct"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
