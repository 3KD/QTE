import numpy as np
from harmonic_analysis import compute_fft_spectrum_from_amplitudes

def test_fft_shapes_and_norm():
    # a cosine should produce symmetric two-sided spectral power
    n = 256
    t = np.arange(n)
    x = np.cos(2*np.pi*5*t/n)  # 5 cycles across n samples
    out = compute_fft_spectrum_from_amplitudes(x, sample_rate=1.0)
    P = out["P"]
    assert P.shape == (n,)
    # normalized power
    np.testing.assert_allclose(float(P.sum()), 1.0, rtol=1e-12, atol=1e-12)
    # DC of a mean-removed windowed cosine should be ~0
    assert out["dc"] < 1e-3
