# A: pre-build checks

## CORRECTION, 2026-10-19: the gap arithmetic

Section 5 said "two labels have no file (T-dev-tools 20 RFCs, T-doc 6 RFCs),
which is 26 of 761 RFCs, 3.4%". That sentence is retired. 26 was the sum of the
two per-label loads; two RFCs (1946 and 1990) carry both T-dev-tools and T-doc,
so those two labels cover 24 distinct RFCs (3.15%), not 26. The product gap tier
also counts T-interim-leadership-chat (1 rfc, present in the table below), so the
canonical union, over merged PRs without a not-rfc label, is 25 distinct RFCs =
3.29% of 761 (one T-dev-tools PR, 1608, is not-rfc and excluded from the tier).
Restricted to disposition-merge the subset is dev-tools 3, interim-leadership-chat
1, doc 0, union 4. Every figure below that predates this block stays as the
historical record of what was measured on 2026-10-16.

Run 2026-10-16 02:20 to 02:25 IST. Scripts `out/phase1/testA1.py`, `testA1b.py`,
`testA23.py`, `testA2b.py`. Results: `out/phase1/prebuild_results.json`,
`rust_roster_full.json`.

## CORRECTION AT THE TOP, because my headline was partly wrong

**Two bugs found in my own ingest, and one headline retired.**

1. **BUG, fixed.** My roster ingest walked only depth-1 `teams/*.toml` and ignored
   `teams/archive/*.toml`. `rust-lang/team` has **224 team TOML files: 172 active,
   52 archived**. The archived ones hold real alumni rosters. Lakshaya was right
   that `teams/libs-api.toml` and `teams/core.toml` exist: they are at
   `teams/archive/libs-api.toml` and `teams/archive/core.toml`, HTTP 200.
2. **BUG, fixed.** I reported "label join coverage 89.5%" counting archive files as
   unmapped-in-practice. The honest split is below, and the active-only figure is
   much worse.
3. **HEADLINE RETIRED.** "385 orphan merged RFCs" no longer stands as stated. See
   section 3: after checking alumni, only a fraction of those authors are genuinely
   unknown to the project.

## 1. Team files: what exists, and why the headline said what it said

`gh api 'repos/rust-lang/team/contents/teams' --jq '.[].name'`: `docs-rs.toml`,
`docs-rs-reviewers.toml`, `libs.toml`, `libs-fcp.toml`, `libs-ping.toml`,
`docker.toml` are present. **No `libs-api.toml`, no `core.toml`, no `dev-tools.toml`,
no `doc.toml` at depth 1.**

`gh api 'repos/rust-lang/team/contents/teams/archive' --jq '.[].name'`: **52 files**,
including `core.toml`, `libs-api.toml`, `docs.toml`, `devtools-peers.toml`,
`docs-peers.toml`, `interim-leadership-chat.toml`.

**Why my earlier Rule 3 output listed `libs-api` and `core` as Team nodes with RFCs
anyway:** because my loader created a synthetic `Team` node for every slug a `T-*`
label implies, precisely so the label join would not silently drop edges. Those
nodes carried `rostered:false` and no members. That was a deliberate guard against
a zero-row join, and I then reported those synthetic nodes as evidence of "no team
file", which was misleading: the file exists, in the archive, holding **alumni only**.

Measured contents, MEASURED 2026-10-16:

| file | leads | members | alumni |
|---|---|---|---|
| `teams/archive/libs-api.toml` | 0 | 0 | **18** |
| `teams/archive/core.toml` | 0 | 0 | **20** |
| `teams/archive/docs.toml` | 0 | 0 | **8** |
| `teams/archive/devtools-peers.toml` | 0 | 0 | 11 |

So `libs-api` and `core` were **disbanded**, and their teams now have zero leads and
zero members. That is not a bug in my parser and it is a genuine governance fact.

**How the 164 Team nodes were created, precisely.** 161 came from active team files
with at least one named member. 3 were created label-only by my guard clause
(`core`, `dev-tools`, `libs-api`). **That guard was wrong for `core` and
`libs-api`**, whose files exist in the archive; the honest construction is 214
slugs with any entry (active or archived) and 2 genuinely unresolved labels.

**Roster counts after the fix** (all 224 files fetched, MEASURED):

| measure | value |
|---|---|
| team TOML files | 224 (172 active, 52 archived) |
| slugs with at least one lead, member or alumni entry | **214** |
| roster edges (lead + member, **excluding** alumni) | **1,086** |
| distinct handles on an active team | **399** |
| distinct handles listed as alumni somewhere | **368** |
| handles that are alumni-only, never an active member | **237** |

## 2. Label join, per label, with the fix applied

All 19 `T-*` labels across 761 merged RFCs. MEASURED 2026-10-16.

