# Reference sites, final list (Part 2.2)

Checked, not assumed: every candidate was loaded and its robots.txt and terms page
read before selection. Method: one page load per site, no login, no crawling, no
mass downloads; screenshots and notes only.

## The eight

| # | site | why it is in |
|---|---|---|
| 1 | linear.app | the reference dark editorial product site; strong type and product framing |
| 2 | vercel.com | large developer platform; disciplined monochrome plus one accent |
| 3 | stripe.com | the classic of docs-adjacent marketing; gradient-free sections, real UI |
| 4 | resend.com | minimal single-purpose product page, useful restraint check |
| 5 | supabase.com | docs plus product hybrid; open-source-native visual language |
| 6 | fly.io | replacement for observablehq.com; distinct voice and illustration style among dev tools |
| 7 | pudding.cool | data journalism (non dev-tool): narrative-driven data presentation |
| 8 | informationisbeautiful.net | data visualisation (non dev-tool): long-lived editorial index |

## Swaps and skips, with the evidence

- observablehq.com: skipped. https://observablehq.com/robots.txt served a bot wall
  (a "Vercel Security Checkpoint" page, not a robots file); automated access is
  effectively blocked. Replaced by fly.io.
- raycast.com: skipped. Its terms of service at https://raycast.com/terms-of-service
  state: "In connection with your use of the Service you will not engage in or use
  any data mining, robots, scraping or similar data gathering or extraction
  methods." No automated access was performed.
- arc.net: allowed (robots.txt permits everything except /api/redirect-links/link/*,
  loads HTTP 200) but not selected; the dev-tool side is held at six sites and
  fly.io takes the open slot.

## Pairing note

Six developer-product sites plus two editorial or data-journalism sites, so the
synthesis cannot collapse into one SaaS landing-page shape. The two editorial
sites are also where the data-presentation patterns for a "data product about
governance" are most likely to come from.
