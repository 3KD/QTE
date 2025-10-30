import pathlib

def test_unit29_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-drift","--inputs","--out-trend",'drift_version="Unit29"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit29 bits: {miss}"

def test_unit29_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit29.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-drift","--inputs","--out-trend",'drift_version="Unit29"',
        '"drift_version": "Unit29"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"endianness": "little"','"qft_kernel_sign": "+"',
        '"manifest_path":','"N":','"backend_names":','"shots_series":','"timestamps_utc":',
        '"hellinger_mean":','"hellinger_max":','"bhattacharyya_mean":','"ks_pvalue_min":',
        '"kl_bits_mean":','"kl_bits_max":','"changepoint_index":','"changepoint_note":',
        '"drift_alert":','"threshold_note":','NVQA_LIVE','Deterministic'
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit29.md missing tokens: {miss}"
