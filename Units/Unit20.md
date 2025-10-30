# Unit 20 — Backend Drift Monitor

Tracks within-backend metric drift across time windows from prior receipts/certificates and emits a JSON drift report.

## CONTRACT (DO NOT CHANGE)

CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-drift
- --inputs
- --out-drift
- --window
- --metric
- drift_version="Unit20"

### Required Drift JSON fields (verbatim keys must exist)
{
  "drift_version": "Unit20",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "metric": "H_Z_bits",
  "window": "7d",
  "items": [
    {
      "backend_name": "ibm_torino",
      "timestamp_utc": "2025-10-29T18:00:00Z",
      "value_bits": 0.9971
    }
  ],
  "per_window": [
    {
      "backend_name": "ibm_torino",
      "t_start_utc": "2025-10-22T00:00:00Z",
      "t_end_utc": "2025-10-29T00:00:00Z",
      "count": 4,
      "mean_bits": 0.9968,
      "stdev_bits": 0.0005,
      "max_abs_delta_bits": 0.0012
    }
  ],
  "summary": {
    "backend_count": 1,
    "window_count": 1,
    "max_backend_drift_bits": 0.0012
  }
}

### Inputs
- Receipts from Units 04/06 that include `"backend_name"`, `"timestamp_utc"`, and the chosen metric.

### Determinism
Given identical inputs, `--metric`, and `--window`, output is deterministic (offline analysis only).
