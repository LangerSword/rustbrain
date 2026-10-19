# 90-second demo script

Five beats: spoken lines on the left, what is on screen on the right. Read at a
conversational 150 words per minute; see the word count section at the bottom. Keep
the order: the archived-team route has to land before the gap, and the refresh diff
before CI.

Before recording: `scripts/start_module.sh 6379` (or reuse a running module and keep
the port consistent), then `FALKORDB_PORT=6379 python3 scripts/load_graph.py`, then
`FALKORDB_PORT=6379 python3 cmd/serve.py`, and open http://127.0.0.1:8788. Have a
terminal already cd'd into the repo next to the browser.

| beat | time | spoken | on screen |
|---|---|---|---|
| 1 | 0:00 to 0:16 | "This is rustbrain. One question about a Rust RFC: who should review it. RFC 1892 carries the label T-libs-api. A naive lookup goes straight to the team the label names: libs-api, archived, zero current members. A dead end." | Terminal: `python3 cmd/route.py 1892 --naive`. The T-libs-api block shows `successor hop not taken` and `naive lookup: 0 current members on libs-api`. |
| 2 | 0:16 to 0:38 | "The graph does what that lookup cannot. It follows the successor edge recorded in the team's own file, libs-api to libs via RFC 3984, and returns the 37 people who own this label today, sorted by their latest RFC activity so the most recent maintainers come first." | The UI at `http://127.0.0.1:8788/?q=1892`: the T-libs-api block, orange SUCCESSOR badge, the route line `libs-api (archived) -> libs via SUCCEEDED_BY (RFC 3984, teams/archive/libs-api.toml:1)`, and the reviewer table scrolled once. |
| 3 | 0:38 to 0:52 | "A label with no successor at all. T-dev-tools sits on 20 of the 761 merged rfcs, no not-rfc counted, and has no team file anywhere. The honest answer is a routing gap, not an empty table." | The UI at `?q=T-dev-tools`: the red TRUE_GAP badge and the gap callout. |
| 4 | 0:52 to 1:08 | "It stays current. The refresh command re-ingests upstream at current HEAD and diffs against the previous snapshot. This diff caught a real roster change: joboet left libs-ping, and the counts moved by exactly one, on the record." | `reports/refresh_20261019_022025.md`, scrolled to `libs-ping: +0/-1 ... left=['joboet']` and the counts table. |
| 5 | 1:08 to 1:24 | "Everything you saw is asserted in CI on the pinned engine: byte-identical ingest, 41 query assertions including direction flips, the routing tiers, the gap counts. Green." | The GitHub Actions run page: the green check and the job list. |

Beat 1 can also be run as `python3 cmd/route.py T-libs-api --naive`; the RFC form is
used above because the demo is about an RFC. The default `python3 cmd/route.py 1892`
shows the graph route for the same RFC, which is beat 2 in terminal form.

## Word count and timing

Spoken column, whitespace-separated words: **184 words**.
At 150 words per minute that is 73.6 seconds; at a slower demo pace of 130 words per
minute it is 84.9 seconds. Both are under the 90 second cap.
Recount after any edit: copy the spoken column and run `wc -w` on it.

## Things not to say

- Do not call the successor map "automatic". It is curated, with a cited file and
  line per entry, and the README says so.
- Do not say the tool knows who *should* approve. It reports who the project's own
  published rosters say is on the team.
- Do not say "company brain" about the data. Rust is a standards foundation and
  element 8 is scored 0 for exactly that reason. The track is Track 03.

Screenshots for the blog and their captions live in `out/blog_evidence/screenshots.md`.

## The revamp

The home page is now six scenes that walk one RFC's route (arrival, dead end, hop, gap, numbers, close) with motion on native scroll only. The beats above still work as a live walkthrough, and the storyboard is the site itself. Design and verification: `out/revamp/20_REVAMP.md` and `out/revamp/30_VERIFY.md`; captures at three widths in `out/revamp/review/`.
