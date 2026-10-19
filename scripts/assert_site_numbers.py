#!/usr/bin/env python3
"""Assert every number the site shows equals the number the snapshot holds.

This is an independent re-derivation (its own code, not an import of the
exporter): the page can never claim a count the data does not support.
Run in CI after scripts/export_site_data.py --check.

Run:  python3 scripts/assert_site_numbers.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
snap = json.load(open(os.path.join(HERE, "data", "snapshot.json")))
site = json.load(open(os.path.join(HERE, "site", "data.json")))
raw = json.load(open(os.path.join(HERE, "data", "rfcs_merged.json")))

bad = []
def check(name, got, want):
    if got != want:
        bad.append("%s: site=%r snapshot=%r" % (name, got, want))

# 1. the file the site was built from is the committed snapshot
check("content_sha256", site["generated_from"]["content_sha256"], snap["content_sha256"])

# 2. node and edge counts
for k, v in snap["counts"].items():
    check("counts.%s" % k, site["counts"].get(k), v)

# 3. hero: the reviewed team really is the successor of the labelled team, and
#    the reviewer count equals that team's roster union of leads and members
edge = site["hero"]["edge"]
succ = {e["from"]: e for e in snap["successor_map"]["edges"]}
check("hero edge is the recorded edge", edge, succ["libs-api"])
owner = snap["teams"]["libs"]
union = {h for h, _r in owner["members"]} | set(owner["leads"])
check("hero reviewer count", len(site["hero"]["reviewers"]), len(union))
check("hero reviewer handles", sorted(r["handle"] for r in site["hero"]["reviewers"]), sorted(union))
# sorted by latest desc, then authored desc (independent recompute)
auth = {}
lat = {}
for r in snap["rfcs"]:
    auth[r["author"]] = auth.get(r["author"], 0) + 1
    lat[r["author"]] = max(lat.get(r["author"], ""), r["created"] or "")
want_first = min(union, key=lambda h: ((lat.get(h) or ""), auth.get(h, 0), h)) if False else None
got_order = [r["handle"] for r in site["hero"]["reviewers"] if r["latest"]]
exp_order = sorted([h for h in union if lat.get(h)], key=lambda h: (lat[h], auth.get(h, 0), h), reverse=True)
# ties on latest are broken by authored desc then handle asc: compare on a rebuilt sort
def exp_sorted():
    rows = [h for h in union]
    rows.sort()
    rows.sort(key=lambda h: auth.get(h, 0), reverse=True)
    rows.sort(key=lambda h: lat.get(h, ""), reverse=True)
    return rows
check("hero reviewer order", [r["handle"] for r in site["hero"]["reviewers"]], exp_sorted())

# 4. gap tiers: per-label loads and distinct RFCs per tier, recomputed
def tier_of(label):
    t = snap["teams"].get(label)
    if t is None:
        return "TRUE_GAP"
    if t["status"] == "active":
        return "ACTIVE"
    return "SUCCESSOR" if label in succ else "TRUE_GAP"

labels = sorted({l for r in snap["rfcs"] for l in r["team_labels"]})
check("labels total", site["gaps"]["labels_total"], len(labels))
tiers = {}
for l in labels:
    tiers.setdefault(tier_of(l), []).append(l)
check("tier label counts", {t: len(v) for t, v in site["gaps"]["tiers"].items()},
      {t: len(v) for t, v in tiers.items()})
for t, ls in tiers.items():
    for row in site["gaps"]["tiers"][t]:
        l = row["label"]
        check("load %s" % l, row["rfcs"], sum(1 for r in snap["rfcs"] if l in r["team_labels"]))
    check("distinct %s" % t, site["gaps"]["distinct"][t],
          len({r["num"] for r in snap["rfcs"] if any(tier_of(l) == t for l in r["team_labels"])}))

# 5. coverage rows: numerator/denominator pairs reproduce the stored percent
for name, pctv, num, den, _def in site["coverage"]:
    if den:
        check("pct %s" % name, pctv, round(100.0 * num / den, 1))

# 6. counts the site quotes in prose
check("rfc_total", site["gaps"]["rfc_total"], len(snap["rfcs"]))
check("bug stats rfc count", site["bugs"]["successor_rfcs"], site["gaps"]["distinct"]["SUCCESSOR"])
check("archived files", site["bugs"]["archived_team_files"], snap["counts"]["teams_archived"])
check("widened authors", site["coverage"][7][3], len({r["user"] for r in raw}))

# 7. gap counts, per label and as a union, plus the strings the pages show
GAP_LABELS = ("dev-tools", "doc", "interim-leadership-chat")
gap_rows = {row["label"]: row["rfcs"] for row in site["gaps"]["tiers"]["TRUE_GAP"]}
for label in GAP_LABELS:
    check("gap load %s" % label, gap_rows.get(label),
          sum(1 for r in snap["rfcs"] if label in r["team_labels"]))
gap_union = len({r["num"] for r in snap["rfcs"]
                 if any(label in r["team_labels"] for label in GAP_LABELS)})
check("gap union", site["gaps"]["distinct"]["TRUE_GAP"], gap_union)
home_page = open(os.path.join(HERE, "site", "index.html"), encoding="utf-8").read()
gaps_page = open(os.path.join(HERE, "site", "gaps", "index.html"), encoding="utf-8").read()
check("home shows the union", ">25</div>" in home_page and "in true gaps" in home_page, True)
check("home figure names the filter", "20 of 761 merged rfcs, no not-rfc" in home_page, True)
for label, n in (("T-dev-tools", 20), ("T-doc", 6), ("T-interim-leadership-chat", 1)):
    check("gaps page row %s = %d" % (label, n),
          ("<td>%s</td>" % label) in gaps_page and ('<td class="num">%d</td>' % n) in gaps_page, True)
check("gaps page union string", "25 distinct rfcs; union over the 761 corpus" in gaps_page, True)
graph_page = open(os.path.join(HERE, "site", "graph", "index.html"), encoding="utf-8").read()
check("home band names its source", "band counts: cmd/gaps.py" in home_page, True)
check("graph page names load_graph", "scripts/load_graph.py" in graph_page, True)
check("graph page names successors.yaml", "data/successors.yaml" in graph_page, True)

print("checked site/data.json against data/snapshot.json")
if bad:
    for b in bad:
        print("MISMATCH:", b)
    print("VERDICT: FAIL, %d mismatches" % len(bad))
    sys.exit(1)
print("VERDICT: PASS, every site number equals the snapshot's number")
