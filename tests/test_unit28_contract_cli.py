import pathlib

def test_unit28_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-receipt-diff","--a","--b","--out-diff",'diff_version="Unit28"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit28 bits: {miss}"

def test_unit28_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit28.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-receipt-diff","--a","--b","--out-diff",'diff_version="Unit28"',
        '"diff_version": "Unit28"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"endianness": "little"','"qft_kernel_sign": "+"',
        '"receipt_a_path":','"receipt_b_path":',
        '"backend_name_a":','"backend_name_b":',
        '"shots_a":','"shots_b":',
        '"hellinger":','"bhattacharyya":',
        '"kl_bits_a_to_b":','"kl_bits_b_to_a":',
        '"chi2":','"ks_pvalue":',
        '"distance_ok":','"threshold_note":','"timestamp_utc":',
        "NVQA_LIVE","Deterministic"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit28.md missing tokens: {miss}"
