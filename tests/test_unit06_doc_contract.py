"""
Unit06 documentation contract test.

Goal: make sure Units/Unit06.md actually contains the
literal contract strings that downstream tools and verifiers rely on.

We already have a CLI-facing test (test_unit06_contract_cli.py) that
looks at nvqa_cli.py for:
    nve-quentroy-cert
    quentroy_version="Unit06"
    loader_version="Unit02"
    endianness="little"
    qft_kernel_sign="+"

This doc test enforces that Unit06.md itself repeats the required fields
for attested_cert.json and the rationale for verification.
"""

import pathlib

def test_unit06_doc_contract_strings_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    u6_doc = (root / "Units" / "Unit06.md").read_text()

    required_bits = [
        "Unit 06 — Quentroy Certificate / Attested Witness Blob",
        "nve-quentroy-cert",
        'quentroy_version="Unit06"',
        'loader_version="Unit02"',
        'endianness="little"',
        'qft_kernel_sign="+"',
        '"nve_version": "Unit01"',
        '"loader_version": "Unit02"',
        '"prep_version": "Unit03"',
        '"exec_version": "Unit04"',
        '"quentroy_version": "Unit06"',
        '"rail_layout":',
        '"qubit_order":',
        '"backend_name":',
        '"shots":',
        '"H_Z_bits":',
        '"H_X_bits":',
        '"KL_to_uniform_bits":',
        '"min_entropy_bits":',
        '"MU_lower_bound_bits":',
        '"psi_fingerprint":',
        '"semantic_hash":',
        '"timestamp_utc":',
        '"hardware_signature":',
        '"integrity_note":',
    ]

    missing = [bit for bit in required_bits if bit not in u6_doc]
    assert not missing, f"Unit06.md missing required contract tokens: {missing}"
