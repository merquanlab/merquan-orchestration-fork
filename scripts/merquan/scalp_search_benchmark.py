#!/usr/bin/env python3
import argparse
import json
import math
import random
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Candidate:
    flags: int
    safa_impulse: float
    dxy_impulse: float
    basket_mask: int
    px: float


# Flag bits for cheap gate
F_MARKET_OPEN = 1 << 0
F_SPREAD_OK = 1 << 1
F_FRESH = 1 << 2
F_NOT_BLACKOUT = 1 << 3
F_SAFA_OK = 1 << 4
REQUIRED_FLAGS = F_MARKET_OPEN | F_SPREAD_OK | F_FRESH | F_NOT_BLACKOUT | F_SAFA_OK


def generate_candidates(n: int, seed: int = 396) -> list[Candidate]:
    rng = random.Random(seed)
    out: list[Candidate] = []

    for _ in range(n):
        flags = 0
        if rng.random() < 0.82:
            flags |= F_MARKET_OPEN
        if rng.random() < 0.88:
            flags |= F_SPREAD_OK
        if rng.random() < 0.93:
            flags |= F_FRESH
        if rng.random() < 0.91:
            flags |= F_NOT_BLACKOUT
        if rng.random() < 0.89:
            flags |= F_SAFA_OK

        # 7-bit agreement mask for top-7 reactive components
        basket_mask = rng.randrange(0, 1 << 7)

        out.append(
            Candidate(
                flags=flags,
                safa_impulse=(rng.random() * 2.0) - 1.0,
                dxy_impulse=(rng.random() * 2.0) - 1.0,
                basket_mask=basket_mask,
                px=4500.0 + (rng.random() * 500.0),
            )
        )
    return out


def heavy_score(c: Candidate) -> float:
    x = c.px * 0.0007
    a = math.sin(x) + math.cos(x * 0.7)
    b = math.log1p(c.px) * 0.031
    z = a + b + (c.safa_impulse * 0.9) - (c.dxy_impulse * 0.45)
    return z


def baseline_eval(candidates: list[Candidate]) -> tuple[int, float]:
    accepted = 0
    score_acc = 0.0

    for c in candidates:
        # Baseline anti-pattern: heavy stack evaluated before cheap sieve.
        s = heavy_score(c)

        if (c.flags & F_MARKET_OPEN) == 0:
            continue
        if (c.flags & F_SPREAD_OK) == 0:
            continue
        if (c.flags & F_FRESH) == 0:
            continue
        if (c.flags & F_NOT_BLACKOUT) == 0:
            continue
        if (c.flags & F_SAFA_OK) == 0:
            continue

        if c.safa_impulse <= 0:
            continue
        if c.dxy_impulse < -0.25:
            continue

        # Agreement threshold: at least 5 of 7
        if c.basket_mask.bit_count() < 5:
            continue

        accepted += 1
        score_acc += s

    return accepted, score_acc


def optimized_eval(candidates: list[Candidate]) -> tuple[int, float]:
    accepted = 0
    score_acc = 0.0

    # Fused sieve: all cheap constraints together.
    for c in candidates:
        if (c.flags & REQUIRED_FLAGS) != REQUIRED_FLAGS:
            continue
        if c.safa_impulse <= 0 or c.dxy_impulse < -0.25:
            continue

        # popcount-based agreement check
        if c.basket_mask.bit_count() < 5:
            continue

        # Heavy math only on survivors
        s = heavy_score(c)
        accepted += 1
        score_acc += s

    return accepted, score_acc


def benchmark(candidates: list[Candidate]) -> dict:
    t0 = time.perf_counter()
    b_count, b_score = baseline_eval(candidates)
    t1 = time.perf_counter()

    o_count, o_score = optimized_eval(candidates)
    t2 = time.perf_counter()

    b_sec = t1 - t0
    o_sec = t2 - t1
    b_tps = len(candidates) / b_sec if b_sec > 0 else 0.0
    o_tps = len(candidates) / o_sec if o_sec > 0 else 0.0
    speedup = (o_tps / b_tps) if b_tps > 0 else 0.0

    return {
        "candidates": len(candidates),
        "baseline": {
            "seconds": b_sec,
            "throughput_per_sec": b_tps,
            "accepted": b_count,
            "score_accumulator": b_score,
        },
        "optimized": {
            "seconds": o_sec,
            "throughput_per_sec": o_tps,
            "accepted": o_count,
            "score_accumulator": o_score,
        },
        "speedup": speedup,
        "accepted_match": (b_count == o_count),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="MERQUAN scalp sieve optimization benchmark")
    ap.add_argument("--candidates", type=int, default=300000)
    ap.add_argument("--seed", type=int, default=396)
    ap.add_argument("--min-speedup", type=float, default=1.30)
    args = ap.parse_args()

    cand = generate_candidates(args.candidates, args.seed)
    res = benchmark(cand)

    status = "pass"
    reasons = []
    if not res["accepted_match"]:
        status = "fail"
        reasons.append("optimized accepted set diverges from baseline")
    if res["speedup"] < args.min_speedup:
        status = "fail"
        reasons.append(
            f"speedup {res['speedup']:.3f} below required {args.min_speedup:.3f}"
        )

    now = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(".vnx-data") / "merquan-benchmarks"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"scalp_search_{now}.json"

    payload = {
        "benchmark": "scalp_search_optimizations",
        "timestamp_utc": now,
        "status": status,
        "reasons": reasons,
        "thresholds": {
            "min_speedup": args.min_speedup,
            "accepted_must_match": True,
        },
        "result": res,
    }

    out_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))

    if status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
