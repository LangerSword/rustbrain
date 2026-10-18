# Site measurements (Part 6.2), measured 2026-10-19 on the deployed site

## Page weight, measured with curl (size over the wire, brotli or gzip)

Per page: html + fonts.css + site.css + site.js + both woff2 fonts.

| page | wire bytes | note |
|---|---|---|
| / | 113,277 | index.html plus the four shared assets |
| /graph/ | 112,701 | |
| /gaps/ | 112,210 | |
| /method/ | 113,241 | |
| /bugs/ | 112,536 | |
| /data.json | 2,611 | fetched only when the demo tabs are used |

The two self-hosted fonts are about 105 KB of that total (woff2 is already
compressed). JS is one file, `site.js`: 3,909 raw bytes, well under the 150 KB
budget (2.6 percent of it).

## Timings in the harness browser (1440x900, cold-ish cache)

| page | DOMContentLoaded | load |
|---|---|---|
| / | 171 ms | 301 ms |
| /graph/ | 596 ms | 617 ms |
| /gaps/ | 178 ms | 197 ms |
| /method/ | 49 ms | 67 ms |
| /bugs/ | 409 ms | 428 ms |

## Largest Contentful Paint

Not measurable in this environment: `performance.getEntriesByType('largest-contentful-paint')`
returned empty even with a buffered PerformanceObserver registered before
navigation. The same limitation hit all eight teardown recordings, so it is the
harness, not the site. The load events above are the honest substitute; the
ASSUMED target of LCP under 2.5 s remains unverified rather than claimed.

## Contrast ratios, computed from the live rendered colours

| pair | ratio | token in the brief |
|---|---|---|
| body text on background | 16.13 | 16.13 |
| h1 on background | 16.13 | 16.13 |
| sub text on background | 10.45 | 10.45 |
| nav link on background | 16.13 | n/a (paper) |
| button label on accent fill | 6.61 | 6.61 |
| demo note on background | 5.37 | 5.37 |

Every pair passes WCAG AA; the live values match the design brief exactly.

## Console errors

Zero. Two checks: a chrome pass over all five pages with `--enable-logging=stderr`
produced no error or console lines, and in-page `error` and `unhandledrejection`
listeners recorded nothing during the full interaction pass.

## Keyboard-only walkthrough (home, first nine tab stops)

skip to content, rustbrain (brand), home, how the graph works, gaps, method and
limits, bugs i found, hero primary button, hero ghost button; focus then moves
into the demo tabs. No traps, no hidden stops, and `:focus-visible` is styled.

## Reduced motion

With `prefers-reduced-motion: reduce` emulated: `matchMedia` matches, and the
button transition computes to `1e-05s` (the 0.01ms rule). The demo result fade is
skipped in JS when reduce is set.

## Interaction

Clicking the T-dev-tools tab renders the true-gap block; switching back to
libs-api renders the RFC block again, from `data.json` fetched at that moment.
No server, no API key, no model.

## Layout shift

Not measured: no layout-shift observer is shipped and none can be retrofitted
into the harness pages. Stated as not measured rather than claimed at zero.
