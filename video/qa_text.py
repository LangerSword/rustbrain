#!/usr/bin/env python3
"""Video QA: text scan and number audit (demo video rules 2, 4 and 5).

Numbers: every number that appears in a caption, storyboard caption or end
card must exist in one of these sources, read at check time:
  - site/data.json (all values, flattened)
  - the recorded command transcripts under out/video/transcripts/
  - the built site html under site/
Any number that cannot be found fails the check.

Text: flags em or en dashes, emoji, banned words, emails, local paths with a
home directory, and the entrant's username.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, "out", "video")


def flat_numbers(obj, acc):
    if isinstance(obj, dict):
        for v in obj.values():
            flat_numbers(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            flat_numbers(v, acc)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        acc.add(str(obj))
        if isinstance(obj, float) and obj.is_integer():
            acc.add(str(int(obj)))
    elif isinstance(obj, str):
        for m in re.finditer(r"\d+(?:\.\d+)?", obj):
            acc.add(m.group(0))


def collect_sources():
    allowed = set()
    flat_numbers(json.load(open(os.path.join(HERE, "site", "data.json"))), allowed)
    trdir = os.path.join(OUT, "transcripts")
    if os.path.isdir(trdir):
        for f in os.listdir(trdir):
            for m in re.finditer(r"\d+(?:\.\d+)?", open(os.path.join(trdir, f), encoding="utf-8", errors="replace").read()):
                allowed.add(m.group(0))
    for root, _d, files in os.walk(os.path.join(HERE, "site")):
        for f in files:
            if f.endswith(".html"):
                for m in re.finditer(r"\d+(?:\.\d+)?", open(os.path.join(root, f), encoding="utf-8", errors="replace").read()):
                    allowed.add(m.group(0))
    return allowed


def gather_video_text():
    texts = {}
    caps = json.load(open(os.path.join(OUT, "captions.json")))
    blobs = []
    for b in caps["beats"]:
        if b.get("captions"):
            blobs += [c["text"] for c in b["captions"]]
        if b.get("caption"):
            blobs.append(b["caption"])
        blobs.append(b["spoken"])
    blobs += [f["label"] for f in caps["facts"]]
    blobs.append(caps["endcard"]["domain"])
    blobs.append(caps["endcard"]["track"])
    texts["captions.json"] = blobs
    return texts


def main():
    bad = []
    allowed = collect_sources()
    texts = gather_video_text()
    banned = ("purple", "glassmorphism", "stock footage", "stock audio", "lorem",
              "placeholder", "todo", "fixme", "dummy", "mock", "fake")
    for name, blobs in texts.items():
        for b in blobs:
            if "\u2014" in b or "\u2013" in b:
                bad.append("%s: em or en dash in %r" % (name, b[:60]))
            if re.search(r"[\U0001F300-\U0001FAFF\u2600-\u27BF]", b):
                bad.append("%s: emoji in %r" % (name, b[:60]))
            low = b.lower()
            for w in banned:
                if w in low:
                    bad.append("%s: banned word %r in %r" % (name, w, b[:60]))
            if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", b):
                bad.append("%s: email in %r" % (name, b[:60]))
            if "/home/" in b or "C:\\\\" in b or "~/" in b:
                bad.append("%s: path in %r" % (name, b[:60]))
            if "lakshaya" in low or "lakshayasharma" in low:
                bad.append("%s: username in %r" % (name, b[:60]))
            if b[:1].isupper():
                pass  # lowercase leaning, not enforced
            for m in re.finditer(r"\d+(?:\.\d+)?", b):
                if m.group(0) not in allowed:
                    bad.append("%s: number %s not in data.json, transcripts or site html, in %r" % (name, m.group(0), b[:70]))
    print("numbers allowed from sources:", len(allowed))
    if bad:
        for x in bad:
            print("DEFECT:", x)
        print("VERDICT: FAIL, %d issues" % len(bad))
        return 1
    print("VERDICT: PASS, every caption number is sourced and the text scan is clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
