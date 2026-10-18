# Clean-clone test transcript

Host: Arch Linux, kernel 7.2.9 (x86_64), no container runtime (`docker` not on PATH).
python3: 3.14.7; this session's python3 has no `pip` module, pyyaml 6.0.3 is importable.
Clones live under /home/lakshaya/.hermes/cache/scratch/ (scratch, not part of the repo).

Run 1 followed the committed README at 2be978d exactly and found two defects.
Both were fixed in 301af5f (README only). Run 2 is a fresh clone at 301af5f and
follows the fixed README exactly, with no extra steps, and is green end to end.

Commit SHAs here are the current-history equivalents after the 2026-10-19
history rewrite (old 6db94e6 -> 2be978d, 17b3ec9 -> 301af5f); the rewrite record is
`history_rewrite.md`. Run 3, from the rewritten history, is appended at the end.

## Run 1, clone at 2be978d

    $ git clone https://github.com/LangerSword/rustbrain
    EXIT=0

    $ python3 -m pip install pyyaml
    /home/lakshaya/.hermes/installs/55fbfd3a46b20aab/environments/f5b7fa9669b9487d9b90ff9e49bf8c3c/venv/bin/python3: No module named pip
    EXIT=1

    $ python3 scripts/build_snapshot.py
    wrote data/snapshot.json
    content_sha256=6732467a070a0a8c7129ff334f5a95a2227cd014783ca8415ca01bb87a353c97
    {"documents": 626, "people": 675, "people_on_active_team": 416, "rfcs": 761, "roster_edges_alumni": 870, "roster_edges_lead": 127, "roster_edges_member": 1050, "roster_edges_roster": 1177, "successor_edges": 4, "teams_active": 172, "teams_archived": 52, "teams_total": 224}
    EXIT=0

    $ python3 scripts/build_snapshot.py --check
    PASS: file intact and byte-identical rebuild, sha256=6732467a070a0a8c7129ff334f5a95a2227cd014783ca8415ca01bb87a353c97

    $ python3 scripts/verify_snapshot.py
    VERDICT: PASS, snapshot matches an independent TOML parser
    EXIT=0

    # README step 2, container option:
    $ docker --version
    bash: docker: command not found
    EXIT=127

    # README step 2, the no-container aside: extract the module from the pinned image
    $ python3 scripts/extract_module.py
    got anonymous pull token (len 2702)
    amd64 manifest digest: sha256:d998ed0dfd91da6208f257dfd61f5330335bd6e7006cfc0fd1ddd761269e2634
    layers: 18
    layer 00  30855435 bytes digest_ok=True
    ...  (all 18 layers digest_ok=True; contains redis-server and falkordb.so)
    module=True redis=True
    OK: now run scripts/start_module.sh
    EXIT=0

    $ scripts/start_module.sh
    port 6399 already listening, nothing to do
    EXIT=0

    $ export FALKORDB_PORT=6379
    $ python3 scripts/load_graph.py
    ConnectionRefusedError: [Errno 111] Connection refused
    EXIT=1

### Defects found in run 1

1. `python3 -m pip install pyyaml` fails on this host (no pip module in the session
   python), and the step is a no-op anyway when pyyaml is already present. The README
   told the reader to run it unconditionally.
2. Port mismatch in the no-container path. The README said to run
   `scripts/start_module.sh` (whose default port is 6399) and then
   `export FALKORDB_PORT=6379`. Here the module was already running on 6399 from the
   main checkout, but even on a fresh host the sequence is contradictory: the module
   would listen on 6399 and load_graph would talk to 6379. Observed failure:
   ConnectionRefusedError. The README also never showed the routing command in the
   setup block even though routing is the product.

## The fix, commit 301af5f

- dependency step is now `python3 -c "import yaml" || pip install pyyaml`;
- the no-container path names its port: `scripts/start_module.sh 6379`, matching
  `FALKORDB_PORT=6379`;
- the "passed with no network" claim replaced: cloning and the image extraction need
  network; the pipeline is offline once the graph is loaded;
- `python3 cmd/route.py 1892` added to the setup block.

