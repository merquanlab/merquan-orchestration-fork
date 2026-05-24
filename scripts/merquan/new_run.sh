#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 <run_id> <task_title>"
  exit 2
fi

RUN_ID="$1"
TASK_TITLE="$2"
ROOT=".vnx-data/merquan-runs/$RUN_ID"

mkdir -p "$ROOT"

cat > "$ROOT/task.md" <<TASK
# Task

$TASK_TITLE
TASK

cat > "$ROOT/plan.md" <<PLAN
# Plan

1. Gather context.
2. Implement bounded change.
3. Verify.
4. Record receipt.
PLAN

cat > "$ROOT/worker_output.md" <<OUT
# Worker Output

(External worker or codex notes go here.)
OUT

cat > "$ROOT/review_codex.md" <<REV
# Codex Final Review

Verdict: PENDING

Notes:
- 
REV

cat > "$ROOT/receipt.json" <<JSON
{
  "run_id": "$RUN_ID",
  "status": "pending",
  "checks": [],
  "approved_by_codex": false
}
JSON

echo "Created run scaffold at $ROOT"
