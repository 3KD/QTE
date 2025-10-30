import pathlib

def test_unit32_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-verify","--archive","--out-report",'verify_version="Unit32"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit32 bits: {miss}"

def test_unit32_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit32.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-verify","--archive","--out-report",'verify_version="Unit32"',
        '"provenance_version": "Unit31"',
        '"archive_format": "tar.gz"',
        '"archive_path":','"archive_sha256":','"manifest_sha256":',
        '"item_count":','"items":','"expected_sha256":','"actual_sha256":',
        '"status":','"mismatches":','"verified_true": true','"timestamp_utc":',
        "Determinism","No live backend calls"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit32.md missing tokens: {miss}"
