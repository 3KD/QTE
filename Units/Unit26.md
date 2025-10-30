# Unit 26 — Live Queue Forecaster & Shot Budget Optimizer

Estimates queue delay on a target backend and proposes a shots batching plan to minimize wall time vs. fidelity loss. Can read prior receipts (Unit04) to infer typical job sizes.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-queue-forecast
- --backend
- --horizon
- --shots
- --out-plan
- queue_version="Unit26"

### Required Plan JSON fields (verbatim keys must exist)
{
  "queue_version": "Unit26",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "endianness": "little",
  "qft_kernel_sign": "+",
  "backend_name": "ibm_torino",
  "horizon": "PT2H",
  "demand_shots": 8192,
  "est_wait_minutes": 37.5,
  "slots": [
    {"submit_after_utc": "2025-10-30T00:00:00Z", "shots": 4096},
    {"submit_after_utc": "2025-10-30T00:25:00Z", "shots": 4096}
  ],
  "policy": {
    "objective": "min_wall_time",
    "max_concurrent_jobs": 2,
    "chunk_size_hint": 4096
  },
  "assumptions": {
    "arrival_rate_jobs_per_min": 0.8,
    "service_time_min_mean": 3.0
  }
}

### Determinism
- Depends on live queue telemetry; treat as **non-deterministic**.
- Offline tests MUST mock queue stats; live path is opt-in via `NVQA_LIVE=1`.

### Notes
- `--horizon` accepts ISO-8601 duration (e.g., `PT2H`) or absolute window `start,end`.
- `--shots` is total requested shots to allocate across plan slots.
