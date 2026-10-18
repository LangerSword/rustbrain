#!/usr/bin/env python3
"""rustbrain refresh: re-ingest and diff against the previous snapshot.

What it diffs, all from the committed snapshots (no network unless --bump):
  - new and removed RFCs
  - RFC outcome changes (none -> merge, merge -> reject, and so on)
  - roster changes per team: joined, left, promoted to lead, stepped down
  - teams archived since the previous snapshot
  - routing gaps opened and closed

Usage:
  python3 cmd/refresh.py                  diff the current snapshot against the last
                                          one kept in data/history/
  python3 cmd/refresh.py --snapshot       keep a copy of the current snapshot in
                                          data/history/ before diffing
  python3 cmd/refresh.py --pin            regenerate PINS.md from scripts/build_snapshot.py,
                                          the single source of truth. No network.
  python3 cmd/refresh.py --bump           re-fetch upstream at CURRENT HEAD, rewrite the
                                          pins in build_snapshot.py AND PINS.md, rebuild,
                                          then diff. Network.
"""
import argparse
import datetime as dt
import importlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
HIST = os.path.join(DATA, "history")
REPORTS = os.path.join(HERE, "reports")


def build_snapshot_module():
    """Import scripts/build_snapshot.py, the one place a pinned revision lives."""
    scripts = os.path.join(HERE, "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import build_snapshot
    return build_snapshot


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def load(path):
    return json.load(open(path))


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise SystemExit("command failed: %s\n%s" % (" ".join(cmd), (r.stderr or r.stdout)[:400]))
    return r.stdout


def teams_members(snap):
    out = {}
    for slug, t in snap["teams"].items():
        out[slug] = {"status": t["status"],
                     "leads": set(t["leads"]),
                     "members": {h for h, _r in t["members"]},
                     "successor": t.get("successor_team")}
    return out


def gaps(snap):
    """Label -> tier, computed the same way the gap report does."""
    succ = {e["from"]: e["to"] for e in snap["successor_map"]["edges"]}
    tiers = {}
    labels = sorted({l for r in snap["rfcs"] for l in r["team_labels"]})
    for l in labels:
        t = snap["teams"].get(l)
        if t is None:
            tiers[l] = "TRUE_GAP"
        elif t["status"] == "active":
            tiers[l] = "ACTIVE"
        elif l in succ:
            tiers[l] = "SUCCESSOR"
        else:
            tiers[l] = "TRUE_GAP"
    return tiers


def diff(old, new):
    d = {}
    o_rfcs = {r["num"]: r for r in old["rfcs"]}
    n_rfcs = {r["num"]: r for r in new["rfcs"]}
    d["rfcs_added"] = sorted(set(n_rfcs) - set(o_rfcs))
    d["rfcs_removed"] = sorted(set(o_rfcs) - set(n_rfcs))
    d["outcome_changed"] = [
        {"num": n, "from": o_rfcs[n]["outcome"], "to": n_rfcs[n]["outcome"]}
        for n in sorted(set(o_rfcs) & set(n_rfcs))
        if o_rfcs[n]["outcome"] != n_rfcs[n]["outcome"]]

    o_t, n_t = teams_members(old), teams_members(new)
    team_changes = []
    for slug in sorted(set(o_t) & set(n_t)):
        a, b = o_t[slug], n_t[slug]
        joined = sorted((b["members"] | b["leads"]) - (a["members"] | a["leads"]))
        left = sorted((a["members"] | a["leads"]) - (b["members"] | b["leads"]))
        promoted = sorted(b["leads"] - a["leads"])
        demoted = sorted(a["leads"] - b["leads"])
        if a["status"] != b["status"] or joined or left or promoted or demoted:
            team_changes.append({"team": slug, "status": "%s -> %s" % (a["status"], b["status"]),
                                 "joined": joined, "left": left,
                                 "promoted_to_lead": promoted, "no_longer_lead": demoted})
    d["teams_added"] = sorted(set(n_t) - set(o_t))
    d["teams_removed"] = sorted(set(o_t) - set(n_t))
    d["team_changes"] = team_changes
    d["teams_newly_archived"] = sorted(s for s in set(o_t) & set(n_t)
                                       if o_t[s]["status"] == "active" and n_t[s]["status"] == "archived")

    og, ng = gaps(old), gaps(new)
    d["gaps_opened"] = sorted(l for l in ng if ng.get(l) == "TRUE_GAP" and og.get(l) != "TRUE_GAP")
    d["gaps_closed"] = sorted(l for l in og if og.get(l) == "TRUE_GAP" and ng.get(l) != "TRUE_GAP")
    d["gap_tier_changed"] = [
        {"label": l, "from": og[l], "to": ng[l]}
        for l in sorted(set(og) & set(ng)) if og[l] != ng[l]]
    d["counts_old"] = old["counts"]
    d["counts_new"] = new["counts"]
    return d


def write_report(d, old_sha, new_sha, path, bumped, pins):
    L = []
    L.append("# Refresh diff")
    L.append("")
    L.append("Generated %s IST." % dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30)))
             .strftime("%Y-%m-%d %H:%M:%S"))
    L.append("")
    L.append("Previous snapshot content_sha256: `%s`" % old_sha)
    L.append("Current  snapshot content_sha256: `%s`" % new_sha)
    L.append("Upstream fetch: %s" % ("re-fetched at current HEAD" if bumped else
                                     "unchanged, pinned revisions reused"))
    L.append("Pins in effect: team `%s`, rfcs `%s`" % (pins["team"][:12], pins["rfcs"][:12]))
    L.append("")
    any_change = False
    def sec(title, items, fmt=str):
        nonlocal any_change
        L.append("## %s: %d" % (title, len(items)))
        if items:
            any_change = True
            for it in items[:40]:
                L.append("- %s" % fmt(it))
            if len(items) > 40:
                L.append("- ... and %d more" % (len(items) - 40))
        L.append("")
    sec("RFCs added", d["rfcs_added"])
    sec("RFCs removed", d["rfcs_removed"])
    sec("RFC outcome changes", d["outcome_changed"],
        lambda x: "#%s %s -> %s" % (x["num"], x["from"], x["to"]))
    sec("Teams added", d["teams_added"])
    sec("Teams removed", d["teams_removed"])
    sec("Teams newly archived", d["teams_newly_archived"])
    sec("Roster changes", d["team_changes"],
        lambda x: "%s: +%d/-%d joined=%s left=%s promoted=%s stepped_down=%s"
                  % (x["team"], len(x["joined"]), len(x["left"]),
                     x["joined"][:4], x["left"][:4], x["promoted_to_lead"][:3], x["no_longer_lead"][:3]))
    sec("Routing gaps OPENED", d["gaps_opened"])
    sec("Routing gaps CLOSED", d["gaps_closed"])
    sec("Gap tier changed", d["gap_tier_changed"],
        lambda x: "%s %s -> %s" % (x["label"], x["from"], x["to"]))
    L.append("## Counts")
    L.append("")
    L.append("| measure | previous | current | delta |")
    L.append("|---|---|---|---|")
    for k in sorted(set(d["counts_old"]) | set(d["counts_new"])):
        a, b = d["counts_old"].get(k), d["counts_new"].get(k)
        delta = (b - a) if isinstance(a, int) and isinstance(b, int) else ""
        L.append("| %s | %s | %s | %s |" % (k, a, b, delta))
    L.append("")
    if not any_change:
        L.append("**No changes detected.** The ingest is a pure function of the pinned")
        L.append("revisions, so a refresh against the same pins is expected to be a no-op.")
        L.append("This is the determinism result, not a failure.")
        L.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    return any_change


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", action="store_true", help="keep a copy of the current snapshot first")
    ap.add_argument("--bump", action="store_true", help="re-fetch upstream at current HEAD")
    ap.add_argument("--pin", action="store_true",
                    help="regenerate PINS.md from scripts/build_snapshot.py (alone: no network)")
    args = ap.parse_args()

    if args.pin and not args.bump:
        bs = build_snapshot_module()
        print("wrote %s (generated from scripts/build_snapshot.py)" % bs.write_pins())
        return 0

    os.makedirs(HIST, exist_ok=True)
    os.makedirs(REPORTS, exist_ok=True)
    snap_path = os.path.join(DATA, "snapshot.json")

    prev = None
    if os.path.isdir(HIST):
        cands = sorted(p for p in os.listdir(HIST) if p.startswith("snapshot_") and p.endswith(".json"))
        if cands:
            prev = os.path.join(HIST, cands[-1])
    if prev is None:
        # First run. Seed the baseline so the next run has something to diff against.
        cur = load(snap_path)
        dest = os.path.join(HIST, "snapshot_%s.json" % cur["content_sha256"][:12])
        if not os.path.exists(dest):
            shutil.copyfile(snap_path, dest)
        print("no previous snapshot; seeded the baseline at %s" % dest)
        print("run this command again to produce a real diff")
        return 0

    if args.bump:
        print("re-fetching upstream at current HEAD")
        import re
        shas, cdates = {}, {}
        for repo, key in (("rust-lang/team", "team"), ("rust-lang/rfcs", "rfcs")):
            out = run(["gh", "api", "repos/%s/commits/main" % repo, "--jq",
                       '.sha + " " + .commit.committer.date'])
            sha, cdate = out.split()
            shas[key], cdates[key] = sha, cdate
            print("  %s HEAD = %s  committer date %s" % (repo, sha, cdate))

        # A bump ALWAYS rewrites the pins. Fetching a new tree while the snapshot still
        # names the old SHA would make the snapshot lie about its own provenance, and
        # rewriting build_snapshot.py alone is exactly how PINS.md drifted before.
        bs_path = os.path.join(HERE, "scripts", "build_snapshot.py")
        src = read(bs_path)
        today = dt.date.today().isoformat()
        for key in ("team", "rfcs"):
            src = re.sub(r'("%s":\s*")[0-9a-f]{40}' % key,
                         lambda m, s=shas[key]: m.group(1) + s, src)
            src = re.sub(r'("%s":\s*\{[^}]*?"retrieved":\s*")[0-9-]+' % key,
                         lambda m, d=today: m.group(1) + d, src, flags=re.S)
            src = re.sub(r'("%s":\s*\{[^}]*?"note":\s*")[^"]*' % key,
                         lambda m, c=cdates[key]: m.group(1) + "committer date " + c,
                         src, flags=re.S)
        with open(bs_path, "w", encoding="utf-8") as f:
            f.write(src)
        bs = importlib.reload(build_snapshot_module())
        print("rewrote PINS in scripts/build_snapshot.py, regenerated %s" % bs.write_pins())

        # Refetch both trees at the new pins. Each fetch script imports its pin from
        # build_snapshot.py, so the subprocess sees the values just written.
        run([sys.executable, os.path.join(HERE, "scripts", "fetch_upstream.py")])
        run([sys.executable, os.path.join(HERE, "scripts", "fetch_rfcs.py")])

    run([sys.executable, os.path.join(HERE, "scripts", "build_snapshot.py")])
    new = load(snap_path)
    old = load(prev)

    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    report = os.path.join(REPORTS, "refresh_%s.md" % stamp)
    changed = write_report(diff(old, new), old["content_sha256"], new["content_sha256"],
                           report, args.bump, new["pins"])
    print("wrote %s" % report)
    print("changes detected: %s" % changed)

    if args.snapshot:
        dest = os.path.join(HIST, "snapshot_%s.json" % new["content_sha256"][:12])
        if not os.path.exists(dest):
            shutil.copyfile(snap_path, dest)
        print("kept %s" % dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
