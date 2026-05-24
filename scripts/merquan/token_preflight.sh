#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 <run_id> [model] [max_input] [max_output]"
  exit 2
fi

RUN_ID="$1"
MODEL="${2:-gpt-5.3-codex}"
MAX_INPUT="${3:-12000}"
MAX_OUTPUT="${4:-2500}"

python3 scripts/merquan/token_preflight.py \
  --run-id "$RUN_ID" \
  --model "$MODEL" \
  --max-input "$MAX_INPUT" \
  --max-output "$MAX_OUTPUT"
