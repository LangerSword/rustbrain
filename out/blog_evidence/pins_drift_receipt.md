# The PINS.md drift, found and fixed

Captured 2026-10-19 IST during the build. Every line below is output of a
command that can be re-run from this repository; the pre-fix lines come from git
history, which keeps them reproducible after the fix.

## What the grep found, before the fix

The committed state before 5411c60, shown via git:

    $ git show 5411c60^:PINS.md | grep -n 'cb0ccabd|a5176049'
8:| github.com/rust-lang/team | cb0ccabd69bc63e3f84f26d764704d939224071f | 2026-10-16 | committer date 2026-10-15T11:17:38Z |

    $ git show 5411c60^:scripts/build_snapshot.py | grep -n 'cb0ccabd|a5176049'
32:PINS = {"team": "a5176049c11ca092994af7a07deb4f62dfe4b55c",

They disagree: PINS.md named the old pin (cb0ccabd, retrieved 2026-10-16) while
build_snapshot.py, snapshot.json and the committed team tree were at a5176049.

## Which side was right, proved by hashing one file at both revisions

    $ sha256sum data/upstream/team/teams/libs-ping.toml
    f98c8bfe0de7f8a21cb47017436b06780b65bb352bbe5590c8230986b909e8ba  (on disk)
    f98c8bfe0de7f8a21cb47017436b06780b65bb352bbe5590c8230986b909e8ba  (remote at a5176049)
    55410c0138aa5191d1cf3e98f27db1eebc1bd3d8be077f07a1552fd8056fabe5  (remote at cb0ccabd)

The on-disk file equals the remote file at a5176049 and differs at cb0ccabd.
`grep -n joboet data/upstream/team/teams/libs-ping.toml` prints nothing, and
reports/refresh_20261019_022025.md records joboet leaving libs-ping in that same
refresh, which is the roster change the bump caught. PINS.md was the stale file.

## Where the pin can live, after the fix

One place: scripts/build_snapshot.py (PINS and PIN_META, including retrieval
dates and the FalkorDB image digest). PINS.md is generated from it by
`python3 cmd/refresh.py --pin`; the fetch scripts import PINS from it; the
successors.yaml header cites it instead of carrying its own copy.

## The gate and its proof, on a scratch branch

- red run, a committed hand-edited PINS.md: Job 0 fails with exit code 1 and the
  diff shows `-cb0ccabd` / `+a5176049`:
  https://github.com/LangerSword/rustbrain/actions/runs/39168272809
- green after the fix commit b79713e: https://github.com/LangerSword/rustbrain/actions/runs/39168340345
- main green at the fix commit 5411c60: https://github.com/LangerSword/rustbrain/actions/runs/39168399472

The CI step itself, .github/workflows/ci.yml Job 0:

    python3 cmd/refresh.py --pin
    git diff --exit-code -- PINS.md

## Current state

    $ grep -n 'cb0ccabd' PINS.md scripts/build_snapshot.py
    (no output: the stale SHA appears in neither file)
