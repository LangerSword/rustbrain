# Extrafazant teardown (measurement only)

Legal gate. https://www.extrafazant.nl/robots.txt serves named AI crawler blocks only, verbatim "User-agent: GPTBot" then "Disallow: /", the same pair repeated for six more AI crawlers. No "User-agent: *" rule exists, so general automated access is not disallowed; the AI crawler intent was honoured by copying nothing. Terms line about automated access: not found (/algemene-voorwaarden and /privacyverklaring fetched, no scraping or bot clause). Two page loads, analytics blocked, no asset, text or code saved.

## why chosen
A dense single page whose story is scroll triggers, SVG strokes and a smooth scroller, the same job rustbrain has to do. It is tagged ScrollTrigger, Observer, DrawSVG, SplitText, Inertia and CustomEase on the GSAP showcase, so it tests which of those actually ship.

## signature technique
Self-measuring stroke draw (GSAP DrawSVG). Each stroked path gets a dash array equal to its own runtime length instead of a hand-tuned value: three nav underline paths measure 300.207, 342.977 and 305.77 units, each carrying the matching literal "L px, 0.1px" dash array at offset 0, so a stroke always fills its own width. The same mechanic runs full screen on the page transition shape, a 1872 by 1170 SVG whose 5106 unit stroke path sits retracted at offset -5106.16 with dash array "0px, 999999px", a wipe a route change completes. Mechanics: one length query per path, split into dash and gap, animate only the offset, so one tween serves every element size.

## mini motion spec

src: M = MEASURED live, D = DERIVED

| trigger | property | from | to | duration | ease | stagger | src |
|---|---|---|---|---|---|---|---|
| ScrollTrigger on featured_title (start 1040, end 1942, toggle play) | yPercent in overflow mask | 100 | 0 | 1.07s | expo.out | 0.07s, 2 targets | M vars, from D |
| same trigger, character pass | yPercent | 100 | 0 | 1.157s | expo.out | 0.0175s, 10 targets | M |
| marquee layer .marquee-advanced__collection | x | continuous | continuous | endless | none (linear) | none | M, 48 px/s over 3 samples |
| drag or wheel layer .marquee-advanced__scroll | x | 107.163 | -144 | 0.6s | none | none | M |
| .section_featured pin over .featured_pin | pin plus scrub | scroll 1665 | scroll 3825 | scrub 0.3 | trigger-linked | n/a | M, pin-spacer offset ran 0 to -2035, pinned element held top 0 |
| .team_list, 6 triggers | scrubbed tweens | scroll 4839 | scroll 8289 | 0.6s per tween | not read | n/a | M |
| hover cursor card .cursor-marquee__card | clip-path, opacity | opacity 0, inset(50% - 3px round 600px) | 1, expanded | not measured | n/a | n/a | M static, hover unreachable headless |
| window.lenis v1.3.17 | scrollY | current | target | lerp 0.165 | lerp mode | n/a | M, smoothWheel true, wheelMultiplier 1.25 |

Not measurable: DrawSVG tween durations and eases, pointer inertia on the custom cursor (scripted pointer input did not move .cursor-marquee), FCP and LCP entries, long tasks, layout shift, and the pinned section's animated property (no change across 26 sampled descendants, scroll 2000 to 3700).

## performance cost
MEASURED on load 1, analytics blocked: 45 resources, 584,570 bytes transferSize, 10 hosts. Scripts 306,645 bytes over 20 files, stylesheet preloads 277,925 bytes over 10. Largest items: hls.js 1.6.11 at 161,336 bytes and 2,938 ms, cookie-flow 2.3.1 at 116,917 bytes and 399 ms. TTFB 594 ms, DOMContentLoaded 6,683 ms, load 7,886 ms. Page has 747 elements, 22 inline SVG, 7 videos, no canvas. Tag Manager blocked by me: entry present, 0 bytes. Long task, layout shift and paint entries empty: unmeasured, not zero.

## accessibility failures observed
1. Reduced motion ignored: with prefers-reduced-motion reduce emulated and page reloaded, the marquee still ran at 48 px/s, Lenis still smoothWheel true.
2. No visible focus indicator: focused first visible link gave outline-style none, outline-width 0px, box-shadow none.
3. Five of six buttons expose no accessible name (menu toggle, four arrow buttons, scroll to top), all type submit with no form on the page.
4. No skip link, and no nav landmark (main, header, footer exist).
5. Twenty images carry an empty alt, none is missing alt.
6. Body cursor is an SVG cursor image, and the hover gated JS cursor layer ignored scripted pointer input, so keyboard equivalence stays unverified.
Passes recorded: lang nl-NL, viewport width=device-width, initial-scale=1 with no zoom block, one h1, no aria-hidden container holds a focusable child.

## how it maps to rustbrain
RFC graph edges are stroked paths of unknown length, so the recipe transfers directly: one DrawSVG tween per edge draws by that path's own getTotalLength, the trick the nav underlines use at three widths. For reviewer tables, copy the masked reveal as measured, yPercent 100 to 0 in an overflow mask, expo.out, 1.0 to 1.16s, stagger 0.0175s on characters and 0.07s on lines, and drive animated counters from that token set. Skip the Lenis layer here: lerp 0.165 with no reduced-motion branch is the one thing this page gets wrong that rustbrain should not adopt.
