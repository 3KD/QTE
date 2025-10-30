import pathlib

def test_unit06_cli_contract_strings_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = [
        "nve-quentroy-cert","--counts","--basis","--out-cert",
        'quentroy_version="Unit06"','endianness="little"','qft_kernel_sign="+"',
        'loader_version="Unit02"','exec_version="Unit04"',
    ]
    miss = [b for b in req if b not in src]
    assert not miss, f"nvqa_cli.py missing Unit06 bits: {miss}"


def test_unit06_doc_contract_strings_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit06.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)","nve-quentroy-cert","--counts","--basis","--out-cert",
        'quentroy_version="Unit06"','"endianness": "little"','"qft_kernel_sign": "+"',
        '"loader_version": "Unit02"','"exec_version": "Unit04"',
        '"H_Z_bits"','"H_X_bits"','"KL_to_uniform_bits"','"min_entropy_bits"','"MU_lower_bound_bits"',
        '"counts_source"','"psi_source"','"rail_layout"','"qubit_order"',
    ]
    miss = [b for b in req if b not in doc]
    assert not miss, f"Unit06.md missing tokens: {miss}"
