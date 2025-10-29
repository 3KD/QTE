import pathlib

def test_unit12_doc_contract_strings_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit12.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-live-smoke",
        "--out-spec","--out-receipt",
        'live_version="Unit12"',
        '"receipt_version": "Unit04"',
        '"backend_name":',
        '"shots":',
        '"rail_layout":',
        '"exec_version": "Unit04"',
        '"endianness": "little"',
        '"qft_kernel_sign": "+"',
    ]
    miss = [b for b in req if b not in doc]
    assert not miss, f"Unit12.md missing required tokens: {miss}"
