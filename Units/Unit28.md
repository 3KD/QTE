# Unit 28 — Cross-Backend Receipt Comparator (A/B diff)

Compares two receipts (e.g., Exec Unit04 + Quentroy Unit06 blobs) produced on different backends/runs/time windows. Emits a deterministic diff JSON with distances / divergence stats and a quick verdict.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-receipt-diff
- --a
- --b
- --out-diff
- diff_version="Unit28"

### Required Diff JSON fields (verbatim keys must exist)
{
  "diff_version": "Unit28",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "endianness": "little",
  "qft_kernel_sign": "+",
  "receipt_a_path": "",
  "receipt_b_path": "",
  "backend_name_a": "",
  "backend_name_b": "",
  "shots_a": 0,
  "shots_b": 0,
  "hellinger": 0.0,
  "bhattacharyya": 0.0,
  "kl_bits_a_to_b": 0.0,
  "kl_bits_b_to_a": 0.0,
  "chi2": 0.0,
  "ks_pvalue": 1.0,
  "distance_ok": true,
  "threshold_note": "cosmetic guidance only",
  "timestamp_utc": ""
}

### Determinism
- Deterministic given two fixed receipts.
- Live generation of receipts is out of scope here; this unit only compares artifacts.
- Live end-to-end exercises are **opt-in** via `NVQA_LIVE=1`.

### Notes
- Inputs `--a` and `--b` accept JSON receipts produced by your pipeline.
- `distance_ok` is a boolean decision from fixed thresholds codified in code/tests.
