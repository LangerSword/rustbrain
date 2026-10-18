# The false v6.0.2 claim, and the receipt that disproved it

Captured 2026-10-19 02:38 IST, from `out/00_container_diff.md` (measured 2026-10-15)
plus the live receipt at `module_version_receipt.txt`.

## The false claim

Earlier notes, including my own `falkordb-engine-gotchas` skill, stated that
`falkordb/falkordb:latest` runs module v6.0.2 because the latest v6.x release was
v6.0.2 from 2026-10-08. The tag did not point where the release list suggested.

## The receipt

Measured 2026-10-15 against the exact image bytes (manifest-list digest
`sha256:b0bdcac2cbaff989e77cb0610439b7a9289e86de033ccbbd4368b66fb680ae7a`):

- `MODULE LIST` reports module `graph`, `ver` `42201`
- `42201` is FalkorDB v4.22.1, published 2026-10-15T06:00:43Z
- the `latest` tag was pushed 2026-10-15T06:03:59Z, three minutes later
- the embedded `REDIS_VERSION` is 8.10.2

Re-confirmed 2026-10-19 from a fresh extraction of the same digest in this repo:
`module=graph ver=42201`, `redis_version:8.10.2`.

## Why it matters for the product

The whole project is calibrated against v4.22.1, and two majors separate it from
v4.18.3 (the embedded `falkordblite` package). Anything developed against the
embedded engine can pass locally and fail for the grader. So the CI pins the image
BY DIGEST and asserts `ver == 42201` before any test runs, and the local module is
extracted from those same bytes rather than taken from a package index.

## The two newer findings that came out of the same probing

1. A pattern expression inside `CASE` is always truthy on this build, so
   `CASE WHEN (p)-[:LEAD]->(o) THEN 'lead'` labelled every member as a lead. The
   working form collects relationship types and tests with `IN`.
2. `ORDER BY` on a raw `max()` puts nulls FIRST under `DESC`, which buries the most
   recent reviewer at the bottom of the table. Both were caught by tests and are
   asserted in `scripts/test_queries.py`.
