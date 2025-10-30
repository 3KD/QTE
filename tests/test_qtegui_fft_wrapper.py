import importlib, pytest, numpy as np

@pytest.mark.skipif(importlib.util.find_spec("harmonic_analysis") is None, reason="harmonic_analysis not available")
def test_fft_wrapper_runs_and_shapes_ok():
    m = importlib.import_module("QTEGUI")
    vec = np.array([1+0j, 0, 0, 0], dtype=complex)
    out = m._fft_from_gui(vec, remove_dc=True, window="hann", pad_len=8)
    assert isinstance(out, dict)
    assert "freq" in out and "P" in out and "dc" in out
