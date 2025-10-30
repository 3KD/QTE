import pathlib

def test_unit27_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-calib-tag","--backend","--window","--out-calib",'calib_version="Unit27"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit27 bits: {miss}"

def test_unit27_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit27.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-calib-tag","--backend","--window","--out-calib",'calib_version="Unit27"',
        '"calib_version": "Unit27"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"endianness": "little"','"qft_kernel_sign": "+"',
        '"backend_name":','"window":','"samples":','"drift_ppm":',
        '"t1_ms_median":','"t2_ms_median":','"readout_error_mean":','"cx_error_mean":',
        '"timestamp_utc":','"notes":',
        "NVQA_LIVE","non-deterministic"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit27.md missing tokens: {miss}"
