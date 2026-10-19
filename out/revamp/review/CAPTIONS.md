# Revamp scene captures, captions

Six scenes at three widths (1440, 768, 390), captured 2026-10-19 from the
local build of the revamp (stage 6). Every number these scenes show is read
from site/data.json and asserted in CI by scripts/assert_site_numbers.py.
Reproduce: npm run build:motion, npm run serve:site, then load the scenes.

| file | caption |
|---|---|
| scene1_arrival_1440.png | arrival: the claim, the single RFC 1892 card with label T-libs-api and its SUCCESSOR tier |
| scene1_arrival_768.png | arrival at 768: same card, one column, the scene rail hidden below 1200 |
| scene1_arrival_390.png | arrival at 390: the card stacks, the headline wraps to two balanced lines |
| scene2_dead_end_1440.png | the dead end: libs-api archived with 0 current members, the roster fan empty, the naive lookup line shown |
| scene2_dead_end_768.png | the dead end at 768: the stage unpinned, the same empty state |
| scene2_dead_end_390.png | the dead end at 390: full-width card and graph, nothing hidden |
| scene3_hop_1440.png | the hop: the SUCCEEDED_BY edge drawn to libs, the recorded quote landed, 5 of 37 reviewers staggered in |
| scene3_hop_768.png | the hop at 768: shorter pin, same beats, everything landed at the pin end |
| scene3_hop_390.png | the hop at 390: no pin, the same draw and roster on one column |
| scene4_gap_1440.png | the gap: T-dev-tools, the route stub stopping mid-line, "route stops here", 20 of 761 merged rfcs |
| scene4_gap_768.png | the gap at 768: the stop bar and labels intact |
| scene4_gap_390.png | the gap at 390: the stub figure full width, nothing clipped |
| scene5_numbers_1440.png | the numbers: counters at 761 / 162 / 138 / 24 / 25 and the three tiers on one bar denominator |
| scene5_numbers_768.png | the numbers at 768: counters in two columns, tier cards stacked |
| scene5_numbers_390.png | the numbers at 390: the band stacks, every value still exact |
| scene6_close_1440.png | the close: what it refuses to do, what it is not, the honest links and the snapshot hash |
| scene6_close_768.png | the close at 768: two columns drop to one, links intact |
| scene6_close_390.png | the close at 390: masked lines revealed, focus outlines visible on tab |
