import pathlib

def test_unit15_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-xbackend","--inputs","--out-consistency","--out-transfer",'cross_version="Unit15"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit15 bits: {miss}"

def test_unit15_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit15.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-xbackend","--inputs","--out-consistency","--out-transfer",'cross_version="Unit15"',
        '"cross_version": "Unit15"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"atlas_version": "Unit07"','"backends":','"sample_count":',
        '"pairwise"','"JSD_between_counts_bits"','"Hellinger_distance"','"agreement_rate_topk"',
        '"transfer_map"','"algo"','"anchor_backend"','"targets"','"mapped_error_bits_rmse"','"mapped_bias_bits"',
        "Determinism","deterministic"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit15.md missing tokens: {miss}"
