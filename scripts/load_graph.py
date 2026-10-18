#!/usr/bin/env python3
"""Load data/snapshot.json into FalkorDB. Deterministic: same snapshot, same graph.

Graph model
-----------
  (:Team   {slug, name, status, successor_team})
  (:Person {handle})
  (:RFC    {num, title, outcome, created, merged_at, author, author_assoc})
  (:Document {path})

  (Person)-[:MEMBER {role:'member'}]->(Team)   person points AT team
  (Person)-[:LEAD   {role:'lead'}]  ->(Team)   person points AT team
  (Person)-[:AUTHORED]->(RFC)                  person points AT rfc
  (Team)-[:GOVERNED]->(RFC)                    team points AT rfc
  (Team)-[:SUCCEEDED_BY {rfc, source, quote}]->(Team)  archived team points AT
                                               its active successor

Env: FALKORDB_HOST (default 127.0.0.1), FALKORDB_PORT (default 6379), GRAPH (default rustbrain)
"""
import json
import os
import socket
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

GRAPH = os.environ.get("GRAPH", "rustbrain")
HOST = os.environ.get("FALKORDB_HOST", "127.0.0.1")
PORT = int(os.environ.get("FALKORDB_PORT", "6379"))


class Resp:
    """Minimal RESP client so the loader needs no third-party dependency."""

    def __init__(self, host=HOST, port=PORT, timeout=120):
        self.s = socket.create_connection((host, port), timeout=timeout)
        self.buf = b""

    def cmd(self, *args):
        out = ("*%d\r\n" % len(args)).encode()
        for a in args:
            b = str(a).encode()
            out += b"$" + str(len(b)).encode() + b"\r\n" + b + b"\r\n"
        self.s.sendall(out)
        return self._read()

    def _read(self):
        hdr = self._line()
        t, rest = hdr[:1], hdr[1:]
        if t == b"-":
            raise RuntimeError("ERR " + rest.decode())
        if t == b"+":
            return rest.decode()
        if t == b":":
            return int(rest)
        if t == b"$":
            n = int(rest)
            return None if n == -1 else self._readn(n + 2)[:n].decode("utf-8", "replace")
        if t == b"*":
            n = int(rest)
            return None if n == -1 else [self._read() for _ in range(n)]
        raise RuntimeError("bad RESP")

    def _readn(self, n):
        while len(self.buf) < n:
            c = self.s.recv(max(65536, n - len(self.buf)))
            if not c:
                raise RuntimeError("closed")
            self.buf += c
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def _line(self):
        while b"\r\n" not in self.buf:
            self.buf += self.s.recv(65536)
        line, _, rest = self.buf.partition(b"\r\n")
        self.buf = rest
        return line

    def q(self, graph, cypher):
        reply = self.cmd("GRAPH.QUERY", graph, cypher)
        return Result(reply)


class Result:
    def __init__(self, reply):
        self.header = reply[0] if reply and isinstance(reply[0], list) else []
        self.rows = reply[1] if len(reply) > 1 and isinstance(reply[1], list) else []
        self.stats = reply[2] if len(reply) > 2 else []

    def __len__(self):
        return len(self.rows)


def qid(s):
    """Escape a string for a single-quoted Cypher literal."""
    return str(s).replace("\\", "\\\\").replace("'", "\\'")


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def run_batch(conn, stmts, chunk=60):
    """FalkorDB needs a WITH between EVERY updating clause, not just the last."""
    for part in chunks(stmts, chunk):
        conn.q(GRAPH, "\nWITH 1 AS _x\n".join(part))


