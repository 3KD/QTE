# Unit 22 — Quantum Metric Aggregator

Aggregates results from multiple quantum experiment receipts into unified global metrics and correlation matrices.

## CONTRACT (DO NOT CHANGE)

CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-aggregate
- --inputs
- --out-metrics
- --metric
- --correlate
- aggregate_version="Unit22"

### Required Aggregation JSON fields (verbatim keys must exist)
{
  "aggregate_version": "Unit22",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "metric": "H_Z_bits",
  "correlate": true,
  "items": [
    {
      "backend_name": "ibm_torino",
      "timestamp_utc": "2025-10-29T18:00:00Z",
      "value_bits": 0.9971
    }
  ],
  "global_metrics": {
    "mean_bits": 0.9968,
    "stdev_bits": 0.0006,
    "min_bits": 0.9957,
    "max_bits": 0.9979,
    "range_bits": 0.0022
  },
  "correlation_matrix": [
    [1.0, 0.98],
    [0.98, 1.0]
  ],
  "summary": {
    "entry_count": 2,
    "metric": "H_Z_bits",
    "is_correlated": true
  }
}

### Determinism
Given identical inputs and parameters, the output is deterministic (offline aggregation only).

### Notes
- Supports both quantum and hybrid simulation results.
