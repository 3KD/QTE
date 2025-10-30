"""
Unit 02 CLI contract test.

We don't exec the CLI yet because nvqa_cli.py is still a TODO stub in this phase.
Instead we assert that nvqa_cli.py source code already declares:
- a subcommand called nve-loader-spec
- an --out-spec flag
- an explicit loader_version="Unit02" string literal

If any of these are missing, then Unit 02 requirements are not wired into the CLI surface,
which means downstream Units 03, 04, 05 cannot rely on stable loader export.
"""

import pathlib

def test_loader_spec_cli_contract():
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_path = root / "nvqa_cli.py"
    cli_src = cli_path.read_text()

    required_snippets = [
        "nve-loader-spec",
        "--out-spec",
        "loader_version=\"Unit02\"",
    ]

    missing = [snippet for snippet in required_snippets if snippet not in cli_src]
    assert not missing, f"nvqa_cli.py missing required CLI surface hints for Unit02: {missing}"
