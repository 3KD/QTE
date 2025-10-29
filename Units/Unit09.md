# Unit 09 — Quentroy Verifier (Recompute & Integrity Check)

Recomputes entropy metrics from counts and verifies a Quentroy certificate (Unit 06) for deterministic integrity.

## CONTRACT (DO NOT CHANGE)
CLI surface that MUST appear literally in nvqa_cli.py:
- nve-verify-cert
- --cert
- --counts
- --out-verdict
- verify_version="Unit09"

### Required inputs
- Quentroy certificate JSON path via `--cert` (produced by Unit 06)
- Counts JSON path via `--counts` (Z or X basis, must match certificate basis)

### Required VERDICT JSON fields (verbatim keys must exist)
{
  "verify_version": "Unit09",
  "cert_path": "",
  "counts_path": "",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "quentroy_version": "Unit06",
  "endianness": "little",
  "qft_kernel_sign": "+",
  "recomputed": {
    "H_Z_bits": 0.0,
    "H_X_bits": 0.0,
    "KL_to_uniform_bits": 0.0,
    "min_entropy_bits": 0.0,
    "MU_lower_bound_bits": 0.0
  },
  "claimed": {
    "H_Z_bits": 0.0,
    "H_X_bits": 0.0,
    "KL_to_uniform_bits": 0.0,
    "min_entropy_bits": 0.0,
    "MU_lower_bound_bits": 0.0
  },
  "tolerance_bits": 1e-12,
  "passed": true,
  "discrepancies": []
}

### Determinism
- For fixed inputs, VERDICT is bit-for-bit stable (fixed numeric tolerance and ordering).
