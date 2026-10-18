# Blog evidence index

One file per item, one line of caption, state on every row. CAPTURED means the file
exists in this repository and holds a real command's output; STILL TO CAPTURE means
it has to be produced. Nothing is listed as captured that is not on disk.

All timestamps IST. Everything was produced by running the code in this repository.
The receipts that name the research tree were copied in verbatim during the build so
the submission is self-contained.

| # | item | caption | state | file |
|---|---|---|---|---|
| 1 | the false v6.0.2 claim | The `latest` tag was believed to be v6.0.2 from the release list; the pinned image's module reports ver 42201, which is v4.22.1, pushed three minutes after that release. | CAPTURED | `false_v602_claim.md` |
| 2 | the MODULE LIST receipt | Live `MODULE LIST` from the running engine whose bytes were extracted from the pinned digest: `module=graph ver=42201`, `redis_version:8.10.2`. This output only; the extractor's download log is not cited. | CAPTURED | `module_version_receipt.txt` |
| 3 | my query-direction mistake | One edge, two forms: outbound returns 1 row, inbound returns 0 (correct Cypher), and the unlabelled inbound form returns 1 row with bindings swapped. The arrows were backwards and I called it an engine defect. | CAPTURED | `direction_receipt.txt` |
| 4 | 35 orphans to 385 to 83 | Three figures, three definitions: 35 of a 111-RFC sample; 385 of 761 on the pre-fix roster; 83 was the merge-labelled subset of the 385, not an orphan count. Corrected: 381 not on an active team, 169 in no team file and no alumni, 41 the merge subset. | CAPTURED | `20_orphan_figure_correction.md`, `16_kill_test.md` |
| 5 | 89.5% vs 73.7% | 17 of 19 labels resolve to some team file (89.5%); only 14 resolve to an ACTIVE team (73.7%). The first figure was true and misleading on its own. | CAPTURED | `readme_numbers.txt`, README coverage table |
| 6 | the depth-1 walk that missed 52 archived teams | The roster read `teams/*.toml` and never looked in `teams/archive/`, which holds 52 more files including `libs-api` and `core`. The other three bugs it hid, and the tomllib verifier that caught them, are in the same file. | CAPTURED | `01_snapshot_bugs.md` |
| 7 | the clock drift | Hours-left arithmetic ran off the local clock; three network servers checked during the build showed the same instant was 2 hours 40 minutes past the stated window. One curl would have caught it. | CAPTURED | `clock_drift_receipt.txt` |
| 8 | the libs-api and core resolution | Both archived teams name their successor in their own file (RFC 3984, RFC 3392); the audit re-opened all four cited lines, 4 of 4 verified, and the tier is 162 merged RFCs = libs-api 138 + core 24. | CAPTURED | `successor_audit.md`, `data/successors.yaml` |
| 9 | the PINS drift fix | PINS.md and fetch_upstream.py named `cb0ccabd` while build_snapshot.py, snapshot.json and the committed tree were at `a5176049`; one file hashed at both revisions settled it, and CI Job 0 now fails on any drift. Red and green run links are in the receipt. | CAPTURED | `pins_drift_receipt.md` |
| 10 | routing examples | One per tier plus the naive contrast: RFC 1892 (active label plus successor hop), T-libs-api (0 members naive, 37 after the hop), T-dev-tools (true gap), T-cargo (active); and a real OPEN PR, 4016, routed at capture time. | CAPTURED | `routing_examples.md`, `open_pr_routing.txt` |
| 11 | refresh diffs | A same-pin refresh is a no-op (the determinism result), and the bumped refresh caught a real roster change: `joboet` left `libs-ping`, member edges 1051 to 1050. | CAPTURED | `reports/refresh_20261019_021858.md`, `reports/refresh_20261019_022025.md` |
| 12 | green CI link | Latest green run on `main` at capture time (commit b5ec788, 26s), with the engine pinned by digest, PINS.md drift-gated in Job 0, and the naive dead-end line asserted. | CAPTURED | https://github.com/LangerSword/rustbrain/actions/runs/39170593830 |
| 13 | UI screenshots | Three states at 1280 CSS px, device scale 2: RFC 1892 through the successor hop, T-dev-tools as a true gap, T-cargo as an ordinary active route. Captions in `screenshots.md`. | CAPTURED | `ui_rfc1892_successor_hop.png`, `ui_true_gap_dev_tools.png`, `ui_active_team_cargo.png` |
| 14 | a screenshot of CI green | The Actions run page as rendered: green check, `Status: Success`, `build-and-test` passed, 26s, for readers who will not click through. | CAPTURED | `ci_green.png` |
| 15 | the 90-second demo recording | Follow `docs/DEMO.md`, five beats, 178 spoken words; not yet recorded. | STILL TO CAPTURE | screen recording |
| 16 | the blog post itself | Write from this index and the files it names. | STILL TO CAPTURE | post |
| 17 | emails found in the vendored tree and removed | 542 of 683 vendored people files carried an email field, 55 team files carried 180 contact lines, and 109 upstream source/test/doc files carried example or bot addresses; after removal the email regex returns zero matches on the tracked tree. | CAPTURED | `email_removal_receipt.md` |
