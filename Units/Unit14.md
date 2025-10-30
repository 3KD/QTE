# Unit 14 — Drift Monitor & Device Trend Report

Aggregates historical **Quentroy certificates / receipts** to quantify **backend drift** over time and produce a signed trend report.

## CONTRACT (DO NOT CHANGE)

CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-drift-scan
- --inputs               # newline- or comma-separated list of cert/receipt paths
- --out-report           # JSON summary with drift metrics
- --out-trend            # JSON/NDJSON time series
- drift_version="Unit14"

### Required Report Fields (docs MUST mention exact keys)
{
  "drift_version": "Unit14",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "atlas_version": "Unit07",
  "backend_name": "",
  "time_window": { "start_utc": "", "end_utc": "" },
  "sample_count": 0,
  "metrics": {
    "H_Z_bits_mean": 0.0,
    "H_X_bits_mean": 0.0,
    "KL_to_uniform_bits_mean": 0.0,
    "min_entropy_bits_p05": 0.0,
    "min_entropy_bits_p50": 0.0,
    "min_entropy_bits_p95": 0.0
  },
  "stability_flags": {
    "drift_detected": false,
    "regression_vs_baseline": false
  },
  "baseline": {
    "psi_fingerprint": "",
    "semantic_hash": ""
  }
}

### Determinism
Given identical inputs (order-insensitive) and fixed binning/quantiles, the **report is deterministic**.

### Notes
- Inputs should be Quentroy certs and/or Exec receipts from Units 04/06.
- Trend output is a time series aligned on `timestamp_utc` found in inputs.
- This unit does **not** require cloud access; it is pure aggregation.
