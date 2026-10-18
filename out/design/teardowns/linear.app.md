# linear.app design teardown (study)

MEASURED 2026-10-19 IST. Method: one local headless Chromium page load at 1440x900 and 390x844 (screenshots) plus computed-style and DOM probes on one cloud browser page load at 1440x900; no login. Read patterns, reuse nothing.

## Compliance
Robots.txt (https://linear.app/robots.txt) served: 'User-Agent: * / Disallow: /api/ / Disallow: /cdn-cgi/ / Allow: /api/og/'. Terms of use read at https://linear.app/terms (HTTP 200); no clause prohibiting automated access was found in the served document. Observed: one page load for this study, no login.

## Fonts and size scale (MEASURED)
- Body stack: "Inter Variable", "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif; self-hosted variable woff2 in resource timing.
- h1 64px / lh 64px / weight 510 / ls -1.408px at 1440; 56px / 61.6px / 510 / -1.232px at 780px.
- h2 40px / 44px / 510 / -0.88px. h3 20px / 26.6px / 590 / -0.24px.
- p 15px / 24px / 400 / -0.165px. Nav and button labels 13px / 510.
- Pattern: mid weights (510) not bold, negative tracking scaling with size, h1 line-height equal to its size.

## Colour tokens and contrast ratios (MEASURED)
- bg #08090A; primary #F7F8F8; secondary #8A8F98; tertiary #D0D6E0; light pill #E5E5E6; accent #5E6AD2; lime #E4F222 (one quote card).
- Contrast (WCAG formula, computed in JS): #F7F8F8 on #08090A 18.73; #8A8F98 on #08090A 6.13; #D0D6E0 on #08090A 13.64; #08090A on #E5E5E6 15.83; white on #5E6AD2 4.70; #5E6AD2 on #08090A 4.24, so the accent is a surface colour, not small type.
- Hierarchy comes from three grey tiers, not hue.

## Spacing scale and grid (MEASURED)
- main is display flex / column, padding 72px 0 0, no max-width; homepage root container max-width 1436px; hero spans near full bleed (widths 1425 to 1466).
- h1 margin 0; sub-paragraph block margined 31px above.
- Four product sections: padding 128px top and bottom, no variation. Header fixed, 73px, 1px bottom border rgba(255,255,255,0.08).
- Values seen (8, 16, 20, 31, 72, 128, 224) suggest an 8px base; inferred, not proven.

## Hero pattern (first 5 seconds)
- Fixed blurred bar, 9 targets, one light pill CTA right.
- Single h1 at 64px, two lines, top y=272 of 900.
- Under it one 15px grey line plus a small announcement link to its right.
- At y=485 a 1440x810 product capture starts, so headline and product UI share the first screen.
- No illustration, no gradient mesh: black surface, one line of text, then the product.

## How the product is shown (MEASURED)
- DOM media: 39 img, 0 video, 0 canvas, 0 picture, 231 svg.
- Hero is a real UI capture (sidebar, issue with activity feed, reviews panel, floating agent panel) in a wrapper div (class ...shade hide-laptop), image loading=lazy.
- Later sections use inline SVG and CSS chrome (window frame, gradient shade) plus real avatars (14px rendered, 144px natural).

## Section rhythm (MEASURED)
- Product sections 1226, 1229, 1232, 1220px tall at y 2546, 3782, 5021, 6263, each padded 128px top and bottom; then a 564px block, then a prefooter with 224px margins.
- Height 10175px at 780px viewport; homepage root 9394px at 1440.
- Alternation never varies: text, product visual, text, product visual.

## Navigation (MEASURED)
- Fixed header, transparent, backdrop-filter blur(20px), hairline border.
- 9 top bar targets: brand mark, Product, Resources (buttons), Customers, Pricing, Now, Contact (links, 13px), Log in, Sign up.
- All on one row at 780px; the 390px capture was not probed for its menu, so nothing is claimed there.

## CTA treatment (MEASURED)
- "Sign up": radius 9999px, height 32, padding 0 12px, 13px / 510, bg #E5E5E6, text #08090A, 1px border same colour.
- "Log in": transparent bg, #8A8F98 text, same pill.
- Closing "Get started": same pill, larger (44px, 127px wide).
- One shape and one colour family for every action; #5E6AD2 only on utility surfaces such as the skip link.

## Motion (MEASURED)
- First 3000 elements: 87 with a non-zero transition, 153 with a running animation.
- Samples: border-color and background 0.1s cubic-bezier(0.25, 0.46, 0.45, 0.94); colour and background 0.1s, same easing.
- prefers-reduced-motion: 8 matching media queries across 66 stylesheets; 48 were cross-origin and unreadable, so 8 is a lower bound.

## Page weight and JS size (MEASURED, partial)
- Document 168 KB transfer, 1228 KB decoded (navigation timing at 1440x900); 250 resource entries, 195 with .js in the URL.
- Only 5 of 250 entries exposed transferSize; 245 reported 0 because cross-origin responses carry no Timing-Allow-Origin here, so JS and CSS byte totals are not measurable this way.
- Timings at 1440x900: TTFB 676ms, DOMContentLoaded 942ms, load 1298ms.

## LCP (MEASURED)
- getEntriesByType('largest-contentful-paint') returned an empty list; a buffered PerformanceObserver attached after load reported 1268, 2488 and 2656ms. Final 2656ms, approximate because of the late attach.

## Closing
Borrow as patterns:
1. Three grey text tiers on one near-black surface (#F7F8F8, #8A8F98, #D0D6E0) build hierarchy with no extra hue, and the accent stays a surface colour.
2. Proof in the first viewport: hero copy stops near 60 percent of the fold and a real product capture starts inside it.
3. One geometry for every action: a single pill at 32px and 44px plus a transparent variant.

Generic or overused:
1. The fixed blurred top bar with a hairline border is the default of every developer tool site and differentiates nothing.
2. Four identical 128px padded blocks alternating text and screenshot: legible with the images removed, so the rhythm carries no meaning.

Would not suit rustbrain:
- Uniform glossy black with low chrome works only because the product shot is bright and dense. rustbrain is a data product about Rust team governance with a dark editorial bent, so it needs visible structure (rules, texture, type contrast) in the dark; flat black would deaden long form reading.
