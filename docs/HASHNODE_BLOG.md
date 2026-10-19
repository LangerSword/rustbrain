# 162 rust rfcs point at dead teams. here is how i routed them without an llm.

**live site:** [langersword.github.io/rustbrain](https://langersword.github.io/rustbrain/)
**repository:** [github.com/LangerSword/rustbrain](https://github.com/LangerSword/rustbrain)
**latest green ci:** [actions/runs/39195941817](https://github.com/LangerSword/rustbrain/actions/runs/39195941817)

try routing rust rfc 1892 by the book. it deprecates `mem::uninitialized` in favor of `MaybeUninit`, and it carries two team labels: `T-lang` and `T-libs-api`. if you look up `libs-api` in the rust project's own team repository (`rust-lang/team`), you find `teams/archive/libs-api.toml`. current leads: zero. current members: zero.

and `T-libs-api` is not some dusty edge case. it sits on **138 merged rfcs**. `T-core` sits on another **24**, and `core` is archived with zero members too. if you build a routing tool that just joins a pull request label to a team roster, 162 of the 761 merged rfcs in rust history hit a brick wall.

most people building a "company brain" right now try to paper over this with embeddings. they chunk a thousand markdown files into a vector store, wire up an openai key, and hope cosine similarity guesses who should review a proposal. when a team gets disbanded, the vectors do not know. the bot just hallucinates a polite paragraph and tags someone who left the project in 2019.

i did not want a chatbot guessing governance. "who owns this decision today" is a graph traversal. either the team is active, or its file names the team that replaced it, or nobody owns the label at all. when nobody owns it, the tool should not make up a name. it should say there is a gap.

so i built **rustbrain**. it routes rust rfcs to the active reviewers that the project's own files name, running on falkordb (`ver 42201`, v4.22.1) with zero language models in the path.

## the one line at the top of the file

when i actually opened `teams/archive/libs-api.toml`, the answer was sitting on line 1 in a comment:

```toml
# Library API has been incorporated into Library with RFC#3984
```

`teams/archive/core.toml` had the same thing on line 1:

```toml
# Core has been replaced by the leadership council with RFC#3392
```

my first instinct was to write a regex that scrapes comments out of archived toml files at runtime. i killed that idea in ten minutes. comment scraping is how you silently route a team to the wrong place when someone rewords a sentence.

there are 52 archived team files in `rust-lang/team`. i scanned every comment across all 52 files (`out/blog_evidence/successor_audit.md`). only 4 of them actually name a successor (`libs-api` -> `libs`, `core` -> `leadership-council`, `libs-contributors` -> `libs`, `wg-traits` -> `types`). three others (`docs`, `interim-leadership-chat`, `devtools-peers`) are archived with no successor note, and the remaining 45 say nothing at all.

so instead of pretending a parser is smart, i put those 4 edges in a curated file, `data/successors.yaml`, with the exact file path, line number, and verbatim quote for each one. at build time, `scripts/build_snapshot.py` opens every cited file on disk and checks that the quote is still on that exact line. if upstream edits the comment, the build fails loudly instead of guessing.

**[ IMAGE 1 - rfc 1892 routed through the successor hop: upload out/blog_evidence/ui_rfc1892_successor_hop.png ]**
*rfc 1892 carries T-libs-api. because libs-api is archived with 0 members, the graph walks SUCCEEDED_BY (rfc 3984, teams/archive/libs-api.toml:1) to libs and returns the 37 current reviewers sorted by their latest rfc.*

## the graph and the 0..3 hop query

the ingest script (`scripts/build_snapshot.py`) reads two pinned public repos (`rust-lang/team` at `a5176049c11ca0` and `rust-lang/rfcs` at `d2705ad64ba47`) and compiles them into `data/snapshot.json` (sha256 `6732467a070a...`). `scripts/load_graph.py` loads that snapshot into falkordb over raw resp.

the graph holds four node types and five directed edge types:

- **nodes:** 224 `Team` nodes (172 active, 52 archived), 675 `Person` nodes (github handles only), 761 `RFC` nodes (merged pull requests without a `not-rfc` label), and 626 `Document` nodes (`text/NNNN-*.md` paths).
- **edges:** 1,050 `MEMBER` edges `(Person)->(Team)`, 127 `LEAD` edges `(Person)->(Team)`, 592 `AUTHORED` edges `(Person)->(RFC)`, 395 `GOVERNED` edges `(Team)->(RFC)`, and 4 `SUCCEEDED_BY` edges `(Team)->(Team)`.

once `SUCCEEDED_BY` is an edge in the graph, you do not need separate code paths for active teams and dead teams. one cypher query (`queries/routing.cypher`) handles the whole thing:

```cypher
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

the `0` in `*0..3` matters just as much as the `3`. when you route `T-cargo` (42 merged rfcs), it takes `0` hops because `cargo` is already active. when you route `T-libs-api`, `libs-api` fails `WHERE owner.status = 'active'`, takes `1` hop across `SUCCEEDED_BY`, and lands on `libs` (37 active reviewers). in sql, writing a variable-depth walk where the chain might be zero hops or three hops means writing a recursive cte joined to a roster table and a grouped max. in cypher, it is twelve characters: `[:SUCCEEDED_BY*0..3]`.

look at the `ORDER BY latest DESC, authored DESC` line at the bottom too. my first version sorted reviewers by `authored DESC` alone. that immediately put `alexcrichton` at the top of the list because he authored 42 rfcs, except his last rfc was in february 2018. sorting by total volume routes current work to retired maintainers. sorting by `latest DESC` puts `nia-e` (`2026-07-15`) and `folkertdev` (`2026-07-01`) at the top where they belong.

**[ IMAGE 2 - T-cargo routed directly in 0 hops: upload out/blog_evidence/ui_active_team_cargo.png ]**
*T-cargo takes 0 hops through the exact same query and lands on the 8 current members of cargo.*

## when the answer is "nobody"

across the 761 merged rfcs, there are 19 distinct `T-*` labels in use (`cmd/gaps.py`).
- **tier 1 (active):** 14 labels resolve straight to an active team (357 distinct rfcs, 46.9% of the corpus).
- **tier 2 (successor hop):** 2 labels (`T-libs-api` with 138, `T-core` with 24) resolve through one `SUCCEEDED_BY` hop (162 distinct rfcs).
- **tier 3 (true gaps):** 3 labels have nowhere to go.

take `T-dev-tools`. it sits on **20 merged rfcs** (out of 761, `not-rfc` excluded). there is no `dev-tools.toml` in `teams/` and none in `teams/archive/`. there is a `teams/devtools.toml` (no hyphen) and an archived `devtools-peers.toml`, which are different slugs. `T-doc` sits on **6 merged rfcs**; `doc.toml` does not exist, and `teams/archive/docs.toml` is archived with no successor note. `T-interim-leadership-chat` sits on **1 merged rfc** and is archived with no successor. (two rfcs, 1946 and 1990, carry both `T-dev-tools` and `T-doc`, so the three gap labels total 27 label loads across **25 distinct rfcs**.)

when you run `python3 cmd/route.py T-dev-tools`, rustbrain prints `ROUTING GAP: TRUE_GAP` and stops. a tool that guesses `devtools` when the label says `dev-tools` is hiding a governance bug.

**[ IMAGE 3 - T-dev-tools flagged as a true gap: upload out/blog_evidence/ui_true_gap_dev_tools.png ]**
*T-dev-tools sits on 20 merged rfcs with no team file anywhere. the UI flags a true gap instead of returning an empty table.*

## five times my own code lied to me

the hardest part of this project was not falkordb. it was catching all the places where my own scripts printed green numbers that were completely wrong. every receipt below is committed in `out/blog_evidence/`.

### 1. the backwards cypher arrow i blamed on the engine
early on, my ingest created `(Team)-[:GOVERNED]->(RFC)` and `(Person)-[:AUTHORED]->(RFC)`. then i wrote a test query with the arrow pointing the other way: `(Team)<-[:GOVERNED]-(RFC)`.

cypher does not throw a syntax error when an arrow points the wrong way. a pattern that matches nothing just returns zero rows. i saw zero rows on inbound and non-zero rows on outbound, decided falkordb had a silent inbound-edge bug, and actually wrote a note claiming the engine was broken.

then i ran a 3-line check on a throwaway graph (`out/blog_evidence/direction_receipt.txt`):
- `(a:A)-[:R]->(b:B)` returned `1` row: `[['a', 'b']]`.
- `(a:A)<-[:R]-(b:B)` returned `0` rows: `[]`.
- unlabelled `(a)<-[:R]-(b)` returned `1` row: `[['b', 'a']]`.

the engine was doing textbook cypher. my arrows were backwards. now every `.cypher` file in `queries/` has the ingest directions written in a comment block at the top, and `scripts/test_queries.py` runs both the forward query (asserting `> 0` rows) and the flipped query (asserting `== 0` rows) on every ci push.

### 2. four bugs in one regex toml parser
before i wrote `scripts/verify_snapshot.py` to check my snapshot against python's standard `tomllib`, my snapshot builder had four separate bugs (`out/blog_evidence/01_snapshot_bugs.md`):

1. **it only walked `teams/*.toml`** (172 files) and completely missed `teams/archive/*.toml` (52 files). that made `libs-api` and `core` look like missing files instead of archived teams.
2. **an empty list swallowed the next list.** in `libs-api.toml`, `members = []` sits right above `alumni = [...]`. my non-greedy regex ran straight past the empty `[]` and counted 18 alumni as 18 active members.
3. **inline table roles got counted as people.** four files (`compiler.toml`, `leadership-council.toml`, `mentees.toml`, `maintainers-in-residence.toml`) mix plain strings with inline tables like `{ github = "lqd", roles = ["council-rep-compiler"] }`. my string scraper pulled every quoted string out of the block, so `compiler` reported 78 leads instead of 2, and role names like `"compiler-maintainer"` and `"gsoc"` showed up as github users.
4. **the corruption check could not fail.** `build_snapshot.py --check` rebuilt the snapshot in memory and compared its hash to the `content_sha256` field stored inside `data/snapshot.json`, but it never hashed the file on disk. i edited `counts.rfcs` to `999` in `data/snapshot.json`, ran `--check`, and it printed `PASS`.

i replaced the regex list scraper with a bracket-matching parser, added `verify_snapshot.py` so `tomllib` checks every team count in ci, fixed `--check` to hash the on-disk bytes first, and added a negative test in ci (`scripts/corrupt_snapshot.py`) that intentionally corrupts `data/snapshot.json` and fails the workflow if `--check` does not exit nonzero.

### 3. the `falkordb:latest` tag trap and two real engine quirks
if you look at the falkordb github releases page, you see `v6.0.2`. i assumed `falkordb/falkordb:latest` on docker hub was `v6.0.2`.

on this machine i did not even have a docker daemon running, so i wrote `scripts/extract_module.py` to pull the 18 image layers directly from the docker registry by digest (`sha256:b0bdcac2cbaff989e77cb0610439b7a9289e86de033ccbbd4368b66fb680ae7a`), verify every layer sha256, and extract `falkordb.so` and `redis-server`. when i booted the extracted binary and ran `MODULE LIST` (`out/blog_evidence/module_version_receipt.txt`), it reported `ver=42201` on `redis_version:8.10.2`. `42201` is **falkordb v4.22.1**, pushed three minutes after the release tag (`out/blog_evidence/false_v602_claim.md`).

testing directly against `ver 42201` caught two real cypher behaviors that would have broken routing in production:
- putting a pattern inside a `CASE` expression (`CASE WHEN (p)-[:LEAD]->(owner) THEN 'lead'`) evaluates to true on every row in `ver 42201`, which marked all 37 members of `libs` as team leads. collecting relationship types with `collect(DISTINCT type(r)) AS kinds` and checking `'LEAD' IN kinds` works properly.
- `ORDER BY max(authored.created) DESC` sorts `NULL` values **first**, which put the 14 members of `libs` who have never authored an rfc above the people who authored one this year. wrapping `latest` in `coalesce(latest, '')` fixes the sort.

### 4. the orphan number that changed three times
at hour 6, i ran a sample of 111 recent rfcs and claimed "35 orphan rfcs". when i pulled all 761 merged rfcs (before fixing the archived-team bug), that number jumped to 385. then i wrote a note claiming **83** rfcs were authored by people with "no current team membership and no alumni record", except 83 was actually the `disposition-merge` subset of the 385 (`out/blog_evidence/20_orphan_figure_correction.md`). i had glued one definition onto another number's count.

the rule that came out of that mess is simple: no number goes into the readme or the site without its numerator, its denominator, and a ci script (`scripts/verify_readme_numbers.py` and `scripts/assert_site_numbers.py`) that re-derives it from `data/snapshot.json` on every push. the real numbers on the 761-rfc corpus are:
- **381 / 761 (50.1%)** have an author absent from every active team's roster today.
- **169 / 761 (22.2%)** have an author with no people file and no alumni entry in any active or archived team.
- **41 / 761 (5.4%)** are that same never-on-a-team group restricted to `outcome == merge`.

### 5. 542 email addresses in the vendored tree
upstream `rust-lang/team` keeps personal email addresses in 542 of its 683 `people/*.toml` files and 180 contact lines across 55 `teams/*.toml` files. my first commit vendored that tree straight into `data/upstream/team/`.

a reviewer routing demo has no business redistributing 542 maintainers' email addresses. i wrote `scripts/sanitize_contact_fields.py` to strip `email`, `address`, and `extra-emails` at fetch time, replaced the `people/` directory with a handles-only list (`data/upstream/team/people_handles.txt`), and ran `git-filter-repo` across the repository history (`out/blog_evidence/email_removal_receipt.md`, `out/blog_evidence/history_rewrite.md`). running an email regex across every blob in `git rev-list --all` now returns zero matches.

## why element 8 scores 0

the track 03 brief asks for eight elements: people, teams, projects, documents, decisions, a refresh loop (`cmd/refresh.py --bump` caught `joboet` leaving `libs-ping` in `reports/refresh_20261019_022025.md`), an artifact-producing workflow, and a "company-like setting".

i scored rustbrain **7 out of 8**, and gave it a **0** on element 8 (`out/blog_evidence/company_like_0.md`).

rust is a foundation project, not a company. thirteen of the 224 team files mention the rust foundation or funded roles (`teams/program-managers.toml` notes they are *"hired by the Project (via the Foundation)"* and `teams/crates-io-on-call.toml` says *"composed of employees of the Rust Foundation"*), and the repo tree carries 337 repository permission files under `repos/`. but there is no revenue, no customer, no salary, and no reporting line anywhere in this data. team leads hold peer authority, not management authority. calling volunteer governance an org chart just to check a hackathon box would be dishonest, so the readme and the method page state the zero upfront.

**[ IMAGE 4 - ci green on the pinned falkordb digest: upload out/blog_evidence/ci_green.png ]**
*ci runs offline inside the github actions runner plus the digest-pinned falkordb container: PINS.md drift gate, byte-identical snapshot rebuild, tomllib verifier, readme and site number checks, corruption refusal test, and 41 cypher assertions.*

## run it yourself

every command below was tested from a cold clone (`out/blog_evidence/clean_clone.md`):

```bash
git clone https://github.com/LangerSword/rustbrain && cd rustbrain
python3 -c "import yaml" || pip install pyyaml

# 1. verify the snapshot hash and check every roster against python's tomllib
python3 scripts/build_snapshot.py --check
python3 scripts/verify_snapshot.py

# 2. start falkordb (docker digest OR rootless binary extractor)
docker run -d -p 6379:6379 falkordb/falkordb@sha256:b0bdcac2cbaff989e77cb0610439b7a9289e86de033ccbbd4368b66fb680ae7a
# no docker? run: python3 scripts/extract_module.py && scripts/start_module.sh 6379

# 3. load the graph, run all 41 assertions, and route rfc 1892
export FALKORDB_PORT=6379
python3 scripts/load_graph.py
python3 scripts/test_queries.py
python3 cmd/route.py 1892
python3 cmd/route.py 1892 --naive
```

- **live site:** [langersword.github.io/rustbrain](https://langersword.github.io/rustbrain/)
- **source and evidence receipts:** [github.com/LangerSword/rustbrain](https://github.com/LangerSword/rustbrain)
