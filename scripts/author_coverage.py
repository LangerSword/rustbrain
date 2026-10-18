#!/usr/bin/env python3
"""Compute every author-coverage variant with its definition written down, so no
figure can be quoted without its scope.

The earlier mistake this exists to prevent: '83 merged RFCs with no member and no
alumni record' was written down when the 83 was actually the merge-labelled subset
of the 385 RFCs whose author is not on an active team. Two different measures, one
label. Every number below names its denominator AND its definition.
"""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
snap = json.load(open(os.path.join(HERE, "data", "snapshot.json")))
raw = json.load(open(os.path.join(HERE, "data", "rfcs_merged.json")))

teams = snap["teams"]
people = snap["people"]
rfcs = snap["rfcs"]

active_teams = {s for s, t in teams.items() if t["status"] == "active"}


def has_people_file(a):
    return a in people


def on_active_team(a):
    return bool(people.get(a, {}).get("on_active_team"))


def is_alumnus(a):
    return bool(people.get(a, {}).get("alumni_of"))


def report(name, rset, definition):
    n = len(rset)
    print("%-52s %4d / %-4d = %6s" % (name, n, len(rfcs), "%.1f%%" % (100.0 * n / len(rfcs))))
    print("      definition: %s" % definition)


print("SCOPE: the %d merged RFC PRs in rust-lang/rfcs at the pinned SHA" % len(rfcs))
print()
report("A. author is not on an ACTIVE team",
       [r for r in rfcs if not on_active_team(r["author"])],
       "author is absent from every active team's leads/members")
report("B. author has NO people file and NO alumni entry",
       [r for r in rfcs if not has_people_file(r["author"])],
       "author handle appears in no team file at all, active or archived")
report("C. author is not on an active team AND is not an alumnus",
       [r for r in rfcs if not on_active_team(r["author"]) and not is_alumnus(r["author"])],
       "author has no current membership and no alumni record anywhere")
report("D. subset of C that carried a merge label",
       [r for r in rfcs if not on_active_team(r["author"])
        and not is_alumnus(r["author"]) and r["outcome"] == "merge"],
       "same as C, restricted to outcome == merge")
print()
print("distinct author handles, per definition:")
print("  all authors in the RFC corpus:        %d" % len({r["author"] for r in rfcs}))
print("  authors on an active team:            %d" % len({r["author"] for r in rfcs if on_active_team(r["author"])}))
print("  authors with no people file:          %d" % len({r["author"] for r in rfcs if not has_people_file(r["author"])}))
print("  authors never on a team, no alumni:   %d" % len({r["author"] for r in rfcs if not on_active_team(r["author"]) and not is_alumnus(r["author"])}))
print()
all_authors = {r["user"] for r in raw}
print("SCOPE widened: all %d merged PRs, including those labelled not-rfc" % len(raw))
print("  distinct authors:                     %d" % len(all_authors))
print("  on an active team:                    %d = %.1f%%"
      % (len({a for a in all_authors if on_active_team(a)}),
         100.0 * len({a for a in all_authors if on_active_team(a)}) / len(all_authors)))
print()
labels = {}
for r in rfcs:
    for l in r["team_labels"]:
        labels.setdefault(l, 0)
        labels[l] += 1
any_file = [l for l in labels if l in teams]
active_only = [l for l in labels if l in active_teams]
n_any = len({r["num"] for r in rfcs if any(l in teams for l in r["team_labels"])})
n_act = len({r["num"] for r in rfcs if any(l in active_teams for l in r["team_labels"])})
print("LABEL COVERAGE")
print("  labels: %d ; to any file: %d (%.1f%%) ; to active: %d (%.1f%%)"
      % (len(labels), len(any_file), 100.0 * len(any_file) / len(labels),
         len(active_only), 100.0 * len(active_only) / len(labels)))
print("  RFCs with a label resolving to ANY file:     %d / %d = %.1f%%"
      % (n_any, len(rfcs), 100.0 * n_any / len(rfcs)))
print("  RFCs with a label resolving to an ACTIVE team: %d / %d = %.1f%%"
      % (n_act, len(rfcs), 100.0 * n_act / len(rfcs)))
print("  RFCs with NO team label at all: %d / %d = %.1f%%"
      % (len([r for r in rfcs if not r["team_labels"]]), len(rfcs),
         100.0 * len([r for r in rfcs if not r["team_labels"]]) / len(rfcs)))
