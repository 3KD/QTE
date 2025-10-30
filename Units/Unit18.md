# Unit 18 — Noise Drift Monitor

Analyzes **time-ordered receipts/certificates** to quantify backend **drift** in entropy metrics over repeated runs. Produces a machine-readable **drift report** summarizing slope, variance, and excursions against a tolerance band.

## CONTRACT (DO NOT CHANGE)

CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-drift
- --inputs            # newline- or comma-separated list of JSON receipts/certs sorted by time (ascending)
- --out-drift         # JSON drift report path
- --metric            # one of: H_Z_bits,H_X_bits,KL_to_uniform_bits,min_entropy_bits,MU_lower_bound_bits
- --window            # integer window size for rolling stats (e.g., 3,5,7)
- drift_version="Unit18"

### Required Drift JSON fields (verbatim keys must exist)
{
  "drift_version": "Unit18",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "metric": "H_Z_bits",
  "abs_tolerance_bits": 0.02,
  "window": 5,
  "series": [
    {
      "timestamp_utc": "2025-10-29T17:00:00Z",
      "backend_name": "ibm_torino",
      "value_bits": 0.9971
    }
  ],
  "stats": {
    "count": 1,
    "mean_bits": 0.9971,
    "stdev_bits": 0.0,
    "slope_bits_per_hour": 0.0,
    "max_excursion_bits": 0.0
  },
  "excursions": [
    {
      "index": 0,
      "value_bits": 0.9971,
      "delta_from_mean_bits": 0.0,
      "exceeds_tolerance": false
    }
  ],
  "summary": {
    "within_tolerance": true,
    "excursion_count": 0
  }
}

### Inputs
- Receipts produced by earlier units (04/06) containing `"timestamp_utc"`, `"backend_name"`, and the metric fields listed above.

### Determinism
Given identical inputs and a fixed window/tolerance policy, output is deterministic.

### Notes
- Offline analysis (no live backend calls).
- Default `"abs_tolerance_bits"` is policy/documentation, not contract.
