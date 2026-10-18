# Pinned upstream revisions

**generated, do not edit.** Source of truth: `scripts/build_snapshot.py`.
Regenerate with `python3 cmd/refresh.py --pin`.

Every number this project reports is derived from these revisions. Change them
deliberately, never implicitly.

| source | revision | retrieved | note |
|---|---|---|---|
| github.com/rust-lang/team | a5176049c11ca092994af7a07deb4f62dfe4b55c | 2026-10-19 | committer date 2026-10-18T11:10:22Z |
| github.com/rust-lang/rfcs | d2705ad64ba47e812a2b6b19d6f613fb4c14c5e0 | 2026-10-16 | committer date 2026-10-05T10:04:13Z |
| docker.io/falkordb/falkordb | sha256:b0bdcac2cbaff989e77cb0610439b7a9289e86de033ccbbd4368b66fb680ae7a | 2026-10-16 | amd64 manifest-list digest, module reports ver 42201 (v4.22.1) |

## Data policy

Public GitHub data only. The product's stores hold handles only: no real names, no
email addresses, no avatar URLs, no RFC bodies. RFC titles are truncated to 120
characters. The pinned team tree is committed under data/upstream/team so CI needs
no network; it mirrors public rust-lang/team files (scripts/fetch_upstream.py
re-fetches the teams/, people/ and repos/ TOMLs at the pinned SHA), including the
fields upstream itself publishes. CI reads the committed tree plus data/snapshot.json.
