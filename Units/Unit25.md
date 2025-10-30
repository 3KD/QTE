# Unit 25 — Calibration Snapshot Correlator (Noise & Error Budget Over Time)

Pulls backend calibration snapshots over a time window, aggregates key metrics, and correlates them with observed run quality (e.g., from Unit24 matrix rows or Unit04 receipts).

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-calib-snap
- --backends
- --window
- --metrics
- --out-report
- calib_version="Unit25"

### Required Report JSON fields (verbatim keys must exist)
{
  "calib_version": "Unit25",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "qft_kernel_sign": "+",
  "endianness": "little",
  "window": "P7D",
  "backends": ["ibm_torino"],
  "metrics": ["t1","t2","sx_error","readout_error","multi_qubit_error"],
  "snapshots": [
    {
      "backend_name": "ibm_torino",
      "timestamp_utc": "2025-10-30T00:00:00Z",
      "t1": 0.00012,
      "t2": 0.00019,
      "sx_error": 0.0008,
      "readout_error": 0.02,
      "multi_qubit_error": 0.015
    }
  ],
  "correlations": {
    "sx_error_vs_success_prob_r": -0.62,
    "readout_error_vs_fidelity_r": -0.57
  },
  "summary": {
    "strongest_degrader": "readout_error",
    "recommendation": "calibrate readout; increase shots or enable dynamical decoupling"
  }
}

### Determinism
- Report content depends on live calibration data; treat as **non-deterministic**.
- Any offline regression test MUST mock snapshots; live path requires `NVQA_LIVE=1`.

### Notes
- `--window` accepts ISO-8601 duration (e.g., `P7D`), or absolute `start,end` ISO times.
- `--metrics` is a comma-separated list; unknown metrics must be ignored, not fatal.
