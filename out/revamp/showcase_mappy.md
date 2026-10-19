# showcase_mappy.md (teardown 3)

Site: https://meetmappy.com/ (mind-map product). GSAP tags: ScrollTrigger, DrawSVG, Draggable, SplitText, CustomEase.

Preflight: robots.txt says "User-agent: *" then "Allow: /" (https://meetmappy.com/robots.txt); terms page automated access line: not found (https://meetmappy.com/terms). Loads used: 2. No source or asset stored, numbers and class names only.

## why chosen
The homepage is one 9098 px scroll story inside a single map world, so its motion is geometric (connector draws, node labels, a camera), not decorative fade-ins. That is close to rustbrain, where RFC edges must draw and hold while reviewer labels stay attached.

## signature technique
Story-beat driven in-place edge draw inside a panning world. One tree (.map-viewport > .map-camera > .map-world) holds an SVG of viewBox "0 0 5600 3800"; nodes are HTML spans (.thought-node.root, .branch, .leaf) in that world, so one transform carries lines and labels together. Each connector is authored once with inline stroke-dasharray "0px, 999999px", opacity 0, visibility hidden, will-change "opacity, stroke-dashoffset" (MEASURED, 6 paths). The reveal animates dash geometry instead of redrawing, ending at "<length>px, 0.1px" (MEASURED lengths 161.257, 160.214, 138.931, 139.545, 139.545, 139.545 px, stroke rgb(194, 197, 203) at 1.5 px). Beats ride that draw: heading characters flip in one per frame, body text fades up 18 px, figures slide 96 px in at scale 0.96.

## mini motion spec
| trigger | property | from | to | duration | ease | stagger |
|---|---|---|---|---|---|---|
| beat enters view | opacity, translateY | 0, 18 px | 1, 0 px | 0.40 s DERIVED, fit 0.33 to 0.41 s (MEASURED window 0.14 to 0.99 at 16.7 ms) | out family, best fit power4.out rmse 0.008 | none seen |
| figure enters view | opacity | 0 | 1 | 0.58 s DERIVED (rmse 0.006, 31 samples) | power4.out family | none |
| figure enters view | transform x, y, scale | 96, 24 px, 0.96 | 0, 0, 1 | 0.58 s | same | mirrored pair, +96 and -96 px |
| beat heading in view | content visibility | 4 chars | 41 chars | 0.60 s for 37 units MEASURED | one unit per frame | 16.7 ms per char DERIVED |
| edge path enters beat | stroke-dasharray | 0px, 999999px | 161.257px, 0.1px and siblings | not measured | not measured | not measured |
| UI hover, press | transition-duration | n/a | n/a | 0.12 to 0.18 s MEASURED | cubic-bezier(0.23, 1, 0.32, 1) | n/a |
Not measured: edge draw duration, ease and per-path stagger (fires once per load; the recorder missed the single trigger on both loads). Also unmeasured: the camera curve and the JS reduced-motion branch.

## performance cost
- Resources (MEASURED, resource timing, 9 entries): transferSize 827,488 B, decodedBodySize 1,214,092 B. JS 168,680 B of one 506 KB decoded bundle, CSS 10,689 B, images 647,519 B in 5 files (largest 322,651 B). HTML 1,186 B, TTFB 658 ms, load 1,910 ms.
- Long tasks (MEASURED, longtask observer buffered): 105 ms near load, then 60 ms and 112 ms in the 13 s scroll sweep. No third-party requests listed.
- Layout shift (MEASURED, layout-shift observer): zero entries this session.

## accessibility failures observed
- Focus reaches invisible controls: 53 of 62 focusable elements were zero sized, hidden or opacity 0 at the sampled position (MEASURED).
- Content is animation gated: all 7 .map-chapter sections were display none at load; 341 elements at visibility hidden, 240 at opacity 0 (MEASURED at one position), so chapter copy stays outside the accessibility tree until scrolled to.
- Hidden start states are inline styles, not classes (opacity 0, visibility hidden, dash 0px, 999999px on 6 paths; opacity 0 plus 18 px offset on paragraphs and figures): with JS blocked those stay invisible (MEASURED on style attributes).
- Reduced motion: two CSS blocks force animation-duration and transition-duration to 0.001 ms on all elements (MEASURED, computed 1e-06 s under live emulation), which cannot stop inline style tweens. The bundle holds "prefers-reduced-motion" 3 times, so a JS branch exists, but whether the story honours it was not measured.
- Fine (MEASURED): zoom not blocked, skip link, lang en, no positive tabindex, focus-visible rules. Gaps: 2 icon buttons with no readable name, 4 images with empty alt.

## how it maps to rustbrain
Use one world: a single SVG for RFC edges with reviewer labels and node chips in one coordinate space under one camera transform, so lines and labels cannot drift. Copy the cheap half of their mechanic, authoring each connector once and revealing it by animating stroke-dasharray from 0 to the path's measured length on an on-enter trigger, not by redrawing geometry per frame. Adopt the measured budgets (0.40 s fade-up of 18 px, 0.58 s slide-in at 0.96 scale, one character per 16.7 ms, 0.12 to 0.18 s UI transitions) and fix their two a11y errors: keep chapter content in the DOM instead of display none behind scroll, and let a reduced-motion load paint the final state.
