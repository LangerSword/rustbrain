#!/usr/bin/env bash
# Evidence: route a REAL OPEN RFC PR, record the live PR state beside the output.
set -euo pipefail
cd "$(dirname "$0")/.."
echo "Captured: $(TZ=Asia/Kolkata date '+%Y-%m-%d %H:%M:%S IST')"
echo
echo "Live state of rust-lang/rfcs PR 4016 (open at capture time):"
gh api repos/rust-lang/rfcs/pulls/4016 \
  --jq '"  title: \(.title)\n  state: \(.state)\n  labels: \([.labels[].name]|join(", "))\n  created: \(.created_at)"'
echo
echo "rustbrain routing for that PR's team labels:"
FALKORDB_PORT=${FALKORDB_PORT:-6399} python3 cmd/route.py T-cargo T-crates-io
