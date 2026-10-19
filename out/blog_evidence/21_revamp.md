# 21: the revamp, as blog evidence rows

Rows for the blog: what was learned, what was refused, what was measured, and
what the licence says. Everything here points at a receipt in the repo.

## What the reference sites did that was worth learning

| source | what they did | what we took |
|---|---|---|
| santionispirits.com | wheel beats drive discrete scene transitions; scenes hold nearly still between beats; short bursts (0.18 to 0.52 s) read as expensive; the age gate fades out over a measured ~0.87 s after a ~430 ms delay | the beat model: quick, discrete transitions with still holds; the fade timing influenced our UI tokens |
| Extrafazant | self-measuring SVG strokes: dash array equals the path's own runtime length (300.207, 342.977, 305.77 units), only the offset animates; pin 1665 to 3825 with scrub 0.3 | DrawSVG with one getTotalLength per path; scrub 0.3 as the hop token; flip nothing over a hand-tuned dash value |
| mappy | one world coordinate space for SVG edges and HTML labels under one camera; edges authored once with dash hidden, revealed by animating stroke-dasharray; 0.40 s fade-ups on a power-out family | single coordinate space for the graph figure; on-enter draws, never per-frame redraws |
| Staanzza | one trigger per section fires a timeline where several speeds run in parallel (0.5 s fades, 1 s collapses, 3 s pushes); 26 ScrollTriggers; Flip, Observer, SplitText registered live | the leader-timeline pattern per scene, and the Flip use on the result panel |
| IKEA demo | desynchronised ambient loops (16 s to 19 s) so nothing re-syncs; loader rhythm 1.2 s linear with 0 / 200 / 400 ms delays | the counter rhythm (1.2 s), read live as a token; the ambient loops themselves were rejected as decoration |
| A24 (Raviklaassens) | pin 2160 px, 32 s marquee tween, 450 ms dot curve: all single-run claims | nothing shipped from A24: two re-verification sessions could not reproduce the pin or marquee (document measured 900 px with one trivial trigger); recorded as evidence that the verification step matters |

## What we refused to copy

- The zoom-blocking viewport meta, verbatim from santionispirits.com
  (user-scalable=no). Our meta is width=device-width, initial-scale=1.
- Their display fonts (Charles Rosie, PP Nikkei Maru, GT Era: commercial).
  We paired an OFL Didone instead (Bodoni Moda, self-hosted, licence beside
  the file) and kept Inter plus Newsreader.
- Their age-gate pattern itself. We open with a title card, not a legal
  wall; nothing blocks reading.
- Zero reduced-motion handling (santioni: zero references in the bundle;
  Staanzza: zero rule blocks; Extrafazant kept its marquee running under
  reduce). Ours gates everything through gsap.matchMedia; reduce gets the
  static final states.
- Keyboard dead ends (santioni: 14 Tab presses stayed on body). Ours: 16
  stops, all with a visible 2 px focus ring, skip link first.
- No-JS emptiness (santioni: "Please enable javascript"). Ours: full story
  and every final number are in the HTML.
- The GPU blocklist gate that sends software renderers to an unsupported
  page. Ours renders for every renderer; motion degrades, content never.
- Scroll smoothing layers (Lenis at 0.1 to 0.165, ScrollSmoother). We kept
  native scroll: anchors, back button, reload restore and 200 percent zoom
  all verified working.

## Measured frame-drop numbers, before and after

- Reference measure (santionispirits.com, their budget, our machine, RTX
  5060): worst long task 361 ms during boot; 8 boot-side long tasks total;
  steady state ~60 fps. This is the bar the reference sets.
- rustbrain revamp, scripted full-page scroll, desktop 1440: 2 frames over
  25 ms out of 704 rAF samples (0.28 percent), 2 over 50 ms, one boot long
  task (231 ms, bundle parse at t=68 ms), zero console errors.
- rustbrain revamp, mobile 390: 2 of 718 samples over 25 ms (0.28 percent),
  zero long tasks, zero errors.
- After the design review fixes and the reviewer-row fix, the same scroll
  discipline was re-probed end to end at three widths with all counters,
  rows and the drawn edge landing at their final states; no sustained drops
  in any run. Post-fix run: 1440 mean rAF interval 18.29 ms with 2 of 712
  frames over 25 ms (0.28 percent) and two boot long tasks (296 ms, 70 ms);
  390 mean 17.04 ms with 1 of 750 over 25 ms (0.13 percent) and one 89 ms
  boot task; zero console errors in both. JS shipped: 61,059 bytes gzip
  total (gsap plus scenes).

## GSAP licence finding

The standard "no charge" licence (gsap.com/licensing, fetched 2026-10-19)
covers all plugins for this use: "All of GSAP including the plugins that
were formerly members-only like SplitText and MorphSVG can be used in
commercial projects at no charge." Conditions kept: copyright notices stay
in the bundle (esbuild legalComments inline; 7 @license banners), no visual
animation builder product, no reverse engineering for competitive products.
Full quotes and the per-plugin mapping: out/revamp/01_legal_and_licence.md.

## Defects found in the first QA pass, and the fixes

1. Reviewer table rows never faded in (a from() tween into a pre-set zero is
   a no-op). Fixed with set-then-to; re-verified at 1440, 768, 390 and on
   the live URL.
2. Self-hosted fonts 404ed on every page (fonts.css referenced paths
   relative to itself). Fixed; now asserted by the number script.
3. favicon 404 on all five pages. Fixed with an inline data icon.
4. Tier bars compared on an undisclosed denominator. Fixed to shares of the
   largest tier, asserted in CI.
5. Scene-number kickers and a hero scroll cue matched the generic AI pattern
   list. Rewritten and removed.
6. The dead-end phase left an unexplained void. A motion-only line now names
   the state; it fades as the hop fills in.
