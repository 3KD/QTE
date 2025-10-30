import pathlib

def test_unit35_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-regverify","--reg","--out-report",'regverify_version="Unit35"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit35 bits: {miss}"

def test_unit35_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit35.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-regverify","--reg","--out-report",'regverify_version="Unit35"',
        '"regsync_version": "Unit34"',
        '"registry_sha256":','"previous_registry_sha256":','"entry_count": 0',
        '"continuity_ok": true','"hash_ok": true','"structure_ok": true',
        '"issues": []','"timestamp_utc":','Determinism','verification booleans'
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit35.md missing tokens: {miss}"
