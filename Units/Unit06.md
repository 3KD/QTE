# Unit 06 — Quentroy Certificate (v06)

Defines the **Quentroy** certificate file format and CLI for entropy signatures computed from measured counts. Inputs are counts (Z/X) and metadata flowing from Units 01–04. Output is a deterministic JSON certificate consumed by later verification/crypto units.

## Required certificate fields (exact names)
- "quentroy_version": "Unit06"
- "nve_version"
- "endianness": "little"
- "qft_kernel_sign": "+"
- "loader_version": "Unit02"
- "exec_version": "Unit04"
- "backend_name"
- "shots"
- "H_Z_bits"
- "H_X_bits"
- "KL_to_uniform_bits"
- "min_entropy_bits"
- "MU_lower_bound_bits"
- "counts_source"
- "psi_source": "nve-build"
- "rail_layout"
- "qubit_order"

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags (must appear literally in nvqa_cli.py):
- nve-quentroy-cert
- --counts
- --basis
- --out-cert
- quentroy_version="Unit06"
- endianness="little"
- qft_kernel_sign="+"
- loader_version="Unit02"
- exec_version="Unit04"

**Example (documented interface)**:
```bash
./nvqa_cli.py nve-quentroy-cert \
  --counts /path/to/counts.json \
  --basis Z \
  --out-cert /path/to/quentroy_cert.json
```

**Expected behavior:**
- Load counts (Z or X basis).
- Compute entropy bundle (H_*, KL_to_uniform_bits, min_entropy_bits, MU_lower_bound_bits).
- Emit JSON with all **Required certificate fields** above.
- Deterministic for a fixed counts JSON.

**Live path (described):**
- When `NVQA_LIVE=1` and IBM credentials exist in `~/.qiskit/qiskit-ibm.json`:
  - Build ψ (Unit 01), LoaderSpec (Unit 02), PrepSpec (Unit 03), Exec (Unit 04) on `backend_name="ibm_torino"`.
  - Save counts; call `nve-quentroy-cert` to produce the Quentroy certificate.
