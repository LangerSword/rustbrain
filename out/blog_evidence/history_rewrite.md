# History rewrite (1.2): email addresses purged from git history

Done 2026-10-19 IST on https://github.com/LangerSword/rustbrain.

## Exposure check

- visibility `public`, `fork: false`, `forks_count: 0`, `network_count: 0` (GitHub API at the time of the rewrite). No forks existed, so no other GitHub copy held the old blobs.
- Emails were in history: `git log --all -S'@' -- data/upstream/team/people` listed 2 commits, and every vendored team file that carried an `address`/`email` line was committed from the tree commit onward.

## Backup

    $ git bundle create ../rustbrain-backup.bundle --all
    $ git bundle verify ../rustbrain-backup.bundle
    The bundle records a complete history.   (1,483,373 bytes)

## Tool

`git-filter-repo 2.47.0`, installed locally with `uv tool install git-filter-repo`
(no sudo). That is the exact install command.

## Rewrite

    $ printf 'regex:[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}==>***REMOVED***\n' > /tmp/email_rules.txt
    $ git filter-repo --force --invert-paths \
        --path data/upstream/team/people --path data/upstream/team/src \
        --path data/upstream/team/tests --path data/upstream/team/docs \
        --path data/upstream/team/rust_team_data --path data/upstream/team/hardware-keys \
        --path data/upstream/team/.github --path data/upstream/team/Cargo.toml \
        --path data/upstream/team/Cargo.lock --path data/upstream/team/config.toml \
        --path data/upstream/team/README.md --path data/upstream/team/triagebot.toml \
        --path data/upstream/team/.gitignore --path data/upstream/team/.taplo.toml \
        --replace-text /tmp/email_rules.txt
    Parsed 25 commits; new history written in 0.30 seconds.

## Old and new HEAD

    old 0bc2672f43838ab6a81f100cbd0a4076748beb6f
    new 43e717b76bbc3e9673309dcd288e64ce8fb2b2d2

## Proof after the rewrite

    $ git log --all --oneline -- data/upstream/team/people | wc -l
    0
    $ git grep -lIE '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' $(git rev-list --all)
    (no output: no address in any blob of any commit)
    $ python3 scripts/build_snapshot.py --check
    PASS: file intact and byte-identical rebuild, sha256=6732467a...

Repo head after the follow-up docs commit: 1613b9bbd268c83a32c82acebca63ae16ce89e30.
Clean-clone Run 3 on the rewritten history was green; it is recorded at the end of
`clean_clone.md`.

## Commit map, old to new, for commits still reachable

| old | new |
|---|---|
| 0bc2672 | 43e717b |
| 17b3ec9 | 301af5f |
| 25d50f7 | 1e01ccd |
| 342d9d4 | 92546b7 |
| 442ff88 | 442ff88 |
| 5411c60 | c4b1fa1 |
| 589e92b | 589e92b |
| 5a6eec8 | e150d30 |
| 6110d48 | 24c88e4 |
| 672ea7d | d2ed164 |
| 6b6932d | 6b6932d |
| 6db94e6 | 2be978d |
| 76a4b25 | 103d17d |
| 87be1d1 | 50561b8 |
| 9219951 | 9219951 |
| abab173 | 23f6e6c |
| abcd772 | abcd772 |
| ad9dd6e | ad9dd6e |
| b5ec788 | d7d0123 |
| bf3f1cc | bf3f1cc |
| cdcb447 | 4d831ef |
| cdcb984 | aa00cd6 |
| ec4ed68 | e62c9bd |
| f9771c0 | 77eab88 |
| fd5fd4d | 6a088bc |

Notes: Actions run pages from before the rewrite still show the old head SHAs and
remain valid links. The scratch-branch commit b79713e was never on main and is not
in the new history; its run URL is the record. Push after the rewrite:
`git remote add origin <url>` (filter-repo removes origin) then
`git push --force origin main`.
