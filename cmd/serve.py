#!/usr/bin/env python3
"""rustbrain serve: a one-page UI over the graph. No LLM, no build step, no npm.

Type an RFC number or a T-* label, see the team chain, the reviewers, and the gap
flag. Serves one HTML page plus two JSON endpoints, all from the local graph.

Usage:  python3 cmd/serve.py [port]        then open http://127.0.0.1:8788
"""
import json
import os
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "scripts"))
sys.path.insert(0, os.path.join(HERE, "cmd"))
from load_graph import Resp, GRAPH  # noqa: E402

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>rustbrain</title>
<style>
  :root {
    --ink: #16130f; --paper: #f4f1ea; --rule: #d8d2c4;
    --accent: #a8340f; --muted: #6f6555; --ok: #2f5d3a; --warn: #8a5300;
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--paper); color: var(--ink);
         font: 15px/1.5 ui-monospace, SFMono-Regular, Menlo, monospace; }
  header { border-bottom: 2px solid var(--ink); padding: 20px 24px 14px; }
  h1 { margin: 0 0 4px; font-size: 20px; letter-spacing: .04em; }
  header p { margin: 0; color: var(--muted); font-size: 13px; }
  main { padding: 24px; max-width: 1080px; }
  form { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 22px; }
  input { font: inherit; padding: 9px 11px; border: 1px solid var(--ink);
          background: #fff; min-width: 300px; }
  button { font: inherit; padding: 9px 16px; border: 1px solid var(--ink);
           background: var(--ink); color: var(--paper); cursor: pointer; }
  button.alt { background: transparent; color: var(--ink); }
  section { border-top: 1px solid var(--rule); padding: 16px 0; }
  .label { font-weight: 700; font-size: 16px; }
  .tier { display: inline-block; font-size: 12px; padding: 2px 7px; border: 1px solid;
          margin-left: 8px; vertical-align: 1px; }
  .tier-ACTIVE { color: var(--ok); border-color: var(--ok); }
  .tier-SUCCESSOR { color: var(--warn); border-color: var(--warn); }
  .tier-TRUE_GAP { color: var(--accent); border-color: var(--accent); }
  .route { color: var(--muted); font-size: 13.5px; margin: 6px 0 12px; }
  .route b { color: var(--ink); }
  table { border-collapse: collapse; width: 100%; }
  th, td { text-align: left; padding: 5px 10px 5px 0; border-bottom: 1px solid var(--rule); }
  th { font-size: 12px; text-transform: uppercase; letter-spacing: .07em;
       color: var(--muted); font-weight: 600; }
  td.num { text-align: right; font-variant-numeric: tabular-nums; }
  .lead { color: var(--accent); }
  .gap { border-left: 4px solid var(--accent); padding: 12px 14px;
         background: #fdf6f2; margin: 10px 0; }
  .gap strong { color: var(--accent); }
  footer { border-top: 1px solid var(--rule); padding: 16px 24px 40px;
           color: var(--muted); font-size: 12.5px; max-width: 1080px; }
  .hint { color: var(--muted); font-size: 13px; }
</style>
</head>
<body>
<header>
  <h1>rustbrain</h1>
  <p>Route a Rust RFC to the reviewers its own team files name. Archived teams are followed to their recorded successor. No LLM.</p>
</header>
<main>
  <form id="f">
    <input id="q" placeholder="RFC number, or a T-* label (e.g. 1892, T-libs-api)" autofocus>
    <button type="submit">Route</button>
    <button class="alt" type="button" id="gaps">Show all routing gaps</button>
  </form>
  <div id="out"><p class="hint">Data: rust-lang/team and rust-lang/rfcs at the revisions in PINS.md. Handles only.</p></div>
</main>
<footer>
  A label whose team was archived is not a dead end: the graph follows a curated
  successor edge (source file and line recorded) to the active team. A label with no
  successor and no active team is reported as a true gap, not silently dropped.
</footer>
<script>
const out = document.getElementById('out');
const q = document.getElementById('q');

// Every interpolated string below comes from public GitHub records (team slugs,
// label names, PR titles, handles). Handles are alphanumeric plus hyphen, but a
// label name is free-form, so all strings are escaped before they reach innerHTML.
function esc(v) {
  return String(v === null || v === undefined ? '' : v)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
function tierBadge(t) { return `<span class="tier tier-${esc(t)}">${esc(t)}</span>`; }

function renderBlocks(blocks) {
  out.innerHTML = '';
  if (!blocks.length) { out.innerHTML = '<p class="hint">No matching label.</p>'; return; }
  for (const b of blocks) {
    const s = document.createElement('section');
    let html = `<div class="label">${esc(b.label)}${tierBadge(b.tier)}</div>`;
    if (b.rfcs !== null && b.rfcs !== undefined)
      html += `<div class="route">${esc(b.rfcs)} merged RFCs carry this label</div>`;
    if (b.chain && b.chain.length) {
      const c = b.chain[0];
      html += c.final === c.labelled
        ? `<div class="route">route: <b>${esc(c.labelled)}</b> (${esc(c.status)}), no successor hop needed</div>`
        : `<div class="route">route: <b>${esc(c.labelled)}</b> (${esc(c.status)}) &rarr; <b>${esc(c.final)}</b> via SUCCEEDED_BY`
          + ` <span class="hint">(RFC ${esc(c.rfc || 'not recorded')}, ${esc(c.source || '')})</span></div>`;
    }
    if (b.tier === 'TRUE_GAP') {
      html += `<div class="gap"><strong>Routing gap.</strong> No active team owns this label,`
            + ` so there is nobody to route to. Create the team, re-point the label, or stop using it.</div>`;
    } else if (b.people && b.people.length) {
      html += `<table><thead><tr><th>handle</th><th>role</th><th class="num">authored</th>`
            + `<th class="num">latest</th></tr></thead><tbody>`;
      for (const p of b.people) {
        html += `<tr><td>${esc(p.handle)}</td><td class="${p.role === 'lead' ? 'lead' : ''}">${esc(p.role)}</td>`
              + `<td class="num">${esc(p.authored)}</td><td class="num">${esc(p.latest || '-')}</td></tr>`;
      }
      html += `</tbody></table>`;
    } else {
      html += `<div class="gap">team exists but reports 0 current members.</div>`;
    }
    s.innerHTML = html;
    out.appendChild(s);
  }
}

async function route(target) {
  const r = await fetch('/api/route?target=' + encodeURIComponent(target));
  const d = await r.json();
  renderBlocks(d.blocks);
}

// ?q=T-libs-api auto-routes on load, so a screenshot or a shared link shows a
// real result instead of an empty form.
const pre = new URLSearchParams(location.search).get('q');
if (pre) { q.value = pre; route(pre); }

document.getElementById('f').addEventListener('submit', e => {
  e.preventDefault();
  const t = q.value.trim();
  if (t) route(t);
});
document.getElementById('gaps').addEventListener('click', async () => {
  const r = await fetch('/api/gaps');
  const d = await r.json();
  out.innerHTML = `<h3 style="margin:.2em 0 .6em">All labels in use, worst first</h3>`;
  const s = document.createElement('section');
  let html = `<table><thead><tr><th>label</th><th>tier</th><th class="num">RFCs</th>`
           + `<th>successor</th></tr></thead><tbody>`;
  for (const g of d.labels) {
    html += `<tr><td>${esc(g.label)}</td><td>${tierBadge(g.tier)}</td>`
          + `<td class="num">${esc(g.rfcs)}</td><td>${esc(g.successor || '-')}</td></tr>`;
  }
  html += `</tbody></table>`;
  s.innerHTML = html;
  out.appendChild(s);
});
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, fmt, *a):
        sys.stderr.write("[serve] %s\n" % (fmt % a))

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path in ("/", "/index.html"):
            return self._send(200, PAGE, "text/html; charset=utf-8")
        if u.path == "/api/route":
            target = urllib.parse.parse_qs(u.query).get("target", [""])[0]
            return self._send(200, json.dumps(route_target(target)), "application/json")
        if u.path == "/api/gaps":
            return self._send(200, json.dumps(gap_list()), "application/json")
        return self._send(404, "not found", "text/plain")


def parse_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v]
    s = str(v).strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    return [x.strip() for x in s.split(",") if x.strip()]


CHAIN = ("MATCH (labelled:Team {slug:$slug}) "
         "OPTIONAL MATCH path = (labelled)-[:SUCCEEDED_BY*1..3]->(owner:Team) "
         "RETURN labelled.slug, labelled.status, "
         "CASE WHEN owner IS NULL THEN labelled.slug ELSE owner.slug END, "
         "CASE WHEN owner IS NULL THEN coalesce(labelled.successor_team,'') ELSE '' END, "
         "CASE WHEN owner IS NULL THEN '' ELSE owner.slug END")


def route_target(target):
    conn = Resp()
    labels = []
    if target.isdigit():
        rows = conn.q(GRAPH, "MATCH (r:RFC {num:%s}) RETURN r.team_labels" % target).rows
        if rows:
            labels = [("T-" + l, None) for l in parse_list(rows[0][0])]
        else:
            return {"blocks": [], "note": "RFC %s is not in the corpus" % target}
    else:
        s = target[2:].lower() if target.lower().startswith("t-") else target.lower()
        labels = [("T-" + s, s)]

    blocks = []
    for disp, slug in labels:
        slug = slug or disp[2:].lower()
        row = conn.q(GRAPH, CHAIN.replace("$slug", "'%s'" % slug)).rows
        tier = "TRUE_GAP"
        chain = []
        if row:
            lab, status, final, succ_field, successor = row[0]
            if status == "active":
                tier = "ACTIVE"
            elif successor:
                tier = "SUCCESSOR"
            chain = [{"labelled": lab, "status": status, "final": final,
                      "successor": successor, "rfc": None, "source": None}]
            if successor:
                src = conn.q(GRAPH, "MATCH (a:Team {slug:'%s'})-"
                                    "[r:SUCCEEDED_BY]->(b:Team {slug:'%s'}) "
                                    "RETURN r.rfc, r.source" % (slug, successor)).rows
                if src:
                    chain[0]["rfc"] = src[0][0]
                    chain[0]["source"] = src[0][1]
        people = []
        if tier in ("ACTIVE", "SUCCESSOR"):
            owner = chain[0]["final"]
            # ORDER BY must reference the COALESCED alias. Ordering on the raw
            # max() puts null dates FIRST under DESC on this build, which buries the
            # most recent reviewer at the bottom of the table. Measured 2026-10-19.
            q = ("MATCH (o:Team {slug:'%s'}) MATCH (o)<-[r:LEAD|MEMBER]-(p:Person) "
                 "OPTIONAL MATCH (p)-[:AUTHORED]->(a:RFC) "
                 "WITH o,p,collect(DISTINCT type(r)) AS k, count(DISTINCT a) AS n, max(a.created) AS lt "
                 "RETURN p.handle AS handle, "
                 "CASE WHEN 'LEAD' IN k THEN 'lead' ELSE 'member' END AS role, "
                 "n AS authored, coalesce(lt,'') AS latest "
                 "ORDER BY latest DESC, n DESC, p.handle" % owner)
            people = [{"handle": h, "role": r_, "authored": int(n),
                       "latest": lt} for h, r_, n, lt in conn.q(GRAPH, q).rows]
        rfcs = conn.q(GRAPH, "MATCH (r:RFC) WHERE '%s' IN r.team_labels "
                             "RETURN count(DISTINCT r)" % slug).rows[0][0]
        blocks.append({"label": disp, "tier": tier, "chain": chain,
                       "people": people, "rfcs": int(rfcs)})
    return {"blocks": blocks}


def gap_list():
    conn = Resp()
    rows = conn.q(GRAPH,
                  "MATCH (r:RFC) UNWIND r.team_labels AS l WITH l, count(DISTINCT r) AS n "
                  "OPTIONAL MATCH (t:Team {slug:l}) "
                  "OPTIONAL MATCH (t)-[:SUCCEEDED_BY]->(s:Team) "
                  "RETURN l, n, CASE WHEN t IS NULL THEN 'TRUE_GAP' "
                  "WHEN t.status='active' THEN 'ACTIVE' WHEN s IS NOT NULL THEN 'SUCCESSOR' "
                  "ELSE 'TRUE_GAP' END, coalesce(s.slug,'') "
                  "ORDER BY CASE WHEN t IS NULL THEN 'TRUE_GAP' "
                  "WHEN t.status='active' THEN 'ACTIVE' WHEN s IS NOT NULL THEN 'SUCCESSOR' "
                  "ELSE 'TRUE_GAP' END, n DESC").rows
    order = {"TRUE_GAP": 0, "SUCCESSOR": 1, "ACTIVE": 2}
    labels = [{"label": l, "rfcs": int(n), "tier": t, "successor": s} for l, n, t, s in rows]
    labels.sort(key=lambda x: (order[x["tier"]], -x["rfcs"]))
    return {"labels": labels}


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8788
    srv = HTTPServer(("127.0.0.1", port), Handler)
    print("rustbrain UI on http://127.0.0.1:%d" % port)
    print("try: an RFC number such as 1892, or a label such as T-libs-api")
    srv.serve_forever()


if __name__ == "__main__":
    main()
