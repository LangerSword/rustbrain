#!/usr/bin/env bash
# Start the GRADED FalkorDB module for local development.
#
# The module and redis-server come straight out of the pinned container image, so
# this is the same .so the grader loads. scripts/extract_module.py fills .falkorimg/.
#
# Usage:  scripts/start_module.sh [port]      (default port 6399)
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${1:-6399}"
REDIS="$HERE/.falkorimg/x03/usr/local/bin/redis-server"
MODULE="$HERE/.falkorimg/x14/var/lib/falkordb/bin/falkordb.so"
DATADIR="$HERE/.falkorimg/data"

[ -x "$REDIS" ]  || { echo "missing redis-server, run scripts/extract_module.py first"; exit 1; }
[ -f "$MODULE" ] || { echo "missing falkordb.so, run scripts/extract_module.py first"; exit 1; }

mkdir -p "$DATADIR"

if ss -tln 2>/dev/null | grep -q ":$PORT "; then
  echo "port $PORT already listening, nothing to do"
  exit 0
fi

"$REDIS" --port "$PORT" --dir "$DATADIR" --daemonize yes \
         --loadmodule "$MODULE" --save '' --appendonly no
sleep 1

# Prove the version against the value recorded in PINS.md.
python3 - "$PORT" "$HERE" <<'PY'
import sys
sys.path.insert(0, sys.argv[2] + "/scripts")
from load_graph import Resp

port = int(sys.argv[1])
conn = Resp(port=port)
modules = conn.cmd("MODULE", "LIST")
parsed = {}
for m in modules:
    d = {}
    i = 0
    while i + 1 < len(m):
        d[str(m[i])] = m[i + 1]
        i += 2
    parsed[str(d.get("name"))] = d
graph = parsed.get("graph") or {}
ver = str(graph.get("ver") or "unknown")
print("falkordb module ver = %s (expect 42201)" % ver)
print("module path         = %s" % graph.get("path"))
if ver != "42201":
    print("WARNING: module version is not the pinned 42201. The graded image reports 42201.")
    sys.exit(2)
print("OK: graded module running on port %d" % port)
PY
