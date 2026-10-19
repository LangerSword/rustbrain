Site: https://stanzza.design/ home page. Loads used: 2 (one curl HTML fetch, one instrumented browser load), analytics hosts blocked; no assets copied.
Legal: robots.txt (https://stanzza.design/robots.txt) returned HTTP 200 with a 0 byte body, so no User-agent or Disallow line exists. The terms-of-service page (Formal Notice, May 3 2026) has no crawler, bot or automated-access clause; the closest, section 5.2, only requires use "in accordance with current legislation".

## why chosen
Stanzza authors its motion in GSAP 3.15 with ScrollTrigger, SplitText, Observer and Flip registered (MEASURED), matching the rustbrain stack plugin for plugin. Its value is the trigger architecture, not the showcase tags MorphSVG and ScrollSmoother, neither of which exists at runtime (MEASURED).

## signature technique
One technique: enter-triggered multi-duration reveal stack on a Lenis-smoothed page (figures MEASURED). 27 ScrollTriggers, 0 scrubbed, 0 pinned; each fires a timeline on block entry with toggleActions play none none none, one rail reversing on exit. One timeline stacks speeds under one ease family: a background layer drifts 12 to 24 percent of its own height over 3 s, UI chrome fades over 0.5 s, spacers collapse their height over 1 s, and three tile layers scale in parallel from 0.65 to 1.5, 1.25 and 1.0 over 3 s (timeline total 3.2 s). Smoothing is Lenis 1.0.33 (lerp 0.1, smoothWheel true, smoothTouch false), not ScrollSmoother; scripted jumps stay instant.

## mini motion spec
Rows MEASURED: getComputedStyle values at forced progress 0/1; durations, eases and spans from live ScrollTrigger instances, 780x437 viewport.

| trigger (enter scroll px) | property | from | to | duration | ease | stagger |
|---|---|---|---|---|---|---|
| image layer at 278 | y, own-height percent | 0 | -12 percent (-26.25 px on a 218.72 px box) | 3 s | power3.out | none |
| section at 874 to 1158 | height | 284.05 px (65svh) and 109.25 px (25svh) | 0 px | 1 s | power3.out | none |
| section at 1530 to 2404 | scale | 0.65 | 1.5, 1.25 and 1.0 in parallel | 3 s | power3.out | none |
| rail at 8001 to 10470 | x | 0 | -56vw (-428.4 px at 765 px width) | 0.5 s | power3.out | none |
| rail text at 7936 to 10470 | color, opacity | rgb(30,30,30), 1 | rgb(196,194,183), 0 | 1 s | power3.out | none |
| block at 3077 to 3208 | opacity | 1 | 0 | 0.5 s | power3.out | none |

Ease names resolved by sampling each easing function at t = 0.1, 0.25, 0.5, 0.75, 0.9 (MEASURED): the dominant curve returned 0.271, 0.578, 0.875, 0.984, 0.999, which is power3.out; a second family returned 0.438, 0.75, 0.938, which is power2.out. Not measurable: stagger (no tween carried a stagger key; the 20 split headings hold 2 to 5 inline-block line divs each but no GSAP tween targeted them), scroll interpolation (0 scrubbed triggers), frame-level replay under reduced motion (headless rAF throttling).

## performance cost
- Document: 83 KB transfer, 329 KB decoded (MEASURED, nav timing).
- Subresources: 31 entries, 48 KB reported transfer, 169 KB decoded; 29 of 31 report 0 bytes because cross-origin CDN files send no Timing-Allow-Origin, so true weight is higher (MEASURED).
- Heaviest reported asset: swiper bundle, 44.3 KB transfer, 2043 ms load (MEASURED). Long tasks: 0 from a pre-load PerformanceObserver; cumulative layout shift 0 (MEASURED).
- Frames: 134 rAF frames in 2200 ms, mean delta 16.6 ms, max 21 ms, replaying the 3 s scale stack (MEASURED). Drivers: 186 img elements, 4 videos, 81 svg roots holding 104 paths, 323 elements with will-change (MEASURED).
- Not measurable: cross-origin bytes, LCP, paint, background-tab frames.

## accessibility failures observed
- Reduced motion: 0 rule blocks with prefers-reduced-motion across 11 scanned stylesheets, 1 blocked by CORS (MEASURED). With reduce forced, Lenis stayed smooth at lerp 0.1 and durations stayed 3 s down to 0.12 s, so no runtime gate was detected; no frame-level confirmation possible.
- Focus: 15 of 30 sampled tabbable elements showed no visible indicator (outline-style none, no box shadow) (MEASURED).
- 4 focusable links or buttons sit at computed opacity 0; 31 of 77 links have no accessible name; 186 of 186 images carry alt="" (MEASURED).
- 4 videos: no controls, no tabindex, so the keyboard cannot play or pause them (MEASURED).
- Structure: 2 h1, 0 main landmarks, 17 nav landmarks (MEASURED). Zoom passes: viewport meta is width=device-width, initial-scale=1, no maximum-scale or user-scalable (MEASURED).

## how it maps to rustbrain
Rustbrain can take the one-trigger, several-speeds pattern: one ScrollTrigger per section, graph or reviewer table, firing a leader timeline where edge drawing, row fades and counter tweens run 0.5 s to 3 s in parallel under power3.out, with 0 scrub so readers are never locked to scroll progress. Everything measured here ships with core GSAP plus ScrollTrigger, SplitText, Observer and Flip, so the MorphSVG and ScrollSmoother tags should not drive the build; Lenis at lerp 0.1 gives the smoothing feel free. Invert the accessibility findings: add a reduce branch and visible focus rings.
