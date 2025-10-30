# Unit 13 — Replay & Receipt Reproducer

Recreate counts by replaying an Exec receipt (from Unit 04 runs) on the same or override backend. Produces fresh counts and a provenance note for audit.

## CONTRACT (DO NOT CHANGE)
CLI surface (must appear literally in `nvqa_cli.py`):
- nve-replay
- --receipt
- --out-counts
- --backend
- replay_version="Unit13"

### Required JSON fields (these keys MUST appear in docs and artifacts)
{
  "replay_version": "Unit13",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "endianness": "little",
  "qft_kernel_sign": "+",
  "rail_layout": "",
  "qubit_order": "",
  "backend_name": "",
  "shots": 0,
  "timestamp_utc": "",
  "counts": {},
  "replay_note": "replayed from receipt",
  "source_receipt_path": ""
}

### Behavior
- Input: --receipt path to an Exec receipt JSON (Unit 04).
- Output: --out-counts JSON with fresh counts + provenance fields above.
- Optional: --backend overrides the backend named in the receipt.
- Determinism: given fixed backend/config, behavior is deterministic up to hardware noise.
- Live mode: if NVQA_LIVE=1 and IBM credentials exist, use NVQA_BACKEND (default ibm_torino); otherwise simulate.
