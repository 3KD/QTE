import pathlib

def test_unit19_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-compare","--inputs","--out-compare","--metric","--group-by",'comparator_version="Unit19"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit19 bits: {miss}"

def test_unit19_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit19.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-compare","--inputs","--out-compare","--metric","--group-by",'comparator_version="Unit19"',
        '"comparator_version": "Unit19"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"metric":','"group_by":',
        '"items"','"backend_name"','"timestamp_utc"','"value_bits"',
        '"per_backend"','"count"','"mean_bits"','"stdev_bits"',
        '"pairwise"','"backend_a"','"backend_b"','"delta_mean_bits"',
        '"summary"','"backend_count"','"max_pairwise_delta_bits"',
        "Determinism","Offline","backend_name"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit19.md missing tokens: {miss}"
