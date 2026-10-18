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

print("")
print("README claims to check:")
checks = [
    ("73.7% label->active", pct(len(to_active), len(labels)) == "73.7%"),
    ("89.5% label->any file", pct(len(to_any), len(labels)) == "89.5%"),
    ("63.9% RFCs with an active label",
     pct(len(rfcs_with_active_label), len(rfcs)) == "63.9%"),
    ("97.5% documents joined (636/652)",
     numbered == 636 and len([r for r in rfcs if r.get("document")]) == 636),
]
for name, ok in checks:
    print("  %-52s %s" % (name, "OK" if ok else "MISMATCH"))

docnum = sum(1 for r in rfcs if r.get("document"))
print("")
print("document figure as measured here: %s of 761 RFCs carry a document path" % docnum)
print("the 97.5%% figure is 636 of 652 NUMBERED RFC FILES, a different denominator,")
print("measured from data/rfcs_text_index.json:")
idx = json.load(open(os.path.join(HERE, "data", "rfcs_text_index.json")))
nums = {d["rfc"] for d in idx}
in_corpus = {r["num"] for r in rfcs}
print("  numbered files in the tree: %d" % len(idx))
print("  of those, matching a merged RFC number: %d (%.1f%%)"
      % (len(nums & in_corpus), 100.0 * len(nums & in_corpus) / len(nums)))
