import pathlib

def test_unit34_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-regsync","--attestation","--out-reg",'regsync_version="Unit34"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit34 bits: {miss}"

def test_unit34_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit34.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-regsync","--attestation","--out-reg",'regsync_version="Unit34"',
        '"attest_version": "Unit33"',
        '"registry_sha256":','"attestation_sha256":','"previous_registry_sha256":',
        '"entries": []','"entry_count": 0','"timestamp_utc":','"integrity_note":',
        "Determinism","registry JSON"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit34.md missing tokens: {miss}"
