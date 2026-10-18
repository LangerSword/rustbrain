#!/usr/bin/env python3
"""Print the module receipt: proves which FalkorDB engine is actually running.

This is the receipt the blog evidence needs, and the one that disproved the
earlier v6.0.2 claim.
"""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "scripts"))
from load_graph import Resp  # noqa: E402

port = int(sys.argv[1]) if len(sys.argv) > 1 else 6399
c = Resp(port=port)
print("PING:", c.cmd("PING"))
mods = c.cmd("MODULE", "LIST")
for m in mods:
    d = {}
    i = 0
    while i + 1 < len(m):
        d[str(m[i])] = m[i + 1]
        i += 2
    print("module=%-10s ver=%-8s path=%s" % (d.get("name"), d.get("ver"), d.get("path")))

info = c.cmd("INFO", "server")
if isinstance(info, str):
    for line in info.splitlines():
        if line.startswith("redis_version") or line.startswith("redis_mode"):
            print(line)
print("expectation: graph module ver 42201 (v4.22.1), redis-server 8.10.2")
