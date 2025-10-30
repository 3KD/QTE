"""
Unit05 Quentroy / entropy cert contract freeze test.

We assert:
1. nvqa_cli.py exposes nve-quentroy and required flags.
2. Units/Unit05.md CONTRACT section promises all mandatory keys
   like quentroy_version="Unit05", MU_lower_bound_bits, etc.

NOTE:
We only check for substrings. We do NOT parse JSON here.
"""

import pathlib

def test_unit05_cli_and_doc_contract():
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_src = (root / "nvqa_cli.py").read_text()
    u5_doc = (root / "Units" / "Unit05.md").read_text()

    required_cli_bits = [
        "nve-quentroy",
        "--counts",
        "--basis",
        "--out-cert",
        'quentroy_version="Unit05"',
    ]
    missing_cli = [bit for bit in required_cli_bits if bit not in cli_src]

    required_doc_bits = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-quentroy",
        "--counts",
        "--out-cert",
        'quentroy_version="Unit05"',
        "H_Z_bits",
        "H_X_bits",
        "KL_to_uniform_bits",
        "min_entropy_bits",
        "MU_lower_bound_bits",
        "nve_version",
        "rail_layout",
        "exec_version",
        "backend_name",
        "shots",
        "endianness",
        "little",
        "qft_kernel_sign",
        "+",
    ]
    missing_doc = [bit for bit in required_doc_bits if bit not in u5_doc]

    assert not missing_cli, f"nvqa_cli.py missing Unit05 contract tokens: {missing_cli}"
    assert not missing_doc, f"Unit05.md missing contract tokens: {missing_doc}"
