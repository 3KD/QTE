"""
Unit 03 CLI contract test.

This test enforces that nvqa_cli.py *promises* a stable simulation surface
for shot-generation without hardware.

It does NOT run simulation.
It ONLY checks that the CLI file still exposes the literals the rest of
the stack (Unit 04 hardware executor, Unit 05/06 Quentroy cert) expect.

We REQUIRE nvqa_cli.py to contain:

- "nve-run-sim"
- "--shots"
- "backend\": \"sim\""                 # SimResult must say backend: "sim"
- "prep_version\": \"Unit03\""        # PrepSpec version tag
- "qubit_order"                       # explicit little-endian bit ordering
- "rail_layout"                       # semantic rail mapping from Unit 02
- "psi_source\": \"nve-build\""       # traceability back to canonical NVE

If any go missing, you are not allowed to push.
"""

import pathlib

def test_unit03_cli_surface_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_path = root / "nvqa_cli.py"
    cli_src = cli_path.read_text()

    required_snippets = [
        "nve-run-sim",
        "--shots",
        "backend\": \"sim\"",
        "prep_version\": \"Unit03\"",
        "qubit_order",
        "rail_layout",
        "psi_source\": \"nve-build\"",
    ]

    missing = [snippet for snippet in required_snippets if snippet not in cli_src]
    assert not missing, f"nvqa_cli.py missing required Unit03 literals: {missing}"

def test_unit03_cli_does_not_claim_hardware_backend():
    """
    sanity: Unit 03 is SIM ONLY. It MUST NOT say backend:\"ibm\" or \"hardware\"
    as the canonical outcome of nve-run-sim.
    """
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_path = root / "nvqa_cli.py"
    cli_src = cli_path.read_text()

    forbidden = [
        "backend\": \"ibm\"",
        "backend\": \"hardware\"",
    ]
    leaked = [f for f in forbidden if f in cli_src]
    assert not leaked, f"nvqa_cli.py leaks hardware backend text in Unit03 contract: {leaked}"
