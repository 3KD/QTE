
## CONTRACT (DO NOT CHANGE)

This section is machine-checked by pytest.  
If you edit / rename / remove any required tokens here without updating tests, pytest will fail and you will not be allowed to push.

Unit05 definition:
We compute Quentroy Entropy from measurement counts and emit a Quentroy certificate.
Quentroy is the ONLY accepted entropy witness in this project name-space.  
No one is allowed to call it "generic entropy" or silently rename it.

Required CLI subcommand (must exist in nvqa_cli.py and stay spelled exactly like this):
- `nve-quentroy`

Required CLI flags for `nve-quentroy`:
- `--counts`
- `--basis`
- `--out-cert`

Behavioral contract for `nve-quentroy`:
1. Read shot-counts (JSON) produced by Unit03 simulator or Unit04 RunReceipt.  
   Those counts are keyed by observed bitstrings in `"little"` endianness.
2. Read `basis`, which can be:
   - `"Z"`
   - `"X"`
   - `"QFT"`  (the +2π i convention, same `qft_kernel_sign="+"`)
3. Compute the Quentroy Entropy bundle.  
   The Quentroy cert MUST be saved to `--out-cert` as JSON, and MUST include:
   - `quentroy_version="Unit05"`
   - `H_Z_bits`
   - `H_X_bits`
   - `KL_to_uniform_bits`
   - `min_entropy_bits`
   - `MU_lower_bound_bits`
   - `nve_version`
   - `endianness="little"`
   - `qft_kernel_sign="+"`
   - `rail_layout` (copied forward so audit can bind entropy back to semantic rails)
   - `exec_version` (if known; pulled from RunReceipt)
   - `backend_name` and `shots` (if known; pulled from RunReceipt)
4. If any of those mandatory keys are missing, certificate is invalid.

Security / attestation expectations:
- `quentroy_version="Unit05"` is non-negotiable. This tags WHICH Quentroy definition we used.
- We always carry `nve_version` so we can prove which embedding rules generated ψ.
- We always carry `rail_layout` so we can prove which semantic rails (pos/neg, iq_split, etc.) this entropy claim refers to.
- We always carry `qft_kernel_sign="+"` and `endianness="little"` to lock interpretation of bitstrings and Fourier basis.
- We always carry `MU_lower_bound_bits`, which encodes the Maassen–Uffink-style lower bound (uncertainty relation) that links complementary bases. If MU is violated, we treat the run as tampered or non-physical.

Downstream dependency:
- Unit11 (tamper cert) and Unit25 (payload attestation / watermark) will refuse to honor any run that doesn’t ship a Quentroy cert with `quentroy_version="Unit05"` and matching `nve_version`.

## TEST CONTRACT (DO NOT CHANGE)

Relevant tests:
- tests/test_unit05_contract_cli.py

Required CLI surface in nvqa_cli.py:
- subcommand token `nve-quentroy`
  Flags:
    --counts
    --basis
    --out-cert
  Behavior:
    - ingest counts from either:
        * simulator path (Unit03 PrepSpec shot loop), or
        * hardware RunReceipt (Unit04, e.g. ibm_torino)
    - compute Quentroy certificate
    - write QuentroyCert JSON to --out-cert

QuentroyCert MUST include:
- quentroy_version="Unit05"
- per-basis entropy bundle fields:
    "H_Z_bits"
    "H_X_bits"
    "KL_to_uniform_bits"
    "min_entropy_bits"
    "MU_lower_bound_bits"
- provenance fields to tie this cert back to physical execution:
    "nve_version": "Unit01"
    "loader_version": "Unit02"
    "prep_version": "Unit03"
    "exec_version": "Unit04"
    "backend_name": "<backend>"
    "shots": <int>
    "rail_layout": { ... }
    "endianness": "little"
    "qft_kernel_sign": "+"

tests/test_unit05_contract_cli.py literally greps nvqa_cli.py
and Units/Unit05.md for:
- "nve-quentroy"
- "--counts"
- "--out-cert"
- 'quentroy_version="Unit05"'
- "H_Z_bits"
- "H_X_bits"
- "KL_to_uniform_bits"
- "min_entropy_bits"
- "MU_lower_bound_bits"
- "nve_version"
- "rail_layout"
- "exec_version"
- "backend_name"
- "shots"
- "endianness"
- "little"
- "qft_kernel_sign"
- "+"

If any of these disappear or change spelling, pytest fails, because that
would mean we broke auditability: you wouldn't be able to prove that the
entropy signature you're handing someone actually came from the specific
ψ built in Unit01, loaded via Unit02, prepared in Unit03, executed in
Unit04 on a named backend, with known rail_layout, endianness="little",
and qft_kernel_sign="+".

This is the tamper witness / certification path and will later drive
payload attestation and cryptographic watermarking.
