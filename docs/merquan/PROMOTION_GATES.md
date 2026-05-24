# MERQUAN Promotion Gates

Promotion requires all checks below.

## Required Run Artifacts

- `.vnx-data/merquan-runs/<run_id>/task.md`
- `.vnx-data/merquan-runs/<run_id>/plan.md`
- `.vnx-data/merquan-runs/<run_id>/worker_output.md`
- `.vnx-data/merquan-runs/<run_id>/review_codex.md`
- `.vnx-data/merquan-runs/<run_id>/receipt.json`
- `.vnx-data/merquan-runs/<run_id>/token_preflight.json`

## Mandatory Conditions

1. `review_codex.md` contains `Verdict: APPROVED`
2. `receipt.json` has `status = pass`
3. `token_preflight.json` has `status = pass`
4. A scalp benchmark receipt passes:
   - `status = pass`
   - `accepted_match = true`
   - `speedup >= min_speedup`

Benchmark receipt default lookup:

- latest `.vnx-data/merquan-benchmarks/scalp_search_*.json`

Or pass a specific benchmark file to gate command.

## Command

```bash
./scripts/merquan/promote_gate.sh <run_id>
./scripts/merquan/promote_gate.sh <run_id> .vnx-data/merquan-benchmarks/scalp_search_YYYYMMDDTHHMMSSZ.json
```
