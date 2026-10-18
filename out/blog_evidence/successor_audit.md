# Successor map audit

Scope: data/successors.yaml against the pinned rust-lang/team tree committed under
data/upstream/team (revision a5176049c11ca092994af7a07deb4f62dfe4b55c, see PINS.md).
Every line below was re-read from the source file on disk during this audit.

## Entries (N = 4, verified = 4)

| # | from | to | source file:line | quote (verbatim) | line exists |
|---|---|---|---|---|---|
| 1 | libs-api | libs | teams/archive/libs-api.toml:1 | `# Library API has been incorporated into Library with RFC#3984` | YES |
| 2 | core | leadership-council | teams/archive/core.toml:1 | `# Core has been replaced by the leadership council with RFC#3392` | YES |
| 3 | libs-contributors | libs | teams/archive/libs-contributors.toml:1 | `# Library Contributors has been incorporated into Library with RFC#3984` | YES |
| 4 | wg-traits | types | teams/archive/wg-traits.toml:1 | `# Note: this has effectively been replaced by the types team` | YES |

Each check re-opened the file, split it into lines, and required the quoted text to be
a substring of that numbered line. The same check runs at ingest time in
scripts/build_snapshot.py load_successors(), so a reworded line fails the build.

## Completeness scan

Of the 52 archived team files, a full-file scan of comment lines for successor-like
wording (incorporat / replac / supersed / successor / moved to / merged into /
renamed) finds exactly 4 files. All 4 are in the map. No archived team with a
citable successor note is missing from the map. MEASURED at the pinned revision.

## Unmapped archived teams

Explicitly listed in successors.yaml under `unmapped`, each reported as a true gap,
never as a probable rename:

1. docs (reason: no successor note in teams/archive/docs.toml; T-doc label not mapped)
2. interim-leadership-chat (no successor note; no citable target)
3. devtools-peers (no successor note; teams/devtools.toml is a different team)

The other 45 of the 48 archived teams without a SUCCEEDED_BY edge carry no successor
note at all; none is claimed as a rename anywhere.

## The 162 figure, derived

Tier 2 of cmd/gaps.py output, MEASURED with the committed snapshot loaded:

    TIER 2: ARCHIVED WITH A NAMED SUCCESSOR (2 labels, 162 distinct RFCs)
      libs-api   138  archived  libs
      core        24  archived  leadership-council

Derivation chain: successors.yaml entry (line-verified above) -> snapshot
successor_map edge -> :SUCCEEDED_BY edge in FalkorDB -> tier 2 in gaps.py.
libs-api = 138 merged RFCs, core = 24, overlap = 0, union = 162 distinct merged
RFCs. Only these two T-* labels resolve to archived teams with a verified successor
edge; libs-contributors and wg-traits are in the map but no RFC carries those labels.
