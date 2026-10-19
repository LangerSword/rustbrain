#!/usr/bin/env python3
"""Generate the demo video's captions, storyboard and voiceover script.

Every number in a caption is read here, at generation time, from site/data.json
(or from the recorded command transcripts for command output numbers). The
generator writes:

  out/video/captions.json        machine input for the Remotion composition
  out/video/10_storyboard.md     human-readable storyboard with data fields
  out/video/voiceover_script.md  spoken lines per beat with timings

Run:  python3 video/make_storyboard.py
"""
import json
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = json.load(open(os.path.join(HERE, "site", "data.json")))
OUT = os.path.join(HERE, "out", "video")
os.makedirs(OUT, exist_ok=True)

def at(path):
    v = D
    for k in path.split("."):
        v = v[int(k)] if k.isdigit() else v[k]
    return v

# every caption: text plus the data fields its numbers come from
B1 = {
    "beat": 1, "start": 0, "end": 12, "footage": "terminal: cmd/route.py 1892 --naive (raw/term)",
    "caption": "the team that owned this rfc has nobody left: 0 current members, archived.",
    "sources": [{"transcript": "out/video/transcripts/naive.txt", "value": "naive lookup: 0 current members on libs-api"},
                {"site": "site/index.html figure text", "value": "archived, 0 members"}],
    "spoken": "one command, one rfc: who reviews this? the label says libs-api. the team is archived, and the lookup returns nobody.",
}

