"""
Unit 06 CLI surface contract test.

We don't execute nvqa_cli.py here.
We just read the file contents and assert that the CLI text for Unit 06
(Quentroy certificate generation) and the hard invariants are present.

If you change nvqa_cli.py and remove any of these required phrases,
this test fails and you are not allowed to push.

Required phrases:
- "nve-quentroy-cert"
- "--out-cert"
- "quentroy_version=\"Unit06\""
- "loader_version=\"Unit02\""
- "endianness=\"little\""
- "qft_kernel_sign=\"+\""
"""

import pathlib

def test_unit06_cli_contract_strings_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_path = root / "nvqa_cli.py"
    src = cli_path.read_text()

    required_bits = [
        "nve-quentroy-cert",
        "--out-cert",
        "quentroy_version=\"Unit06\"",
        "loader_version=\"Unit02\"",
        "endianness=\"little\"",
        "qft_kernel_sign=\"+\"",
    ]

    missing = [bit for bit in required_bits if bit not in src]
    assert not missing, f"nvqa_cli.py missing required Unit06 contract bits: {missing}"
