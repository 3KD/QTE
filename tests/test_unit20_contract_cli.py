import pathlib

def test_unit20_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-drift","--inputs","--out-drift","--window","--metric",'drift_version="Unit20"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit20 bits: {miss}"

def test_unit20_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit20.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-drift","--inputs","--out-drift","--window","--metric",'drift_version="Unit20"',
        '"drift_version": "Unit20"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"metric":','"window":',
        '"items"','"backend_name"','"timestamp_utc"','"value_bits"',
        '"per_window"','"t_start_utc"','"t_end_utc"','"count"','"mean_bits"','"stdev_bits"','"max_abs_delta_bits"',
        '"summary"','"backend_count"','"window_count"','"max_backend_drift_bits"',
        "Determinism","offline","backend_name"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit20.md missing tokens: {miss}"
