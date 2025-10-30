import pathlib

def test_unit36_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-regrollback","--target-hash","--out-reg",'regrollback_version="Unit36"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit36 bits: {miss}"

def test_unit36_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit36.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-regrollback","--target-hash","--out-reg",'regrollback_version="Unit36"',
        '"regverify_version": "Unit35"',
        '"restored_registry_sha256":','"target_registry_sha256":','"rollback_success": true',
        '"entries_restored": 0','"timestamp_utc":','Determinism','"note":'
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit36.md missing tokens: {miss}"
