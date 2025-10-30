import pathlib

def test_unit22_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-aggregate","--inputs","--out-metrics","--metric","--correlate",'aggregate_version="Unit22"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit22 bits: {miss}"

def test_unit22_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit22.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-aggregate","--inputs","--out-metrics","--metric","--correlate",'aggregate_version="Unit22"',
        '"aggregate_version": "Unit22"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"metric":','"correlate":',
        '"items"','"backend_name"','"timestamp_utc"','"value_bits"',
        '"global_metrics"','"mean_bits"','"stdev_bits"','"min_bits"','"max_bits"','"range_bits"',
        '"correlation_matrix"','"summary"','"entry_count"','"is_correlated"',
        "Determinism","offline","hybrid","simulation"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit22.md missing tokens: {miss}"
