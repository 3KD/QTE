import pathlib

def test_unit09_doc_contract_strings_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit09.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-verify-cert",
        "--cert",
        "--counts",
        "--out-verdict",
        'verify_version="Unit09"',
        '"verify_version": "Unit09"',
        '"cert_path":',
        '"counts_path":',
        '"nve_version": "Unit01"',
        '"loader_version": "Unit02"',
        '"prep_version": "Unit03"',
        '"exec_version": "Unit04"',
        '"quentroy_version": "Unit06"',
        '"endianness": "little"',
        '"qft_kernel_sign": "+"',
        '"recomputed":',
        '"claimed":',
        '"H_Z_bits":',
        '"H_X_bits":',
        '"KL_to_uniform_bits":',
        '"min_entropy_bits":',
        '"MU_lower_bound_bits":',
        '"tolerance_bits": 1e-12',
        '"passed":',
        '"discrepancies":',
    ]
    miss = [b for b in req if b not in doc]
    assert not miss, f"Unit09.md missing required tokens: {miss}"
