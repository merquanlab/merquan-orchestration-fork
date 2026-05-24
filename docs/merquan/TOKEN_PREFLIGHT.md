# MERQUAN Token Preflight

Token preflight prevents oversized dispatches and keeps model spend predictable.

## Purpose

Before dispatching a run, estimate token usage from run artifacts and fail fast when input exceeds budget.

## Files

- `scripts/merquan/token_preflight.py`
- `scripts/merquan/token_preflight.sh`
- Output: `.vnx-data/merquan-runs/<run_id>/token_preflight.json`

## Usage

```bash
# default model/budgets
./scripts/merquan/token_preflight.sh demo-run-001

# explicit model and caps
./scripts/merquan/token_preflight.sh demo-run-001 gpt-5.3-codex 12000 2500
```

## Behavior

- Uses `tiktoken` when available (`cl100k_base` encoding).
- Falls back to heuristic estimation if `tiktoken` is not installed.
- Exits non-zero when estimated input tokens exceed `max_input`.

## Recommended policy

- Keep preflight as mandatory for all promoted runs.
- Tune per task class:
  - quick patch: lower input cap
  - deep review: higher input cap
- Keep Codex final approval regardless of preflight pass.

