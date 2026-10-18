# vercel.com teardown

Design study, 2026-10-19 IST. One page load, 1440x900 and 390x844, no login.

## Compliance

Robots.txt (https://vercel.com/robots.txt) served: 'User-Agent: * / Content-Signal: search=yes, ai-input=yes, ai-train=no / Allow: /api/og/* / Disallow: /api/ / Disallow: /oauth' (excerpt; the homepage is not disallowed; note the ai-train=no signal was recorded and no model training is involved in this study). Terms read at https://vercel.com/legal/acceptable-use-policy (HTTP 200), which states: 'This Acceptable Use Policy ("Policy") applies to all customers' and their users' use of services provided by Vercel Inc.' No clause prohibiting automated reading of public marketing pages was found. Observed: one page load, no login.

## Fonts and size scale (MEASURED)

- Body: GeistSans, "GeistSans Fallback", 16px/24, weight 400.
- Mono contexts: "Geist Mono", ui-monospace fallback, 16px/24 (used for small labels and kickers).
- h1: 64px/64 (line ratio 1.0), weight 400, letter-spacing -3.84px (-0.06em).
- h2: 56px/56, weight 450, letter-spacing -3.36px.
- Scale in use: 64, 56, 24, 22, 20, 18, 16, 14, 12 px.
- Nav and small buttons 14px/500. Hero CTAs 16px/500.
- The tight negative tracking is what makes a 64px sans read as a poster instead of a blog heading.

## Colour tokens and contrast (MEASURED)

- Canvas #FAFAFA, ink #171717, secondary #4D4D4D, surface #FFFFFF, hairline #EBEBEB, focus blue #0072F5.
- The CTA accent is ink, not a hue. The only chromatic token observed was the focus/skip-link blue.
- Ratios: ink on canvas 17.18:1; white on ink 17.93:1; secondary on canvas 8.10:1; blue on canvas 4.26:1 (fine for large text and UI, misses 4.5 for body copy).

## Spacing scale and grid (MEASURED)

- Page container max-width 1448px, display flex, padding 0 24px, so a 1400px content column at 1440.
- Section padding resolves to 0px at section level. Vertical rhythm is carried by fixed-height wrapper blocks, so no 4/8 step padding scale is readable there.
- Readable gaps: h1 block bottom 456 to CTA top 488 is 32px. Container gutter 24px.
- Hero geometry: h1 at x24 y328, 349 wide, 128 tall (two lines). CTA 124x40 at y488.

## Hero pattern (first 5 seconds)

- The whole first screen is one poster. "Agentic Infrastructure" sits low left in a 349px column at 64px, while a large canvas artwork (454x381 at x -32 y -5, bleeding past the container edge) holds the top left. A short vertical link list (Backends, Agents, Enterprise) sits right.
- Two doors under the headline: "Deploy now" filled, "Talk to sales" outlined, plus a mono kicker line.
- In 5 seconds you get a name, a claim, two doors and one artwork. No dashboard, no code block, no feature grid above the fold.
- The fold line then closes on a monochrome customer logo strip.

## How the product is shown

- 15 img, 52 svg, 1 canvas, 0 video. In the first viewport only the canvas exceeds 120x80, so no real product screenshot appears above the fold.
- Evidence order is artwork first, customer logos second, app imagery later down the page.
- Trade-off: strong brand recall, weak answer to "what does the tool actually look like" for a first time visitor.

## Section rhythm

- Document height 5323px. Bands: hero 64 to 900 (836 tall), logo band ending 1108, product band 1108 to 3461 (2353), then bands at 3669 (718) and 3806 (580).
- Effective band pitch about 868px. No rules, no alternating background colours: separation comes from content density alone.

## Navigation

- Desktop nav: Products, Resources, Enterprise, Pricing. Right cluster: Get a Demo, Log In, Sign Up.
- Chrome buttons are 32px tall, 6px radius, 14px/500. Hero CTAs are 40px tall and fully pill.
- Two radius systems on purpose: compact 6px utility chrome, pill for the marketing decision.

## CTA treatment

- Primary: ink fill, white label, pill, 40px tall, 16px/500, 12px side padding.
- Secondary: white fill, ink label, 1px hairline, same pill.
- "Sign Up" is the only ink button in the header, which makes it the loudest element before the hero.

## Motion (MEASURED)

- 1139 elements sampled: 143 carry a non-zero transition, 3 carry a running animation. Durations cluster at 0.1, 0.15, 0.2, 0.3 and 0.5s.
- A prefers-reduced-motion media query is present in the stylesheets (6 sheets scanned, 0 blocked by CORS). The CSS layer respects the preference.

## Page weight and JS size (MEASURED)

- 154 resources. Total transfer 2756.8 KB: JS 2180.9 KB (79 percent), CSS 171.4 KB, fonts 221.9 KB, images 1.4 KB, other 181.1 KB.
- 16 resources reported transferSize 0 (cached or opaque), so the real total is slightly higher.
- Timing: TTFB 266 ms, DOMContentLoaded 1202 ms, load 7364 ms.

## LCP (MEASURED)

- PerformanceObserver with buffered entries: 15648 ms, element H1, size 51303. That lands far past the load event, so it describes a cold lab session with heavy JS, not a field number. Read it as "slow in this lab", not as Vercel's real user LCP.

## Closing

Borrow (patterns):

1. Poster hero: one 64px claim in a narrow left column, one artwork bleeding off the grid, two doors. Nothing else on the first screen.
2. Two radius systems: 6px for product chrome, pill for the two marketing choices. It separates "tool" from "decision" without spending colour.
3. Contrast by typography: a 9 step scale from 12 to 64 with -0.06em tracking at display sizes, and a 17:1 ink on off white base that needs no accent hue.

Generic or overused:

1. A monochrome strip of enterprise customer logos directly under the hero. Every infrastructure vendor ships this band.
2. Mono type for small labels and micro CTAs. It signals "developer" cheaply and is now the default move.

Unsuitable for rustbrain (dark editorial data product):

- The canvas led, screenshot free hero depends on a bespoke 3D artwork plus a 2.1 MB JS bundle to carry the first screen. A dark editorial data product needs its first screen to be readable data, not a rendered brand object, and cannot spend 79 percent of its weight on client JS.
