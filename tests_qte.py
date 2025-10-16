
import os, math, cmath, numpy as np
import importlib
se = importlib.import_module("series_encoding")

def test_j0_egf_finite():
    v = se.get_series_amplitudes("J0", 32, amp_mode="egf", normalize=True)
    assert len(v)==32 and np.isfinite(np.linalg.norm(v))

def test_qft_rail_norm():
    v = se.get_series_amplitudes("QFT[sin(2*pi*x); N=64; a=0; b=1; ifft][rail]",
                                 64, amp_mode="terms", normalize=True)
    assert len(v)==64 and np.isclose(np.linalg.norm(v), 1.0)

def test_polylog_core():
    v1 = se.compute_series_value("Li(2,-0.9)", terms=4000)
    v2 = se.compute_series_value("polylog(3, 0.5)", terms=4000)
    v3 = se.compute_series_value("polylog(2, 0.9+0.2j)", terms=4000)
    for v in (v1, v2, v3):
        assert np.isfinite(abs(complex(v)))

def test_bessel_values():
    for n in (0,1,2,5):
        val = se.compute_series_value(f"J{n}(1.0)", terms=8000)
        assert np.isfinite(abs(complex(val)))

def test_maclaurin_syntax():
    v = se.get_series_amplitudes("Maclaurin[log(1+x); auto_r; real_coeffs]", 16,
                                 amp_mode="terms", normalize=True)
    assert len(v)==16 and np.all(np.isfinite(v))
