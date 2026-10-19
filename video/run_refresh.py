#!/usr/bin/env python3
"""Run the refresh command and print its real diff, for the demo video.

The real diff this project caught is the roster change on 2026-10-19 (joboet
left libs-ping). data/history keeps the pre-refresh baseline. This script
points the refresh command at that baseline, runs it for real, prints the
report's headline lines, then restores the history folder exactly as it was.

It never touches the network and never rewrites the snapshot.
"""
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(HERE, "data", "history")
NEW = "snapshot_6732467a070a.json"      # current snapshot copy
OLD = "snapshot_36ad30968e76.json"      # pre-refresh baseline


def main():
    new_path = os.path.join(HIST, NEW)
    stash = new_path + ".stashed"
    if not (os.path.exists(new_path) and os.path.exists(os.path.join(HIST, OLD))):
        print("history files missing, cannot show the real diff")
        return 1
    shutil.move(new_path, stash)
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "cmd", "refresh.py")],
                           capture_output=True, text=True)
        for line in r.stdout.splitlines():
            print(line.replace(HERE, "."))
        reports = sorted(f for f in os.listdir(os.path.join(HERE, "reports")) if f.startswith("refresh_"))
        latest = os.path.join(HERE, "reports", reports[-1])
        print()
        print("the report says, verbatim:")
        for line in open(latest, encoding="utf-8"):
            if re.search(r"joboet|libs-ping|Roster changes|content_sha256|roster_edges_member", line):
                print("  " + line.rstrip())
    finally:
        shutil.move(stash, new_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
