# Self-critique (Part 6.3): five weakest things, three fixed, before and after

## The five weakest things found

1. **The real result sat below the fold.** The chosen concept says the fold shows
   the route and the graph together; the built page had the result block one
   section lower. Weakest thing on the site, because it undercut the one idea the
   hero exists to carry.
2. **Mobile nav tap targets were short.** At 390 the nav wrapped to two lines with
   small targets; usable, but below the standard the rest of the page holds.
3. **The reviewer roster did not name its parent.** Five named people under the
   chain could be read as belonging to the archived team; the columns needed a
   "libs roster" attribution.
4. **LCP and CLS are unverified.** The harness cannot measure LCP and no layout
   shift observer exists; the targets are labeled ASSUMED in the brief and remain
   unverified rather than claimed.
5. **The stats band is text-light on mobile.** At 390 the five stats stack into
   two columns of small labels; readable, but the least confident typography on
   the site.

## Fixed in the Part 6.3 commit (the top three)

1. The routing result block now sits inside the hero column, directly under the
   demo tabs; at 1440 the reviewer rows enter the first viewport beside the graph.
   Before: `shots/home_1440.png`. After: `shots/after_home_1440.png`.
2. Nav links get 6px vertical padding and 15px type at 700px and below.
   Before: `shots/home_390.png`. After: `shots/after_home_390.png`.
3. The figure caption now reads "libs roster: 5 of 37 reviewers, sorted by latest
   authored RFC", naming the parent team.

Items 4 and 5 stand as recorded weaknesses; 4 cannot be honestly fixed in this
environment, and 5 is a judgment call left to the entrant.

## Banned-list check against the built site

| banned | status |
|---|---|
| purple or blue-purple gradients | none; one accent (#ff6a3d) on a warm near-black |
| generic AI visuals | none; no raster images at all |
| three identical cards in a row | none; lists and tables instead |
| fake dashboard screenshots | none; the product is shown live from real JSON |
| stock illustrations | none |
| lorem ipsum | grep: 0 |
| emoji as icons | none |
| glassmorphism | none; solid surfaces and hairlines |
| em or en dashes | grep over site/: 0 |
| (added) logo strips, bento grids, promo pills, decorative mono, colour-cycling text | none; the demo pills and mono labels are functional |

## Against the teardown notes

The site borrows the economy the teardowns measured (one accent, three grey
tiers, type-led hierarchy), shows its numbers as text the way the two editorial
sites do, and ships 3.9 KB of JS against the 1.2 to 3.0 MB the developer sites
measured. It keeps none of the generic devices (logo strip, bento default,
promo pill, hero gradient art) that the synthesis lists as overused.
