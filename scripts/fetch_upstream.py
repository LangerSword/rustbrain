#!/usr/bin/env python3
"""Re-fetch the pinned upstream trees into data/upstream at the pins in scripts/build_snapshot.py.

Run by `cmd/refresh.py --bump`; CI never runs it. Fetches the TOML trees this
repository vendors: teams/, people/ and repos/.
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
UP = os.path.join(DATA, "upstream")

# The pin lives in exactly one place: scripts/build_snapshot.py. A second copy here
# is how PINS.md and this script drifted from the snapshot before.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_snapshot import PINS  # noqa: E402

UA = "rustbrain-snapshot/1.0"


def gh(url):
    r = subprocess.run(["gh", "api", url], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("gh api %s failed: %s" % (url, r.stderr[:200]))
    return json.loads(r.stdout)


def curl(url, dest):
    r = subprocess.run(["curl", "-sSL", "-H", "User-Agent: " + UA, "--max-time", "60",
                        "-o", dest, "-w", "%{http_code}", url], capture_output=True, text=True)
    if r.stdout.strip() != "200":
        raise SystemExit("fetch %s http=%s" % (url, r.stdout.strip()))
    return os.path.getsize(dest)


def main():
    os.makedirs(os.path.join(UP, "team", "teams"), exist_ok=True)
    os.makedirs(os.path.join(UP, "team", "teams", "archive"), exist_ok=True)
    os.makedirs(os.path.join(UP, "team", "people"), exist_ok=True)

    # --- team repo: the TOML trees this repository vendors ---
    tree = gh("repos/rust-lang/team/git/trees/%s?recursive=1" % PINS["team"])["tree"]
    n = 0
    for e in tree:
        p = e["path"]
        if not p.endswith(".toml"):
            continue
        if p.startswith(("teams/", "people/", "repos/")):
            d = os.path.join(UP, "team", p)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            curl("https://raw.githubusercontent.com/rust-lang/team/%s/%s" % (PINS["team"], p), d)
            n += 1
    print("team repo: fetched %d toml files at %s" % (n, PINS["team"][:12]))

    # --- rfcs repo: merged PR metadata + text/ file index (names only, NO bodies) ---
    merged = []
    page = 1
    while True:
        batch = gh("repos/rust-lang/rfcs/pulls?state=closed&per_page=100&page=%d&sort=created&direction=asc" % page)
        if not batch:
            break
        for pr in batch:
            if not pr.get("merged_at"):
                continue
            merged.append({"num": pr["number"], "title": pr.get("title", ""),
                           "user": pr["user"]["login"],
                           "assoc": pr.get("author_association"),
                           "created_at": pr.get("created_at"),
                           "merged_at": pr.get("merged_at"),
                           "labels": [l["name"] for l in (pr.get("labels") or [])]})
        if len(batch) < 100:
            break
        page += 1
        time.sleep(0.25)
    merged.sort(key=lambda x: x["num"])
    json.dump(merged, open(os.path.join(DATA, "rfcs_merged.json"), "w"))
    print("rfcs repo: %d merged PRs at %s" % (len(merged), PINS["rfcs"][:12]))

    # text/ index: path, rfc number, and the first metadata lines. NO body.
    tree2 = gh("repos/rust-lang/rfcs/git/trees/%s?recursive=1" % PINS["rfcs"])["tree"]
    texts = sorted(t["path"] for t in tree2
                   if t["path"].startswith("text/") and re.match(r"^text/\d{4}-.*\.md$", t["path"]))
    print("rfcs repo: %d numbered text/*.md in tree" % len(texts))
    index = []
    for p in texts:
        num = int(re.match(r"^text/(\d{4})-", p).group(1))
        index.append({"rfc": num, "path": p})
    json.dump(index, open(os.path.join(DATA, "rfcs_text_index.json"), "w"))
    print("wrote rfcs_text_index.json with %d entries (paths only, no bodies)" % len(index))
    print("NOTE: document start_date / tracking_issue are filled by scripts/enrich_docs.py")


if __name__ == "__main__":
    main()
