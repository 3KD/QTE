import pathlib

def test_unit10_doc_contract_strings_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit10.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-attest",
        "--cert",
        "--verdict",
        "--out-attestation",
        'attest_version="Unit10"',
        '"attest_version": "Unit10"',
        '"cert_path":',
        '"verdict_path":',
        '"nve_version": "Unit01"',
        '"loader_version": "Unit02"',
        '"prep_version": "Unit03"',
        '"exec_version": "Unit04"',
        '"quentroy_version": "Unit06"',
        '"verify_version": "Unit09"',
        '"endianness": "little"',
        '"qft_kernel_sign": "+"',
        '"git_commit":',
        '"python_version":',
        '"qiskit_version":',
        '"backend_name":',
        '"backend_properties_digest":',
        '"receipt_chain":',
        '"exec_receipt_sha256":',
        '"counts_sha256":',
        '"cert_sha256":',
        '"verdict_sha256":',
        '"manifest_sha256":',
        '"passed":',
        '"determinism_note":',
    ]
    miss = [b for b in req if b not in doc]
    assert not miss, f"Unit10.md missing required tokens: {miss}"
