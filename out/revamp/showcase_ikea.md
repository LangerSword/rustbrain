# IKEA "Desmontando los 30" - measurement-only teardown

Loaded: https://www.family.ikea.es/desmontando-los-30/ (2 loads, second with reduced-motion emulated), 780x437 headless Chromium. The /demos/ path from the brief is Basic-auth guarded (401, realm "Demos home"); no credentials used. robots.txt (https://www.family.ikea.es/robots.txt): "User-agent: *" then an empty "Disallow:" (nothing disallowed); header x-robots-tag: none. Terms: no automated-access line found (automat*, robot*, scrap*: zero hits); they forbid reproducing content, so this file keeps measurements only (timings, roles, fonts, bytes). Figures MEASURED unless tagged.

## why chosen

The page is a full-height snap-scroll deck of chapters, the same reading pattern rustbrain needs for a long RFC narrative. Its ambient motion is CSS-only transform loops with measured uneven timing, a cheap alternative to one long timeline.

## signature technique

Desynchronised ambient drift layers. Four or more decorative layers each run their own long keyframe loop over transform only (one over background-position): 16 s, 17 s, 18.25 s, 19 s, with start delays of 0.6 s and 1.1 s, so no two loops re-synchronise and the composite never visibly repeats. Each loop steps through 9 to 11 stops with small offsets (up to 14 px, 1.3 deg, 2 percent scale). Mechanics: pure CSS, ease-in-out infinite, stagger via animation-delay, no per-frame JS, no animation library.

## mini motion spec

| trigger | property | from | to | duration | ease | stagger |
|---|---|---|---|---|---|---|
| page load, infinite | transform scale, 3 loader dots | scale(1) | scale(0.5) at 33.3 %, back at 66.7 % | 1200 ms | linear | 200 ms (delays 0 / 200 / 400) |
| page load, infinite | transform translate + rotate, float layer 1 | translate(0,0) rotate(-0.8deg) | translateY(-14px) rotate(0.9deg) at mid | 17 s | ease-in-out | none |
| page load, infinite | transform translate, float layer 2 | translate(0,0) | translate(2px,-13px) at 40 % | 18.25 s | ease-in-out | 0.6 s delay |
| page load, infinite | transform translateY + scale, float layer 3 | translateY(0) scale(1) | translateY(-11px) scale(1.02) at 50 % | 19 s | ease-in-out | 1.1 s delay |
| hover on room hotspot | transform + opacity (ring) | scale(0) translateY(-15 %) | scale(1.3), opacity 0 | 2 s | ease-in-out | restarts per hover |
| overlay fade (live) | opacity | 0 | 1 | 150 ms | cubic-bezier(0.33, 1, 0.68, 1) | none |

Method: getAnimations() timing plus keyframes, cross-checked against CSSOM; the hover row is CSSOM only (no live instance). Also measured, trimmed for the cap: counter float 3.9 s ease-in-out (translateY 0 to -2.5px, rotate -0.55deg); room panel transition 1 s cubic-bezier(0.175, 0.885, 0.32, 1.275), 0.3 s child.

Could not be measured: the chapter choreography (scrub, pinning, crossfades, reveal stagger). The intro video gate never cleared: both WebM sources stayed at readyState 0 / networkState 2 with no error, the counter froze at 0 %, the smooth-scroll root stayed stopped, and scroll clamped at 0 (scrollHeight 851 px vs clientHeight 350 px) even after load fired at 7260 ms. Scroll timings are unknown, not zero.

## performance cost

transferSize sums: 549356 B over 50 entries, then 921374 B over 73 at settle (scripts 644353 B / 22, link 261335 B / 33). Document 7579 B; TTFB 199 ms, DOMContentLoaded 1872 ms, load 7260 ms. Fonts: 2 woff2, 59016 + 57796 = 116812 B, 21.3 % of first-load transfer (DERIVED); NotoIKEALatin 400 and 700. intro.webm 2938493 B by HEAD (never buffered, excluded); master30.webm also referenced. Long tasks: buffered observer 0 entries; buffered layout-shift summed 0.0000 (headless, one run). Five infinite loops run from load before any input.

## accessibility failures observed

- prefers-reduced-motion: only 3 blocks exist (gradient layer, float layers, scroll arrow). Loader dot pulse, both counter float layers and the hover ring pulse are uncovered; with reduce emulated the 3 loader-dot animations still ran and snap stayed y mandatory.
- 2 autoplay looping videos with no controls, no track and no aria-label; one is not muted.
- 7 buttons and the header logo link expose no accessible name.
- The 0 % progress counter has no role and no aria-live, so progress is never announced.
- No skip affordance for the locked intro; when the video stalls the page is unusable and scroll is clamped.
- viewport meta allows zoom (width=device-width, initial-scale=1), listed for completeness.

## how it maps to rustbrain

Give each decorative SVG layer of the RFC graph its own GSAP tween with a distinct long duration (roughly 17 / 18.25 / 19 s) and a staggered delay, so background motion never pulses in unison; one timeline would re-sync. Reuse the measured loader pattern for the animated counters (1200 ms linear scale loop, 200 ms delay steps) but gate it behind gsap.matchMedia() for reduced motion, which this reference fails to do, and reserve ScrollTrigger for real beats such as DrawSVG paths and SplitText headers. Avoid the reference's locked-scroll gate: rustbrain should render content even if media fails to load.