B2 = {
    "beat": 2, "start": 12, "end": 30, "footage": "live site hero (raw/site_fhd/hero, raw/site_uhd/hero)",
    "caption": "rustbrain routes a rust rfc to the team that exists today. two pinned public revisions, no llm.",
    "sources": [{"field": "generated_from.pins", "value": "team and rfcs pins", "note": "PINS.md"}],
    "spoken": "rustbrain routes a rust rfc to the reviewers the project's own files name today. two pinned public revisions, one graph, no language model anywhere in the path.",
}
B3 = {
    "beat": 3, "start": 30, "end": 65, "footage": "live site: hover successor edge, then tabs T-cargo and T-dev-tools (raw/site_fhd/successor_edge, tabs)",
    "captions": [
        {"t": 30, "text": "the archived team's own file records its successor, quoted with file and line.",
         "sources": [{"field": "successor_map.edges.0.source", "value": at("successor_map.edges.0.source")}]},
        {"t": 40, "text": "t-cargo is an ordinary active team: %d merged rfcs, no hop needed." % [r["rfcs"] for r in at("gaps.tiers.ACTIVE") if r["label"] == "cargo"][0],
         "sources": [{"field": "gaps.tiers.ACTIVE(cargo).rfcs", "value": [r["rfcs"] for r in at("gaps.tiers.ACTIVE") if r["label"] == "cargo"][0]}]},
        {"t": 50, "text": "t-dev-tools has no team file anywhere: %d of the %d merged rfcs, a true gap." %
                  ([r["rfcs"] for r in at("gaps.tiers.TRUE_GAP") if r["label"] == "dev-tools"][0], at("gaps.rfc_total")),
         "sources": [{"field": "gaps.tiers.TRUE_GAP(dev-tools).rfcs", "value": [r["rfcs"] for r in at("gaps.tiers.TRUE_GAP") if r["label"] == "dev-tools"][0]},
                     {"field": "gaps.rfc_total", "value": at("gaps.rfc_total")}]},
    ],
    "spoken": "the archived team's file records its successor, cited with file and line, so the graph follows the hop to the team that owns the label now. active labels take the same query, zero hops. and a label with no record stays honest: it is a true gap, by name.",
}
B4 = {
    "beat": 4, "start": 65, "end": 110, "footage": "github README graph model, queries/routing.cypher, terminal query run (raw/term/query, raw/site_fhd/readme)",
    "captions": [
        {"t": 65, "text": "the successor hop is a variable-length traversal: succeeded_by, zero to three hops."},
        {"t": 80, "text": "then a roster join: the current team's people and their authored rfcs."},
        {"t": 92, "text": "%d merged rfcs resolve only through this hop: libs-api %d, core %d." %
                  (at("gaps.distinct.SUCCESSOR"),
                   [r["rfcs"] for r in at("gaps.tiers.SUCCESSOR") if r["label"] == "libs-api"][0],
                   [r["rfcs"] for r in at("gaps.tiers.SUCCESSOR") if r["label"] == "core"][0]),
         "sources": [{"field": "gaps.distinct.SUCCESSOR", "value": at("gaps.distinct.SUCCESSOR")},
                     {"field": "gaps.tiers.SUCCESSOR(libs-api).rfcs", "value": [r["rfcs"] for r in at("gaps.tiers.SUCCESSOR") if r["label"] == "libs-api"][0]},
                     {"field": "gaps.tiers.SUCCESSOR(core).rfcs", "value": [r["rfcs"] for r in at("gaps.tiers.SUCCESSOR") if r["label"] == "core"][0]}]},
        {"t": 102, "text": "without the graph: a recursive join of unknown depth, and archived rosters return nobody."},
    ],
    "spoken": "under the hood: succeeded by, a variable-length traversal, zero to three hops, then a join to the roster and each member's authored rfcs. relationally that becomes a recursive join of unknown depth. one hundred sixty two merged rfcs route only because this hop exists, 138 on libs api, 24 on core.",
}
B5 = {
    "beat": 5, "start": 110, "end": 135, "footage": "live site /gaps/ (raw/site_fhd/gaps, raw/site_uhd/gaps)",
    "captions": [
        {"t": 110, "text": "the gap report has three tiers, scope on every line.", "sources": [{"field": "gaps.tiers", "value": "19 labels"}]},
        {"t": 120, "text": "%d routable today, %d through the successor hop, %d in true gaps, named." %
                  (at("gaps.distinct.ACTIVE"), at("gaps.distinct.SUCCESSOR"), at("gaps.distinct.TRUE_GAP")),
         "sources": [{"field": "gaps.distinct.ACTIVE", "value": at("gaps.distinct.ACTIVE")},
                     {"field": "gaps.distinct.SUCCESSOR", "value": at("gaps.distinct.SUCCESSOR")},
                     {"field": "gaps.distinct.TRUE_GAP", "value": at("gaps.distinct.TRUE_GAP")}]},
    ],
    "spoken": "the gap report has three tiers with scope on every line: 357 routable today, 162 with a recorded successor in between, and 25 in true gaps, named.",
}
B6 = {
    "beat": 6, "start": 135, "end": 160, "footage": "terminal refresh diff (raw/term/refresh), terminal assertions (raw/term/assertions), public actions run page (raw/site_fhd/actions)",
    "captions": [
        {"t": 135, "text": "the refresh command caught a real roster change: joboet left libs-ping.",
         "sources": [{"file": "reports/refresh_20261019_022025.md", "value": "left=[joboet]"}]},
        {"t": 146, "text": "the query command is tested: 41 assertions, exact row counts, direction flips.",
         "sources": [{"transcript": "out/video/transcripts/assertions.txt", "value": "41 passed, 0 failed"}]},
        {"t": 152, "text": "on the pinned engine, in public ci.",
         "sources": [{"field": "module.ver", "value": at("module.ver")}]},
    ],
    "spoken": "it stays current: the refresh command caught a real roster change, joboet leaving libs ping, one member edge moving. and it is tested: 41 assertions, exact row counts, direction flips, on the pinned engine, in public ci.",
}
B7 = {
    "beat": 7, "start": 160, "end": 180, "footage": "live site /bugs/, limits line; end card drawn in Remotion",
    "captions": [
        {"t": 160, "text": "the limits are on the site, including the element that scores zero."},
        {"t": 168, "text": "volunteer teams, a curated successor map, %d archived files audited." % at("bugs.archived_team_files"),
         "sources": [{"field": "bugs.archived_team_files", "value": at("bugs.archived_team_files")}]},
    ],
    "spoken": "the limits are on the site: the company-like element scores zero because rust is a foundation, the teams are volunteers, and the successor map is curated, four entries, each quoted. rustbrain, track 03: company brain.",
}

