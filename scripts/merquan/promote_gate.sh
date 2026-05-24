#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <run_id> [benchmark_receipt_json]"
  exit 2
fi

RUN_ID="$1"
BENCH_FILE="${2:-}"
ROOT=".vnx-data/merquan-runs/$RUN_ID"
BENCH_DIR=".vnx-data/merquan-benchmarks"

required=(task.md plan.md worker_output.md review_codex.md receipt.json token_preflight.json)
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

receipt_status=$(python3 - <<PY
import json
p='$ROOT/receipt.json'
with open(p,'r',encoding='utf-8') as f:
    d=json.load(f)
print(d.get('status',''))
PY
)
if [ "$receipt_status" != "pass" ]; then
  echo "FAIL: receipt.json status is '$receipt_status' (need 'pass')"
  exit 1
fi

preflight_status=$(python3 - <<PY
import json
p='$ROOT/token_preflight.json'
with open(p,'r',encoding='utf-8') as f:
    d=json.load(f)
print(d.get('status',''))
PY
)
if [ "$preflight_status" != "pass" ]; then
  echo "FAIL: token_preflight.json status is '$preflight_status' (need 'pass')"
  exit 1
fi

if [ -z "$BENCH_FILE" ]; then
  if [ ! -d "$BENCH_DIR" ]; then
    echo "FAIL: benchmark directory not found: $BENCH_DIR"
    exit 1
  fi
  BENCH_FILE="$(ls -1t "$BENCH_DIR"/scalp_search_*.json 2>/dev/null | head -n 1 || true)"
fi

if [ -z "$BENCH_FILE" ] || [ ! -f "$BENCH_FILE" ]; then
  echo "FAIL: benchmark receipt not found (provide as arg2 or create scalp_search_*.json)"
  exit 1
fi

python3 - <<PY
import json, sys
p='$BENCH_FILE'
with open(p,'r',encoding='utf-8') as f:
    d=json.load(f)
status=d.get('status')
speedup=float(d.get('result',{}).get('speedup',0.0))
accepted_match=bool(d.get('result',{}).get('accepted_match',False))
min_speedup=float(d.get('thresholds',{}).get('min_speedup',1.30))
if status!='pass':
    print(f"FAIL: benchmark status is '{status}' in {p}")
    sys.exit(1)
if not accepted_match:
    print(f"FAIL: benchmark accepted_match=false in {p}")
    sys.exit(1)
if speedup < min_speedup:
    print(f"FAIL: benchmark speedup {speedup:.3f} < threshold {min_speedup:.3f} in {p}")
    sys.exit(1)
print(f"BENCH_OK: speedup={speedup:.3f}, threshold={min_speedup:.3f}, file={p}")
PY

echo "PASS: run $RUN_ID is promotable"
