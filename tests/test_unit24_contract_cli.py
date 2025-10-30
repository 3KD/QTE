import pathlib

def test_unit24_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-backend-matrix","--backends","--program","--shots","--out-matrix",'matrix_version="Unit24"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit24 bits: {miss}"

def test_unit24_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit24.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-backend-matrix","--backends","--program","--shots","--out-matrix",'matrix_version="Unit24"',
        '"matrix_version": "Unit24"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"qft_kernel_sign": "+"','"endianness": "little"',
        '"program_name":','"shots":','"backends":','"rows":',
        '"backend_name":','"queue_time_s":','"run_time_s":','"total_time_s":',
        '"success_prob":','"fidelity_est":','"timestamp_utc":',
        '"summary":','"fastest_backend":','"highest_fidelity_backend":',
        "Determinism","NVQA_LIVE","simulator","non-deterministic"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit24.md missing tokens: {miss}"
