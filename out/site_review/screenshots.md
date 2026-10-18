# Site screenshots, captions

All shots were captured from the deployed site, https://langersword.github.io/rustbrain,
with headless Chrome at device scale 1. Widths: 1440x900, 768x900, 390x844.
Files live in `out/site_review/shots/`.

| file | caption |
|---|---|
| home_1440.png | landing at 1440: type-led claim, the live RFC 1892 result with the successor hop, the inline SVG graph, the numbers band below |
| home_768.png | landing at 768: one column, same order, result before graph |
| home_390.png | landing at 390: single column, no horizontal scroll, nav wraps to two lines |
| graph_1440.png | how the graph works: node and edge tables with directions and counts |
| graph_768.png | graph page at 768 |
| graph_390.png | graph page at 390, code block scrolls inside its own box |
| gaps_1440.png | the gap report: tier totals band and the active-tier table |
| gaps_768.png | gaps at 768 |
| gaps_390.png | gaps at 390, tables collapse to single column |
| method_1440.png | method and limits: pipeline, pins, the coverage table with denominators |
| method_768.png | method at 768 |
| method_390.png | method at 390 |
| bugs_1440.png | bugs i found in my own findings: five corrections with receipts |
| bugs_768.png | bugs at 768 |
| bugs_390.png | bugs at 390 |
| after_home_1440.png | landing after the critique fixes: the reviewer table now enters the first viewport beside the graph |
| after_home_390.png | landing at 390 after the fixes: taller nav tap targets, roster caption names its parent |

The before/after pair for the fold fix is `home_1440.png` versus
`after_home_1440.png`; both were measured from the live site, the first before the
Part 6.3 commit, the second after it.
