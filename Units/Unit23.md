# Unit 23 — Drift Detector (Temporal Stability Auditor)

Detects statistical drift across sequences of receipts/certificates over time.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-drift
- --inputs
- --window
- --threshold
- --out-report
- drift_version="Unit23"

### Required Drift Report JSON fields (verbatim keys must exist)
{
  "drift_version": "Unit23",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "window": 20,
  "threshold": 0.05,
  "metric": "H_Z_bits",
  "items": [
    {
      "timestamp_utc": "2025-10-29T20:00:00Z",
      "backend_name": "ibm_torino",
      "value_bits": 0.9967
    }
  ],
  "tests": [
    {"name": "KS_two_sample", "p_value": 0.91},
    {"name": "CUSUM", "alarm": false}
  ],
  "alarms": false,
  "segments": [
    {"start_idx": 0, "end_idx": 19, "mean_bits": 0.9968, "stdev_bits": 0.0006}
  ],
  "summary": {
    "count": 40,
    "drift_detected": false,
    "last_change_point": null
  }
}

### Determinism
Offline analysis is deterministic for fixed inputs/params.

### Notes
- Intended to monitor Quentroy/Exec metrics longitudinally.
