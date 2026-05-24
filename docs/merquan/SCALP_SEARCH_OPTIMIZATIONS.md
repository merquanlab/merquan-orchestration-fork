# MERQUAN Scalp Search Optimizations

This module applies the search-optimization philosophy from the Erdos search-lab pattern (early rejection, fused passes, skip-empty-work) to MERQUAN's 5m/15m scalp candidate pipeline.

## Objective

Run cheap validity checks first and execute heavy signal math only for survivors.

## Applied Mapping

- Kummer carry / governor prefilter idea -> cheap candidate sieve in front of heavy stack.
- Fused segmented sieve -> single fused gate for all cheap constraints.
- popcount optimization -> bit-count style agreement checks.
- skip-no-multiples idea -> skip candidates with no useful signal contribution.
- branchless orientation -> compact boolean gate expression with minimal branch churn.

## Output

Benchmark receipt files are written to:

`.vnx-data/merquan-benchmarks/scalp_search_<timestamp>.json`

## Usage

```bash
python3 scripts/merquan/scalp_search_benchmark.py --candidates 300000 --min-speedup 1.30
```

Pass criteria:

- accepted candidate count matches baseline logic
- optimized throughput is at least configured threshold above baseline

