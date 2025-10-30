# Unit 21 — Cross-Backend Consistency Audit

Compares receipts/certificates across **multiple IBM backends** for a chosen metric and window, emitting a JSON audit of cross-backend deltas and flags.

## CONTRACT (DO NOT CHANGE)

CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-xbackend
- --inputs
- --out-audit
- --backends
- --metric
- --window
- xbackend_version="Unit21"

### Required Audit JSON fields (verbatim keys must exist)
{
  "xbackend_version": "Unit21",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "metric": "H_Z_bits",
  "window": "7d",
  "backends": ["ibm_torino","ibm_osaka"],
  "pairs": [
    {
      "a": "ibm_torino",
      "b": "ibm_osaka",
      "count_a": 5,
      "count_b": 4,
      "mean_a_bits": 0.9968,
      "mean_b_bits": 0.9973,
      "abs_delta_bits": 0.0005,
      "max_abs_delta_bits": 0.0014,
      "p_value": 0.12,
      "flag_inconsistent": false
    }
  ],
  "summary": {
    "backend_count": 2,
    "pair_count": 1,
    "max_pair_delta_bits": 0.0014,
    "any_inconsistent": false
  }
}

### Inputs
- Receipts/Quentroy artifacts from Units 04/06 including `"backend_name"`, `"timestamp_utc"`, and the chosen metric.

### Determinism
Given identical inputs, `--backends`, `--metric`, and `--window`, output is deterministic (offline).
