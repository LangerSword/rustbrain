# 40: the revamp, delivered (stage 7 summary)

Everything below points at a receipt. The numbers are in
out/revamp/30_VERIFY.md and out/blog_evidence/21_revamp.md.

## What changed

- site/index.html: rebuilt as six scenes, static first, every final number in
  the no-JS HTML.
- site/assets/site.css: scene layout, rail, tier bars, masks; tokens from
  out/design/30_DESIGN.md unchanged.
- site/assets/site.js: render() returns a promise and window.RB is exposed so
  the motion layer can wrap the demo swap; without GSAP it is the whole demo.
- motion/: tokens.js, scenes (arrival, route, gap, numbers, close),
  index.js with gsap.matchMedia gating, debug.js registry;
  scripts/build_motion.mjs bundles it to site/assets/motion.js (gsap 3.15.0,
  pinned; licence banners kept).
- site/debug/index.html: scrub every ScrollTrigger and every scene timeline.
- scripts/assert_site_numbers.py: extended to re-derive counter values, SVG
  label numbers, tier bar widths, font files and the no-JS text from the
  snapshot; CI fails on any disagreement.
- site/assets/fonts.css: font files now resolve (they 404ed on every page
  before this).
- README.md, docs/DEMO.md, out/design/30_DESIGN.md: revamp sections added.
- out/revamp/: this file set (skills, licence, teardown, picks, design,
  verify, review captures with captions).

## Measured performance (all MEASURED, this machine)

- Frame cadence during scripted full-page scroll: 1440: 2 of 712 samples over
  25 ms (0.28 percent); 390: 1 of 750 over 25 ms (0.13 percent); no sustained
  drops, zero console errors.
- Long tasks: boot only (worst 296 ms, bundle parse); none during scroll.
- JS: 61,059 bytes gzip total; page transfer 283,516 bytes with fonts.
- Page length: 7,133 px at 1440 (7.9 viewports), 5,339 px at 390.
- Reduced motion: zero pinned triggers, static final states, verified.
- Live: https://langersword.github.io/rustbrain/ (edge draws itself, 11
  counters exact, zero console errors).

## Defects found in the first QA pass and how each was fixed

1. Reviewer rows never revealed (from() into a pre-set zero). Fixed and
   re-verified at three widths and live.
2. Fonts 404 on all pages. Fixed; asserted by the number script now.
3. favicon 404 everywhere. Fixed with an inline data icon.
4. Tier bars on an undisclosed denominator. Fixed; asserted.
5. Scene-number kickers and a scroll cue (generic AI pattern list).
   Rewritten and removed.
6. Dead-end void unexplained. Motion-only state line added.

## Not done, stated plainly

- Firefox and WebKit: not tested. Playwright refused to install them on this
  machine (host requirements validation failed); Chromium 156 carried every
  measurement above.
- Header nav wraps to three rows at 390 px; accepted, labels stay whole.
- Audio: no audio on the site (out of scope for this brief).
- A24 showcase numbers: rejected after failed re-verification; nothing from
  it shipped.
- REA evidence is session-scoped (its evidence ids live in REA's own store);
  the structural findings are reproduced in teardown files with methods.

## Related work in this repo at the same time

A parallel workstream produced the three-minute demo video (video/ tooling,
out/video/ renders and QA) and the concise STE-100 README; those files are
not this brief's and were left to that workstream, except the short revamp
sections appended to README and docs/DEMO.md.
