import pathlib

def test_unit18_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-drift","--inputs","--out-drift","--metric","--window",'drift_version="Unit18"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit18 bits: {miss}"

def test_unit18_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit18.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-drift","--inputs","--out-drift","--metric","--window",'drift_version="Unit18"',
        '"drift_version": "Unit18"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"metric":','"abs_tolerance_bits":','"window":',
        '"series"','"timestamp_utc"','"backend_name"','"value_bits"',
        '"stats"','"count"','"mean_bits"','"stdev_bits"','"slope_bits_per_hour"','"max_excursion_bits"',
        '"excursions"','"index"','"delta_from_mean_bits"','"exceeds_tolerance"',
        '"summary"','"within_tolerance"','"excursion_count"',
        "Determinism","Offline","backend_name"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit18.md missing tokens: {miss}"
