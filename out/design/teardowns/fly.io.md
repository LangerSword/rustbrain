# Fly.io homepage teardown

Design study, 2026-10-19 IST. One page load, no login. Patterns studied, not copied.

## Compliance

Robots.txt (https://fly.io/robots.txt) served: 'User-agent: * / Content-Signal: search=yes, ai-input=yes, ai-train=yes / Allow: / / Disallow: /dashboard'. Terms read at https://fly.io/legal/terms-of-service/ (HTTP 200); no clause prohibiting automated reading of public marketing pages was found. Observed: one page load, no login.

## Fonts and size scale

MEASURED body "Fricolage Grotesque", ui-sans-serif, system-ui, sans-serif, 16px/24px weight 325. h1 Mackinac, ui-serif, Georgia, serif, 72px/68.4px weight 500, tracking -1.44px, #2e2e2e. h2 36px section titles, 16px weight 325 eyebrow. Hero paragraph 20.5px/27.675px, margin-top 16px. Buttons and nav 14.5px to 15.5px, weight 450 to 500. Mobile h1 34.71px. A warm serif carries one sentence, a very light grotesque carries everything else.

## Colour tokens and contrast ratios

MEASURED background #f4f6eb, white bands below. Text #2e2e2e, muted body rgba(40,25,80,0.75), nav #686082. Accent #7c3aed, tint #e6e0fe, tint border #d4c4fd.
MEASURED contrast: h1 on #f4f6eb 12.43:1, paragraph 12.43:1, white on #7c3aed 5.70:1, nav #686082 on white 5.86:1. All pass AA. Accent only on actions.

## Spacing scale and grid

MEASURED container max-width 1728px, content 1225px to 1377px, block layout, no CSS grid on the main column. All six sections have padding-top 0 and padding-bottom 96px; side padding 24px, 100px for inset panels. h1 margin-bottom 0px, wrapper owns the gap. Page height 7793px at 1440. One number, 96, repeated.

## Hero pattern (first 5 seconds)

OBSERVED white nav, logo left, seven links, Log In and Sign Up right.
MEASURED h1 at y=274, x=74, 137px tall, two lines: "Computers" / "for agents".
OBSERVED subcopy "Sandboxes aren't enough. Give your agent a real computer and get back to building." Primary CTA at y=514, 137 by 48px; secondary is a text link, "Onboard your agent".
OBSERVED right half: hand drawn pastel server towers with bird faces on a blue to pink to lavender gradient.
First five seconds: four words, a creature that is also a computer, one purple button.

## How the product is shown

MEASURED 27 img, 12 svg, 0 video, 0 canvas, 2 iframe, one a 1px Stripe frame. No real UI in the first viewport; the hero is a bespoke illustration, 1425 by 644 desktop, 390 by 317 mobile.
MEASURED deeper sections use tall gradient panels, 356 by 876 mobile, and stacked screenshots 356 by 1989 and 2298. Product is static screenshot stories in gradient frames, not a live demo. Section names state outcomes, the screenshot is the evidence.

## Section rhythm

MEASURED six sections, heights 146, 752, 396, 1002, 355, 1027, each closing with 96px. Order: logo strip, Sprites and Machines split, agent cloud statement, Machines detail, filesystem detail, "Nothing to Manage". Alternating density, no dividers, no bordered cards, no alternating backgrounds.

## Navigation

MEASURED white bar, 40px controls, links 14.5px weight 450 to 500: Products, Docs, Customers, Pricing, Articles, Community, Status. Products opens a mega panel of two groups, Products (Machines, Sprites, Managed Postgres) and Features (Private Networking, Autoscaling, Zero Downtime Deploys, Granular Routing, Monitoring), plus docs links. Log In is a tinted chip, Sign Up is filled accent.

## CTA treatment

MEASURED #7c3aed fill, white label, radius 8px, no shadow, no gradient, no border. 40px tall in nav, 48px in body, padding 0 20px, label 15.5px weight 450. Secondary #e6e0fe fill, #7c3aed text, 1px #d4c4fd border. "Start for Free" repeats at y=514, 2322 and later, same shape every time.

## Motion

MEASURED 105 of 525 sampled elements have a transition; 0 running CSS animations. prefers-reduced-motion query present. Hover colour only, nothing auto plays.

## Page weight and JS size

MEASURED 27 resources, 1637 KB total: JS 794 KB, CSS 288 KB, images 551 KB, fonts 0 KB in that bucket (a 143 KB woff2 reports as a link). Largest: app.js 460 KB, stripe.js 253 KB, decorative webp 351 KB, CSS 119 KB, posthog 77 KB. TTFB 598ms, DOMContentLoaded 5733ms, load 6081ms.

## LCP if measurable

MEASURED not measurable via this API, largest-contentful-paint returned no entries. Fallback first-contentful-paint 8676ms in the cloud browser, indicative only.

## Closing

Borrow:
1. Two type roles with a wide weight gap: serif at 500 for the one big claim, grotesque at 325 for everything else. Hierarchy without extra colours.
2. One accent for every action plus one tint of it for the secondary button. No grey ghost, no shadows, three colour tokens.
3. Constant 96px bottom padding, zero top, so content sets the cadence. Rhythm with no divider lines.

Generic or overused:
1. Pastel gradient hero with hand drawn anthropomorphic characters. Charming, but the default SaaS illustration look, and it needs commissioned art per section.
2. Six wordmarks as the first thing under the fold, with no numbers, quotes or outcomes.

Unsuitable for rustbrain: the illustrated character system. It needs bespoke art per section, sets a playful tone that fights a systems audience, and it justifies the 351 KB decorative webp and 460 KB app bundle ahead of the first command.
