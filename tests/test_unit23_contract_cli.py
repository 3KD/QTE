import pathlib

def test_unit23_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-drift","--inputs","--window","--threshold","--out-report",'drift_version="Unit23"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit23 bits: {miss}"

def test_unit23_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit23.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-drift","--inputs","--window","--threshold","--out-report",'drift_version="Unit23"',
        '"drift_version": "Unit23"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"window":','"threshold":','"metric":',
        '"items"','"timestamp_utc"','"backend_name"','"value_bits"',
        '"tests"','"KS_two_sample"','"CUSUM"','"p_value"','"alarm"',
        '"alarms"','"segments"','"mean_bits"','"stdev_bits"',
        '"summary"','"count"','"drift_detected"','"last_change_point"',
        "Determinism","Offline","longitudinal"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit23.md missing tokens: {miss}"
