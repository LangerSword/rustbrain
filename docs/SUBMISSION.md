# Submission checklist

Everything here is either DONE with a path you can open, or ENTRANT TO DO with the
exact next step. Nothing is marked done on the strength of an intention. Links and
SHAs reflect the history after the 2026-10-19 rewrite
(`out/blog_evidence/history_rewrite.md`).

Current CI: https://github.com/LangerSword/rustbrain/actions (badge in the README).
Latest verified green runs at the time of writing:
CI https://github.com/LangerSword/rustbrain/actions/runs/39195941817 (commit 9995f46),
Pages deploy https://github.com/LangerSword/rustbrain/actions/runs/39195941823.

## Submission pack, paste ready

- live site: https://langersword.github.io/rustbrain/
- repository: https://github.com/LangerSword/rustbrain
- latest green CI run: https://github.com/LangerSword/rustbrain/actions/runs/39195941817
- demo script: `docs/DEMO.md`, five beats, 184 spoken words (MEASURED); 73.6 seconds
  at 150 words per minute, 84.9 seconds at 130 (rates ASSUMED, word count MEASURED)
- the three screenshots:
  - `out/blog_evidence/ui_rfc1892_successor_hop.png`: RFC PR 1892 routed through the
    SUCCEEDED_BY hop, T-libs-api (archived) to libs, 37 reviewers sorted by latest activity
  - `out/blog_evidence/ui_true_gap_dev_tools.png`: T-dev-tools as a true gap,
    20 of the 761 merged rfcs, nobody to route to
  - `out/blog_evidence/ui_active_team_cargo.png`: T-cargo as an ordinary active route,
    42 merged rfcs, no successor hop needed

Project description, for the entry form (135 words, lowercase-leaning, no dashes):

```
rustbrain routes a rust rfc to the reviewers its own team files name. two public
repos, two pinned revisions, one falkordb graph: 224 teams, 675 people, 761 merged
rfcs. when a label points at a team that was archived, the graph follows the
successor edge that team's file records, cited by file and line, instead of
returning nothing: 162 merged rfcs route only because of that hop. a label with no
successor is reported as a true gap, by name. there is no llm and no api key in the
path; the ingest is deterministic, the routing command writes a reviewer list, and
every number on the site is asserted in ci against the committed snapshot. handles
only, no names or emails, and the limits page states the one element this data
cannot honestly claim.
```

Sixty-word version (62 words, measured):

```
rustbrain routes a rust rfc to the reviewers its own files name. when a label
points at an archived team, the graph follows the successor edge its file records,
to the team that owns the label today: 162 merged rfcs route only through that hop.
labels with nowhere to go are reported as true gaps. no llm; every number asserted
in ci.
```

## In the repository

| # | artifact | state | where |
|---|---|---|---|
| 1 | working product, routing an RFC to reviewers | DONE | `cmd/route.py`, `cmd/serve.py` |
| 2 | archived team followed to its successor | DONE | `data/successors.yaml`, `queries/routing.cypher` |
| 3 | routing-gap report, three tiers, scope on each count | DONE | `cmd/gaps.py`, `out/blog_evidence/gap_report.txt` |
| 4 | refresh command with a real diff | DONE | `cmd/refresh.py`, `reports/refresh_20261019_022025.md` |
| 5 | deterministic ingest with a self-check | DONE | `scripts/build_snapshot.py --check` |
| 6 | 41 query assertions including direction flips | DONE | `scripts/test_queries.py` |
| 7 | independent parser verification of the roster | DONE | `scripts/verify_snapshot.py` |
| 8 | README with graph model, queries, setup, limits, disclosures | DONE | `README.md` |
| 9 | one-page UI, reachable with one command | DONE | `cmd/serve.py` |
| 10 | CI green, engine pinned by digest, PINS.md drift-gated | DONE | `.github/workflows/ci.yml` Job 0, run links above |
| 11 | demo script, five beats, 184 spoken words, under 90 seconds | DONE | `docs/DEMO.md` |
| 12 | upstream revisions and data policy, generated | DONE | `PINS.md` |
| 13 | clean-clone transcript, runs 1 to 3 | DONE | `out/blog_evidence/clean_clone.md` |
| 14 | successor map audit, 4 of 4 entries verified | DONE | `out/blog_evidence/successor_audit.md` |
| 15 | blog evidence index with captions and state | DONE | `out/blog_evidence/INDEX.md` |
| 16 | handles-only data policy, emails removed and purged | DONE | `out/blog_evidence/email_removal_receipt.md`, `history_rewrite.md` |
| 17 | UI screenshots, three states, 1280 CSS px, DPR 2 | DONE | `out/blog_evidence/ui_rfc1892_successor_hop.png`, `ui_true_gap_dev_tools.png`, `ui_active_team_cargo.png` |
| 18 | CI green screenshot | DONE | `out/blog_evidence/ci_green.png` |
| 19 | project site, five pages, deployed | DONE | https://langersword.github.io/rustbrain/ (built from `site/` by `.github/workflows/pages.yml`) |
| 20 | site review: screenshots at three widths, measurements, critique | DONE | `out/site_review/` |

## ENTRANT TO DO

| item | next step |
|---|---|
| record the demo video | five beats in `docs/DEMO.md`; the spoken column is 184 words; record, then link the file here |
| publish the blog post and record its URL | write from `out/blog_evidence/INDEX.md`; do not draft prose before the recording |
| press submit | after the video and the post URL exist |
| track selection | the work is Track 03 ("Company Brain"); confirm the track on the submission form |

## Things a judge will check, and where the answer is

| question | answer |
|---|---|
| Does it run? | `README.md` "Setup, tested from a clean clone", and `out/blog_evidence/clean_clone.md` (three runs, the third on the rewritten history) |
| Is FalkorDB load bearing? | `queries/routing.cypher` and the README's Rule 3 argument: 162 merged RFCs (libs-api 138 plus core 24) resolve only through the 0..3 hop plus roster join |
| Does CI pass? | the run links above, badge in the README |
| What are the numbers? | `out/blog_evidence/readme_numbers.txt`; every README figure re-derived by `scripts/verify_readme_numbers.py` and asserted in CI; the site's own counts are re-derived by `scripts/assert_site_numbers.py` |
| What is it not? | the README's honest limits and `out/blog_evidence/company_like_0.md` (element 8 is 0) |
| Was AI used? | the README's AI-assistant disclosure; corrections live in `out/blog_evidence/` (`20_orphan_figure_correction.md` and the index) |

## Deliberately not claimed

- Not "agent does work" in the LLM sense. There is no model in this repository.
  Element 7 scores 1 because the routing command produces a saved artifact.
- Not "all labels route". 14 of 19 resolve to an active team, 17 of 19 to some file.
- Not "the successor map is complete". Four entries, each with a cited source line;
  of the 52 archived team files, 4 carry a note and all 4 are mapped, 3 are listed
  unmapped with a reason each, and the other 45 carry none.
- Not "company brain". The track is Track 03; the setting is a standards foundation.
