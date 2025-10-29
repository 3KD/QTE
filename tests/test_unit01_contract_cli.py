"""
Unit 01 CLI contract test.

Goal:
- Assert nvqa_cli.py *advertises* the required Unit 01 guarantees so nobody
  "cleans up wording" and silently breaks downstream units.

We grep for required literals that MUST remain stable:

Required literals:
- "nve-build"                       (Unit01 front door)
- "--out-meta"                      (metadata output path flag)
- "nve_version=\"Unit01\""          (canonical version tag)
- "endianness=\"little\""           (canonical little-endian basis claim)
- "qft_kernel_sign=\"+\""           (canonical + sign convention for QFT)
- "||ψ||₂ ≈ 1e-12"                  (normalization guarantee string)
- "nve-similarity"                  (symmetry CLI)
- "similarity symmetry tolerance 1e-12" (symmetry rule literal)

If any of these disappear, this test fails and you DON'T PUSH.
"""

import pathlib
import pytest

def test_unit01_cli_surface_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_path = root / "nvqa_cli.py"
    cli_src = cli_path.read_text()

    required_snippets = [
        "nve-build",
        "--out-meta",
        'nve_version="Unit01"',
        'endianness="little"',
        'qft_kernel_sign="+"',
        "||ψ||₂ ≈ 1e-12",
        "nve-similarity",
        "similarity symmetry tolerance 1e-12",
    ]

    missing = [snippet for snippet in required_snippets if snippet not in cli_src]
    assert not missing, f"nvqa_cli.py missing required Unit01 literals: {missing}"

@pytest.mark.parametrize(
    "forbidden",
    [
        # make sure nobody tries to rename Quentroy back to generic "entropy cert" here
        # Unit01 is allowed to SAY 'Quentroy Entropy' but it is NOT allowed
        # to call it something generic like 'generic_entropy' without saying Quentroy.
        "generic_entropy_signature",
    ],
)
def test_unit01_no_forbidden_weasel_words(forbidden):
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_path = root / "nvqa_cli.py"
    cli_src = cli_path.read_text()
    assert forbidden not in cli_src, f"forbidden term '{forbidden}' leaked into nvqa_cli.py"
