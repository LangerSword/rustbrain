#!/usr/bin/env python3
"""Scrub contact fields from the vendored rust-lang/team TOML trees.

Policy: the repository carries no email addresses and no contact fields. The
product only reads team names, subteam links, header comments and the [people]
lists from the vendored tree; the contact-bearing fields (email, address,
extra-emails and any line carrying an address value, including bare strings in
multi-line arrays) are dropped. Everything else is left byte for byte.

Run after a fetch, or in place:
  python3 scripts/sanitize_contact_fields.py            scrub data/upstream/team/teams and repos
  python3 scripts/sanitize_contact_fields.py --check    report contacts that would be dropped, change nothing

scripts/fetch_upstream.py applies scrub_text() to every vendored TOML before it
is written, so a fresh fetch never lands contact fields on disk either.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEAM = os.path.join(HERE, "data", "upstream", "team")

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
CONTACT_KEY_RE = re.compile(r"^\s*(email|address|extra-emails)\s*=")


def _bracket_delta(line):
    """Net [ minus ] on a line, ignoring brackets inside quoted strings (none of the
    contact lines carry any, but keep it honest)."""
    depth, in_str, quote = 0, False, ""
    for c in line:
        if in_str:
            if c == quote:
                in_str = False
        elif c in "\"'":
            in_str, quote = True, c
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
    return depth


def scrub_text(text):
    """Return text with contact lines removed. A line is dropped when its key is a
    contact field (email, address, extra-emails) or when it carries an address
    value; dropping such a line also drops any multi-line array it opens, so the
    output stays valid TOML (a kept closer bracket would not parse). Comment words
    like 'email' stay: only lines with an actual address value are dropped."""
    kept, lines, i = [], text.splitlines(keepends=True), 0
    while i < len(lines):
        line = lines[i]
        if CONTACT_KEY_RE.match(line) or EMAIL_RE.search(line):
            depth = _bracket_delta(line)
            while depth > 0 and i + 1 < len(lines):
                i += 1
                depth += _bracket_delta(lines[i])
            i += 1
            continue
        kept.append(line)
        i += 1
    return "".join(kept)


def scrub_tree(root, check=False):
    changed = []
    for dirpath, _dirs, files in os.walk(root):
        for fn in sorted(files):
            if not fn.endswith(".toml"):
                continue
            p = os.path.join(dirpath, fn)
            with open(p, encoding="utf-8", errors="replace") as f:
                text = f.read()
            out = scrub_text(text)
            if out != text:
                changed.append(p)
                if not check:
                    with open(p, "w", encoding="utf-8") as f:
                        f.write(out)
    return changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    args = ap.parse_args()
    total = []
    for sub in ("teams", "repos"):
        root = os.path.join(TEAM, sub)
        changed = scrub_tree(root, check=args.check)
        total += changed
        print("%s/%s: %d files %s" % (sub, "*", len(changed),
              "would change" if args.check else "scrubbed"))
    for p in total[:10]:
        print("  " + os.path.relpath(p, HERE))
    if len(total) > 10:
        print("  ... and %d more" % (len(total) - 10))
    return 0


if __name__ == "__main__":
    sys.exit(main())
