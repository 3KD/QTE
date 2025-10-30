import pathlib

def test_unit25_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-calib-snap","--backends","--window","--metrics","--out-report",'calib_version="Unit25"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit25 bits: {miss}"

def test_unit25_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit25.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-calib-snap","--backends","--window","--metrics","--out-report",'calib_version="Unit25"',
        '"calib_version": "Unit25"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"qft_kernel_sign": "+"','"endianness": "little"',
        '"window":','"backends":','"metrics":','"snapshots":',
        '"backend_name":','"timestamp_utc":',
        '"t1":','"t2":','"sx_error":','"readout_error":','"multi_qubit_error":',
        '"correlations":','"summary":','"strongest_degrader":','"recommendation":',
        "Determinism","NVQA_LIVE","non-deterministic"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit25.md missing tokens: {miss}"
