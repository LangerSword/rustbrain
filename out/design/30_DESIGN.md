# Design brief (Part 4), written before the build

## Concept, 3 sentences

rustbrain's site is a printed report about a running tool: the fold shows one
real RFC routed through its recorded successor hop to the people who own it
today, rendered from the committed snapshot. Nothing is illustrated; the route
line, the reviewer table and the graph are drawn from the same JSON the demo
reads, the graph as inline SVG built from real nodes and edges. Every number on
the site can be re-exported with `scripts/export_site_data.py` and is asserted
equal to `data/snapshot.json` in CI, so the page cannot claim a count the data
does not support.

## Page list

1. `/` landing: type-led claim; the live routed example (RFC 1892, label
   T-libs-api, archived, followed by SUCCEEDED_BY to libs via RFC 3984, 37
   reviewers with the first five rows); the inline SVG graph; a numbers band
   (761 merged RFCs, 162 routing only through the hop, 138 libs-api, 24 core,
   25 true-gap RFCs), each with scope on the line; one-paragraph honesty note
   that the demo runs from a precomputed snapshot.
2. `/graph/` how the graph works: node and edge tables, the 0..3 hop query with
   its edge directions, the direction test explained, the four cited successor
   lines quoted from `data/successors.yaml`, and the Rule 3 argument in plain
   words.
3. `/gaps/` the gap report: three tiers with live counts and scope (14 active
   labels, 2 archived-with-successor carrying 162 RFCs, 3 true-gap labels
   carrying 25 RFCs), per-label loads, and a pointer to the committed
   `out/blog_evidence/gap_report.txt`.
4. `/method/` methodology and limits: the ingest pipeline, the pins (team
   a5176049, retrieved 2026-10-19; rfcs d2705ad6, retrieved 2026-10-16), the
   coverage table with denominators, the handles-only policy, element 8 scored
   0 with the funded teams named, the curated successor map's limits, and the
   AI-assistant disclosure.
5. `/bugs/` bugs I found in my own findings: the query-direction mistake, 35 to
   385 to 83 and the corrected 381/169/41, the depth-1 walk that missed 52
   archived files, the clock drift, the PINS drift; each entry links into
   `out/blog_evidence/`, and the page states the two rules that survived
   (assert a non-zero row count for every known-good query; every number gets a
   definition and a denominator in the same sentence).

## Design tokens

Palette (dark, warm). Contrast ratios MEASURED with the WCAG relative-luminance
formula; all text pairs pass AA (4.5:1), no pair relies on large-text leniency.

| token | value | use | contrast on bg |
|---|---|---|---|
| bg | `#14110e` | page | n/a |
| surface | `#1c1814` | cards, bands | paper on surface 15.13 |
| paper | `#f2ede4` | body text | 16.13 |
| secondary | `#c9c0b2` | secondary text | 10.45 |
| tertiary | `#918877` | nonessential labels | 5.37 |
| accent | `#ff6a3d` | links, actions, the successor hop | 6.61 |
| ink on accent | `#14110e` on `#ff6a3d` | primary buttons | 6.61 |
| tier active | `#86b96e` | ACTIVE badge and bars | 8.22 |
| tier successor | `#e0a458` | SUCCESSOR badge and hop | 8.62 |
| tier true gap | `#f2705e` | TRUE_GAP badge and bars | 6.50 |
| hairline | `rgba(242,237,228,0.14)` | rules and table lines | structural only |

Type: Newsreader (display, OFL-1.1) plus Inter (UI and tables, OFL-1.1), both
self-hosted woff2, licences shipped beside the files. Scale (px): 12.5 / 14 /
16 / 20 / 28 / 40 / 56 / 72; line-height 1.45 body, 1.08 display over 40; letter
tracking -0.02em at 40 and up. Fallbacks: Georgia, 'Times New Roman', serif;
system-ui, -apple-system, 'Segoe UI', sans-serif.

Spacing scale (px): 4, 8, 12, 16, 24, 32, 48, 64, 96, 128. Radius: 3 controls,
8 cards, full pill for tags. Shadow: none; separation by hairline. Motion:
transform and opacity only, 120ms hover, 200ms enter, easing
cubic-bezier(0.2, 0.7, 0.3, 1).

## Motion rules

Purposeful only: link and control feedback, the demo result swapping when the
target changes, nothing animating on load, no parallax, no scroll-jacking.
`prefers-reduced-motion: reduce` sets every duration and delay to 0.01ms and
disables the result fade.

