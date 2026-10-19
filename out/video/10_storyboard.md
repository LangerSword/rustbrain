# Demo video storyboard (DRAFT captions, the entrant edits)

Generated from site/data.json (snapshot 6732467a070a) by video/make_storyboard.py.
Every caption number is read from the field named beside it; none is typed by hand.

| beat | seconds | footage source | caption (DRAFT) | number field(s) |
|---|---|---|---|---|
| 1 | 0 to 12 | terminal: cmd/route.py 1892 --naive (raw/term) | the team that owned this rfc has nobody left: 0 current members, archived. | {"transcript": "out/video/transcripts/naive.txt", "value": "naive lookup: 0 current members on libs-api"}; {"site": "site/index.html figure text", "value": "archived, 0 members"} |
| 2 | 12 to 30 | live site hero (raw/site_fhd/hero, raw/site_uhd/hero) | rustbrain routes a rust rfc to the team that exists today. two pinned public revisions, no llm. | {"field": "generated_from.pins", "value": "team and rfcs pins", "note": "PINS.md"} |
| 3 | 30 to 65 | live site: hover successor edge, then tabs T-cargo and T-dev-tools (raw/site_fhd/successor_edge, tabs) | the archived team's own file records its successor, quoted with file and line. / t-cargo is an ordinary active team: 42 merged rfcs, no hop needed. / t-dev-tools has no team file anywhere: 20 of the 761 merged rfcs, a true gap. | {"field": "successor_map.edges.0.source", "value": "teams/archive/core.toml:1"}; {"field": "gaps.tiers.ACTIVE(cargo).rfcs", "value": 42}; {"field": "gaps.tiers.TRUE_GAP(dev-tools).rfcs", "value": 20}; {"field": "gaps.rfc_total", "value": 761} |
| 4 | 65 to 110 | github README graph model, queries/routing.cypher, terminal query run (raw/term/query, raw/site_fhd/readme) | the successor hop is a variable-length traversal: succeeded_by, zero to three hops. / then a roster join: the current team's people and their authored rfcs. / 162 merged rfcs resolve only through this hop: libs-api 138, core 24. / without the graph: a recursive join of unknown depth, and archived rosters return nobody. | {"field": "gaps.distinct.SUCCESSOR", "value": 162}; {"field": "gaps.tiers.SUCCESSOR(libs-api).rfcs", "value": 138}; {"field": "gaps.tiers.SUCCESSOR(core).rfcs", "value": 24} |
| 5 | 110 to 135 | live site /gaps/ (raw/site_fhd/gaps, raw/site_uhd/gaps) | the gap report has three tiers, scope on every line. / 357 routable today, 162 through the successor hop, 25 in true gaps, named. | {"field": "gaps.tiers", "value": "19 labels"}; {"field": "gaps.distinct.ACTIVE", "value": 357}; {"field": "gaps.distinct.SUCCESSOR", "value": 162}; {"field": "gaps.distinct.TRUE_GAP", "value": 25} |
| 6 | 135 to 160 | terminal refresh diff (raw/term/refresh), terminal assertions (raw/term/assertions), public actions run page (raw/site_fhd/actions) | the refresh command caught a real roster change: joboet left libs-ping. / the query command is tested: 41 assertions, exact row counts, direction flips. / on the pinned engine, in public ci. | {"file": "reports/refresh_20261019_022025.md", "value": "left=[joboet]"}; {"transcript": "out/video/transcripts/assertions.txt", "value": "41 passed, 0 failed"}; {"field": "module.ver", "value": "42201"} |
| 7 | 160 to 180 | live site /bugs/, limits line; end card drawn in Remotion | the limits are on the site, including the element that scores zero. / volunteer teams, a curated successor map, 52 archived files audited. | {"field": "bugs.archived_team_files", "value": 52} |

## End card

domain: rustbrain.langersword.in; line: track 03: company brain; three facts: 761 merged rfcs (gaps.rfc_total); 162 route only through the successor hop (gaps.distinct.SUCCESSOR); 25 in true gaps (gaps.distinct.TRUE_GAP)

## Spoken script word counts (150 wpm)

| beat | seconds | words | seconds at 150 wpm |
|---|---|---|---|
| 1 | 0 to 12 | 20 | 8.0 |
| 2 | 12 to 30 | 27 | 10.8 |
| 3 | 30 to 65 | 49 | 19.6 |
| 4 | 65 to 110 | 51 | 20.4 |
| 5 | 110 to 135 | 27 | 10.8 |
| 6 | 135 to 160 | 37 | 14.8 |
| 7 | 160 to 180 | 35 | 14.0 |
| total | 0 to 180 | 246 | 98.4 |
