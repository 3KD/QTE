# Unit 15 — Cross-Backend Consistency & Transferability Report

Compares **Quentroy certificates / Exec receipts** from multiple IBM backends to quantify
consistency and to derive a simple **transferability map** (how well results from one
backend predict another).

## CONTRACT (DO NOT CHANGE)

CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-xbackend
- --inputs                 # newline- or comma-separated list of cert/receipt paths across ≥2 backends
- --out-consistency        # JSON with pairwise divergences / agreement stats
- --out-transfer           # JSON with transferability map/fit summary
- cross_version="Unit15"

### Required Consistency/Transfer JSON fields (exact keys must be present)
{
  "cross_version": "Unit15",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "atlas_version": "Unit07",
  "backends": ["ibm_torino","ibm_osaka"],
  "sample_count": 0,
  "pairwise": [
    {
      "a": "ibm_torino",
      "b": "ibm_osaka",
      "JSD_between_counts_bits": 0.0,
      "Hellinger_distance": 0.0,
      "agreement_rate_topk": 0.0
    }
  ],
  "transfer_map": {
    "algo": "LINEAR_REG_V1",
    "anchor_backend": "ibm_torino",
    "targets": [
      {
        "backend": "ibm_osaka",
        "mapped_error_bits_rmse": 0.0,
        "mapped_bias_bits": 0.0
      }
    ]
  }
}

### Determinism
Given identical inputs and fixed seeds/fit procedure, outputs are deterministic.

### Notes
- Inputs are outputs from Units 04/06 (receipts/certs) labeled with `backend_name`.
- This unit is offline analysis (no cloud calls).