def main():
    snap = json.load(open(os.path.join(HERE, "data", "snapshot.json")))
    conn = Resp()
    try:
        conn.cmd("GRAPH.DELETE", GRAPH)
    except RuntimeError:
        pass
    conn.q(GRAPH, "RETURN 1")

    teams, people, rfcs = snap["teams"], snap["people"], snap["rfcs"]
    succ = snap["successor_map"]["edges"]

    print("loading teams=%d people=%d rfcs=%d successors=%d"
          % (len(teams), len(people), len(rfcs), len(succ)))

    run_batch(conn, [
        "CREATE (:Team {slug:'%s', name:'%s', status:'%s', successor_team:%s})"
        % (qid(s), qid(t.get("name") or s), t["status"],
           ("'%s'" % qid(t["successor_team"])) if t.get("successor_team") else "NULL")
        for s, t in sorted(teams.items())
    ])
    run_batch(conn, ["CREATE (:Person {handle:'%s'})" % qid(h) for h in sorted(people)])
    run_batch(conn, [
        "CREATE (:RFC {num:%d, title:'%s', outcome:'%s', created:'%s', merged_at:'%s', author:'%s', author_assoc:'%s', team_labels:[%s]})"
        % (r["num"], qid(r["title"]), r["outcome"], r["created"], r["merged_at"],
           qid(r["author"]), r["author_assoc"],
           ",".join("'%s'" % qid(l) for l in r["team_labels"]))
        for r in rfcs
    ])
    docstmts = []
    seen = set()
    for r in rfcs:
        if r.get("document") and r["document"] not in seen:
            seen.add(r["document"])
            docstmts.append("CREATE (:Document {path:'%s', rfc:%d})" % (qid(r["document"]), r["num"]))
    run_batch(conn, docstmts)

    edges = []
    for h, p in sorted(people.items()):
        for slug in p["member_of"]:
            edges.append("MATCH (p:Person {handle:'%s'}), (t:Team {slug:'%s'}) "
                         "CREATE (p)-[:MEMBER {role:'member'}]->(t)" % (qid(h), qid(slug)))
        for slug in p["lead_of"]:
            edges.append("MATCH (p:Person {handle:'%s'}), (t:Team {slug:'%s'}) "
                         "CREATE (p)-[:LEAD {role:'lead'}]->(t)" % (qid(h), qid(slug)))
    print("roster edges to create: %d" % len(edges))
    run_batch(conn, edges, chunk=40)

    auth = ["MATCH (p:Person {handle:'%s'}), (r:RFC {num:%d}) CREATE (p)-[:AUTHORED]->(r)"
            % (qid(r["author"]), r["num"]) for r in rfcs if r["author"] in people]
    print("AUTHORED edges (author resolves to a person node): %d of %d rfcs" % (len(auth), len(rfcs)))
    run_batch(conn, auth, chunk=40)

    gov = ["MATCH (t:Team {slug:'%s'}), (r:RFC {num:%d}) CREATE (t)-[:GOVERNED]->(r)"
           % (qid(l), r["num"]) for r in rfcs for l in r["team_labels"]]
    print("GOVERNED edges (team file must exist for the label): %d" % len(gov))
    run_batch(conn, gov, chunk=40)

    sedges = ["MATCH (a:Team {slug:'%s'}), (b:Team {slug:'%s'}) "
              "CREATE (a)-[:SUCCEEDED_BY {rfc:%s, source:'%s', quote:'%s'}]->(b)"
              % (qid(e["from"]), qid(e["to"]),
                 e["rfc"] if e["rfc"] else "NULL",
                 qid(e["source"]), qid(e["quote"])) for e in succ]
    print("SUCCEEDED_BY edges: %d" % len(sedges))
    run_batch(conn, sedges)

    print("\nGraph loaded. Node and edge counts:")
    for name, cy in [
        ("Team", "MATCH (n:Team) RETURN count(n)"),
        ("Person", "MATCH (n:Person) RETURN count(n)"),
        ("RFC", "MATCH (n:RFC) RETURN count(n)"),
        ("Document", "MATCH (n:Document) RETURN count(n)"),
        ("MEMBER", "MATCH ()-[r:MEMBER]->() RETURN count(r)"),
        ("LEAD", "MATCH ()-[r:LEAD]->() RETURN count(r)"),
        ("AUTHORED", "MATCH ()-[r:AUTHORED]->() RETURN count(r)"),
        ("GOVERNED", "MATCH ()-[r:GOVERNED]->() RETURN count(r)"),
        ("SUCCEEDED_BY", "MATCH ()-[r:SUCCEEDED_BY]->() RETURN count(r)"),
    ]:
        print("  %-14s %s" % (name, conn.q(GRAPH, cy).rows[0][0]))


if __name__ == "__main__":
    main()
