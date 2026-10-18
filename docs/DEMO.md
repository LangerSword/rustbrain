# 90-second demo script

Two columns: what you say, and what is on screen. Read the spoken lines as written
or change them, but keep the beats in order: the archived-team route is the whole
point, and it has to land before the gap list.

Before you hit record: `scripts/start_module.sh 6399`, then
`FALKORDB_PORT=6399 python3 scripts/load_graph.py`, then
`FALKORDB_PORT=6399 python3 cmd/serve.py`, and open the page. Have a terminal
window open beside the browser, already `cd`'d into the repo.

| time | spoken | on screen |
|---|---|---|
| 0:00 to 0:10 | "This is rustbrain. It answers one question about a Rust RFC: who should review it, according to the project's own team files." | the UI, empty input. Type `T-libs-api` and press Route. |
| 0:10 to 0:25 | "This label is on 138 merged RFCs. The team it names, `libs-api`, was archived and has zero members. A tool that stopped there would return nothing for 138 decisions." | the result: `T-libs-api` with the orange SUCCESSOR badge, and the route line `libs-api (archived) -> libs via SUCCEEDED_BY (RFC 3984, teams/archive/libs-api.toml:1)`. |
| 0:25 to 0:40 | "So the graph follows the successor that the file itself records, and lands on the 37 people who own this label today. Sorted by the date of their most recent RFC, because sorting by count alone routes you to people who left years ago." | scroll the reviewer table. Point at the `lead` rows in orange. |
| 0:40 to 0:52 | "Same query, one label that has no successor. `T-dev-tools` sits on 20 merged RFCs and there is no team file for it anywhere, so the honest answer is a gap, not an empty table." | type `T-dev-tools`, press Route. The red TRUE_GAP badge and the gap callout. |
| 0:52 to 1:05 | "Now the whole picture. Every label in use, worst tier first: 14 active, 2 archived with a successor carrying 162 RFCs between them, and 3 true gaps." | click "Show all routing gaps". The full table. |
| 1:05 to 1:20 | "Underneath: 224 teams, 675 people, 761 merged RFCs, 626 documents. The ingest is a pure function of two pinned revisions, so it is byte-reproducible, and CI asserts every query's exact row count with the engine pinned by image digest." | switch to terminal: `python3 scripts/build_snapshot.py --check` and let it print PASS. |
| 1:20 to 1:30 | "No LLM anywhere in this path. Rust is a volunteer foundation, not a company, and the README says so: that is the one element of eight it cannot honestly claim." | the README's honest-limits table, scrolled to element 8. |

## Shots to capture while recording

1. The `T-libs-api` result with the successor route line legible. This is the money shot.
2. The reviewer table showing `lead` versus `member` and the latest column descending.
3. `T-dev-tools` with the TRUE_GAP badge and the gap callout.
4. The all-gaps table showing the three tiers.
5. `build_snapshot.py --check` printing PASS.
6. The README limits table, element 8 row.

## Things not to say

- Do not call the successor map "automatic". It is curated, with a cited file and
  line per entry, and the README says so.
- Do not say the tool knows who *should* approve. It reports who the project's own
  published rosters say is on the team.
- Do not say "company brain" about the data. Rust is a standards foundation. The
  track is Track 03; the data is what it is.
