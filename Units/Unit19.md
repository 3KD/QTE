# Unit 19 — Cross-Backend Comparator

Compares **receipts/certificates** from multiple backends to quantify **cross-hardware consistency** for selected entropy metrics. Outputs a machine-readable **comparison report** with per-backend stats and pairwise deltas.

## CONTRACT (DO NOT CHANGE)

CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-compare
- --inputs            # newline- or comma-separated list of JSON receipts/certs (any order)
- --out-compare       # JSON comparison report path
- --metric            # one of: H_Z_bits,H_X_bits,KL_to_uniform_bits,min_entropy_bits,MU_lower_bound_bits
- --group-by          # one of: backend,timestamp
- comparator_version="Unit19"

### Required Comparison JSON fields (verbatim keys must exist)
{
  "comparator_version": "Unit19",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "metric": "H_Z_bits",
  "group_by": "backend",
  "items": [
    {
      "backend_name": "ibm_torino",
      "timestamp_utc": "2025-10-29T18:00:00Z",
      "value_bits": 0.9971
    }
  ],
  "per_backend": [
    {
      "backend_name": "ibm_torino",
      "count": 1,
      "mean_bits": 0.9971,
      "stdev_bits": 0.0
    }
  ],
  "pairwise": [
    {
      "backend_a": "ibm_torino",
      "backend_b": "ibm_osaka",
      "delta_mean_bits": 0.0012
    }
  ],
  "summary": {
    "backend_count": 1,
    "max_pairwise_delta_bits": 0.0
  }
}

### Inputs
- Receipts produced by Units 04/06 containing `"backend_name"`, `"timestamp_utc"`, and the metric fields listed above.

### Determinism
Given identical inputs and selected `--metric`/`--group-by`, output is deterministic. Offline analysis only.

### Notes
- This unit does **not** call live backends; it consumes existing artifacts.
