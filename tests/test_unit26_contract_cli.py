import pathlib

def test_unit26_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    src = (root / "nvqa_cli.py").read_text()
    req = ["nve-queue-forecast","--backend","--horizon","--shots","--out-plan",'queue_version="Unit26"']
    miss = [r for r in req if r not in src]
    assert not miss, f"nvqa_cli.py missing Unit26 bits: {miss}"

def test_unit26_doc_contract_tokens_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit26.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-queue-forecast","--backend","--horizon","--shots","--out-plan",'queue_version="Unit26"',
        '"queue_version": "Unit26"',
        '"nve_version": "Unit01"','"loader_version": "Unit02"','"prep_version": "Unit03"','"exec_version": "Unit04"',
        '"endianness": "little"','"qft_kernel_sign": "+"',
        '"backend_name":','"horizon":','"demand_shots":','"est_wait_minutes":',
        '"slots":','"policy":','"assumptions":',
        "NVQA_LIVE","non-deterministic"
    ]
    miss = [r for r in req if r not in doc]
    assert not miss, f"Unit26.md missing tokens: {miss}"