## Targets (ASSUMED, to be measured on the built site)

- LCP under 2.5s on a throttled run (ASSUMED target).
- Total JS under 150 KB (ASSUMED target).
- No layout shift on load (CLS 0 target).
- First-load page weight under 500 KB per page, fonts included (ASSUMED).

## Banned list

Purple or blue-purple gradients; generic AI-looking visuals; three identical
cards in a row; fake dashboard screenshots; stock illustrations; lorem ipsum;
emoji as icons; glassmorphism everywhere; em or en dashes in any copy. Added
from the teardowns: logo strips as trust filler; bento grids; promo pills;
decorative mono labels; animated colour-cycling text; background-image charts
without text alternatives. Real screenshots only, and the product itself is
shown live from real JSON, not as a screenshot.

## Voice (all lines below are DRAFT, for the entrant to edit)

lowercase-leaning, plain, concrete, no marketing filler.

- h1 DRAFT: "an rfc lands on the right desk, or the tool says why it cannot"
- sub DRAFT: "rustbrain routes a rust rfc to the team its own files say owns it
  today, and reports a true gap when no one does. no llm, two pinned revisions,
  one graph."
- demo caption DRAFT: "live from the committed snapshot: RFC 1892, label
  T-libs-api. the team it names was archived years ago; the graph follows the
  successor edge its own file records."
- honest note DRAFT: "this demo runs from a precomputed snapshot, exported at
  build time by scripts/export_site_data.py. no server, no api key, no model."
- gaps line DRAFT: "162 merged rfcs resolve only because one curated edge
  exists. 25 have nowhere to go, and this page names them."
- footer DRAFT: "handles only. no emails, no names. the numbers are asserted in
  CI against the same snapshot this page ships."

## Hero concepts, low-fi (greybox wireframes in `hero_wireframes.html`)

A. The fold is the route. Two columns at 1440: left (about 56ch) the DRAFT h1,
one-line sub, then the real routing result block: route line plus the first five
reviewer rows with mono numerals. Right: the inline SVG graph, four Team nodes,
one successor edge labelled RFC 3984, a roster fan to named reviewers, one red
gap node. Numbers band below the fold. At 390: one column, result first, graph
after, no horizontal scroll.
B. Document artifact. The fold is the route output styled as a typeset document
with margin annotations; the graph arrives as a section of its own.
C. Graph first. A full-width SVG graph is the hero; the result table sits under
it; the claim shrinks to a kicker above.

Pick: A. It shows the real product and the real graph side by side without
scrolling, keeps the graph legible at a sane size, degrades to one column
cleanly, and needs zero JS to carry meaning. B mimics a terminal instead of
showing the product, and C turns the graph into decoration while the actual
answer (who reviews this) drops below the fold.

## The revamp, 2026-10-19: the scroll is the story of one RFC

The home page is now six scenes with a fixed scene rail: arrival (the RFC
1892 card, masked line reveals), the dead end (the pinned stage empties the
roster to zero, the naive lookup line), the hop (the SUCCEEDED_BY edge draws
itself with DrawSVG, the recorded quote lands, reviewers stagger in), the gap
(T-dev-tools, a stub line that stops), the numbers (counters to their
data.json values, three tiers on one bar denominator), and the close (what it
refuses, what it is not, the hashes). Motion tokens live once in
motion/tokens.js; scenes are separate modules with build and revert; the
whole layer is gated by gsap.matchMedia so reduced motion gets the static
final states. Pins: scenes 2 and 3 share one pinned stage (400% desktop,
scrubbed lighter without a pin on mobile); total page length measured at
7,133 px desktop, 5,339 px at 390. Palette and type are unchanged from this
file; the only new motif is the rail. Design written first in
out/revamp/20_REVAMP.md; what shipped is verified in out/revamp/30_VERIFY.md;
captures at three widths in out/revamp/review/.

The mimic pass (later on 2026-10-19) carried the staging further toward the
reference site's print language: a display Didone (Bodoni Moda, OFL,
self-hosted, licence beside the file) for headlines, counters and plates;
all-caps centered title cards; hairline ornaments with a single accent
diamond; thin outlined controls; a vignette instead of flat darkness; and a
boot cover that lifts like a curtain. Inter stays for UI, Newsreader for
body copy. The reference's own display faces (Charles Rosie, PP Nikkei Maru,
GT Era) are commercial and were neither used nor copied; Bodoni Moda is the
closest open-licence pairing that keeps the repo's OFL-only rule.
