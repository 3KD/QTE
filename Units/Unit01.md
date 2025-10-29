
## TEST CONTRACT (DO NOT CHANGE)

This section is frozen. Pytests assert these exact phrases exist
and they assert the CLI exposes matching knobs. Changing this text
without updating tests will fail the repo.

Relevant tests:
- tests/test_unit01_contract_cli.py
- tests/test_nve_normalization.py
- tests/test_nve_metadata_roundtrip.py
- tests/test_nve_endianness_qftsign.py
- tests/test_nve_similarity_symmetry.py
- tests/test_nve_phase_mode_integrity.py

Required CLI surface in nvqa_cli.py:
- `nve-build`
  Flags:
    --object
    --weighting
    --phase-mode
    --rail-mode
    --N
    --out-psi
    --out-meta
  Behavior:
    - run package_nve(...)
    - emit ψ with L2 norm ||ψ||₂ ≈ 1e-12 from 1.0
    - refuse NaN / Inf / zero norm
    - write metadata JSON with:
        "endianness": "little"
        "qft_kernel_sign": "+"
        "weighting_mode": <string>
        "phase_mode": <string>
        "rail_mode": <string>
        "length": <int>
        "norm_l2": 1.0
        "nve_version": "Unit01"

- `nve-similarity`
  Flags:
    --a
    --b
    --metric
  Behavior:
    - load two ψ
    - compute symmetric similarity (cosine/fidelity-like)
    - enforce "similarity symmetry tolerance 1e-12"

Determinism rules:
- Running `nve-build` twice with the same ObjectSpec MUST produce
  byte-identical ψ arrays (not just allclose) AND identical metadata.
  This is enforced by tests/test_nve_metadata_roundtrip.py.

Normalization + metadata rules:
- `tests/test_nve_normalization.py` demands ||ψ||₂ is within 1e-12 of 1,
  and that ψ has no NaN/Inf.
- `tests/test_nve_endianness_qftsign.py` demands metadata["endianness"] == "little"
  and metadata["qft_kernel_sign"] == "+".
- `tests/test_nve_phase_mode_integrity.py` demands that
  phase_mode=full_complex and phase_mode=magnitude_only give
  distinct ψ (not byte-identical) for the same math object.
- `tests/test_nve_similarity_symmetry.py` demands the similarity metric
  is symmetric within 1e-12.

If any of these fail, Unit01 is invalid and downstream units
(LoaderSpec in Unit02, PrepSpec in Unit03, ExecSpec/RunReceipt in Unit04,
Quentroy in Unit05) are not trusted.
