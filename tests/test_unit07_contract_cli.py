import pathlib

def test_unit07_cli_and_doc_contract():
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_src = (root / "nvqa_cli.py").read_text()
    doc = (root / "Units" / "Unit07.md").read_text()

    required_cli = [
        "nve-atlas",
        "--inputs",
        "--out-embed",
        "--out-clusters",
        'atlas_version="Unit07"',
    ]
    missing_cli = [b for b in required_cli if b not in cli_src]

    required_doc = [
        "Unit 07 — Function Atlas",
        "nve-atlas",
        "--inputs",
        "--out-embed",
        "--out-clusters",
        'atlas_version="Unit07"',
        "## CONTRACT (DO NOT CHANGE)",
    ]
    missing_doc = [b for b in required_doc if b not in doc]

    assert not missing_cli, f"nvqa_cli.py missing Unit07 tokens: {missing_cli}"
    assert not missing_doc, f"Unit07.md missing contract tokens: {missing_doc}"
