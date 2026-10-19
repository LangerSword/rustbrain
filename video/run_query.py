#!/usr/bin/env python3
"""Run the routing query against the local FalkorDB module and print the result.

Real engine, real data: connects to the pinned module on port 6399 (the same
one scripts/start_module.sh starts), runs the exact routing cypher from
queries/routing.cypher for the label libs-api, and prints the row count and the
rows. Used on camera in the demo video.
"""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "scripts"))
from load_graph import Resp, GRAPH  # noqa: E402

PORT = int(os.environ.get("FALKORDB_PORT", "6399"))

QUERY = """MATCH (labelled:Team {slug: $slug})
MATCH (labelled)-[:SUCCEEDED_BY*0..3]->(owner:Team)
WHERE owner.status = 'active'
MATCH (owner)<-[r:LEAD|MEMBER]-(p:Person)
OPTIONAL MATCH (p)-[:AUTHORED]->(authored:RFC)
WITH owner, p, collect(DISTINCT type(r)) AS kinds,
     count(DISTINCT authored) AS authored_count, max(authored.created) AS latest
RETURN owner.slug AS owner, p.handle AS handle,
       CASE WHEN 'LEAD' IN kinds THEN 'lead' ELSE 'member' END AS role,
       authored_count AS authored, coalesce(latest, '') AS latest
ORDER BY latest DESC, authored DESC, handle"""


def main():
    c = Resp(port=PORT)
    rows = c.q(GRAPH, QUERY.replace("$slug", "'libs-api'")).rows
    print("query: queries/routing.cypher (SUCCEEDED_BY*0..3, then the roster join)")
    print("label: libs-api   engine: falkordb module on port %d" % PORT)
    print("rows returned: %d" % len(rows))
    print()
    print("%-22s %-8s %-9s %s" % ("handle", "role", "authored", "latest"))
    for owner, handle, role, authored, latest in rows[:8]:
        print("%-22s %-8s %-9s %s" % (handle, role, authored, latest or "-"))
    print("... %d more rows" % max(0, len(rows) - 8))
    return 0


if __name__ == "__main__":
    sys.exit(main())
