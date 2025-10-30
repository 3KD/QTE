import pathlib

def test_unit11_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_src = (root / "nvqa_cli.py").read_text()
    req = [
        "nve-entropy-witness",
        "--cert",
        "--counts-z",
        "--counts-x",
        "--out-witness",
        'witness_version="Unit11"',
    ]
    miss = [b for b in req if b not in cli_src]
    assert not miss, f"nvqa_cli.py missing Unit11 contract bits: {miss}"
