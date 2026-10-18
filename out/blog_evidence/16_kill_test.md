# TEST 2: the kill test, run now on the full corpus

Run 2026-10-16 02:15 IST. Script: `out/phase1/test2_kill.py`. Results JSON:
`out/phase1/kill_test_results.json`. Source fetch log:
`out/phase1/fetch_full_corpus.log`.

**SCOPE, stated once and repeated beside every number below.** `rust-lang/rfcs`,
`pulls?state=closed` filtered to `merged_at` non-null, `sort=created&direction=asc`,
`per_page=100`, 21 pages, fetched **2026-10-16**. **1,130 merged PRs** total, all
time. Of those, **761 carry no `not-rfc` label** and are treated as RFCs. Roster
reference: 683 `people/*.toml` and 224 `teams/*.toml` files in `rust-lang/team` at
`main`, same date.

## 1. Orphan merged RFCs: 385 of 761, 50.6%

**MEASURED.** Author handle has no `rust-lang/team` `people/*.toml` entry.

- **385** orphan merged RFCs of **761** merged RFCs (50.6%).
- **160** distinct orphan author handles.
- Outcome mix of the 385: `merge` 83, no `disposition-*` label 302.

Note the shift from my earlier sample figure of 35: that was 35 of **111** RFCs
(31.5%) drawn from the 183 most recently updated PRs. The full corpus gives 385 of
761. Both are correct; the sample was small and recent, and recent RFCs are less
likely to be orphaned.

## 2. T-* label to team-file join coverage: 89.5%

**MEASURED** across all 761 merged RFCs.

- **19** distinct `T-*` labels.
- **17 of 19** map exactly to a `teams/*.toml` slug = **89.5%**.
- Unmapped: `T-dev-tools`, `T-doc`.
- **24** RFCs carry at least one unmapped label (3.2% of 761).
- **486** RFCs carry at least one mapped team label (63.9%). The remaining 36.1%
  carry no `T-*` label at all, so they are RFCs the label join cannot reach at all.

My earlier 13 of 14 (92.9%) came from 14 labels in a 183-PR sample. On the full
corpus it is 17 of 19 (89.5%). Lower, still above the 85% bar.

## 3. Orphan rate by year of PR creation

**MEASURED.** `created_at` year, RFCs only, 761 total.

| year | merged RFCs | orphans | rate % |
|---|---|---|---|
| 2014 | 144 | 88 | 61.1 |
| 2015 | 141 | 87 | 61.7 |
| 2016 | 74 | 39 | 52.7 |
| 2017 | 79 | 48 | 60.8 |
| 2018 | 76 | 43 | 56.6 |
| 2019 | 29 | 16 | 55.2 |
| 2020 | 38 | 16 | 42.1 |
| 2021 | 38 | 16 | 42.1 |
| 2022 | 29 | 7 | 24.1 |
| 2023 | 38 | 10 | 26.3 |
| 2024 | 42 | 9 | 21.4 |
| 2025 | 18 | 4 | 22.2 |
| 2026 | 15 | 2 | 13.3 |
| **total** | **761** | **385** | **50.6** |

## 4. The objection, tested: partly correct, and it is still a finding

**MEASURED.**

| window | orphan RFCs | RFCs in window | rate |
|---|---|---|---|
| 2020 and earlier | 337 | 581 | **58.0%** |
| 2021 onward | 48 | 180 | **26.7%** |

The objection I recorded was that "unonboarded" is an artefact of the roster
schema, because `teams/*.toml` describes teams rather than the contributor base.
**The year data supports that objection in the sense that matters**: the rate falls
monotonically from about 61% to about 13%, so the phenomenon is overwhelmingly
historical.

**But the control test cuts the other way, and it is the decisive number.**

- Distinct author handles across all 1,130 merged PRs: **380**.
- Of those, on a team: **97**, which is **25.5%**.

So at most a quarter of everyone who has ever merged a PR in this repo appears in
any team file, in any year, including 2026. If `people/*.toml` were merely a
complete list of *contributors*, the 2026 orphan rate would be near zero. It is
13.3%. **The roster is not a contributor index, and that is exactly why a
contributor-to-team gap is a real, measurable, current property of the project
rather than an artefact of my parsing.**

What I must concede: the *magnitude* is inflated by history, so the demo must not
say "385 people are at risk today". The honest framing is "a minority of merged
decisions have an author with no team affiliation, and the rate has fallen from
61% to 13% as the project formalised its teams, which is itself the finding: the
teams are catching up."

## 4b. CORRECTION ADDED 2026-10-19, read this before quoting section 4

Sections 3 and 4 below contain a mislabelled figure. The "83" was described as
RFCs whose author "holds no current team membership and has no alumni record",
but the number 83 was actually the **merge-labelled subset of the 385 orphan
RFCs**. Two different measures shared one label.

Corrected figures, each re-derived by `rustbrain/scripts/author_coverage.py`
against the committed snapshot and each stated with its own definition:

| measure | definition | value |
|---|---|---|
| author not on an active team | absent from every active team's leads/members | **381 of 761, 50.1%** |
| author in no team file at all, not an alumnus | no people file and no alumni entry | **169 of 761, 22.2%** |
| the same, restricted to `outcome == merge` | the decisions subset | **41 of 761, 5.4%** |

The 385 and 160 figures below were also measured before the archived-team bug was
found, when the roster covered only the 172 depth-1 team files and missed 52
archived ones. Full write-up: `out/20_orphan_figure_correction.md`.

What survives unchanged: the kill verdict (both conditions still clear their bars
by a wide margin on the corrected numbers, 381 against a bar of 40, and 89.5%
against a bar of 85%), and the gap report, which counts labels rather than authors
and was re-verified on 2026-10-19.

## 5. Verdict against the pre-registered kill rule

| condition | measured | bar | result |
|---|---|---|---|
| orphan merged RFCs | **385** | kill if below 40 | **PASS**, 9.6x the bar |
| T-* label join coverage | **89.5%** | kill if below 85% | **PASS**, 4.5 points clear |

**C1 is not killed.** Both pre-registered conditions clear their bars by a wide
margin, and they clear them on the full corpus rather than a sample, which is
stronger than the hour-6 test I originally wrote.

## 6. What this changes for the product

1. The headline number must change. "35 orphan RFCs" was a sample artefact. The
   honest headline is **385 of 761 merged RFCs (50.6%), 160 distinct author
   handles**, scoped to all merged PRs in `rust-lang/rfcs` at 2026-10-16.
2. A second, better headline exists: **97 of 380 authors on a team, 25.5%**. That
   is one subtraction and it is the clearest statement of the gap.
3. The demo should show the year table, not just the total. A judge seeing 50.6%
   with no context will call it a parsing bug; a judge seeing the table sees the
   trend and the control.
4. 36.1% of merged RFCs carry no `T-*` label, so the team join covers under two
   thirds of the corpus. That is a coverage limit the README must state, not hide.