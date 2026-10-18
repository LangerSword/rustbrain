#!/usr/bin/env python3
"""Independent verification of the snapshot using tomllib (a real TOML parser).

If this disagrees with scripts/build_snapshot.py, the snapshot is wrong.
Run: python3 scripts/verify_snapshot.py
"""
import json, os, sys, tomllib

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAM = os.path.join(HERE, "data", "upstream", "team", "teams")


def handles(v):
    """Normalise a people entry, which is either a string or an inline table."""
    if isinstance(v, str):
        return v, []
    if isinstance(v, dict):
        return v.get("github"), sorted(v.get("roles") or [])
    return None, []


def main():
    leads = members = alumni = 0
    slugs = set()
    per = {}
    for d, status in (("", "active"), ("archive", "archived")):
        p = os.path.join(TEAM, d) if d else TEAM
        for fn in sorted(os.listdir(p)):
            if not fn.endswith(".toml"):
                continue
            with open(os.path.join(p, fn), "rb") as f:
                try:
                    doc = tomllib.load(f)
                except tomllib.TOMLDecodeError as e:
                    print("TOML PARSE FAILURE %s/%s: %s" % (d, fn, e))
                    return 2
            slug = fn[:-5]
            slugs.add(slug)
            ppl = doc.get("people") or {}
            L = [handles(x)[0] for x in ppl.get("leads", [])]
            M = [handles(x)[0] for x in ppl.get("members", [])]
            A = [handles(x)[0] for x in ppl.get("alumni", [])]
            per[slug] = (status, L, M, A)
            if status == "active" or slug not in per:
                leads += len(L)
                members += len(M)
            # alumni counted across both dirs
            alumni += len(A)

    snap = json.load(open(os.path.join(HERE, "data", "snapshot.json")))
    c = snap["counts"]
    ok = True

    def cmp(name, got, want):
        nonlocal ok
        flag = "OK  " if got == want else "MISMATCH"
        if got != want:
            ok = False
        print("%-26s tomllib=%-6s snapshot=%-6s %s" % (name, got, want, flag))

    cmp("teams_total", len(slugs), c["teams_total"])
    cmp("teams_active", sum(1 for s, v in per.items() if v[0] == "active"), c["teams_active"])
    cmp("leads", leads, c["roster_edges_lead"])
    cmp("members", members, c["roster_edges_member"])
    cmp("roster total", leads + members, c["roster_edges_roster"])

    # spot-check three teams the regex was known to get wrong at some point
    for slug in ("compiler", "libs", "leadership-council", "libs-api", "core", "mentees"):
        st, L, M, A = per[slug]
        s = snap["teams"][slug]
        good = (len(L) == len(s["leads"]) and len(M) == len(s["members"])
                and len(A) == len(s["alumni"]) and st == s["status"])
        if not good:
            ok = False
        print("  %-22s tomllib L/M/A=%d/%d/%d snapshot=%d/%d/%d %s"
              % (slug, len(L), len(M), len(A), len(s["leads"]), len(s["members"]),
                 len(s["alumni"]), "OK" if good else "MISMATCH"))

    print("\nVERDICT:", "PASS, snapshot matches an independent TOML parser" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
