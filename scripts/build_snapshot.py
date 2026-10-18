#!/usr/bin/env python3
"""Build the deterministic, metadata-only snapshot. Offline. No network in CI.

Inputs (all committed, fetched once into data/ by scripts/fetch_*.py):
  data/upstream/team/            rust-lang/team git tree at the pinned SHA
  data/rfcs_merged.json          merged PR metadata (no bodies)
  data/rfcs_text_index.json      text/NNNN-*.md paths (no bodies)

Output:
  data/snapshot.json             byte-identical across runs; carries content_sha256

Store policy, enforced here and nowhere else:
  handles only, no real names, no emails, no RFC bodies, titles capped at 120 chars.

Usage:
  python3 scripts/build_snapshot.py              write data/snapshot.json
  python3 scripts/build_snapshot.py --check      rebuild and exit 1 on ANY drift
  python3 scripts/build_snapshot.py --write-pins regenerate PINS.md from PINS/PIN_META
"""
import argparse
import hashlib
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(HERE, "data")
TEAM = os.path.join(DATA, "upstream", "team")

# --- Pinned revisions: THE single source of truth ------------------------------
# PINS.md is GENERATED from this block. Never hand-edit it; run
# `python3 cmd/refresh.py --pin` (or `python3 scripts/build_snapshot.py --write-pins`).
# scripts/fetch_upstream.py and scripts/fetch_rfcs.py import their pins from here,
# so a revision can only change in one place.
PINS = {"team": "a5176049c11ca092994af7a07deb4f62dfe4b55c",
        "rfcs": "d2705ad64ba47e812a2b6b19d6f613fb4c14c5e0"}

FALKORDB_IMAGE = "falkordb/falkordb"
# falkordb/falkordb:latest, AMD64 manifest-list digest, read 2026-10-16.
FALKORDB_DIGEST = "sha256:b0bdcac2cbaff989e77cb0610439b7a9289e86de033ccbbd4368b66fb680ae7a"

# Everything PINS.md reports beyond the raw revision. `retrieved` is the date this
# project actually pulled those bytes; `note` anchors the revision to upstream.
PIN_META = {
    "team": {"source": "github.com/rust-lang/team", "retrieved": "2026-10-19",
             "note": "committer date 2026-10-18T11:10:22Z"},
    "rfcs": {"source": "github.com/rust-lang/rfcs", "retrieved": "2026-10-16",
             "note": "committer date 2026-10-05T10:04:13Z"},
    "falkordb": {"source": "docker.io/falkordb/falkordb", "revision": FALKORDB_DIGEST,
                 "retrieved": "2026-10-16",
                 "note": "amd64 manifest-list digest, module reports ver 42201 (v4.22.1)"},
}


def render_pins_md():
    """Render PINS.md from PINS, FALKORDB_DIGEST and PIN_META. No other input."""
    rows = []
    for key in ("team", "rfcs", "falkordb"):
        m = PIN_META[key]
        rev = m.get("revision") or PINS[key]
        rows.append("| %s | %s | %s | %s |" % (m["source"], rev, m["retrieved"], m["note"]))
    return "\n".join([
        "# Pinned upstream revisions",
        "",
        "**generated, do not edit.** Source of truth: `scripts/build_snapshot.py`.",
        "Regenerate with `python3 cmd/refresh.py --pin`.",
        "",
        "Every number this project reports is derived from these revisions. Change them",
        "deliberately, never implicitly.",
        "",
        "| source | revision | retrieved | note |",
        "|---|---|---|---|",
    ] + rows + [
        "",
        "## Data policy",
        "",
        "Public GitHub data only. The repository carries no email addresses and no contact",
        "fields. The product's stores hold handles only: no real names, no email addresses,",
        "no avatar URLs, no RFC bodies; RFC titles are truncated to 120 characters. The",
        "pinned team tree is committed under data/upstream/team so CI needs no network. It",
        "holds the teams/ and repos/ TOMLs with contact fields stripped at fetch time by",
        "scripts/sanitize_contact_fields.py, plus a handles-only people_handles.txt derived",
        "from upstream's people files at fetch time (those files are never written to disk).",
        "CI reads the committed tree plus data/snapshot.json.",
        "",
    ])


