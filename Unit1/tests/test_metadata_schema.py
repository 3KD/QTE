import json
import pytest
import os

def test_metadata_has_required_fields():
    sample_path = "Unit1/metadata/sample_meta.json"
    if not os.path.exists(sample_path):
        pytest.skip("sample_meta.json not found yet; generate after first run of qte_cli")

    with open(sample_path) as f:
        obj = json.load(f)

    required_top = ["label", "n_qubits", "N_trunc", "amp_mode"]
    for r in required_top:
        assert r in obj, f"missing required key {r}"

    assert "norm_info" in obj, "missing norm_info"
    assert "endianness" in obj or "conventions" in obj, "missing endianness/conventions"
    assert "qft_kernel_sign" in obj or "conventions" in obj, "missing qft_kernel_sign"
    assert "fft_normalization" in obj or "conventions" in obj, "missing fft_normalization"
