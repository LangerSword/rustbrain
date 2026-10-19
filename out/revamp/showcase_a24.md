# A24 clone teardown (motion only)

Site https://a24.raviklaassens.com/ | loads 2 of 2 | 1440x900 emulated, analytics blocked pre navigation.
Robots (https://a24.raviklaassens.com/robots.txt): "User-agent: *" / "Allow: /"
Terms on automated access: not found; no legal route served (9 probed paths all 404), sitemap lists content routes only.
Tags: M1 observer on style writes, M2 live GSAP read, CSS computed style, D derived.

## why chosen
GSAP 3.15 runs live with ScrollTrigger, Observer, InertiaPlugin and CustomEase, so scroll mechanics read off real instances rather than eyeballed frames, and the media wall sits on a Webflow fallback layout, the same fallback pressure a static rustbrain build faces. Flip and Draggable were not registered and no flip marker existed in the DOM (M2).

## signature technique
Scrub linked pinned stage with depth handoff. ScrollTrigger pins div.featured_pin for 2160 px of scroll (start 1665, end 3825, pinSpacing true, M2). Its 3 slides advance by stepping the pin body translateY 0 to 2160 px as one discrete jump per index (M1, sampled every 260 px, exact pixel unresolved between 3780 and 4040). The outgoing slide leaves translate3d(0, -40px, -120px) at opacity 1 to translate(0, 810px) at opacity 0 (M1). A ring rotates 2.9 deg at scrollY 1700 to 180 deg at 4040 (M1; D 7.6 deg per 100 px). Scroll position is the timeline, no per frame ease; samples plateau, so scrub catch up not 1:1 (D, low confidence).

## mini motion spec
| trigger | property | from | to | duration | ease | stagger |
|---|---|---|---|---|---|---|
| scroll in once (M1) | transform + opacity, button wrap | translate3d(0, 22.01px, 0), op 0.083 | translate3d(0, 0, 0), op 1 | 799 ms | not measured, no ease token in inline writes | n/a |
| scroll in once (M1) | transform, masked line and char reveal | translate(0%, 128.6%) line, translate(0%, 131.3%) char | translate(0px, 0) | 1066 ms line window, 1366 ms char window (1385 writes) | not measured | not measured, no replay on second pass |
| loop (M2) plus net (M1, D) | xPercent, marquee | translateX(-94.16%) | translateX(-19.66%) | 32 s tween, 9263 ms window | linear "none"; constant rate assumed, a wrap breaks it | 74.5% of 1536 px = 1144 px, 123 px/s; 2nd window 112 px/s |
| scroll scrub (M1) | transform 3D + opacity, featured slide | translate3d(0, -40px, -120px), op 1 | translate(0, 810px), op 0 | pin range 2160 px | scroll position | n/a |
| hover (CSS) | rotate + scale, button dots | declared | hover | 450 ms | cubic-bezier(0.32, 0.72, 0, 1) | 32 ms, delays 0/0.032/0.064 s |
Also measured: cursor text strip 10 s linear infinite (M2); icon scale 750 ms linear() spring peak 1.1424 (M1).
Not measurable: GSAP ease shapes (CustomEase instances are anonymous), cursor follow lag (0 px box, no transform under synthetic pointer moves, headless), per char stagger.

## performance cost
Resource timing, 22 entries (M2): transferSize sums to 16291 B only, 21 of 22 report 0 (cache, opaque cross origin), so read encoded body: 760093 B total, script 429823 B in 8 files, css 86186 B in 2, fonts 228093 B in 3; document 7813 B body. Nav responseEnd 110 ms, DOMContentLoaded 149 ms, load 174 ms; LCP 504 ms on an image; CLS 1.97 summed; long tasks: one buffered entry, 65 ms at 310 ms (document start injection threw, may undercount). 627 DOM nodes; 53 images, image bytes not measurable (cross origin, 0 sizes).

## accessibility failures observed
1. Reduced motion: of 38 stylesheets only 2 @media (prefers-reduced-motion) blocks exist, both scoped to (hover: hover) and (pointer: fine), both targeting hover and focus selectors on two buttons; nothing guards reveals, the pinned scrub or the marquee, and under emulated reduce both translateXCursor animations still ran (M2).
2. Focus: the second Tab stop, the header logo anchor, computed outline none 0px and no box shadow, so no visible indicator; the first Tab stop, a cookie banner close button, did show a 2 px solid outline (M2).
3. The first focusable element is a cookie banner dismissal control, ahead of the site nav (M2).
4. No aria live region (0 elements) while the pinned stage swaps 3 slides and a trailer lightbox exists (M2 count; D that changes go unannounced).
5. Zoom meta width=device-width, initial-scale=1 with no user-scalable=no passes; also 0 missing alt on 53 images, 0 positive tabindex, 0 focusables in aria-hidden.

## how it maps to rustbrain
Pin the SVG graph with one ScrollTrigger and let scroll drive routing order, one team per index step, the outgoing node receding in Z (measured -120 px) and fading, so graph, reviewer table and counters share one stage. Drive counters and the RFC ticker from one long linear xPercent tween (measured 32 s) instead of a JS interval loop, and reuse the measured curves for small state changes: 450 ms cubic-bezier(0.32, 0.72, 0, 1) with 32 ms per dot delay, 525 ms overshoot curve for arrows. Add the reduced motion guard the reference lacks, covering reveals, the scrub and the ticker.
