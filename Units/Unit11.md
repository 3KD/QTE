# Unit 11 — Entropy Witness & Cross-Basis Consistency

Computes a deterministic **entropy witness** that cross-checks Z/X basis entropy/KL vs. expectations embedded in the Quentroy certificate (Unit 06). Produces a witness JSON with pass/fail and rationale.

## CONTRACT (DO NOT CHANGE)
CLI surface that MUST appear literally in nvqa_cli.py:
- nve-entropy-witness
- --cert
- --counts-z
- --counts-x
- --out-witness
- witness_version="Unit11"

### Required inputs
- `--cert` : path to Quentroy certificate JSON (Unit 06)
- `--counts-z` : path to Z-basis counts JSON
- `--counts-x` : path to X-basis counts JSON
- `--out-witness` : path to write witness JSON

### Required WITNESS JSON fields (verbatim keys must exist)
{
  "witness_version": "Unit11",
  "cert_path": "",
  "counts_z_path": "",
  "counts_x_path": "",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "quentroy_version": "Unit06",
  "endianness": "little",
  "qft_kernel_sign": "+",
  "backend_name": "",
  "shots": 0,
  "H_Z_bits_expected": 0.0,
  "H_Z_bits_measured": 0.0,
  "H_X_bits_expected": 0.0,
  "H_X_bits_measured": 0.0,
  "KL_Z_to_uniform_bits": 0.0,
  "KL_X_to_uniform_bits": 0.0,
  "uncertainty_bound_bits": 0.0,
  "delta_H_bits": 0.0,
  "passed": true,
  "rationale": ""
}

### Behavior (documentation)
- Deterministic for fixed inputs (canonical JSON with sorted keys & fixed float formatting).
- Uses counts to recompute H_Z/H_X and KL(·||uniform).
- Checks uncertainty / lower-bound consistency and tolerance windows defined in Unit 06.
