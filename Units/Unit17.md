# Unit 17 — Cross-Backend Equivalence Harness

Compares receipts/certificates from **different backends** (e.g., simulator vs. ibm_torino) for metric-level equivalence within configured tolerances. Emits a machine-readable **equivalence report**.

## CONTRACT (DO NOT CHANGE)

CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-xbackend
- --inputs                 # newline- or comma-separated list of JSON receipts/certs
- --out-equivalence        # JSON report path
- --metric                 # one of: H_Z_bits,H_X_bits,KL_to_uniform_bits,min_entropy_bits,MU_lower_bound_bits
- xbackend_version="Unit17"

### Required Equivalence JSON fields (verbatim keys must exist)
{
  "xbackend_version": "Unit17",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "atlas_version": "Unit07",
  "metric": "KL_to_uniform_bits",
  "abs_tolerance_bits": 0.02,
  "pairs_compared": [
    {
      "backend_a": "ibm_torino",
      "backend_b": "sim",
      "count": 42,
      "mean_diff_bits": 0.001,
      "max_abs_diff_bits": 0.007,
      "within_tolerance": true
    }
  ],
  "summary": {
    "total_pairs": 1,
    "pass_pairs": 1,
    "fail_pairs": 0
  },
  "failures": [
    {
      "backend_a": "",
      "backend_b": "",
      "reason": "exceeded tolerance"
    }
  ]
}

### Inputs
- Receipts produced by Units 04/06 including `"backend_name"` and the metric fields listed above.

### Determinism
Given identical inputs and fixed selection policy, the output is deterministic.

### Notes
- This unit is **offline** (no live backend calls).
- Default `"abs_tolerance_bits"` SHOULD be documented by the CLI help and is part of policy, not the contract.
