import pathlib

def test_unit10_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_src = (root / "nvqa_cli.py").read_text()
    req = [
        "nve-attest",
        "--cert",
        "--verdict",
        "--out-attestation",
        'attest_version="Unit10"',
    ]
    miss = [b for b in req if b not in cli_src]
    assert not miss, f"nvqa_cli.py missing Unit10 contract bits: {miss}"
