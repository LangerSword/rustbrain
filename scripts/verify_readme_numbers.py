#!/usr/bin/env python3
"""Re-derive every coverage figure quoted in README.md, from the committed snapshot.

If a number here disagrees with the README, the README is wrong. Run: python3 scripts/verify_readme_numbers.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
snap = json.load(open(os.path.join(HERE, "data", "snapshot.json")))

teams = snap["teams"]
rfcs = snap["rfcs"]
succ = {e["from"] for e in snap["successor_map"]["edges"]}
active = {s for s, t in teams.items() if t["status"] == "active"}

labels = sorted({l for r in rfcs for l in r["team_labels"]})
to_active = [l for l in labels if l in active]
to_any = [l for l in labels if l in teams]
no_file = [l for l in labels if l not in teams]

rfcs_with_active_label = [r for r in rfcs if any(l in active for l in r["team_labels"])]
docs = [r for r in rfcs if r.get("document")]
numbered = sum(1 for r in rfcs if r.get("document"))
authors = {r["author"] for r in rfcs}
people = snap["people"]
on_team = {a for a in authors if people.get(a, {}).get("on_active_team")}

orphans = [r for r in rfcs if r["author"] not in people]
orphans_merged = [r for r in orphans if r["outcome"] == "merge"]
no_member_no_alumni = [r for r in rfcs
                       if r["author"] not in people
                       or not people[r["author"]]["on_active_team"]]
no_member_no_alumni = [r for r in no_member_no_alumni
                       if not people.get(r["author"], {}).get("alumni_of")]

def pct(a, b):
    return "%.1f%%" % (100.0 * a / b) if b else "n/a"

rows = [
    ("labels total", len(labels), None),
    ("labels resolving to an ACTIVE team", len(to_active), pct(len(to_active), len(labels))),
    ("labels resolving to ANY file", len(to_any), pct(len(to_any), len(labels))),
    ("labels with no file at all", len(no_file), ", ".join(no_file)),
    ("RFCs total", len(rfcs), None),
    ("RFCs with >=1 active-team label", len(rfcs_with_active_label),
     pct(len(rfcs_with_active_label), len(rfcs))),
    ("documents present on RFC nodes", numbered, None),
    ("distinct authors", len(authors), None),
    ("authors on an active team", len(on_team), pct(len(on_team), len(authors))),
    ("orphan-author RFCs (no people file)", len(orphans), pct(len(orphans), len(rfcs))),
    ("orphan-author RFCs that carried merge", len(orphans_merged), None),
    ("RFCs with no current member AND no alumni record", len(no_member_no_alumni),
     pct(len(no_member_no_alumni), len(rfcs))),
    ("successor edges", snap["counts"]["successor_edges"], None),
    ("teams total / active", "%d / %d" % (snap["counts"]["teams_total"],
                                          snap["counts"]["teams_active"]), None),
    ("roster edges (lead+member)", snap["counts"]["roster_edges_roster"], None),
    ("people", snap["counts"]["people"], None),
]
print("%-56s %-8s %s" % ("measure", "value", "rate / note"))
for name, val, extra in rows:
    print("%-56s %-8s %s" % (name, val, extra or ""))

idx = json.load(open(os.path.join(HERE, "data", "rfcs_text_index.json")))
raw_prs = json.load(open(os.path.join(HERE, "data", "rfcs_merged.json")))
merged_any = {r["num"] for r in raw_prs}
nums = {d["rfc"] for d in idx}
in_corpus = {r["num"] for r in rfcs}
no_label = [r for r in rfcs if not r["team_labels"]]
any_file = [r for r in rfcs if any(l in teams for l in r["team_labels"])]
act_file = [r for r in rfcs if any(l in active for l in r["team_labels"])]

print("")
print("README claims, asserted one by one. A mismatch here means the README is wrong.")
checks = [
    ("labels -> active team is 73.7% (14/19)", pct(len(to_active), len(labels)) == "73.7%"),
    ("labels -> any file is 89.5% (17/19)", pct(len(to_any), len(labels)) == "89.5%"),
    ("RFCs with an active-team label is 46.9% (357/761)",
     len(act_file) == 357 and pct(len(act_file), len(rfcs)) == "46.9%"),
    ("RFCs with any-file label is 63.9% (486/761)",
     len(any_file) == 486 and pct(len(any_file), len(rfcs)) == "63.9%"),
    ("RFCs with no label at all is 34.2% (260/761)",
     len(no_label) == 260 and pct(len(no_label), len(rfcs)) == "34.2%"),
    ("numbered RFC files joining to a merged RFC is 96.0% (626/652)",
     len(idx) == 652 and len({d["rfc"] for d in idx} & in_corpus) == 626
     and pct(len(nums & in_corpus), len(idx)) == "96.0%"),
    ("authors on an active team over 761 RFCs is 35.1% (85/242)",
     len(on_team) == 85 and len(authors) == 242
     and pct(len(on_team), len(authors)) == "35.1%"),
    ("no membership and no alumni is 22.2% (169/761)",
     len(no_member_no_alumni) == 169),
]
bad = 0
for name, ok in checks:
    if not ok:
        bad += 1
    print("  %-56s %s" % (name, "OK" if ok else "MISMATCH"))
print("")
print("VERDICT: %s" % ("PASS, every README number reproduces" if not bad
                       else "FAIL, %d claim(s) do not reproduce" % bad))
sys.exit(1 if bad else 0)
