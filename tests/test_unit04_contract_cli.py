"""
Unit04 exec path contract freeze test.

We assert:
1. nvqa_cli.py exposes nve-run-exec and required flags.
2. Units/Unit04.md CONTRACT section promises the frozen execution/receipt layout.

We DO NOT parse JSON here; we just assert critical substrings exist.
"""

import pathlib

def test_unit04_cli_and_doc_contract():
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_src = (root / "nvqa_cli.py").read_text()
    u4_doc = (root / "Units" / "Unit04.md").read_text()

    # CLI surface expectations we require to appear in nvqa_cli.py
    required_cli_bits = [
        "nve-run-exec",
        "--object",
        "--weighting",
        "--phase-mode",
        "--rail-mode",
        "--N",
        "--shots",
        "--backend",
        "--out-spec",
        "--out-receipt",
        'exec_version="Unit04"',
    ]
    missing_cli = [bit for bit in required_cli_bits if bit not in cli_src]

    # Doc contract expectations we require to appear in Unit04.md
    required_doc_bits = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-run-exec",
        "--out-spec",
        "--out-receipt",
        'exec_version="Unit04"',
        '"endianness": "little"',
        '"qft_kernel_sign": "+"',
        '"receipt_version": "Unit04"',
        '"rail_layout"',
        '"backend_name"',
        '"shots"',
    ]
    missing_doc = [bit for bit in required_doc_bits if bit not in u4_doc]

    assert not missing_cli, f"nvqa_cli.py missing Unit04 contract tokens: {missing_cli}"
    assert not missing_doc, f"Unit04.md missing contract tokens: {missing_doc}"
