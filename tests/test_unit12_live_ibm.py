import os, json, subprocess, tempfile, pathlib, sys
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]

@pytest.mark.skipif(os.getenv("NVQA_LIVE") != "1", reason="NVQA_LIVE!=1; skipping live IBM smoke")
def test_live_smoke_ibm_exec(tmp_path):
    cli = ROOT / "nvqa_cli.py"
    assert cli.exists(), "nvqa_cli.py missing"

    out_spec = tmp_path / "prep_spec.json"
    out_receipt = tmp_path / "run_receipt.json"

    cmd = [
        sys.executable, str(cli),
        "nve-run-exec",                       # rely on Unit 04 live path via backend flag
        "--object", "Maclaurin[sin(x)]",
        "--weighting", "egf",
        "--phase-mode", "full_complex",
        "--rail-mode", "iq_split",
        "--N", "8",
        "--shots", "64",
        "--backend", os.getenv("NVQA_BACKEND", "ibm_torino"),
        "--out-spec", str(out_spec),
        "--out-receipt", str(out_receipt),
    ]
    # Prefer short timeout to avoid hanging CI
    env = dict(os.environ)
    env.setdefault("PYTHONUNBUFFERED","1")
    proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=900)
    assert proc.returncode == 0, f"nve-run-exec failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"

    data = json.loads(out_receipt.read_text())
    # Schema sanity (names must exist; values may vary)
    for k in ["receipt_version","backend_name","shots","rail_layout","exec_version","endianness","qft_kernel_sign"]:
        assert k in data, f"receipt missing key: {k}"
    assert data["receipt_version"] == "Unit04"
    assert data["endianness"] == "little"
    assert data["qft_kernel_sign"] == "+"
    assert int(data["shots"]) > 0
