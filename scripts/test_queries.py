#!/usr/bin/env python3
"""Query tests: exact rows, non-zero row counts, AND direction-flip checks.

The direction-flip assertions are the point. A Cypher pattern that matches nothing
returns ZERO ROWS with no error, so a query written against the wrong arrow looks
like a correct empty answer. For each real query there is a flipped twin that MUST
return zero; if the flipped twin ever returns rows, the schema changed under us.

Run:  python3 scripts/test_queries.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "scripts"))
from load_graph import Resp, GRAPH  # noqa: E402

QUERIES = os.path.join(HERE, "queries")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def strip_comments(cypher):
    return "\n".join(l for l in cypher.splitlines() if not l.strip().startswith("//"))


class Check:
    def __init__(self, conn):
        self.conn = conn
        self.passed = self.failed = 0

    def rowcount(self, label, cypher, want=None, expect_nonzero=True):
        n = len(self.conn.q(GRAPH, cypher).rows)
        ok = (n > 0) if expect_nonzero else (n == 0)
        if want is not None:
            ok = ok and (n == want)
        print("  %-58s rows=%-5s %s" % (label, n, "PASS" if ok else "FAIL"))
        self.passed += ok
        self.failed += (not ok)
        return n

    def value(self, label, cypher, want):
        rows = self.conn.q(GRAPH, cypher).rows
        got = rows[0][0] if rows else None
        ok = str(got) == str(want)
        print("  %-58s got=%-8s want=%-8s %s" % (label, got, want, "PASS" if ok else "FAIL"))
        self.passed += ok
        self.failed += (not ok)
        return got


def main():
    snap = json.load(open(os.path.join(HERE, "data", "snapshot.json")))
    c = snap["counts"]
    conn = Resp()
    t = Check(conn)

    print("== graph totals, pinned to the snapshot ==")
    t.value("teams", "MATCH (n:Team) RETURN count(n)", c["teams_total"])
    t.value("people", "MATCH (n:Person) RETURN count(n)", c["people"])
    t.value("rfcs", "MATCH (n:RFC) RETURN count(n)", c["rfcs"])
    t.value("documents", "MATCH (n:Document) RETURN count(n)", c["documents"])
    t.value("MEMBER edges", "MATCH ()-[r:MEMBER]->() RETURN count(r)", c["roster_edges_member"])
    t.value("LEAD edges", "MATCH ()-[r:LEAD]->() RETURN count(r)", c["roster_edges_lead"])
    t.value("SUCCEEDED_BY edges", "MATCH ()-[r:SUCCEEDED_BY]->() RETURN count(r)", c["successor_edges"])
    t.rowcount("GOVERNED edges exist", "MATCH ()-[r:GOVERNED]->() RETURN r LIMIT 1")
    t.rowcount("AUTHORED edges exist", "MATCH ()-[r:AUTHORED]->() RETURN r LIMIT 1")

    print("\n== routing query, per team, exact rows ==")
    routing = strip_comments(read(os.path.join(QUERIES, "routing.cypher")))
    for slug, want in [("libs-api", None), ("core", 7), ("libs", None), ("dev-tools", 0), ("doc", 0)]:
        cy = routing.replace("$slug", "'%s'" % slug)
        n = t.rowcount("routing T-%s" % slug, cy, want=want,
                       expect_nonzero=(want is None or want > 0))
    # libs-api must route to libs and return the same people count as libs itself
    a = len(conn.q(GRAPH, routing.replace("$slug", "'libs-api'")).rows)
    b = len(conn.q(GRAPH, routing.replace("$slug", "'libs'")).rows)
    ok = a == b and a > 0
    print("  %-58s %s==%s %s" % ("libs-api routes to the same set as libs", a, b, "PASS" if ok else "FAIL"))
    t.passed += ok; t.failed += (not ok)

    print("\n== DIRECTION FLIPS: each must return ZERO rows ==")
    flips = [
        ("successor edge is ONE-DIRECTIONAL: nothing points back at libs-api, must be zero",
         "MATCH (t:Team)-[:SUCCEEDED_BY]->(a:Team {slug:'libs-api'}) RETURN t.slug LIMIT 1"),
        ("successor chain terminates: libs is active so it has no successor, must be zero",
         "MATCH (l:Team {slug:'libs'})-[:SUCCEEDED_BY]->(x:Team) RETURN x.slug LIMIT 1"),
        ("person points at rfc named AUTHORED, correct form",
         "MATCH (p:Person)-[:AUTHORED]->(r:RFC) RETURN p.handle LIMIT 1"),
        ("same pattern flipped, must be zero",
         "MATCH (p:Person)<-[:AUTHORED]-(r:RFC) RETURN p.handle LIMIT 1"),
        ("team points at rfc named GOVERNED, correct form",
         "MATCH (t:Team)-[:GOVERNED]->(r:RFC) RETURN t.slug LIMIT 1"),
        ("same pattern flipped, must be zero",
         "MATCH (t:Team)<-[:GOVERNED]-(r:RFC) RETURN t.slug LIMIT 1"),
        ("person points at team named MEMBER, correct form",
         "MATCH (p:Person)-[:MEMBER]->(t:Team) RETURN p.handle LIMIT 1"),
        ("same pattern flipped, must be zero",
         "MATCH (p:Person)<-[:MEMBER]-(t:Team) RETURN p.handle LIMIT 1"),
    ]
    for label, cy in flips:
        expect_zero = "must be zero" in label
        t.rowcount(label, cy, expect_nonzero=not expect_zero)

    print("\n== gap tiers: 3 tiers, counts must match the snapshot ==")
    tiers = conn.q(GRAPH, "MATCH (t:Team) OPTIONAL MATCH (t)-[:SUCCEEDED_BY]->(s:Team) "
                          "RETURN CASE WHEN t.status='active' THEN 'ACTIVE' "
                          "WHEN s IS NOT NULL THEN 'SUCCESSOR' ELSE 'TRUE_GAP' END AS tier, "
                          "count(*) ORDER BY tier").rows
    got = {r[0]: int(r[1]) for r in tiers}
    print("  tiers: %s" % got)
    t.value("ACTIVE count", "MATCH (t:Team) WHERE t.status='active' RETURN count(t)", c["teams_active"])
    t.value("SUCCESSOR count",
            "MATCH (t:Team)-[:SUCCEEDED_BY]->(:Team) RETURN count(DISTINCT t)", c["successor_edges"])
    want_gap = c["teams_total"] - c["teams_active"] - c["successor_edges"]
    t.value("TRUE_GAP count (=total-active-successor)",
            "MATCH (t:Team) WHERE t.status<>'active' AND NOT (t)-[:SUCCEEDED_BY]->(:Team) "
            "RETURN count(t)", want_gap)

    print("\n== gap report: labels used by RFCs, tiering ==")
    gr = strip_comments(read(os.path.join(QUERIES, "gap_report.cypher")))
    rows = conn.q(GRAPH, gr).rows
    print("  gap_report rows: %d" % len(rows))
    labels = {r[0] for r in rows}
    for must in ("libs-api", "core", "dev-tools", "doc", "cargo", "lang"):
        ok = must in labels
        print("  %-58s %s" % ("label %s present" % must, "PASS" if ok else "FAIL"))
        t.passed += ok; t.failed += (not ok)

    print("\n== gap report: exact tier membership and loads ==")
    tier_rows = conn.q(GRAPH, "MATCH (r:RFC) UNWIND r.team_labels AS l "
                              "WITH l, count(DISTINCT r) AS n "
                              "OPTIONAL MATCH (t:Team {slug:l}) "
                              "OPTIONAL MATCH (t)-[:SUCCEEDED_BY]->(s:Team) "
                              "RETURN l, n, CASE WHEN t IS NULL THEN 'TRUE_GAP' "
                              "WHEN t.status='active' THEN 'ACTIVE' "
                              "WHEN s IS NOT NULL THEN 'SUCCESSOR' ELSE 'TRUE_GAP' END "
                              "ORDER BY l").rows
    tier = {r[0]: (int(r[1]), r[2]) for r in tier_rows}
    for label, want_n, want_tier in [
        ("libs-api", 138, "SUCCESSOR"), ("core", 24, "SUCCESSOR"),
        ("dev-tools", 20, "TRUE_GAP"), ("doc", 6, "TRUE_GAP"),
        ("interim-leadership-chat", 1, "TRUE_GAP"),
        ("lang", 263, "ACTIVE"), ("cargo", 42, "ACTIVE"),
    ]:
        got = tier.get(label)
        ok = got is not None and got[0] == want_n and got[1] == want_tier
        print("  %-58s %s %s" % ("label %s = %s RFCs, %s" % (label, want_n, want_tier),
                                 got, "PASS" if ok else "FAIL"))
        t.passed += ok; t.failed += (not ok)
    counts = {}
    for _l, _n, tr in tier_rows:
        counts[tr] = counts.get(tr, 0) + 1
    ok = counts == {"ACTIVE": 14, "SUCCESSOR": 2, "TRUE_GAP": 3}
    print("  %-58s %s %s" % ("tier label counts", counts, "PASS" if ok else "FAIL"))
    t.passed += ok; t.failed += (not ok)

    print("\n== ordering: the most recent reviewer must be FIRST ==")
    order_q = ("MATCH (o:Team {slug:'libs'}) MATCH (o)<-[r:LEAD|MEMBER]-(p:Person) "
               "OPTIONAL MATCH (p)-[:AUTHORED]->(a:RFC) "
               "WITH o,p,collect(DISTINCT type(r)) AS k, count(DISTINCT a) AS n, max(a.created) AS lt "
               "RETURN p.handle AS handle, coalesce(lt,'') AS latest "
               "ORDER BY latest DESC, n DESC, handle")
    rows = conn.q(GRAPH, order_q).rows
    first, last = rows[0], rows[-1]
    ok = first[1] != "" and last[1] == ""
    print("  %-58s first=%s last=%s %s"
          % ("newest first, undated last", first, last, "PASS" if ok else "FAIL"))
    t.passed += ok; t.failed += (not ok)

    print("\n%d passed, %d failed" % (t.passed, t.failed))
    return 1 if t.failed else 0


if __name__ == "__main__":
    sys.exit(main())
