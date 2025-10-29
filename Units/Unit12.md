# Unit 12 — IBM Backend Live Smoke & Receipt Verifier

A minimal live execution path against IBM Quantum Cloud to validate end-to-end wiring:
Unit 01 (ψ) → Unit 02 (LoaderSpec) → Unit 03 (PrepSpec) → Unit 04 (Exec) → counts JSON.
Writes a **RunReceipt** JSON and asserts key fields.

## CONTRACT (DO NOT CHANGE)
CLI surface that MUST appear literally in `nvqa_cli.py`:
- nve-live-smoke
- --object
- --weighting
- --phase-mode
- --rail-mode
- --N
- --shots
- --backend
- --out-spec
- --out-receipt
- live_version="Unit12"

### Required receipt keys (verbatim names must exist)
{
  "receipt_version": "Unit04",
  "backend_name": "",
  "shots": 0,
  "rail_layout": "",
  "exec_version": "Unit04",
  "endianness": "little",
  "qft_kernel_sign": "+"
}

### Notes
- This unit is **live** only when `NVQA_LIVE=1`.
- Backend default for smoke: `"ibm_torino"` (override with `--backend`).
- Determinism is not guaranteed for measurement outcomes; we verify **schema** and **plausible counts**.
