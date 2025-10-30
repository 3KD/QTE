import pathlib

def test_unit14_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-drift-scan","--inputs","--out-report","--out-trend",'drift_version="Unit14"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit14 bits: {miss}"

def test_unit14_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit14.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-drift-scan","--inputs","--out-report","--out-trend",'drift_version="Unit14"',
        '"drift_version": "Unit14"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"atlas_version": "Unit07"','"backend_name":','"time_window":','"start_utc"','"end_utc"','"sample_count"',
        '"metrics"','"H_Z_bits_mean"','"H_X_bits_mean"','"KL_to_uniform_bits_mean"',
        '"min_entropy_bits_p05"','"min_entropy_bits_p50"','"min_entropy_bits_p95"',
        '"stability_flags"','"drift_detected"','"regression_vs_baseline"',
        '"baseline"','"psi_fingerprint"','"semantic_hash"',
        "deterministic"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit14.md missing tokens: {miss}"
