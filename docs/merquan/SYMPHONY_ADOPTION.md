# MERQUAN Symphony Adoption (Server-Only)

This layer adopts the valuable parts of OpenAI Symphony without replacing the existing VNX runtime.

## Goal

Use isolated implementation runs with deterministic promotion gates while keeping Codex as final decision authority.

## Scope

- Keep current orchestration runtime.
- Add a structured task-run folder model.
- Require evidence artifacts before promotion.
- Keep all execution server-side (`161` / `139`).

## Run Model

Each implementation run lives in:

`.vnx-data/merquan-runs/<run_id>/`

Required artifacts:

- `task.md` - exact bounded task.
- `plan.md` - short execution plan.
- `worker_output.md` - worker result.
- `review_codex.md` - Codex final review.
- `receipt.json` - run metadata and outcomes.

## Promotion Gate

A run can be promoted only if all are true:

1. All required artifacts exist.
2. `review_codex.md` explicitly says `APPROVED`.
3. `receipt.json` has `status = pass`.
4. Tests/checks listed in receipt are green.

## Role Policy

- Codex: primary operator and final gate.
- External agents (Claude/others): optional bounded workers.
- External output is advisory until Codex promotes.

## Why this improves MERQUAN

- Fewer cross-task regressions.
- Better traceability for investor/institutional diligence.
- Cleaner rollback boundaries.

