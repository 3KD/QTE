# Unit 29 — Longitudinal Drift Monitor

Scans a **time-ordered series of receipts** (e.g., Unit04 exec receipts and/or Unit06 quentroy certs) and reports trend statistics and changepoints. Outputs a deterministic drift summary JSON.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-drift
- --inputs
- --out-trend
- drift_version="Unit29"

### Required Drift JSON fields (verbatim keys must exist)
{
  "drift_version": "Unit29",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "endianness": "little",
  "qft_kernel_sign": "+",
  "manifest_path": "",
  "N": 0,
  "backend_names": [],
  "shots_series": [],
  "timestamps_utc": [],
  "hellinger_mean": 0.0,
  "hellinger_max": 0.0,
  "bhattacharyya_mean": 0.0,
  "ks_pvalue_min": 1.0,
  "kl_bits_mean": 0.0,
  "kl_bits_max": 0.0,
  "changepoint_index": -1,
  "changepoint_note": "",
  "drift_alert": false,
  "threshold_note": "cosmetic guidance only"
}

### Determinism
- Deterministic given the same ordered input set and parameters.
- Live acquisitions are **opt-in** via `NVQA_LIVE=1`; this unit itself only analyzes existing artifacts.

### Notes
- `--inputs` accepts a text manifest of JSON paths or a glob that resolves to receipts in chronological order.
- Emit one trend JSON at `--out-trend`.
