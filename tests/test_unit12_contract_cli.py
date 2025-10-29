import pathlib

def test_unit12_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_src = (root / "nvqa_cli.py").read_text()
    req = [
        "nve-live-smoke","--object","--weighting","--phase-mode","--rail-mode",
        "--N","--shots","--backend","--out-spec","--out-receipt",'live_version="Unit12"',
    ]
    miss = [b for b in req if b not in cli_src]
    assert not miss, f"nvqa_cli.py missing Unit12 literals: {miss}"
