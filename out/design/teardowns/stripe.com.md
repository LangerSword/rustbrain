# stripe.com design teardown

Site: https://stripe.com (geo-redirected to https://stripe.com/in this run). Timestamp: 2026-10-19 IST. One page load, no login, study only.

## Compliance
Robots.txt (https://stripe.com/robots.txt) was fetched; it carries Sitemap entries and path-level rules for specific user agents (for example 'Sitemap: https://stripe.com/sitemap/sitemap.xml'); the homepage is not disallowed. https://stripe.com/legal is served as a client-rendered page; no prohibition on reading public marketing pages appeared in the served HTML. Observed: one page load, no login.

## Fonts and size scale
Body stack: sohne-var, "SF Pro Display", sans-serif (variable 1 to 1000). Second family: SourceCodePro 500, used only for code.
Measured at a 780x437 viewport (desktop breakpoint):
- body 16px / 400, ink rgb(6,27,49) on white
- h1 34px / 39.1px, weight 300, tracking -0.68px, max-width 679px
- h2 28px / 29.96px, weight 300, tracking -0.28px
- p 28px / 29.96px, weight 300, muted rgb(100,116,141)
- nav 18px, filled CTA 16px / 400
Pattern: big light-weight display type, negative tracking, tight 1.07 display line-height.

## Colour tokens and contrast ratios
- accent and CTA fill rgb(83,58,253) = #533AFD
- ink rgb(6,27,49) = #061B31; muted copy rgb(100,116,141) = #64748D
- secondary purple rgb(127,125,252) = #7F7DFC (most common non-neutral fill, 31 nodes)
- pale blue rgb(229,237,245), near-white rgb(248,250,253), lavender rgb(232,233,255)
- proof band rgb(13,23,56) = #0D1738
Contrast (2 decimals, computed in page): white on #533AFD = 6.19; link #533AFD on white = 6.19; muted paragraph on white = 4.75; h1 main ink span on white passes; h1 sub-copy measured 2.39 at capture (it hue-cycles, see Motion).
First filled button: bg rgb(83,58,253), white text, radius 4px, padding 15.5px 24px 16.5px.

## Spacing scale and grid
- container max-width 1266px
- 8px base: button group gap 8px, grid row gap 40px, column gutter 16px, nav gap 24px
- hero is a real CSS grid (hero-section__layout-grid), 16px gutters, not floats
- section elements measure 0px padding; rhythm sits on inner wrappers (hero title top edge 191px)
- page height 14836px at 780px wide, 15 sections: a long scroll-driven page

## Hero pattern (first 5 seconds)
First paint 836ms, TTFB 520ms. Live counter line ("Global GDP running on Stripe"), then h1: "Financial infrastructure to grow your revenue. Accept payments, offer financial services and implement custom revenue models, from your first transaction to your billionth." One filled CTA "Request an invite", a "Start now" nav CTA, abstract animated gradient wave on the right (webp fallback frame, no product shot), then the customer logo band and h2 "Flexible solutions for every business model." Promise, then proof, then depth. No product UI in the first viewport.

## How the product is shown
40 img, 190 svg, 1 canvas (300x150 default, effectively unused), 0 video, 4 iframes, no pre or code nodes. Product appears as crafted imagery, not live UI: modular-solutions-bento-card modules, a bento-terminal.png mockup, product photos (payments-electric-kettle, payments-hoodie) served as 80px thumbs inside cards. Small lazy imagery rather than heavy screenshots.

## Section rhythm
White sections dominate, broken twice: a navy stats band rgb(13,23,56) with the big numbers (135+, US$1.9tn) and a lavender bento block. Headings are short declaratives ("The backbone of global commerce", "Powering businesses of all sizes."). Thin rules and card borders divide; almost no shadows.

## Navigation
Top level Products, Solutions, Developers, Resources, Pricing, then Sign in and Start now, with Contact sales in the menu footer. Panels carry a "See all products" callout and audience entries (Stripe for enterprises / startups / platforms). Dual CTA persists in the bar.

## CTA treatment
One filled style everywhere: #533AFD, white text, 4px radius, about 16px vertical padding, no gradient, no shadow. Secondary actions are plain text or white fill with accent text ("Watch now"). Accent is reserved for action, which is why it still reads as emphasis on a 14836px page.

## Motion
Sampled 2683 elements: 701 with non-zero transition-duration, 3 running keyframe animations. The hero art animates continuously and the h1 sub-copy animates its colour (green rgb(129,184,26), 2.39 contrast, at capture). No prefers-reduced-motion rule was readable: stylesheets are cross-origin (b.stripecdn.com), cssRules inspection throws, and matchMedia reduce was false. Inconclusive, not a confirmed absence.

## Page weight and JS size
115 requests, 1407 KB transferred: JS 1159 KB, images 72 KB, fonts 70 KB, other 107 KB. CSS reported 0 KB because the cross-origin stylesheet initiator was not attributed in this snapshot; navigation document transfer was 187 KB. JS is about 82 percent of transfer: a JavaScript-heavy React/Next marketing stack.

## LCP
not measurable via this API (largest-contentful-paint returns no entries here). Paint data: first-contentful-paint 836ms, TTFB 520ms, DOMContentLoaded 1136ms, load 1140ms.

## Closing
Borrow (patterns):
1. Accent budget: one saturated accent (#533AFD) spent only on filled CTAs and links, everything else ink, near-white or pale blue.
2. Promise, proof, depth: hero states the promise with abstract art, a logo band proves adoption, bento cards show depth. First paint stays light (FCP 836ms) while the page still sells.
3. One dark band as a rhythm break: a navy section carrying three big numbers interrupts an all-white page and gives the scroll a spine.

Generic / overused:
1. Customer logo strip directly under the hero: logos as trust filler, near-universal.
2. Bento grid of feature cards with a "See all products" callout: the default shape for every 2024 onward SaaS page.

Unsuitable for rustbrain:
The hue-cycling hero paragraph. It measured 2.39:1 contrast at capture, so text fails readable contrast while still drifting, and it pays a continuous repaint cost. rustbrain is a tool surface where text must stay stable and legible: keep prose one colour and put motion in one bounded decorative element.
