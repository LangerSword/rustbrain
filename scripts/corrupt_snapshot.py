#!/usr/bin/env python3
"""Corrupt data/snapshot.json on purpose, to prove --check refuses it.

Used by CI. If --check passes after this runs, the drift check is not actually
checking the file, which is a real bug this test exists to catch.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(HERE, "data", "snapshot.json")
d = json.load(open(p))
before = d["counts"]["rfcs"]
d["counts"]["rfcs"] = before + 1
with open(p, "w", encoding="utf-8") as f:
    json.dump(d, open(p) if False else f, sort_keys=True, indent=1)
print("corrupted: counts.rfcs %s -> %s" % (before, before + 1))
sys.exit(0)