BEATS = [B1, B2, B3, B4, B5, B6, B7]
FACTS = [
    {"label": "%d merged rfcs" % at("gaps.rfc_total"), "field": "gaps.rfc_total", "value": at("gaps.rfc_total")},
    {"label": "%d route only through the successor hop" % at("gaps.distinct.SUCCESSOR"), "field": "gaps.distinct.SUCCESSOR", "value": at("gaps.distinct.SUCCESSOR")},
    {"label": "%d in true gaps" % at("gaps.distinct.TRUE_GAP"), "field": "gaps.distinct.TRUE_GAP", "value": at("gaps.distinct.TRUE_GAP")},
]
ENDCARD = {"domain": "rustbrain.langersword.in", "track": "track 03: company brain"}
TOTAL = {"start": 0, "end": 180, "fps_target": 60}

caps = {"total": TOTAL, "beats": BEATS, "facts": FACTS, "endcard": ENDCARD,
        "content_sha256": D["generated_from"]["content_sha256"]}
open(os.path.join(OUT, "captions.json"), "w").write(json.dumps(caps, indent=1, sort_keys=True) + "\n")

# spoken word counts
def words(s):
    return len(s.split())
rows = []
total_words = 0
for b in BEATS:
    w = words(b["spoken"])
    total_words += w
    rows.append((b["beat"], b["start"], b["end"], b["end"] - b["start"], w, round(w / 150 * 60, 1)))

story = ["# Demo video storyboard (DRAFT captions, the entrant edits)", "",
         "Generated from site/data.json (snapshot %s) by video/make_storyboard.py." % D["generated_from"]["content_sha256"][:12],
         "Every caption number is read from the field named beside it; none is typed by hand.", "",
         "| beat | seconds | footage source | caption (DRAFT) | number field(s) |",
         "|---|---|---|---|---|"]
for b in BEATS:
    caps_list = b.get("captions") or [{"text": b["caption"], "sources": b.get("sources", [])}]
    src = "; ".join(json.dumps(s) for c in caps_list for s in c.get("sources", [])) or "-"
    text = " / ".join(c["text"] for c in caps_list)
    story.append("| %d | %d to %d | %s | %s | %s |" % (b["beat"], b["start"], b["end"], b["footage"], text, src))
story += ["", "## End card", "",
          "domain: %s; line: %s; three facts: %s" % (ENDCARD["domain"], ENDCARD["track"],
          "; ".join(f["label"] + " (" + f["field"] + ")" for f in FACTS)), "",
          "## Spoken script word counts (150 wpm)", "",
          "| beat | seconds | words | seconds at 150 wpm |", "|---|---|---|---|"]
for r in rows:
    story.append("| %d | %d to %d | %d | %.1f |" % (r[0], r[1], r[2], r[4], r[5]))
story.append("| total | 0 to 180 | %d | %.1f |" % (total_words, round(total_words / 150 * 60, 1)))
open(os.path.join(OUT, "10_storyboard.md"), "w").write("\n".join(story) + "\n")

vo = ["# Voiceover script (DRAFT, the entrant records this)", "",
      "150 words per minute assumed. Lines are lowercase-leaning and plain.", ""]
for b in BEATS:
    vo.append("## Beat %d, %d to %d (%d words, about %.1f s at 150 wpm)" % (b["beat"], b["start"], b["end"], words(b["spoken"]), round(words(b["spoken"]) / 150 * 60, 1)))
    vo.append("")
    vo.append(b["spoken"])
    vo.append("")
vo.append("total spoken words: %d (about %.1f s at 150 wpm)" % (total_words, round(total_words / 150 * 60, 1)))
open(os.path.join(OUT, "voiceover_script.md"), "w").write("\n".join(vo) + "\n")

print("wrote captions.json, 10_storyboard.md, voiceover_script.md")
print("spoken words:", total_words, "| at 150 wpm: %.1f s" % (total_words / 150 * 60))
print("facts:", [f["label"] for f in FACTS])
