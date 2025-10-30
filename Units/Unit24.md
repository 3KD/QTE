# Unit 24 — Backend Benchmark Matrix (Cross-Backend Health & Speed)

Runs a fixed micro-program across multiple IBM backends (or simulators) and aggregates timing/quality metrics into a matrix for comparison.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-backend-matrix
- --backends
- --program
- --shots
- --out-matrix
- matrix_version="Unit24"

### Required Matrix JSON fields (verbatim keys must exist)
{
  "matrix_version": "Unit24",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "qft_kernel_sign": "+",
  "endianness": "little",
  "program_name": "bell_pair_latency",
  "shots": 1024,
  "backends": [
    "ibm_torino",
    "ibmq_qasm_simulator"
  ],
  "rows": [
    {
      "backend_name": "ibm_torino",
      "queue_time_s": 12.3,
      "run_time_s": 0.51,
      "total_time_s": 12.81,
      "success_prob": 0.973,
      "fidelity_est": 0.965,
      "timestamp_utc": "2025-10-30T00:00:00Z"
    }
  ],
  "summary": {
    "fastest_backend": "ibmq_qasm_simulator",
    "highest_fidelity_backend": "ibm_torino"
  }
}

### Determinism
- Offline (simulator) path is deterministic for fixed seeds/params.
- Live IBM path is non-deterministic and gated behind NVQA_LIVE=1.

### Notes
- `--program` names a tiny canonical circuit (e.g., `bell_pair_latency`, `qft_n3`).
- `--backends` accepts a comma-separated list (e.g., `ibm_torino,ibmq_qasm_simulator`).
