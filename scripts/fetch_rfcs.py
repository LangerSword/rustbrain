#!/usr/bin/env python3
"""Fetch rust-lang/rfcs metadata at the pinned SHA. Network script, CI never runs it.

Stores PR metadata and the text/ filename index. NO RFC bodies.
"""
import json, os, re, subprocess, time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
RFCS_SHA = "d2705ad64ba47e812a2b6b19d6f613fb4c14c5e0"


def gh(url, tries=4):
    for i in range(tries):
        r = subprocess.run(["gh", "api", url], capture_output=True, text=True)
        if r.returncode == 0:
            return json.loads(r.stdout)
        time.sleep(2 + 2 * i)
    raise SystemExit("gh api failed after %d tries: %s -> %s" % (tries, url, r.stderr[:200]))


def main():
    merged, page = [], 1
    while True:
        batch = gh("repos/rust-lang/rfcs/pulls?state=closed&per_page=100&page=%d&sort=created&direction=asc" % page)
        if not batch:
            break
        for pr in batch:
            if not pr.get("merged_at"):
                continue
            merged.append({"num": pr["number"], "title": (pr.get("title") or "")[:120],
                           "user": pr["user"]["login"], "assoc": pr.get("author_association"),
                           "created_at": pr.get("created_at"), "merged_at": pr.get("merged_at"),
                           "labels": [l["name"] for l in (pr.get("labels") or [])]})
        if len(batch) < 100:
            break
        page += 1
    merged.sort(key=lambda x: x["num"])
    json.dump(merged, open(os.path.join(DATA, "rfcs_merged.json"), "w"))
    print("rfcs: %d merged PRs at %s" % (len(merged), RFCS_SHA[:12]))

    tree = gh("repos/rust-lang/rfcs/git/trees/%s?recursive=1" % RFCS_SHA)
    texts = sorted(t["path"] for t in tree["tree"]
                   if t["path"].startswith("text/") and re.match(r"^text/\d{4}-.*\.md$", t["path"]))
    index = [{"rfc": int(re.match(r"^text/(\d{4})-", p).group(1)), "path": p} for p in texts]
    json.dump(index, open(os.path.join(DATA, "rfcs_text_index.json"), "w"))
    print("rfcs: %d numbered text/*.md in the tree at %s (paths only)" % (len(index), RFCS_SHA[:12]))


if __name__ == "__main__":
    main()
