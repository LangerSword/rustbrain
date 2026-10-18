# supabase.com design teardown (school design study, learn patterns only)

Date: 2026-10-19 IST. One page load, no login, 1440x900 and 390x844 shots plus DOM probes.

## Compliance block

Robots.txt (https://supabase.com/robots.txt) served: 'User-agent: * / Allow: /' plus explicit Allow: / blocks for GPTBot, ClaudeBot, Google-Extended and PerplexityBot; 'Content-Signal: ai-train=yes, search=yes, ai-input=yes'. Terms read at https://supabase.com/terms (HTTP 200), which states: 'IF YOU DO NOT ACCEPT THESE TERMS, YOU MAY NOT ACCESS OR USE THE SERVICES.' No clause restricting automated reading of public marketing pages was found. Observed: one page load, no login.

## Fonts and size scale (MEASURED)

Body: Inter plus system fallbacks, base 16px. Headline face: Manrope.
- h1 46px / 500 / line-height 46px / tracking normal / margin-bottom 0px, inside a 536px grid column.
- Hero paragraph 14px / 500 / line-height 19.25px. Section headings 34px / 600. Bento card titles (h2) 16px / 600. Card body 14px / 500. CTA label 14px / 500. Nav link 14px / 500, nav small CTA 12px / 500.
Inference: one display face for headlines, one UI face for the rest, 1.0 line-height on h1, no negative tracking.

## Colour tokens and contrast ratios (MEASURED)

- Background oklch(0.995 0 337.5), pixel-verified #fdfdfd.
- Ink oklch(0.1 0 337.5) = #030303. Hairline borders: same ink at 8 percent alpha.
- Accent / filled CTA oklch(0.525 0.12 157.5), pixel-verified #117f50 (deep green). Logo bolt reads brighter green in the shot.
- CTA label #fafcfb.
- Contrast via JS luminance helper: h1 on background 20.30, body paragraph 5.42, link on background 20.59, CTA label on CTA fill 4.94.

## Spacing scale and grid (MEASURED)

Container max-width 1280px (most common in DOM). Hero is CSS grid, template 536px 536px. Radii cluster 8, 10.67, 16, 21.33px, pills fully round. Nav band 65px. Sections carry pt/pb 0; block heights 270 to 949px. Document height 7691px, no sideways overflow.

## Hero pattern (first 5 seconds, MEASURED)

Nav bar, then two columns: left, "Build in a weekend" in ink over "Scale to millions" in accent; right, muted 14px paragraph naming the product surface. Under the headline, filled accent CTA "Start your project" plus outlined "Request a demo", then a bento grid begins in the first viewport (Postgres, Auth, Edge Functions visible, four cards cut at the fold). At 390 wide: same order, hamburger nav, buttons side by side, first three cards visible.

## How the product is shown (MEASURED)

No hero photo, no video, no canvas (video 0, canvas 0, iframe src empty). Counts: 147 img incl srcset variants, 146 svg, 2 pre, 2 code. Product appears as light-mode SVG mock UI inside cards: auth rows, a code pill ($ supabase functions deploy), a globe of nodes. Later: dashboard block, React guide, starter kits, customer logos, community posts, open source stats. Product chrome is illustrated, never a live screenshot.

## Section rhythm (MEASURED)

Nine main sections, stacked with no gaps: hero 949px, logo strip 270px, dashboard 862px, React 696px, starters 898px, customers 812px, community 909px, open source 373px, final CTA 375px. Each opens with a 34px / 600 heading then a card grid; hairlines, not shadows, split zones.

## Navigation (MEASURED)

One 65px bar on a sticky wrapper (div.sticky top-0 z-40), near-white, 1px bottom hairline. Order: Skip to content, Product, Developers, Solutions, Pricing, Docs, Blog, 111.6K (GitHub stars), Sign in, Start your project. Three dropdowns, three links, one proof number, one small filled CTA. Mobile: logo plus hamburger.

## CTA treatment (MEASURED)

Primary: accent fill, #fafcfb label, radius 9.29px, padding 8px 16px, 14px / 500, 38px tall, no border. Secondary: white fill, ink label, 1px 8 percent border, same geometry. Nav variant: radius 8px, padding 4px 10px, 12px, 26px tall. The pair repeats at 6429px as the closing CTA. Two weights, one accent, zero gradients.

## Motion (MEASURED)

First 3000 elements: 1511 have a non-zero transition duration, 15 run named animations (card micro motion). A prefers-reduced-motion query exists in CSS, not active by default.

## Page weight and JS size (MEASURED)

109 resource entries. Total transferSize 459.2 KB: document 92.8 KB, link-initiated (CSS, fonts, preloads) 428.7 KB, images 11.6 KB, fetch 16 KB. File counts: 56 js, 4 css, 3 woff2, 20 svg. JS size is not measurable via this API: every .js entry reported transferSize 0 (cached at read time, cross-origin sizes withheld). Cached encoded sums: jpeg 195.5 KB, jpg 165.3 KB. Timings: TTFB 181 ms, DOMContentLoaded 1031 ms, load 1639 ms.

## LCP (MEASURED)

LCP 816 ms, element a text SPAN (entry size 24822 px2), equal to first contentful paint 816 ms; first paint 692 ms. LCP is text; homepage JPEGs sit mostly below the fold.

## Closing

Borrow (3 patterns):
1. Two-column hero copy pair: big claim left, muted 14px product surface list right, CTAs under the claim. Promise plus inventory in one look.
2. Bento cards whose art is abstract mock UI in accent plus grays: features explained without shots of a live app.
3. Token discipline: one accent, 8 percent hairlines, a small radius set, two font roles. It looks built, not decorated.

Generic / overused (2):
1. "Trusted by fast-growing companies worldwide" logo strip. Every devtool ships one and it reads as filler.
2. GitHub star count in the nav ("111.6K") as proof. Cheap to copy, dates fast.

Unsuitable for rustbrain (1):
The light near-white surface with hairlines and bright SVG mock UI. If rustbrain serves systems or CLI users, that illustration-heavy bento sells the wrong texture; a code-first surface would be honest.

Failures: local headless Chrome wrote no PNG with --virtual-time-budget and a fresh --user-data-dir; --timeout=15000 worked; a section-padding probe returned 0px (padding lives on inner wrappers) so block heights were used; one js() probe failed with a SyntaxError and was rewritten; the first LCP fetch was empty so a buffered PerformanceObserver was used; JS transfer size not measurable, see above.
