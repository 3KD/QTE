import pathlib

def test_unit33_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-attest","--report","--out-attestation",'attest_version="Unit33"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit33 bits: {miss}"

def test_unit33_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit33.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-attest","--report","--out-attestation",'attest_version="Unit33"',
        '"verify_version": "Unit32"',
        '"report_sha256":','"attestation_sha256":','"archive_sha256":','"manifest_sha256":',
        '"item_count":','"mismatches":','"verified_true": true',
        '"signer":','"signature_alg": "ed25519"','"signature_b64":','"timestamp_utc":',
        "Determinism","attestation JSON"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit33.md missing tokens: {miss}"
