# 30: stage 6 verification, measured

Method: local server (python http.server, site/), Playwright Chromium 156
headless on the RTX 5060 (ANGLE-Vulkan), CDP screencast for frames, rAF
sampler and PerformanceObserver in-page, CDP Performance metrics. Every
figure below is MEASURED on this machine unless tagged otherwise.

## 6.1 frame-level inspection

- Two scripted scrolls: desktop 1440 (454 screencast frames, median interval
  16.7 ms) and mobile 390 (414 frames, median 16.7 ms). Contact sheets
  assembled with ffmpeg, inspected with vision.
- The first desktop frame is pre-paint black (97 percent of pixels under
  luminance 40, 0.2 percent light): the black start is before first paint,
  not a flash of unstyled content. By roughly 1 second the page matches the
  verified styled hero exactly (pixel stats identical to the still capture:
  mean 26.3, 90 percent dark, 2.1 percent light).
- No clipped text, no overlapping elements and no mask artifacts at rest.
  Contact-sheet "defects" were re-checked at full size and are mid-scroll
  offsets, intended hidden states (the result box during the dead end), or
  counters mid-count. No sticky defects found.
- One vision call on a near-black thumbnail produced invented details; the
  finding was rejected after pixel-level verification. Note recorded so the
  method (pixels over prose for ambiguous frames) is explicit.

## 6.2 measurements

| figure | desktop 1440 | mobile 390 |
|---|---|---|
| rAF samples, mean interval | 704, 18.05 ms | 718, 17.40 ms |
| rAF p95 | 17 ms | 17 ms |
| frames over 25 ms | 2 of 704 (0.28%) | 2 of 718 (0.28%) |
| frames over 50 ms | 2 | 2 |
| long tasks | 1 (231 ms, at t=68 ms, bundle parse) | 0 |
| console errors | 0 | 0 |
| transfer (page total) | 283,516 B | 283,516 B |
| scroll height | 7,133 px (7.9 viewports) | 5,339 px (6.3 viewports) |

- JS weight: site/assets/motion.js is 157.6 KB raw, 61,059 bytes gzip
  (gsap 3.15.0 plus all five plugins plus the scene code); site.js is under
  2 KB. Total JS gzip is under the 200 KB budget with room; reported here as
  the shipped number.
- Counters at both widths ended at their data-final values (11 of 11), and
  no number moved during the scrolls.

## 6.3 robustness checks

- JavaScript disabled: the story, all five band numbers and "5 of 37" are in
  the HTML and readable (checked by text probe plus screenshot).
- prefers-reduced-motion: emulate reduce, reload: zero pin spacers, zero
  SplitText spans, every counter already at its final value, static layout.
- Keyboard walk: 16 stops in order (skip link first, then brand, nav, the
  scene rail, CTAs, task buttons); every stop shows a visible 2 px focus
  outline.
- Zoom: 200 percent equivalent (720x450 at deviceScaleFactor 2): no
  horizontal scroll (scrollWidth 720 equals innerWidth).
- Back button and reload: hash navigation adds history; back returns to the
  previous position; reload restores the scroll position natively
  (history.scrollRestoration "auto", y=3000 restored).
- Resize cycle 1440 to 390 and back, twice: ScrollTrigger count constant at
  10, pin spacers 1 on desktop and 0 on mobile, no growth after repeated
  resizes (no leaks across media change).
- Browsers tested: Chromium 156. Firefox and WebKit: Playwright refused to
  install them here (host requirements validation failed on this Arch
  machine), so they are NOT tested; said plainly instead of assumed.

## 6.4 design review and fixes

Skill run: design-taste-frontend (the brief's stated design review skill),
applied per scene. Five weakest items found:

1. Scene-number kickers ("scene 02, the dead end") duplicate the rail and
   read as decorative section numbering. FIXED: kickers now name the beat
   ("the dead end, then the hop.", "the gap", "the numbers").
2. A scroll cue line sat in the hero. FIXED: removed (the cue is banned by
   the review's rules and adds nothing).
3. The dead-end phase left a large empty pocket where the result box will
   later appear. FIXED: a motion-only line now explains the emptiness
   ("no reviewers to show: the archived team has none today.") and fades as
   the hop fills in.
4. Tier bars previously shared no disclosed denominator. FIXED in stage 5b:
   bars are shares of the largest tier (357), stated in the note.
5. Header nav wraps to three rows at 390 px. NOT fixed: acceptable at that
   width, labels stay whole, and the mobile read shows no overflow.

Post-push probe (the last check before wrap) caught a real defect the sheet
review had hinted at: at the end of the hop the reviewer TABLE ROWS stayed
invisible. Cause: the rows reveal was written as a from() tween whose target
had already been pre-set to opacity 0, so it animated 0 into 0 (a no-op;
gsap from() reads the current value as the end). Fixed by setting the start
state (opacity 0, y 14) once and using a to() tween to (1, 0). Re-verified at
the end of the pin at 1440, 768 and 390: rows 1,1,1,1,1, roster count 37,
result box opacity 1, timeline 3.4 of 3.4 seconds. This defect and fix ship
in the follow-up commit; blame the first pass, credit the probe.

Before and after captures: revamp_s1/s2_dead/s3_hop/s5 (before) and
revamp_s2_dead/revamp_s3_hop (after, in out/revamp/shots, gitignored).

## 6.5 automated checks

- scripts/assert_site_numbers.py: PASS. It now re-derives counter values,
  every SVG label number, tier bar widths, the font files on disk and the
  no-JS text, all from data/snapshot.json.
- Full local test script (npm test: snapshot check, verifier, README
  numbers, export check, asserts): PASS.
- Text scan of the built site: zero em or en dashes, zero lorem ipsum, zero
  distinctive strings from any reference site. The only email addresses are
  inside GSAP's mandatory @license banners (jack@greensock.com, 7 notices),
  kept because the GSAP licence forbids removing notices; no person data of
  ours exists anywhere.

## 6.6 publish

Pushed as e7bacf4. CI run 39203108492 green (30 s), Pages run 39203108605
green (14 s). Live check on https://langersword.github.io/rustbrain/ after
deploy: title and headline correct, 11 counters with correct data-final
values, motion bundle live, the successor edge caught mid-draw (dash
68.6471 px of the path, still animating), zero console errors. The reviewer
row defect above was found by the post-push probe, fixed, re-verified at
three widths and redeployed in a follow-up commit.

## 6.7 the cinematic pass (santioni feel)

The owner asked for the reference site's feel, not just its mechanics. What
changed, all inside the same constraints: every scene is now a full viewport
stage; a veil lifts off each scene as it enters (0.62 s, expo.inOut, motion
only); the hero is a title sequence that plays on load (kicker, hairline
draw, masked lines, card settle); the display scale went up (h1 to 102 px at
1440, counters to 92 px); the hop gained a scanning spark along the drawn
edge and a 1.4 s camera push on the graph; the gap got a stop pulse and a
beat of stillness; a 2 px progress hairline runs across the top; kickers and
figures carry light parallax. Reduced motion still gets the static final
states, no-JS still gets the full story, and every veil is created by the
motion bundle so it cannot hide content from a page without JavaScript.

Re-measured after the pass: 1440 mean rAF interval 17.35 ms with 2 of 744
frames over 25 ms (0.27 percent); 390 mean 16.92 ms, 2 of 750 (0.27
percent); boot long tasks 202 / 96 / 51 ms at 1440 and 106 ms at 390;
zero console errors both. Assert suite still PASS; captures re-shot at three
widths in out/revamp/review/.
