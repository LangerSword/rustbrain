#!/usr/bin/env python3
"""Wait for the FalkorDB service container, then assert the module version.

Fails loudly if the module reports anything other than 42201 (v4.22.1), because
the whole project is calibrated against that build: different versions differ on
parser limits and on what dbms.procedures() lists.
"""
import sys
import time

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
from load_graph import Resp  # noqa: E402

EXPECTED = "42201"

for attempt in range(40):
    try:
        c = Resp()
        if c.cmd("PING") == "PONG":
            mods = c.cmd("MODULE", "LIST")
            versions = {}
            for m in mods:
                d = {}
                i = 0
                while i + 1 < len(m):
                    d[str(m[i])] = m[i + 1]
                    i += 2
                versions[str(d.get("name"))] = str(d.get("ver"))
            print("modules:", versions)
            got = versions.get("graph")
            if got != EXPECTED:
                raise SystemExit("FAIL: graph module ver %s, expected %s" % (got, EXPECTED))
            print("OK: graph module ver %s" % got)
            sys.exit(0)
    except SystemExit:
        raise
    except Exception as e:
        print("attempt %d: %s" % (attempt + 1, str(e)[:80]))
    time.sleep(2)

raise SystemExit("FAIL: FalkorDB never became ready")
