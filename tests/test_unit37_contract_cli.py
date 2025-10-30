import pathlib

def test_unit37_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-regdiff","--old","--new","--out-diff",'regdiff_version="Unit37"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit37 bits: {miss}"

def test_unit37_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit37.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-regdiff","--old","--new","--out-diff",'regdiff_version="Unit37"',
        '"old_registry_sha256":','"new_registry_sha256":',
        '"added_keys": []','"removed_keys": []','"modified_keys": []','"modified_detail": {}','"timestamp_utc":'
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit37.md missing tokens: {miss}"
