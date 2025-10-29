import pathlib

def test_unit09_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_src = (root / "nvqa_cli.py").read_text()
    req = [
        "nve-verify-cert",
        "--cert",
        "--counts",
        "--out-verdict",
        'verify_version="Unit09"',
    ]
    miss = [b for b in req if b not in cli_src]
    assert not miss, f"nvqa_cli.py missing Unit09 contract bits: {miss}"
