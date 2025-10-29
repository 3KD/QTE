import pathlib

def test_unit11_doc_contract_strings_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit11.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-entropy-witness",
        "--cert",
        "--counts-z",
        "--counts-x",
        "--out-witness",
        'witness_version="Unit11"',
        '"witness_version": "Unit11"',
        '"cert_path":',
        '"counts_z_path":',
        '"counts_x_path":',
        '"nve_version": "Unit01"',
        '"loader_version": "Unit02"',
        '"prep_version": "Unit03"',
        '"exec_version": "Unit04"',
        '"quentroy_version": "Unit06"',
        '"endianness": "little"',
        '"qft_kernel_sign": "+"',
        '"backend_name":',
        '"shots":',
        '"H_Z_bits_expected":',
        '"H_Z_bits_measured":',
        '"H_X_bits_expected":',
        '"H_X_bits_measured":',
        '"KL_Z_to_uniform_bits":',
        '"KL_X_to_uniform_bits":',
        '"uncertainty_bound_bits":',
        '"delta_H_bits":',
        '"passed":',
        '"rationale":',
    ]
    miss = [b for b in req if b not in doc]
    assert not miss, f"Unit11.md missing required tokens: {miss}"
