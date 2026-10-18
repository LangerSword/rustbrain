# pudding.cool (The Pudding) design teardown

MEASURED 2026-10-19 IST. Index only, 1440x900 and 390x844, local headless Chrome, no login.

## Compliance

No robots.txt is served (https://pudding.cool/robots.txt returned a 404 page). The about page (https://pudding.cool/about/) was read; it contains no clause restricting automated access to the index page. This study observed exactly one page load, no login, screenshots for study only.

## Fonts and size scale

MEASURED 3 stacks, 5 sizes. Display `"Gooper SemiCondensed", "Iowan Old Style", Times, serif`: h3 32px / 500 / line height 32px / tracking -0.8px. Body `"Atlas Grotesk", -apple-system, Helvetica, Arial, sans-serif`: p 14px / 18.55px. Labels `"Atlas Typewriter", Menlo, Consolas, Monaco, monospace`: button 12.8px uppercase. No h1 or h2 exists; headings are h3 (27) and h4. Seven font files, 420 KB; Gooper ships as .woff at 100 KB each, a Tiempos woff2 sits in no stack.

## Colour tokens and contrast ratios

MEASURED ink `rgb(38,38,38)` #262626, black #000000, grey #6D6D6D. Card block cycle: #9A4CAD, #FBCD51, #F693FF, #E68F33, #F0E4A8, #4C82B8. First coloured element in DOM order is `div.screenshot` at #9A4CAD, so accent hex #9A4CAD, cycled per story. Contrast (JS and Python luminance): ink on white 15.13, black on white 21.00, meta grey on white 5.17, black on purple 4.01, under 4.5, but that block art is raster, not DOM text. The nav pill measures 1.00 because pill shape and label sit in a sticker PNG: an artifact.

## Spacing scale and grid

MEASURED main `max-width: 1280px` centred; page 6786px at 1440, 9270px at 390. Story list is flex wrap, 30 items, 3 per row, no gap token: card 426 x 593, sub-pixel gutter, separation comes from card art. Row pitch 593px (rows at y 240, 833). Header padding 32 / 16, margin bottom 24. Sticky bar 80px, padding 16. Footer margin top 60, three columns 365 / 389, 48px gap. Spacing: 16, 24, 32, 48, 60.

## Hero pattern, first 5 seconds

MEASURED no hero headline. Header text `A digital publication that...` plus `makes cool shit on the internet`, tagline 14px Atlas Grotesk, beside a centred script wordmark drawn as a sticker and three sticker pills (about, subscribe, more). Then a search field `Find a story...` (32px, 6px radius, monospace) and six 48px filter pills. The first card row starts at y 240, so work fills the fold. Nav links: The Pudding, About, subscribe. First card titles: life after death?, mowing experiment, english vocab lists.

## How the work is shown, illustration vs screenshot

MEASURED both, split by role. Chrome is illustrated sticker PNGs with black outlines (about@2x, subscribe@2x). Content is screenshots: each card is a 394x394 block with `overflow: hidden`, framing a jpg of the story at 282x329. Counts: 60 img, 7 svg, 0 video, 0 canvas, 0 iframe. The index sells the work with proof of the work.

## Section rhythm

MEASURED one unit, twelve times: block, monospace uppercase `#225` plus `OCT 2026`, lowercase 32px serif title, 14px one line dek. Identical internals make the rhythm the 593px row and a six hue colour cycle. No heading, no grouping, no divider; the sticky bar is the only interruption.

## Navigation

MEASURED two layers: a `position: fixed` nav at z-index 1001, 900px tall, an off-canvas menu; a `position: sticky; top: 0` bar, z-index 1000, 80px, white, with search and filters. The footer carries donate, subscribe, links, merchandise.

## CTA treatment

MEASURED subscribe is the only real CTA: a header sticker pill with arrow icon and 12.8px uppercase monospace label. The footer repeats it at 365x364 beside a donate section ($2/month on Patreon). No coloured button exists in CSS: CTA colour lives in the PNG art, so the page stays two-tone ink and white.

## Motion

MEASURED restrained. Of 631 nodes, 102 carry a transition and 0 a keyframe animation. Transitions are transform only, 0.2s and 0.25s ease, on wordmark, nav and cards. One `prefers-reduced-motion` rule exists and nothing animates on load.

## Page weight and JS size

MEASURED 4778.5 KB total, 86 requests: images 4229.3 KB over 48 files (largest 2026_02_happy-map.jpg 448 KB), fonts 420 KB over 7, JS 67.1 KB over 22 files (149.4 decoded, 2 script tags, largest 14 KB), CSS 11.7 KB (43.4 decoded), document 32.6 KB (140.9 decoded). TTFB 840ms, FCP 1584ms, DOMContentLoaded 1391ms, load 2548ms.

## LCP

MEASURED 2132ms, element IMG, size 93058px, resource 2026_06_mow.jpg. `getEntriesByType` returned nothing; a buffered PerformanceObserver returned it. No LCP at 390: that run threw a client error.

## Closing

Borrow:
1. One uniform card skeleton, art as a 1:1 block with a cycled per item colour: the feed stays scannable, colour does the wayfinding.
2. A monospace uppercase microlabel pair above each title (number plus month): items read as issues and the catalogue is dated with no archive page.
3. A hard motion budget: transform only, 0.2 to 0.25s, nothing on load, one prefers-reduced-motion rule.

Generic or overused:
1. Sticker pill chrome plus full screen drawer: a 900px fixed overlay for three links is more navigation than the job needs.
2. A flat reverse chronological feed with filter chips and no grouping: pleasant to browse, costly to scan when a site has few pages.

Unsuitable for rustbrain:
Card art as story screenshots. rustbrain is a data product about Rust governance, so cards should carry live signal (RFC and tracker counts) rather than a picture of its own page. This index spends 4.2 MB on 48 images to say little.

## Failures and method notes

- The instructed binary `chromium-1243/chrome-linux64/chrome` gave no screenshot: it hung past 150s for pudding.cool and example.com across new headless, old headless, single-process and no-zygote variants. Shots came from the sibling headless_shell 1243 build.
- The cloud browser session died on a CDP device metrics call; work resumed on a local headless shell (port 9333). Two index loads occurred; all numbers come from the second, 1440x900 load.
- The 390px run logged `TypeError: Cannot read properties of undefined (reading 'slug')` yet rendered; its LCP probe was not retried.
