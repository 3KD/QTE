# Unit 27 — Hardware Drift Monitor & Calibration Tagger

Aggregates backend calibration snapshots over a window, estimates drift, and emits a tag object you can attach to receipts (Unit04/Unit06/Unit13). Useful to correlate result variance with hardware conditions.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-calib-tag
- --backend
- --window
- --out-calib
- calib_version="Unit27"

### Required Calibration JSON fields (verbatim keys must exist)
{
  "calib_version": "Unit27",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "endianness": "little",
  "qft_kernel_sign": "+",
  "backend_name": "ibm_torino",
  "window": "P1D",
  "samples": 5,
  "drift_ppm": 12.3,
  "t1_ms_median": 110.4,
  "t2_ms_median": 92.7,
  "readout_error_mean": 0.015,
  "cx_error_mean": 0.008,
  "timestamp_utc": "2025-10-30T00:00:00Z",
  "notes": "rolling median across window"
}

### Determinism
- Live telemetry dependent; treat as **non-deterministic**.
- Offline tests should only validate presence of keys and CLI literals.
- Live execution is opt-in via `NVQA_LIVE=1`.

### Notes
- `--window` accepts ISO-8601 duration (e.g., `P1D`, `PT6H`).
- Output is intended to be embedded into receipts as a `calibration_tag`.
