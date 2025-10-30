import pathlib

def test_unit16_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-drift","--inputs","--out-trend","--out-alerts",'drift_version="Unit16"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit16 bits: {miss}"

def test_unit16_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit16.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-drift","--inputs","--out-trend","--out-alerts",'drift_version="Unit16"',
        '"drift_version": "Unit16"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"atlas_version": "Unit07"','"sources":','"backends":','"metrics":','"window_days":',
        '"trend"','"fit_model"','"trend_bits_per_day"','"stderr"','"r2"','"samples"',
        '"changepoints"','"delta_bits"','"zscore"','"severity"','"policy"','"z_hi"','"z_med"',
        "Determinism","deterministic","timestamp_utc","backend_name"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit16.md missing tokens: {miss}"