## Run 2, fresh clone at 301af5f

    $ git clone https://github.com/LangerSword/rustbrain && cd rustbrain
    EXIT=0    (HEAD 301af5f)

    $ python3 -c "import yaml" || pip install pyyaml
    EXIT=0  (yaml import ok, nothing installed)

    $ python3 scripts/build_snapshot.py
    wrote data/snapshot.json
    content_sha256=6732467a070a0a8c7129ff334f5a95a2227cd014783ca8415ca01bb87a353c97
    EXIT=0

    $ python3 scripts/build_snapshot.py --check
    PASS: file intact and byte-identical rebuild, sha256=6732467a070a0a8c7129ff334f5a95a2227cd014783ca8415ca01bb87a353c97
    EXIT=0

    $ python3 scripts/verify_snapshot.py
    teams_total  tomllib=224  snapshot=224  OK
    ...          (six sample teams agree on leads/members/alumni)
    VERDICT: PASS, snapshot matches an independent TOML parser
    EXIT=0

    $ python3 scripts/extract_module.py
    got anonymous pull token (len 2702)
    amd64 manifest digest: sha256:d998ed0dfd91da6208f257dfd61f5330335bd6e7006cfc0fd1ddd761269e2634
    layers: 18, every layer digest_ok=True
    module=True redis=True
    EXIT=0

    $ scripts/start_module.sh 6379
    falkordb module ver = 42201 (expect 42201)
    OK: graded module running on port 6379
    EXIT=0

    $ export FALKORDB_PORT=6379
    $ python3 scripts/load_graph.py
    Graph loaded. Node and edge counts:
      Team 224, Person 675, RFC 761, Document 626
      MEMBER 1050, LEAD 127, AUTHORED 592, GOVERNED 395, SUCCEEDED_BY 4
    EXIT=0

    $ python3 scripts/test_queries.py
    ...  41 passed, 0 failed
    EXIT=0

    $ python3 cmd/route.py 1892
    T-lang      route: lang (active), no successor hop needed        [tier ACTIVE]
    T-libs-api  route: libs-api (archived) --SUCCEEDED_BY--> libs    [tier SUCCESSOR, 1 hop]
                37 current members, first row nia-e (lead, latest 2026-07-15)
    EXIT=0

    $ python3 cmd/serve.py        # left running on http://127.0.0.1:8788
    $ curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8788/
    200
    $ curl -s 'http://127.0.0.1:8788/api/route?target=T-libs-api'
    tier SUCCESSOR | route: libs-api -> libs | 37 people
    $ curl -s 'http://127.0.0.1:8788/api/route?target=T-doc'
    tier TRUE_GAP | label: T-doc

## Result

A cold clone at 301af5f runs with the README commands only, no extra steps: ingest
(byte-identical), independent verifier, pinned module, graph load, 41 query
assertions, routing on a real RFC PR, and the UI serving HTTP 200 with correct
tiers. The only steps that touch the network are the clone itself and the image
layer download in the no-container path.

## Run 3, fresh clone at 1613b9b, after the history rewrite

The rewritten history was cloned into a fresh directory and the README was followed
literally; port 6379 was free so the clone started its own extracted module.

    $ git clone https://github.com/LangerSword/rustbrain && cd rustbrain
    EXIT=0    (HEAD 1613b9b)
    $ python3 -c "import yaml" || pip install pyyaml
    EXIT=0
    $ python3 scripts/build_snapshot.py
    content_sha256=6732467a070a0a8c7129ff334f5a95a2227cd014783ca8415ca01bb87a353c97
    $ python3 scripts/build_snapshot.py --check
    PASS: file intact and byte-identical rebuild, sha256=6732467a...
    $ python3 scripts/verify_snapshot.py
    VERDICT: PASS, snapshot matches an independent TOML parser
    $ python3 scripts/extract_module.py
    ... 18 layers digest_ok=True; module=True redis=True
    $ scripts/start_module.sh 6379
    falkordb module ver = 42201 (expect 42201)
    OK: graded module running on port 6379
    $ export FALKORDB_PORT=6379; python3 scripts/load_graph.py
    Team 224, Person 675, RFC 761, Document 626; MEMBER 1050, LEAD 127,
    AUTHORED 592, GOVERNED 395, SUCCEEDED_BY 4
    $ python3 scripts/test_queries.py
    41 passed, 0 failed
    $ python3 cmd/route.py 1892
    T-lang (active), no successor hop needed; T-libs-api -> libs via SUCCEEDED_BY
    $ python3 cmd/serve.py    (http://127.0.0.1:8788)
    GET / HTTP 200; T-libs-api SUCCESSOR libs-api -> libs, 37 people; T-doc TRUE_GAP

Result: the cold clone is green on the rewritten history, with the vendored tree
carrying no contact fields and people handles only.
