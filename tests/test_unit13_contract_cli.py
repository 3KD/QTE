import pathlib, os

def test_unit13_cli_literals_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    cli_src = (root / "nvqa_cli.py").read_text()
    required = [
        "nve-replay",
        "--receipt",
        "--out-counts",
        "--backend",
        'replay_version="Unit13"',
        'endianness="little"',
        'qft_kernel_sign="+"',
        'loader_version="Unit02"',
        'exec_version="Unit04"',
    ]
    missing = [r for r in required if r not in cli_src]
    assert not missing, f"nvqa_cli.py missing Unit13 literals: {missing}"

def test_unit13_doc_contract_strings_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit13.md").read_text()
    required = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-replay",
        "--receipt",
        "--out-counts",
        "--backend",
        'replay_version="Unit13"',
        '"nve_version": "Unit01"',
        '"loader_version": "Unit02"',
        '"prep_version": "Unit03"',
        '"exec_version": "Unit04"',
        '"endianness": "little"',
        '"qft_kernel_sign": "+"',
        '"rail_layout":',
        '"qubit_order":',
        '"backend_name":',
        '"shots":',
        '"timestamp_utc":',
        '"counts":',
        '"replay_note":',
        '"source_receipt_path":',
    ]
    missing = [r for r in required if r not in doc]
    assert not missing, f"Unit13.md missing contract tokens: {missing}"

def test_unit13_live_smoke_is_skip_by_default():
    assert os.getenv("NVQA_LIVE") in (None, "0"), "Live tests should be opt-in via NVQA_LIVE=1"
