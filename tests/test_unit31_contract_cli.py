import pathlib

def test_unit31_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-provenance","--inputs","--out-archive",'provenance_version="Unit31"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit31 bits: {miss}"

def test_unit31_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit31.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-provenance","--inputs","--out-archive",'provenance_version="Unit31"',
        '"provenance_version": "Unit31"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"endianness": "little"','"qft_kernel_sign": "+"',
        '"archive_format": "tar.gz"','"item_count":','"items":','"sha256":','"bundle_sha256":',
        '"deterministic_ordering": true','Determinism'
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit31.md missing tokens: {miss}"
