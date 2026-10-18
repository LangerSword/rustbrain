import sys
sys.path.insert(0, "/home/lakshaya/projects/rustbrain/scripts")
from load_graph import Resp, GRAPH
c = Resp(port=6399)
import subprocess
_stamp = subprocess.run(["bash","-lc","TZ=Asia/Kolkata date '+%Y-%m-%d %H:%M:%S IST'"],
                        capture_output=True, text=True).stdout.strip()
print("DIRECTION RECEIPT, captured %s" % _stamp)
print("module ver 42201, graph %s" % GRAPH)
print()
print("An edge (a)-[:R]->(b) created in a throwaway graph, then both forms run:")
c.cmd("GRAPH.DELETE", "dirtest") if False else None
try:
    c.cmd("GRAPH.DELETE", "dirtest")
except RuntimeError:
    pass
c.q("dirtest", "RETURN 1")
c.q("dirtest", "CREATE (:A {n:'a'}), (:B {n:'b'})")
c.q("dirtest", "MATCH (a:A {n:'a'}), (b:B {n:'b'}) CREATE (a)-[:R]->(b)")
for label, q in [
    ("outbound (a:A)-[:R]->(b:B)   ", "MATCH (a:A)-[:R]->(b:B) RETURN a.n, b.n"),
    ("inbound  (a:A)<-[:R]-(b:B)   ", "MATCH (a:A)<-[:R]-(b:B) RETURN a.n, b.n"),
    ("unlabeled (a)<-[:R]-(b)      ", "MATCH (a)<-[:R]-(b) RETURN a.n, b.n"),
]:
    r = c.q("dirtest", q)
    print("  %s rows=%d %s" % (label, len(r.rows), r.rows))
print()
print("Zero on the inbound form is CORRECT Cypher: no edge points into 'a'.")
print("With labels dropped, the inbound form matches the edge and swaps the bindings,")
print("which proves the engine is not skipping anything.")
print()
print("What I actually did wrong: my ingest created Team->RFC and Person->RFC, so my")
print("two 'asymmetric' queries were asking opposite questions. Both measurements were")
print("right; the conclusion I drew from them was wrong. I called it a silent engine")
print("defect without printing the ingest Cypher first.")
c.cmd("GRAPH.DELETE", "dirtest")