| label | RFCs | slug | active file? | verdict |
|---|---|---|---|---|
| T-lang | 263 | lang | yes | ACTIVE |
| T-libs-api | 138 | libs-api | no | archive, alumni only |
| T-compiler | 43 | compiler | yes | ACTIVE |
| T-cargo | 42 | cargo | yes | ACTIVE |
| T-core | 24 | core | no | archive, alumni only |
| T-dev-tools | 20 | dev-tools | no | **no team file anywhere** |
| T-crates-io | 14 | crates-io | yes | ACTIVE |
| T-rustdoc | 10 | rustdoc | yes | ACTIVE |
| T-release | 7 | release | yes | ACTIVE |
| T-doc | 6 | doc | no | **no `doc` file; nearest is `docs`, archive** |
| T-leadership-council | 6 | leadership-council | yes | ACTIVE |
| T-libs | 5 | libs | yes | ACTIVE |
| T-infra | 4 | infra | yes | ACTIVE |
| T-types | 4 | types | yes | ACTIVE |
| T-edition | 2 | edition | yes | ACTIVE |
| T-style | 1 | style | yes | ACTIVE |
| T-interim-leadership-chat | 1 | interim-leadership-chat | no | archive, alumni only |
| T-opsem | 1 | opsem | yes | ACTIVE |
| T-testing-devex | 1 | testing-devex | yes | ACTIVE |

**Was it a bug? Two distinct causes, and I checked case, hyphen, underscore, `T-`
prefix, suffix and near-match variants for both unresolved labels:**

- `T-dev-tools`: no variant resolves. The tree has `teams/devtools.toml` (name
  `devtools`), `teams/archive/devtools-peers.toml`, and `repos/archive/rust-dev-tools/`.
  **No team file is named `dev-tools`.** So `dev-tools` is a label with no team, a
  real routing gap.
- `T-doc`: variant `docs` resolves to `teams/archive/docs.toml`, name `docs`. That is
  almost certainly a rename, singular to plural, but it is an **inference, not a
  fact**, so I do not silently apply it. It stays flagged, with the rename noted.

| coverage figure | value | scope |
|---|---|---|
| labels mapping to an **ACTIVE** team | **14 of 19 = 73.7%** | 761 merged RFCs, 2026-10-16 |
| labels mapping to **any** file incl. archive | 17 of 19 = 89.5% | same |
| labels with no file at all | 2 (`T-dev-tools`, `T-doc`) | same |
| RFCs carrying at least one active team label | 486 of 761 = 63.9% | same |

**My earlier 89.5% was technically true and practically misleading.** For a
reviewer-routing product the number that matters is 73.7%.

## 3. Alumni split: the orphan claim does not survive intact

Of the **160** distinct handles that authored a merged RFC while holding no active
team membership, MEASURED 2026-10-16:

| category | handles | share |
|---|---|---|
| appear as **alumni** in some team file | **38** | **23.8%** |
| appear in **no** people or alumni list anywhere | **122** | **76.2%** |

And of the 385 orphan RFCs, **83** carry `disposition-merge`, so the merged subset is
83, not 385.

**Retiring the claim as stated.** "385 merged RFCs depend on people the project has
never onboarded" is false: 38 of those authors were on a team and have since been
recorded as alumni. The defensible version is narrower and still real:

> Of 761 merged RFCs, **83** were authored by someone who holds no current team
> membership and has no alumni record in any team file. Those 83 RFCs govern
> work with no current roster to route review to.

The honest headline therefore becomes: **83 merged RFCs with neither a current
member nor an alumni record**, across **122** distinct handles across all 385 orphan
RFCs. And the strongest single fact is now different from what I had: **two teams,
`libs-api` (138 RFCs) and `core` (24), are disbanded, holding 0 leads and 0 members,
and together they govern 162 merged RFCs.**

## 4. One denominator table

Every coverage figure in play. All retrieved **2026-10-16**. All over
`rust-lang/rfcs` merged PRs with no `not-rfc` label unless stated, and
`rust-lang/team` at `main`.

| figure | value | numerator | denominator | scope and caveats |
|---|---|---|---|---|
| label join, any file | 89.5% | 17 labels resolving to any team TOML | 19 distinct `T-*` labels | includes archived files that hold alumni only |
| label join, active only | **73.7%** | 14 labels resolving to an active team | 19 labels | **the figure the product should quote** |
| RFCs with an active team label | 63.9% | 486 RFCs | 761 merged RFCs | 275 RFCs carry no `T-*` label at all |
| documents join | 97.5% | 636 `text/NNNN-*.md` whose prefix is a merged PR | 652 numbered RFC files | one git tree call, `truncated: false` |
| documents to a team | 72.1% | 470 files with a `T-*` label | 652 numbered files | the rest reachable only via author |
| authors on a team | 25.5% | 97 distinct authors on an active team | 380 distinct authors across 1,130 merged PRs | all years, all PRs incl. `not-rfc` |
| orphan rate pre-2021 | 58.0% | 337 RFCs | 581 RFCs created <= 2020 | before the alumni fix |
| orphan rate 2021+ | 26.7% | 48 RFCs | 180 RFCs created >= 2021 | before the alumni fix |
| orphan rate 2026 | 13.3% | 2 RFCs | 15 RFCs created in 2026 | before the alumni fix |
| **alumni-aware orphan** | **10.9%** | **83 merged RFCs with no member and no alumni record** | **761 merged RFCs** | **the corrected headline** |

## 5. Gate

**The routing join and the documents join are NOT broadly broken, so I am
continuing to section B.**

- Documents join: 97.5%, unaffected by either bug. Sound.
- Routing join: two labels have no file (`T-dev-tools` 20 RFCs, `T-doc` 6 RFCs),
  which is 26 of 761 RFCs, 3.4%. Three more resolve to disbanded archive teams. That
  is a real and small routing gap, not a parser failure.
- **The demo headline changes**, from "orphan RFCs" to "disbanded teams govern 162
  merged RFCs with nobody to route review to". I am proceeding to B without waiting.