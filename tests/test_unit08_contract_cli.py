import pathlib

def test_unit08_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_src = (root / "nvqa_cli.py").read_text()
    req = [
        "nve-atlas-report",
        "--embed",
        "--clusters",
        "--out-report",
        "--out-fig",
        'report_version="Unit08"',
    ]
    miss = [b for b in req if b not in cli_src]
    assert not miss, f"nvqa_cli.py missing Unit08 contract bits: {miss}"
