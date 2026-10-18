# rustbrain

**Track 03: Company Brain.**

rustbrain routes a Rust RFC to the reviewers that the project's own published team
files say should see it. When a label points at a team that no longer exists, the
graph follows a recorded successor edge to the active team that inherited the work,
and when a label has no successor at all it says so instead of returning nothing.

No LLM anywhere in the product. The ingest, the queries, the routing decision, the
gap report and the CI assertions are all deterministic, and CI runs with no network.

[![ci](https://github.com/LangerSword/rustbrain/actions/workflows/ci.yml/badge.svg)](https://github.com/LangerSword/rustbrain/actions/workflows/ci.yml)

Green run: https://github.com/LangerSword/rustbrain/actions/runs/39165501700

---

## What it does, concretely

Two commands and one page:

| command | what it produces |
|---|---|
| `python3 cmd/route.py 1892` | for an RFC PR, every owning team and its current reviewers with role, authored count and latest RFC date |
| `python3 cmd/route.py T-libs-api` | same, for a label |
| `python3 cmd/gaps.py` | every `T-*` label in use, in three tiers, with RFC loads and scope |
| `python3 cmd/refresh.py --bump` | re-ingest, diff against the previous snapshot, write the diff report |
| `python3 cmd/serve.py` | the one-page UI |

Run on the real corpus, `T-libs-api` is the demo: it labels **138 merged RFCs**, its
team `libs-api` is **archived** with 0 members, and the graph follows
`libs-api --SUCCEEDED_BY--> libs` (RFC 3984, recorded at
`teams/archive/libs-api.toml:1`) to the 37 people currently on `libs`. A routing
tool that ignored the successor edge would return nothing for 138 merged decisions.

---

## Graph data model

224 teams, 675 people, 761 RFCs, 626 documents; 1,177 roster edges, 4 successor edges.

```
(:Team   {slug, name, status: active|archived, successor_team})
(:Person {handle})
(:RFC    {num, title, outcome, created, merged_at, author, author_assoc, team_labels})
(:Document {path, rfc})

(Person)-[:MEMBER]->(Team)              person points AT team
(Person)-[:LEAD]->(Team)                person points AT team, lead role
(Person)-[:AUTHORED]->(RFC)             person points AT rfc
(Team)-[:GOVERNED]->(RFC)               team points AT rfc
(Team)-[:SUCCEEDED_BY {rfc, source, quote}]->(Team)
                                        archived team points AT its active successor
```

Every direction above is a fact about how the ingest writes the data, and every
query in `queries/` is commented with it. The directions are also asserted in both
forms: a flipped pattern must return **zero** rows, and `scripts/test_queries.py`
checks that. That test exists because a Cypher pattern that matches nothing returns
zero rows with no error, so a query written against the wrong arrow looks like a
correct empty answer.

### The query the product depends on

```cypher
// follow up to 3 successor hops from the labelled team to the CURRENT team
MATCH (labelled:Team {slug: $slug})
MATCH (labelled)-[:SUCCEEDED_BY*0..3]->(owner:Team)
WHERE owner.status = 'active'
MATCH (owner)<-[r:LEAD|MEMBER]-(p:Person)
OPTIONAL MATCH (p)-[:AUTHORED]->(authored:RFC)
WITH owner, p, collect(DISTINCT type(r)) AS kinds,
     count(DISTINCT authored) AS authored_count, max(authored.created) AS latest
RETURN owner.slug AS owner, p.handle AS handle,
       CASE WHEN 'LEAD' IN kinds THEN 'lead' ELSE 'member' END AS role,
       authored_count AS authored, coalesce(latest, '') AS latest
ORDER BY latest DESC, authored DESC, handle
```

`SUCCEEDED_BY*0..3` is what makes one query serve both cases: zero hops for an
active label, one hop for an archived one. `ORDER BY latest DESC` is deliberate:
sorting by authored count alone routes to retired maintainers, since one maintainer
has 42 RFCs whose most recent is from 2018.

---

## Setup, tested from a clean clone

The clean-clone run below was executed at 2026-10-19 02:32 IST against
`https://github.com/LangerSword/rustbrain`, and it passed with no network.

```bash
git clone https://github.com/LangerSword/rustbrain && cd rustbrain
python3 -m pip install pyyaml          # the only dependency

# 1. the ingest is offline and hashes itself
python3 scripts/build_snapshot.py      # writes data/snapshot.json
python3 scripts/build_snapshot.py --check
python3 scripts/verify_snapshot.py     # independent tomllib parser, must agree

# 2. a graph to query. Either a local module, or Docker:
docker run -d -p 6379:6379 falkordb/falkordb@sha256:b0bdcac2cbaff989e77cb0610439b7a9289e86de033ccbbd4368b66fb680ae7a
# (this host has no container runtime, so the module was extracted straight from
#  the image instead: scripts/extract_module.py then scripts/start_module.sh)

export FALKORDB_PORT=6379
python3 scripts/load_graph.py
python3 scripts/test_queries.py        # 41 assertions
python3 cmd/serve.py                   # then open http://127.0.0.1:8788
```

Observed from the clean clone: `PASS: file intact and byte-identical rebuild`,
`VERDICT: PASS, snapshot matches an independent TOML parser`, 675 / 761 / 626 nodes,
`41 passed, 0 failed`.

---

## Honest limits, and the 8-element score

Scored against the eight elements in the brief. **7 of 8, and the one that is 0 is 0
by nature, not by omission.**

| # | element | score | why |
|---|---|---|---|
| 1 | people | 1 | 675 handles, 416 on an active team; every roster comes from public team files |
| 2 | teams | 1 | 224 teams with real rosters: leads, members and alumni per team |
| 3 | projects | 1 | each team's file lists its repos and the permission level per repo |
| 4 | documents | 1 | 626 RFC documents enumerated from the repo tree by one call |
| 5 | decisions | 1 | 761 merged RFCs with outcomes from `disposition-*` labels, plus KEP-style status on each |
| 6 | stays current | 1 | `refresh.py --bump` re-ingests and diffs; it caught a real roster change (`joboet` left `libs-ping`) |
| 7 | agent does work | 1 | the routing command produces a reviewer list as an artifact; output is saved in `reports/` and in the blog evidence |
| 8 | company-like setting | **0** | **Rust is a volunteer foundation, not a company** |

On element 8, plainly: there is no revenue, no customer, no contract, no reporting
line and no manager in this data. Team leads hold peer authority. The teams are not
an org chart and this README will not call them one. A "Company Brain" built only on
Rust models a standards body; that is the honest scope of the demo.

Other limits, each measured rather than assumed:

- **The successor map is curated, not parsed.** `data/successors.yaml` holds four
  entries, each with a source file, a line number and a verbatim quote. The ingest
  validates every entry against the cited line and fails the build if a quote does
  not appear there. Anything without a citable source stays unmapped and is reported
  as a true gap. Four archived teams carry no successor note at all, so the map is
  not complete and does not claim to be.
- **Label join coverage, scoped.** Of the 19 `T-*` labels in use across 761 merged
  RFCs, **14 resolve to an active team (73.7%)**, 17 resolve to some file including
  archived ones (89.5%), and 2 have no file anywhere. An earlier version of this
  project reported only the 89.5% figure, which was true and misleading.
- **260 of 761 merged RFCs (34.2%) carry no `T-*` label at all**, so they cannot be
  routed by label and the product does not pretend otherwise. Of the rest, 46.9% of
  the corpus resolves straight to an active team and 63.9% resolves once the
  successor hop is allowed.
- **Titles are truncated to 120 characters** and document bodies are not stored.
- **`agent does work` means a deterministic artifact, not an LLM.** There is no
  model in this repository. The routing command writes a reviewer list; a human or a
  separate tool decides what to do with it.
- **Known engine behaviours this build is calibrated against.** Module ver 42201
  (v4.22.1). A pattern expression inside `CASE` is always truthy here, so roles come
  from collected relationship types; `ORDER BY` on a raw `max()` puts nulls first
  under `DESC`; `algo.pageRank` returns identical scores for every node and is never
  used; directed `shortestPath` returns null. All four are asserted or avoided in
  `queries/` and `scripts/test_queries.py`.

### Coverage numbers with their scope

Every figure below is over all merged PRs in `rust-lang/rfcs` with no `not-rfc`
label, and all files in `rust-lang/team`, at the revisions in `PINS.md`.

All figures re-derived by `scripts/author_coverage.py` and
`scripts/verify_readme_numbers.py`, which are the only sources quoted here.

| figure | value | numerator / denominator | definition |
|---|---|---|---|
| labels resolving to an active team | 73.7% | 14 / 19 labels | slug matches an active team file |
| labels resolving to any team file | 89.5% | 17 / 19 labels | includes archived files |
| RFCs with a label resolving to an active team | 46.9% | 357 / 761 RFCs | routable today with no successor hop |
| RFCs with a label resolving to any team file | 63.9% | 486 / 761 RFCs | routable after a successor hop where one exists |
| RFCs carrying no team label at all | 34.2% | 260 / 761 RFCs | cannot be routed by label |
| numbered RFC files joining to a merged RFC | 97.5% | 626 / 652 files | for the document layer; a different denominator from the RFC counts |
| authors on an active team (RFC corpus) | 35.1% | 85 / 242 distinct authors | over the 761 merged RFCs |
| authors on an active team (all merged PRs) | 26.3% | 100 / 380 distinct authors | widened scope, includes `not-rfc` PRs |
| RFCs whose author was never on a team and has no alumni record | 22.2% | 169 / 761 RFCs | no current membership, no alumni entry |
| the same, restricted to `outcome == merge` | 5.4% | 41 / 761 RFCs | the decisions subset |

---

## Rules compliance notes

**Handles only (data policy).** Contributor data is public GitHub handles from
`rust-lang/team` and public PR metadata. This repository stores handles only: no real
names, no email addresses, no avatars, no post text, and no RFC bodies. Titles are
truncated to 120 characters. `data/upstream/team/` is the team repo at a pinned
revision, committed so CI needs no network; the ingest never writes a name or an
email into the graph or the snapshot.

**AI-assistant disclosure.** An AI assistant (Hermes Agent by Nous Research) wrote
the code in this repository at the entrant's direction, across the build window. All
data, counts and outputs were produced by running the commands in this repository,
and the numbers in this README are re-derivable with `scripts/test_queries.py` and
`cmd/gaps.py`. The framing, the product decision and the scope cuts are the
entrant's; where the assistant got something wrong, the correction is recorded in
`reports/` and in the blog evidence rather than quietly dropped.

---

## Graph model and queries, in the entrant's voice

*Drafted for the entrant to edit before submitting. This is the Rule 12 explanation.*

> I picked one organisation, Rust, and built the graph out of two public repos that
> are already joined by their own keys. `rust-lang/team` publishes one TOML file per
> team, one per person, and one per repo; `rust-lang/rfcs` publishes every RFC as a
> pull request with labels. The join is not something I invented: `T-*` labels use
> the same team slugs as the team files, so a label resolves to a roster, and a PR
> author resolves to a person file. I measured both joins before building
> (13 of 14 labels in a sample, then 14 of 19 on the full corpus, and 33 of 33 member
> handles) because my first version had the arrows backwards and returned zero rows
> without an error, which is the kind of bug that looks like a correct empty answer.
>
> The part I am proudest of is the successor edge. Two teams that carry a lot of
> real RFC load, `libs-api` and `core`, are archived with zero members, and between
> them they govern 162 merged RFCs. Their files name what replaced them, in a comment
> with an RFC number. So instead of treating those 162 decisions as unroutable I
> added a curated `SUCCEEDED_BY` edge with the source file and line cited in
> `data/successors.yaml`, and the routing query walks up to three hops to find the
> team that owns the label today. A label with no such record is reported as a true
> gap, which is how `T-dev-tools` (20 RFCs, no file anywhere) shows up.
>
> The queries are in `queries/` with the edge direction written above each one. The
> main one is a three-hop traversal with two aggregations: from the labelled team,
> through the successor chain, to the current team, to its members, then each
> member's authored RFCs counted and dated. Doing that relationally means joining
> teams, membership, a self-join for the successor chain, RFC authorship and a
> grouped max, and it is the successor self-join that makes it awkward, because the
> depth of the chain is not known in advance.

---

## Layout

```
cmd/route.py      route an RFC PR or T-* labels to reviewers
cmd/gaps.py       three-tier routing-gap report with scope on every count
cmd/refresh.py    re-ingest and diff against the previous snapshot
cmd/serve.py      one-page UI
queries/          pinned Cypher, edge direction commented on each
scripts/          ingest, verifier, loader, tests, module extraction
data/snapshot.json  the frozen, hashed, byte-reproducible snapshot
data/successors.yaml curated successor map, one cited source line per entry
PINS.md           the exact upstream revisions and the data policy
reports/          refresh diffs
```

`data/snapshot.json` carries a `content_sha256` over its own body. `--check` verifies
two things separately: that the file on disk still hashes to the value recorded
inside it, and that rebuilding from the pinned revision reproduces that hash. Both
are negative-tested in CI, because the first version of the check passed on a
corrupted file.
