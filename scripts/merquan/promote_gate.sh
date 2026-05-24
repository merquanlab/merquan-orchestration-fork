#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <run_id>"
  exit 2
fi

RUN_ID="$1"
ROOT=".vnx-data/merquan-runs/$RUN_ID"

required=(task.md plan.md worker_output.md review_codex.md receipt.json)
for f in "${required[@]}"; do
  if [ ! -f "$ROOT/$f" ]; then
    echo "FAIL: missing $ROOT/$f"
    exit 1
  fi
done

if ! grep -q "Verdict: APPROVED" "$ROOT/review_codex.md"; then
  echo "FAIL: review_codex.md is not APPROVED"
  exit 1
fi

status=$(python3 - <<PY
import json
p='$ROOT/receipt.json'
with open(p,'r',encoding='utf-8') as f:
    d=json.load(f)
print(d.get('status',''))
PY
)

if [ "$status" != "pass" ]; then
  echo "FAIL: receipt.json status is '$status' (need 'pass')"
  exit 1
fi

echo "PASS: run $RUN_ID is promotable"
