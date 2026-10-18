# Blog evidence 1: three bugs the snapshot builder had, found by testing

Timestamps 2026-10-16, 01:43 to 01:52 IST, repo ~/projects/rustbrain.

## Bug 1: only depth-1 teams read, 52 archived files ignored
`teams/libs-api.toml` and `teams/core.toml` do not exist at depth 1. They are at
`teams/archive/`. Measured: 224 team TOML files, 172 active, 52 archived. Found by
the entrant asking me to print the headers. Both files hold 0 leads, 0 members and
their full alumni list, and each names its successor in a comment:
`# Library API has been incorporated into Library with RFC#3984` and
`# Core has been replaced by the leadership council with RFC#3392`.

## Bug 2: an empty list swallowing the next list
`members = []` followed by `alumni = [ ... ]`: my non-greedy regex ran past the empty
members list and counted 18 alumni as 18 members. libs-api showed members=18 when the
truth is members=0, alumni=18.

## Bug 3: role names counted as people
Fix for bug 2 then broke `leads` on one-line lists, and a later version counted the
strings inside inline tables, so `compiler` reported 78 leads (truth 2) and the word
`compiler-maintainer` appeared as if it were a person's handle. Same for `gsoc` and
`ospp` in mentees.

## What caught it
An independent verifier, `scripts/verify_snapshot.py`, parses every team file with
`tomllib` and compares against my regex-based snapshot. It found bugs 2 and 3. The
final report:

    teams_total    tomllib=224  snapshot=224  OK
    teams_active   tomllib=172  snapshot=172  OK
    leads          tomllib=127  snapshot=127  OK
    members        tomllib=1051 snapshot=1051 OK
    roster total   tomllib=1178 snapshot=1178 OK
    VERDICT: PASS, snapshot matches an independent TOML parser

## Bug 4: the drift check that could not fail
`--check` compared the rebuild against the hash FIELD stored in the file, but never
hashed the file itself. Editing `counts.rfcs` to 999 still printed PASS. Fixed with a
second check that hashes the on-disk file. Now corrupting a number produces:
`FAIL: committed snapshot is corrupt, recorded=98f0f195... actual=5a2776fc...` and
exit code 1.

## Final frozen counts (MEASURED 2026-10-16, scope in the snapshot)
teams 224 (172 active, 52 archived), roster edges 1178 (127 lead + 1051 member),
alumni edges 870, people 675, on an active team 416, RFCs 761, documents 626.
snapshot content_sha256=98f0f19552ef4026a2f7e9ce2f85f671b3a93008b2f70faf1119e679976fd84c
