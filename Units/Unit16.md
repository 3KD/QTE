# Unit 16 — Temporal Drift & Stability Monitor

Analyzes a time-ordered set of receipts/certificates to estimate **hardware drift** and **stability** over time. Produces a trend file and machine-readable alerts when stability breaks thresholds.

## CONTRACT (DO NOT CHANGE)

CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-drift
- --inputs               # newline- or comma-separated list of JSON receipts/certs containing timestamp_utc and backend_name
- --out-trend            # JSON with per-backend time-series + trend fits
- --out-alerts           # JSON with detected changepoints and alert severities
- drift_version="Unit16"

### Required Drift JSON fields (exact keys must be present)
{
  "drift_version": "Unit16",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "atlas_version": "Unit07",
  "sources": 0,
  "backends": ["ibm_torino"],
  "metrics": ["H_Z_bits","H_X_bits","KL_to_uniform_bits","min_entropy_bits","MU_lower_bound_bits"],
  "window_days": 7,
  "trend": [
    {
      "backend": "ibm_torino",
      "metric": "H_Z_bits",
      "fit_model": "LINEAR_V1",
      "trend_bits_per_day": 0.0,
      "stderr": 0.0,
      "r2": 0.0,
      "samples": 0
    }
  ]
}

### Required Alerts JSON fields (exact keys must be present)
{
  "drift_version": "Unit16",
  "changepoints": [
    {
      "backend": "ibm_torino",
      "metric": "KL_to_uniform_bits",
      "timestamp_utc": "",
      "delta_bits": 0.0,
      "zscore": 0.0,
      "severity": "info"
    }
  ],
  "policy": {
    "z_hi": 3.0,
    "z_med": 2.0
  }
}

### Determinism
Given identical inputs and fixed seeds, outputs are deterministic.

### Notes
- Inputs come from Units 04/06; must include `"timestamp_utc"` and `"backend_name"`.
- This unit is offline analysis (no live backend calls).
