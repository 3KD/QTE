import pathlib

def test_unit30_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-consistency","--inputs","--out-report",'consistency_version="Unit30"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit30 bits: {miss}"

def test_unit30_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit30.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-consistency","--inputs","--out-report",'consistency_version="Unit30"',
        '"consistency_version": "Unit30"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"endianness": "little"','"qft_kernel_sign": "+"',
        '"manifest_path":','"N_pairs":','"backend_pairs":','"metric":',
        '"pairwise_stats":','"hellinger_mean":','"hellinger_max":','"bhattacharyya_mean":',
        '"kl_bits_mean":','"ks_pvalue_min":','"inconsistency_alert":','"threshold_note":',
        'NVQA_LIVE','Determinism'
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit30.md missing tokens: {miss}"
