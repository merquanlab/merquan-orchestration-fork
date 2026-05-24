#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path


def estimate_tokens(text: str) -> int:
    try:
        import tiktoken  # type: ignore
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        # Fallback heuristic when tiktoken is unavailable.
        # ~4 chars/token is a common coarse estimate.
        return max(1, len(text) // 4)


def read_paths(paths):
    chunks = []
    for p in paths:
        fp = Path(p)
        if fp.is_file():
            chunks.append(fp.read_text(encoding="utf-8", errors="ignore"))
    return "\n\n".join(chunks)


def main():
    ap = argparse.ArgumentParser(description="MERQUAN token preflight for dispatch budgeting")
    ap.add_argument("--run-id", required=True, help="Run ID under .vnx-data/merquan-runs/<run_id>")
    ap.add_argument("--model", default="gpt-5.3-codex", help="Model label for reporting")
    ap.add_argument("--max-input", type=int, default=12000, help="Max allowed input tokens")
    ap.add_argument("--max-output", type=int, default=2500, help="Planned output token budget")
    ap.add_argument("--extra-file", action="append", default=[], help="Additional file paths to include")
    args = ap.parse_args()

    repo = Path.cwd()
    run_root = repo / ".vnx-data" / "merquan-runs" / args.run_id
    preflight_root = run_root
    preflight_root.mkdir(parents=True, exist_ok=True)

    default_files = [
        run_root / "task.md",
        run_root / "plan.md",
        run_root / "worker_output.md",
    ]
    all_paths = [str(p) for p in default_files] + args.extra_file
    input_text = read_paths(all_paths)

    input_tokens = estimate_tokens(input_text)
    total_budget = input_tokens + args.max_output
    status = "pass" if input_tokens <= args.max_input else "fail"

    out = {
        "run_id": args.run_id,
        "model": args.model,
        "max_input_tokens": args.max_input,
        "max_output_tokens": args.max_output,
        "estimated_input_tokens": input_tokens,
        "estimated_total_tokens": total_budget,
        "status": status,
        "files_used": all_paths,
        "estimator": "tiktoken_cl100k_base_or_fallback",
    }

    out_path = preflight_root / "token_preflight.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(out, indent=2))

    if status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
