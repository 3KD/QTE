import pathlib

def test_unit17_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-xbackend","--inputs","--out-equivalence","--metric",'xbackend_version="Unit17"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit17 bits: {miss}"

def test_unit17_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit17.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-xbackend","--inputs","--out-equivalence","--metric",'xbackend_version="Unit17"',
        '"xbackend_version": "Unit17"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"atlas_version": "Unit07"','"metric":','"abs_tolerance_bits":',
        '"pairs_compared"','"backend_a"','"backend_b"','"mean_diff_bits"','"max_abs_diff_bits"','"within_tolerance"',
        '"summary"','"total_pairs"','"pass_pairs"','"fail_pairs"','"failures"','"reason"',
        "Determinism","offline","backend_name"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit17.md missing tokens: {miss}"
