# Self-audit: README numbers, dashes and flagged phrases

Run 2026-10-19. One row per number the README states, with the file it comes
from and whether it was re-derived today. Re-derivations run today:
`scripts/verify_readme_numbers.py` (PASS), `scripts/author_coverage.py`,
`cmd/gaps.py`, `scripts/load_graph.py`, `scripts/test_queries.py` (41 passed),
`cmd/route.py 1892`, and the clean-clone Run 3 module receipt (ver 42201).

| README number | context | source file | re-derived today |
|---|---|---|---|
| 224 teams | graph model | data/snapshot.json counts.teams_total | yes, load_graph + build output |
| 172 active / 52 archived | graph model, limits | data/snapshot.json counts | yes, verify_snapshot + successor audit |
| 675 people | graph model, element 1 | data/snapshot.json counts.people | yes, same |
| 416 on an active team | element 1 | data/snapshot.json counts.people_on_active_team | yes, build output |
| 761 RFCs | throughout | data/snapshot.json counts.rfcs | yes, same |
| 626 documents | graph model, element 4 | data/snapshot.json counts.documents | yes, same |
| 1050 MEMBER / 127 LEAD / 592 AUTHORED / 395 GOVERNED / 4 SUCCEEDED_BY | edge table | load_graph.py output | yes, ran today |
| 1177 roster edges (lead plus member) | prose | counts.roster_edges_roster | yes, same |
| 138 merged RFCs on libs-api | hero, rule 3, element 3 evidence | cmd/gaps.py | yes, ran today |
| 24 on core; 162 combined | rule 3, limits | cmd/gaps.py | yes, ran today |
| 37 current libs reviewers | hero sentence | cmd/route.py 1892 output | yes, ran today |
| 0 members on libs-api | hero sentence | data/snapshot.json teams.libs-api.members | yes, snapshot check |
| RFC 3984 at teams/archive/libs-api.toml:1 | hero sentence | data/successors.yaml | yes, successor audit (4 of 4 verified) |
| 337 repository files, 140 under archive | element 3 | out/blog_evidence/repo_permissions.txt | yes, generated today |
| write 206, maintain 127, triage 15 entries | element 3 | repo_permissions.txt | yes, generated today |
| 107 distinct teams in repos/ | element 3 | repo_permissions.txt | yes, generated today |
| 652 numbered files | element 4 | data/rfcs_text_index.json | yes, verify asserts len 652 |
| 241 disposition-merge of 761; 520 none | element 5 | data/rfcs_merged.json labels | yes, counted today |
| 52 archived files; 4 notes mapped; 3 unmapped; 45 with none | successor limit | out/blog_evidence/successor_audit.md | yes, audit run today |
| 19 labels; 14 active (73.7%); 17 any file (89.5%); 2 no file | limits, coverage | verify_readme_numbers.py + author_coverage.py | yes, both ran today, PASS |
| 357 / 761 (46.9%); 486 / 761 (63.9%); 260 / 761 (34.2%) | limits, coverage | author_coverage.py | yes, ran today |
| 626 / 652 (96.0%) | coverage | verify_readme_numbers.py | yes, PASS today |
| 85 / 242 (35.1%); 169 / 761 (22.2%); 41 / 761 (5.4%) | coverage | author_coverage.py | yes, ran today |
| 100 / 380 (26.3%), widened scope | coverage | author_coverage.py | yes, ran today |
| 381 / 761 (50.1%) | orphan correction receipt | out/blog_evidence/20_orphan_figure_correction.md + author_coverage.py | yes, ran today |
| 120-character title cap | limits, policy | scripts/build_snapshot.py | yes; longest title today is 111 chars |
| 41 query assertions | setup, element 6 | scripts/test_queries.py | yes, 41 passed today |
| module ver 42201 (v4.22.1) | limits | out/blog_evidence/module_version_receipt.txt + clean-clone Run 3 | yes, ver 42201 printed today |
| 42 RFCs whose most recent is from 2018 | ORDER BY note | data/snapshot.json per-author counts | yes, checked today; authors with 42 RFCs: {'alexcrichton': '2018-02-07'} |
| 13 of 14 labels in a sample; 33 of 33 member handles | voice block (historical) | research receipts (16_kill_test.md, falkor research tree) | no, sample figures from the research phase; superseded by the full-corpus numbers above |

## Dashes and flagged phrases

Searched with a Python scan over the tracked files in `README.md`, `docs/` and `out/`
(line numbers are exact):

em dash (U+2014) and en dash (U+2013):
    (no matches)

"defect":
    out/blog_evidence/INDEX.md:15: | 3 | my query-direction mistake | One edge, two forms: outbound returns 1 row, inbound returns 0 (correct Cypher), and the unlabelled inbound form re
    out/blog_evidence/clean_clone.md:7: Run 1 followed the committed README at 2be978d exactly and found two defects.
    out/blog_evidence/clean_clone.md:62: ### Defects found in run 1
    out/blog_evidence/direction_receipt.txt:16: defect without printing the ingest Cypher first.

"no document corpus":
    (no matches)

"35 orphan":
    out/blog_evidence/16_kill_test.md:133: 1. The headline number must change. "35 orphan RFCs" was a sample artefact. The
    out/blog_evidence/INDEX.md:16: | 4 | 35 orphans to 385 to 83 | Three figures, three definitions: 35 of a 111-RFC sample; 385 of 761 on the pre-fix roster; 83 was the merge-labelled 

Reading of the matches: the only dash hits would be printed above; the phrase hits are
all inside corrections or captions (the index caption that retracts the engine-defect
conclusion, and the kill-test line that calls the 35-orphan figure a sample artefact),
so every occurrence is a record of a wrong claim, not a restatement of one.

