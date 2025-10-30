import pathlib

def test_unit21_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-xbackend","--inputs","--out-audit","--backends","--metric","--window",'xbackend_version="Unit21"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit21 bits: {miss}"

def test_unit21_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit21.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-xbackend","--inputs","--out-audit","--backends","--metric","--window",'xbackend_version="Unit21"',
        '"xbackend_version": "Unit21"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"metric":','"window":',
        '"backends":','"pairs":','"summary":',
        '"a":','"b":','"count_a":','"count_b":','"mean_a_bits":','"mean_b_bits":','"abs_delta_bits":','"max_abs_delta_bits":','"p_value":','"flag_inconsistent":',
        '"backend_count":','"pair_count":','"max_pair_delta_bits":','"any_inconsistent":',
        "Determinism","offline","backend"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit21.md missing tokens: {miss}"