def write_pins(path=None):
    path = path or os.path.join(HERE, "PINS.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(render_pins_md())
    return path

# Order matters: first match wins.
DISPOSITIONS = ("merge", "approve", "reject", "postpone")


def read(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def people_block(text):
    m = re.search(r"\[people\](.*?)(\n\[|\Z)", text, re.S)
    return m.group(1) if m else ""


def list_block(block, key):
    """Return the raw text INSIDE `key = [ ... ]`, or None if the key is absent.

    Bracket-matched, so it handles a one-line list (`leads = ["a", "b"]`), a
    multi-line list, an empty list (`members = []`), and a list whose closing
    bracket sits on a later line. A regex cannot do this safely: a non-greedy match
    on `members = []` followed by `alumni = [...]` runs past the empty list and
    swallows the alumni handles, and a line-based scan on a one-line `leads = [..]`
    runs into the NEXT list. Both bugs were live here before this function.
    """
    m = re.search(r"^[ \t]*" + key + r"[ \t]*=[ \t]*\[", block, re.M)
    if not m:
        return None
    i, depth, in_str, quote = m.end(), 1, False, ""
    start = i
    while i < len(block):
        c = block[i]
        if in_str:
            if c == quote:
                in_str = False
        elif c in "\"'":
            in_str, quote = True, c
        elif c == "[":
            depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0:
                return block[start:i]
        i += 1
    return block[start:]


def str_list(block, key):
    """Plain handle list: members = ["a", "b"]"""
    seg = list_block(block, key)
    if not seg:
        return []
    return [h for h in re.findall(r"[\"']([^\"']+)[\"']", seg) if h]


def obj_list(block, key):
    """Inline table list, as used by leadership-council, mentees, maintainers-in-residence
       and part of compiler:
       members = [ { github = "lqd", roles = ["council-rep-compiler"] }, ... ]
       MEASURED 2026-10-16: 4 of 224 team files use this shape. Both are parsed."""
    seg = list_block(block, key)
    if not seg:
        return []
    out = []
    for entry in re.findall(r"\{([^}]*)\}", seg):
        g = re.search(r"github\s*=\s*[\"']([^\"']+)[\"']", entry)
        if not g:
            continue
        rm = re.search(r"roles\s*=\s*\[([^\]]*)\]", entry)
        roles = re.findall(r"[\"']([^\"']+)[\"']", rm.group(1)) if rm else []
        out.append({"handle": g.group(1), "roles": sorted(set(roles))})
    return out


def str_list_without_objs(block, key):
    """Plain strings in the SAME list as inline tables, which is how compiler.toml is
       written (22 objects and 55 strings in one members list). Braces are stripped
       first so the object keys are not read as handles."""
    seg = list_block(block, key)
    if not seg:
        return []
    seg = re.sub(r"\{[^}]*\}", "", seg)
    return [h for h in re.findall(r"[\"']([^\"']+)[\"']", seg) if h]


def parse_team(path, status):
    text = read(path)
    slug = os.path.basename(path)[:-5]
    name = re.search(r'^name\s*=\s*["\']([^"\']+)', text, re.M)
    sub = re.search(r'^subteam-of\s*=\s*["\']([^"\']+)', text, re.M)
    successor_note = successor_team = successor_rfc = None
    m = re.search(r"^#\s*(.+?)\s*$", text, re.M)
    if m:
        successor_note = m.group(1)
        rm = re.search(r"RFC\s*#?(\d+)", successor_note)
        if rm:
            successor_rfc = int(rm.group(1))
        inh = re.search(r"incorporated into\s+([A-Za-z0-9 _-]+?)\s+with", successor_note)
        rep = re.search(r"replaced by the\s+([A-Za-z0-9 _-]+?)\s+with", successor_note)
        if inh:
            successor_team = inh.group(1).strip().lower().replace(" ", "-")
        elif rep:
            successor_team = rep.group(1).strip().lower().replace(" ", "-")
    blk = people_block(text)
    leads = str_list(blk, "leads")
    members = [{"handle": h, "roles": []} for h in str_list_without_objs(blk, "members")] + obj_list(blk, "members")
    # alumni can ALSO hold inline tables (compiler and mentees both do), so it takes
    # the same two-pass treatment as members. A plain string scan would count the
    # role names ("compiler-maintainer", "gsoc") as handles.
    alumni = sorted(set(str_list_without_objs(blk, "alumni")) | {o["handle"] for o in obj_list(blk, "alumni")})
    merged = {}
    for m_ in members:
        merged.setdefault(m_["handle"], set()).update(m_["roles"])
    return {
        "slug": slug,
        "name": name.group(1) if name else slug,
        "status": status,
        "subteam_of": sub.group(1) if sub else None,
        "leads": sorted(set(leads)),
        "members": sorted((h, sorted(r)) for h, r in merged.items()),
        "alumni": alumni,
        "successor_note": successor_note,
        "successor_rfc": successor_rfc,
        "successor_team": successor_team,
    }


def resolve_successor(teams, slug_hint):
    """The comment says 'incorporated into Library', but the team SLUG is 'libs'.
       Resolve a human-readable hint to a real team slug by trying slug, then name,
       then a light singular/plural trim, and return None rather than guessing."""
    if not slug_hint:
        return None
    cands = {slug_hint, slug_hint + "s", slug_hint.rstrip("s")}
    for s in cands:
        if s in teams:
            return s
    for t in teams.values():
        if (t["name"] or "").strip().lower() == slug_hint:
            return t["slug"]
    return None


def load_successors(teams):
    """Read data/successors.yaml, a CURATED file with a cited source line per entry.

    The ingest deliberately does NOT parse successor hints out of team comments at
    runtime. A curated map with a file and line number per entry is auditable; a
    comment scraper is not, and it silently mis-maps when a comment is reworded.
    Every field is validated here so a typo fails the build instead of producing a
    wrong route.
    """
    path = os.path.join(DATA, "successors.yaml")
    if not os.path.exists(path):
        raise SystemExit("FAIL: missing %s" % path)
    doc = yaml.safe_load(read(path)) or {}
    edges, problems = {}, []
    for e in doc.get("successors") or []:
        for k in ("from", "to", "source_file", "source_line", "quote"):
            if not e.get(k):
                problems.append("entry missing %s: %r" % (k, e))
        if e.get("from") not in teams:
            problems.append("from-team %r is not a known team" % e.get("from"))
        elif teams[e["from"]]["status"] != "archived":
            problems.append("from-team %r is not archived" % e["from"])
        if e.get("to") not in teams:
            problems.append("to-team %r is not a known team" % e.get("to"))
        elif teams[e["to"]]["status"] != "active":
            problems.append("to-team %r is not active" % e["to"])
        # The cited source must actually contain the quote on that line.
        sf = os.path.join(TEAM, e.get("source_file", ""))
        if not os.path.exists(sf):
            problems.append("source_file missing: %s" % e.get("source_file"))
        else:
            lines = read(sf).splitlines()
            n = int(e.get("source_line") or 0)
            if not (1 <= n <= len(lines)) or e["quote"] not in lines[n - 1]:
                problems.append("quote not found at %s:%s" % (e.get("source_file"), n))
        edges[e["from"]] = e
    if problems:
        for p in problems:
            print("SUCCESSOR MAP PROBLEM: " + p)
        raise SystemExit("FAIL: successors.yaml did not validate")
    return edges


def collect_teams():
    teams = {}
    base = os.path.join(TEAM, "teams")
    for fn in sorted(os.listdir(base)):
        if fn.endswith(".toml"):
            t = parse_team(os.path.join(base, fn), "active")
            teams[t["slug"]] = t
    arch = os.path.join(base, "archive")
    for fn in sorted(os.listdir(arch)):
        if fn.endswith(".toml"):
            t = parse_team(os.path.join(arch, fn), "archived")
            teams.setdefault(t["slug"], t)   # an active file always wins
    return teams


def build():
    teams = collect_teams()
    successors = load_successors(teams)
    for t in teams.values():
        e = successors.get(t["slug"])
        t["successor_team"] = e["to"] if e else None
        t["successor_source"] = ("%s:%s" % (e["source_file"], e["source_line"])) if e else None
        t["successor_quote"] = e["quote"] if e else None
        t["successor_rfc"] = e.get("rfc") if e else None
        t["successor_resolved"] = e["to"] if e else None
    people = {}

    def touch(h):
        people.setdefault(h, {"handle": h, "member_of": [], "lead_of": [], "alumni_of": []})

    for slug in sorted(teams):
        t = teams[slug]
        for h in t["leads"]:
            touch(h)
            people[h]["lead_of"].append(slug)
            people[h]["member_of"].append(slug)
        for h, _roles in t["members"]:
            touch(h)
            people[h]["member_of"].append(slug)
        for h in t["alumni"]:
            touch(h)
            people[h]["alumni_of"].append(slug)
    for h in people:
        for k in ("member_of", "lead_of", "alumni_of"):
            people[h][k] = sorted(set(people[h][k]))
        people[h]["on_active_team"] = any(teams[s]["status"] == "active" for s in people[h]["member_of"])

    docs = {d["rfc"]: d["path"] for d in json.load(open(os.path.join(DATA, "rfcs_text_index.json")))}
    rfcs = []
    for r in json.load(open(os.path.join(DATA, "rfcs_merged.json"))):
        if "not-rfc" in r["labels"]:
            continue
        outcome = next((o for o in DISPOSITIONS if "disposition-" + o in r["labels"]), "none")
        rfcs.append({
            "num": r["num"], "title": (r["title"] or "")[:120], "outcome": outcome,
            "created": (r["created_at"] or "")[:10], "merged_at": (r["merged_at"] or "")[:10],
            "author": r["user"], "author_assoc": r.get("assoc") or "NONE",
            "team_labels": sorted({l[2:].lower() for l in r["labels"] if l.lower().startswith("t-")}),
            "document": docs.get(r["num"]),
        })
    rfcs.sort(key=lambda x: x["num"])

    snap = {
        "schema_version": 3,
        "pins": PINS,
        "falkordb_image": {"name": FALKORDB_IMAGE, "digest": FALKORDB_DIGEST},
        "successor_map": {
            "curated": True,
            "file": "data/successors.yaml",
            "note": ("Hand-checked, one cited source file and line per entry. Not parsed "
                     "from comments at runtime."),
            "edges": [
                {
                    "from": e["from"], "to": e["to"], "rfc": e.get("rfc"),
                    "source": "%s:%s" % (e["source_file"], e["source_line"]),
                    "quote": e["quote"],
                }
                for _s, e in sorted(successors.items())
            ],
            "unmapped": [
                {"team": u["team"], "reason": " ".join(str(u["reason"]).split())}
                for u in (yaml.safe_load(read(os.path.join(DATA, "successors.yaml"))) or {}).get("unmapped", [])
            ],
        },
        "counts": {
            "teams_total": len(teams),
            "teams_active": sum(1 for t in teams.values() if t["status"] == "active"),
            "teams_archived": sum(1 for t in teams.values() if t["status"] == "archived"),
            "roster_edges_lead": sum(len(t["leads"]) for t in teams.values()),
            "roster_edges_member": sum(len(t["members"]) for t in teams.values()),
            "roster_edges_roster": sum(len(t["leads"]) + len(t["members"]) for t in teams.values()),
            "roster_edges_alumni": sum(len(t["alumni"]) for t in teams.values()),
            "successor_edges": len(successors),
            "people": len(people),
            "people_on_active_team": sum(1 for p in people.values() if p["on_active_team"]),
            "rfcs": len(rfcs),
            "documents": sum(1 for r in rfcs if r["document"]),
        },
        "teams": teams,
        "people": people,
        "rfcs": rfcs,
    }
    body = json.dumps(snap, sort_keys=True, indent=1, ensure_ascii=True)
    snap["content_sha256"] = hashlib.sha256(body.encode()).hexdigest()
    return snap


def strip_and_hash(doc):
    """Hash a snapshot document EXACTLY as build() does: same serialisation, with
    the content_sha256 field removed. Used to prove the on-disk file is intact."""
    d = {k: v for k, v in doc.items() if k != "content_sha256"}
    body = json.dumps(d, sort_keys=True, indent=1, ensure_ascii=True)
    return hashlib.sha256(body.encode()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write-pins", action="store_true",
                    help="regenerate PINS.md from PINS/PIN_META and exit")
    args = ap.parse_args()
    if args.write_pins:
        print("wrote %s" % write_pins())
        return 0
    snap = build()
    path = os.path.join(DATA, "snapshot.json")
    if args.check:
        if not os.path.exists(path):
            print("FAIL: no committed snapshot")
            return 1
        old = json.load(open(path))
        # Check 1: the FILE ON DISK must hash to the value recorded inside it.
        # Without this, editing a number in the committed snapshot still passed.
        on_disk = strip_and_hash(old)
        if old.get("content_sha256") != on_disk:
            print("FAIL: committed snapshot is corrupt, recorded=%s actual=%s"
                  % (old.get("content_sha256"), on_disk))
            return 1
        # Check 2: rebuilding from the pinned sources must reproduce that same hash.
        if snap["content_sha256"] != old["content_sha256"]:
            print("FAIL: drift, committed=%s rebuilt=%s"
                  % (old["content_sha256"], snap["content_sha256"]))
            return 1
        print("PASS: file intact and byte-identical rebuild, sha256=%s" % snap["content_sha256"])
        return 0
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(snap, sort_keys=True, indent=1, ensure_ascii=True))
    print("wrote %s" % path)
    print("content_sha256=%s" % snap["content_sha256"])
    print(json.dumps(snap["counts"], sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
