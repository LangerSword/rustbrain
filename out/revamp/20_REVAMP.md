# 20: the revamp design, written before code

Motion explains the product. The scroll is the story of one RFC: it arrives
labelled, dies at an archived team, crosses its recorded successor edge, hits
a true gap, and ends on the numbers and the limits. Every scene shows real
data from site/data.json; motion marks the beats a reader would otherwise
have to reconstruct.

## Scenes, triggers and the data behind them

| # | scene | motion | GSAP features | pin | data fields |
|---|---|---|---|---|---|
| 1 | arrival: RFC 1892 card, label T-libs-api, tier badge | masked line reveal, badge drops last | SplitText + mask, timeline on enter | none | hero.rfc, hero.label, hero.rfc_title, hero.tier |
| 2 | dead end: naive lookup lands on archived libs-api, roster empties to 0 | stage pins; roster rows leave staggered; 0 count lands | ScrollTrigger pin, timeline, scrub 0.5 | 1.5 vh desktop | graph.chain[0] (archived), route line copy, 0 current members (derived from archived status) |
| 3 | the hop: SUCCEEDED_BY edge draws to libs, quote and source land, reviewers stagger in | edge draws (self-measuring), quote line rises, 37 rows stagger | pin, scrub 0.3, DrawSVG, SplitText, Flip (roster panel swap from empty), timeline | 2.5 vh desktop | graph.edge.from/to/rfc/quote/source, hero.reviewers order |
| 4 | the gap: T-dev-tools finds no team; the route stops | stub edge draws a third of its length and stops; space stays empty; gap label fades | DrawSVG with clamped draw, timeline | none (0.6 vh spacer holds the beat) | graph.gap.label, graph.gap.rfcs |
| 5 | the numbers: counters to final values, three tiers with scope labels | counters 1.2 s, tier bars scale, scope labels masked in | timeline on enter, counters, SplitText | none | counts.rfcs 761; gaps.distinct 357/162/25; tiers loads 138/24; labels_total 19; tier scope strings |
| 6 | honesty and close: limits, bugs page, repo | masked lines, links fade, footer hash | timeline on enter | none | generated_from.content_sha256 first 12 chars, static limits copy |

All figures above come from site/data.json at build time; the assert script
checks the final HTML, the counter end values and every SVG label against it.

## Pinned scenes and scroll length per breakpoint

- Desktop 1440: pinned scenes are 2 (1.5 viewport heights) and 3 (2.5 viewport
  heights). Total page length target 8 to 10 viewport heights (7,200 to 9,000
  px at 900 tall), ASSUMED here, measured in stage 6 and recorded.
- Mobile 390: pinned scene is 3 only (1.5 viewport heights, scrub true).
  Total 7 to 9 viewport heights (5,900 to 7,600 px at 844 tall), ASSUMED,
  measured in stage 6.
- Reduced motion: zero pins, zero scrub, static final states; a single
  opacity fade of 0.2 s at most.

## Features per scene, from the picks (10_picks.md)

Scene 3 is the spine: self-measuring stroke draw plus pin and scrub 0.3, both
re-verified on Extrafazant and mappy. Scene 2 and 5 use the Staanzza leader
timeline pattern (corrected scrub 0.8 set, multi-speed parallel). Scenes 1, 5
and 6 use masked reveals with the measured tokens (expo.out, 1.05 s lines,
0.07 s line stagger, 0.0175 s character stagger). Scene 5 counters follow the
IKEA confirmed rhythm of 1.2 s. Flip runs once, on the scene 2 to 3 roster
panel swap, so the refill is a transition instead of a hard switch. Nothing
from A24 enters the build (single-run claims, not reproduced).

## Motion tokens (one file: motion/tokens.js)

- eases: arrive = expo.out, leave = expo.in, ui = power2.out, draw = none
  (linear offset is correct for a draw)
- durations (s): reveal 1.05, quote 0.6, ui 0.18, count 1.2, rowOut 0.5,
  rowIn 0.55, drawPer100 0.35 (scaled by measured path length), fade 0.2
- staggers (s): line 0.07, char 0.0175, row 0.06, tier 0.12
- scrub: hop 0.3, deadend 0.5

These are starting values from measured references; the shipped values are
recorded in stage 6.

## Visual identity

Original, not a recolour of anything. Fonts stay Newsreader and Inter (OFL,
self-hosted). Palette evolves out/design/30_DESIGN.md: bg #14110e, surface
#1c1814, paper #f2ede4, accent #ff6a3d for the hop, tier colours unchanged
(green active, amber successor, red true gap). New structural motif: a thin
scene rail on the left with six ticks and the current scene marked, plus
scene kickers in the existing mono-label style. Full-height scenes, hairline
rules, no canvas-first layout, no full-bleed artwork, nothing that needs a
GPU to be readable. Banned list enforced (no purple gradients, no
glassmorphism, no stock illustration, no fake dashboards, no three identical
cards, no emoji, no lorem ipsum, no em or en dashes in copy).

## Hard requirements, mapped

1. Progressive enhancement: every scene is complete HTML with final numbers
   in text before any script runs; motion only swaps in enhancements.
2. prefers-reduced-motion: gsap.matchMedia gates every scene's motion; reduce
   gets final states and at most a 0.2 s opacity fade.
3. No scroll hijacking: native scroll only; anchors, back button, reload
   restore, text selection and 200 percent zoom all keep working; viewport
   meta stays width=device-width, initial-scale=1.
4. Accessibility: skip link kept; one h1 per page; visible focus (2 px
   outline token); SplitText output gets an aria-label on the parent with
   aria-hidden spans; SVG figures keep title and desc; scene headings in
   order.
5. Mobile: gsap.matchMedia 390 branch; scene 3 pin shortened to 1.5 vh,
   scrub true, staggers halved; identical content, lighter timeline.
6. Cleanup: motion/scenes/*.js each export build and revert; motion/index.js
   runs each scene inside its own gsap.context and reverts on media change
   and resize; stage 6 includes the resize leak test.
7. Performance: transform and opacity only; target JS gzip total at or under
   200 KB with the shipped number reported; no sustained dropped frames in
   the scripted scroll; measured and reported, not assumed.
8. Data integrity: scripts/assert_site_numbers.py is extended to parse the
   built HTML (no-JS state), the counter data-final attributes and every SVG
   text label; any disagreement fails CI.

## Sketches and the pick

Three greybox sketches in out/revamp/wireframes.html (one screen each, no
colour): A "report spine" (full-width scenes on a single column, scene rail
left, figures inline); B "console stage" (left number rail with the running
route state, right stage for the figure); C "split ledger" (story column left,
sticky figure column right for scenes 2 to 4). One-line reasons:

- A: reads like the printed report the concept already is, stacks cleanly to
  390 without a second design, and gives scenes 2 to 4 the full width they
  need for the graph story.
- B: the running route state is a strong idea but the number rail crowds the
  graph at 1440 and has no honest mobile form.
- C: beautiful at 1440, but a sticky figure column fights the story on
  mobile and doubles the layout code for one breakpoint.

Pick: A, with one element borrowed from B: the scene rail carries the current
route state (label, tier) as its tick annotation on desktop.

Then build without waiting: static HTML first, motion layered on top, commit
per scene.
