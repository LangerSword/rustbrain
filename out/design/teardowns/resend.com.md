# resend.com teardown (design study)

2026-10-19 IST. One measured page load of https://resend.com/ (no login, no crawl) plus two local headless renders for the study screenshots. Study only.

## Compliance (verbatim)

Robots.txt (https://resend.com/robots.txt) served: 'User-agent: * / Allow: /' with 'Content-Signal: ai-train=yes, search=yes, ai-input=yes'. Terms read at https://resend.com/legal/terms-of-service (HTTP 200), which states: 'If you do not agree with or cannot comply with this Agreement, then you may not use the Service, so please read carefully.' No clause prohibiting automated access to public marketing pages was found. Observed: one page load, no login.

## Fonts and size scale

MEASURED: body `inter, ui-sans-serif, system-ui, sans-serif` 16px/400. h1 `domaine` (display serif) 96px/400, line-height 96px, tracking -0.96px. h2 `aBCFavorit` (grotesque) 56px/400, line-height 67.2px, tracking -2.8px. Paragraph 18px/400/27px, max-width 480px, margin-bottom 32px. Links and pills 14px/500, buttons 16px/600, badges 14px/400. Families loaded: inter 100-900, aBCFavorit 400/500, domaine 400, commitMono 400. Serif for the one hero line, grotesque sans elsewhere, mono for code; negative tracking grows with size (about -1 percent).

## Colour tokens and contrast ratios

MEASURED: background rgb(0,0,0), primary text rgb(240,240,240), muted text rgb(161,164,165). Only chromatic token: pale blue overlay rgba(214,235,253,0.11 to 0.19) on pills and cards, about #292D30 over black. Hero background is two full-bleed raster layers (light ray, floor), sampled average #0B060C. Accent reference: #D6EBFD, low alpha only.

Contrast, luminance helper, 2 decimals: h1 18.43, muted paragraph 8.37, Documentation link 8.37, CTA label white on its own fill 14.37, CTA fill #2A2A29 against page black 1.46, so the button reads by border and elevation rather than luminance. All text passes 4.5:1.

## Spacing scale and grid

MEASURED: sections `px-6 py-12 sm:py-24` inside `max-w-5xl md:max-w-7xl`: container 1280px, 1024px narrow, side padding 24px, vertical padding 96px. Hero padding-bottom 32px, next section margin-top 80px, hero capped near 950px with `md:h-screen`. Section heights 759, 1306, 1552, 1358, 1458, 1367, 1416px on one 96px rhythm.

## Hero pattern (first 5 seconds)

MEASURED order: badge "Join us at Resend Forward" (32px pill, gradient hairline border), h1 "Email for developers" on two lines, paragraph beginning "The best way to reach humans instead of spam folders", then "Get started" and "Documentation". Left-aligned copy column, empty right side crossed by the light ray. First viewport media: only two background layers (alt "Floor background", "Light ray background"). No screenshot, code block or product surface above the fold: one claim, one proof sentence, two exits.

## How the product is shown

MEASURED counts: 73 img, 5 video, 103 svg, 1 iframe, 0 canvas. Videos are silent looping mp4s at 170x170px, one per section heading. Headings include Integrate this morning, First-class developer experience, Test mode, Modular webhooks, Write using a delightful editor. Three 389x90 `button`s carry the 19 percent tint (Intuitive analytics, Full visibility, Domain authentication) to switch section content. Product story is small 3D loops plus wide stills, never live UI.

## Section rhythm

MEASURED section tops 575, 1334, 2640, 4191, 5550, 7007, 8374 after a 437px hero, document about 14100px. Slabs run a screen to a screen and a half tall on identical 96px padding, no full-bleed colour change.

## Navigation

MEASURED: sticky header 58px, `sticky top-0 z-40`, 200ms transition. Wide: Features, Company, Enterprise, Help, Docs, AI, Pricing, Log in, Get started. Narrow: Pricing, Log in, Get started plus "Open main menu". Links 14px/500 muted; "Log in" a 32px pill with transparent 1px border; "Get started" pill with 2px border at 5 percent white.

## CTA treatment

MEASURED hero primary "Get started": anchor 133x48px, radius 16px, padding 0 20px, label 16px/600 white, computed backgroundColor transparent with a 2px border at rgba(255,255,255,0.05), rendered fill sampled #2A2A29, a raised charcoal chip, no bright brand colour. Secondary "Documentation": 163x48px, radius 16px, padding 0 20px, 16px/600 muted rgb(161,164,165), 1px transparent border. Both share height and radius: hierarchy comes from fill, border weight and colour, not size.

## Motion

MEASURED, first 3000 elements: 2488 sampled, 141 with non-zero transition, 5 with a running animation. Motion is mostly hover colour, border and small transform. A prefers-reduced-motion rule is present. Ambient motion lives in the looping videos, not in animated sections.

## Page weight and JS size

MEASURED, Resource Timing, 141 resources: total 6312.2 KB. JS 2976.0 KB, CSS 156.0 KB, image 528.3 KB, font 624.8 KB, other 2027.1 KB (mostly mp4). TTFB 659 ms, DOMContentLoaded 1478 ms, load 7012 ms. JS is about 47 percent of bytes.

## LCP

not measurable via this API: Largest Contentful Paint returned 0 entries. Paint: first paint and first contentful paint both 1312 ms.

## Closing

Borrow:
1. Split type by role: one display serif for the single hero line, grotesque sans for headings and UI, mono for code, tracking scaled to size.
2. Calm surface, active light: near-black canvas, one full-bleed light layer, one low-alpha blue tint for interactive surfaces, no second brand colour.
3. Same-size same-radius button pair with hierarchy from fill and border weight, on a repeated 96px rhythm in a 1280px container so a very long page stays predictable.

Generic or overused:
1. Dark hero with promo pill, two-line aspirational headline, muted proof sentence and two CTAs: the default developer-tool opener, signalling category rather than product.
2. Small looping 3D mp4 clips as the only product imagery: 170px square, about 2 MB of video, no real UI in the first viewport.

Unsuitable for rustbrain: roughly 3 MB of client JS plus about 2 MB of looped video for a static story. rustbrain should ship server rendered markup and static images, keeping JS near zero until a genuinely interactive surface exists.