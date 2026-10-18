# Information is Beautiful: design teardown
MEASURED 2026-10-19 IST. One load of https://informationisbeautiful.net/ in headless Chrome at 1440x900 and 390x844; DOM probes at a 1440 viewport. No redirect (redirectCount 0, final host informationisbeautiful.net).

## Compliance
Robots.txt (https://informationisbeautiful.net/robots.txt) served: 'User-agent: * / Disallow: /home-new' plus explicit Allow: / blocks for GPTBot, ChatGPT-User, OAI-SearchBot and ClaudeBot. The about page (https://informationisbeautiful.net/about/) was read; it contains no clause restricting automated access to the index page. Observed: one page load, no login, screenshots for study only.

## Fonts and size scale
- Headings: Quicksand, 600 to 700. Hero h2 32px/35.2, promo h2 36px/39.6, card h2 21px/26.67, sub h3 20px/22.
- Body and UI: IBM Plex Sans, 400. p 16px/24, nav 14 to 15px, button 16px.
- MEASURED 0 h1 and 14 h2: the mission line is the top h2, not an h1. Body default is font-family sans-serif at 16px.
- Scale in use: 15, 16, 18.72 (h3 default), 20, 21, 28, 32, 36. No weight above 700.

## Colour tokens and contrast ratios
MEASURED pairs (WCAG ratio):
- ink #4F4F56 on base #F9F9F9: 7.72:1 (mission, card titles)
- nav #2A2A2E on #FFFFFF: 14.29:1
- accent pink #F06292 on #F9F9F9: 2.90:1 (inline mission links)
- muted paragraph #BDBDBD on #F9F9F9: 1.78:1 (footer note)
- surfaces: base #F9F9F9, cards #FAFAFA, chips and promo base #EEEEEE
- promo gradient #D14980 to #F0C33D (to left); event chips #FDD835 with #333333 text
Pink marks links and single words, never body copy; at 2.90:1 it fails AA for small text.

## Spacing scale and grid
- Body max-width 2600px. Hero inner container 864px wide with 32px padding (800px text column), display flex.
- Main grid: display grid, 3 columns of 436.33px, gap 28px, total 1365px.
- MEASURED section boxes: hero 194px, promo 240px, filters 114px, grid 1322px, bottom promo 96px. Every section padding is 0; only the bottom promo has margin-top 36px.
- Rhythm comes from full-bleed band heights and inner spacing, not section padding. Chips use 12px padding and 0 radius; cards use 0 0 2px 2px radius and a 0 2px 2px rgba(0,0,0,0.1) shadow.

## Hero pattern (first 5 seconds)
1. White header: flower mark plus lowercase wordmark left, 8 small dark nav links, search, SUBSCRIBE.
2. Centred two line mission h2 at 32px, with pink inline links inside the sentence.
3. A full-bleed gradient band directly below: white h2 "Learn to create impactful infographics & data visuals", one white subline, five small yellow event chips.
4. "Stories about" filter row, then the top edge of the 3 column card grid about 620px down.
No hero image, no h1, no carousel. Type and one gradient do the work.

## How the work is shown
- MEASURED 12 card thumbnails are CSS background-image PNGs at 1030x520; the DOM has 3 img elements (SVG logos), 0 svg, 0 canvas, 0 video, 0 iframe.
- Charts on the index are flat raster crops: 2:1 decorative art, not live charts, nothing to hover. Interactivity sits behind the card link.
- Card anatomy: image band, 21px Quicksand title, no byline or date in the visible grid probe.

## Section rhythm
White hero (194) -> gradient promo (240) -> white filters (114) -> long white grid (1322) -> grey promo strip (96). One colour interruption per screen, then a long editorial run. Cards repeat at a fixed 3 up cadence with 28px gutters.

## Navigation
Header row: About, Workshops, Books, Work, Store, Blog, More, SUBSCRIBE. The menu panel adds Home, Data, Contact, Search and social links (Facebook, Twitter, Instagram, Threads, RSS). Links are small, sentence case, dark, no underline; the only filled header control is the grey SUBSCRIBE button. At 765px the row collapses to a "Menu" button.

## CTA treatment
- SUBSCRIBE: #EEEEEE ground, #2A2A2E text, 16px, 0 radius, asymmetric padding 12px 12px 12px 24px, envelope icon.
- Workshop chips: #FDD835 ground, #333 text, 15px/700, 3px 7px padding, 2px radius. They read as event tags, not buttons.
- Filters: #EEEEEE chips, lowercase, 16px/400, 12px padding, square corners.
No large primary button; the gradient band itself is the CTA.

## Motion
MEASURED 39 of 447 sampled elements have a transition, 0 have an animation. Durations are 0.1s and 0.2s. Hover and menu states only, no scroll effects. No prefers-reduced-motion rule in the stylesheets and the media query did not match. Weakness: the site ignores the user motion preference even though motion is minimal.

## Page weight and JS size
MEASURED 25 resource requests. 22 returned zero transferSize (cross-origin or cached), so total weight is not measurable via this API. Measurable only: document 6.2KB, manifest 0.5KB, favicon 1.1KB, analytics pixel 0.3KB, about 8.2KB combined; that is a lower bound, not page weight.
JS: 1 script, main.min.js, size not measurable (reported 0). CSS: 1 stylesheet, style.min.css, size not measurable.
Navigation timing: TTFB 1024ms, DOMContentLoaded 2472ms, load 2777ms.

## LCP
MEASURED 12220ms, element DIV, image SM-IIB-AI-Suing-Featured-1030x520-1.png, captured with a buffered PerformanceObserver after load. Cloud browser and cold cache inflate it; read as an upper bound, not a field score.

## Closing
Borrow (3):
1. Type-only hero: one sentence at 32px, two lines, accent words as inline links. No image, fast first paint.
2. One gradient band as the only loud surface, carrying the single commercial message and small event chips.
3. Fixed 3 up card grid with 28px gutters and 2:1 crops, so a long index scans like a contact sheet.

Generic (2):
1. Eleven lowercase filter chips: tag soup that pushes the first card below the fold.
2. The same newsletter ask at top (SUBSCRIBE) and bottom (promo strip).

Unsuitable for rustbrain:
The background-image card art. It has no alt text, no srcset and no lazy loading semantics, and the chart pixels are not text. rustbrain routes RFCs to teams and must show names, counts, dates and gap tiers that users can read, copy and filter; raster art would hide the data and fail accessibility. Use DOM text and inline SVG for any graph.
