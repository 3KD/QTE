import numpy as np

def ok(msg): print("[OK]", msg)

# FFT spectrum
from harmonic_analysis import compute_fft_spectrum_from_amplitudes
x = np.cos(2*np.pi*5*np.arange(256)/256)
P, freqs, meta = compute_fft_spectrum_from_amplitudes(x, remove_dc=True, window="hann", pad_len=256)
np.testing.assert_allclose(float(P.sum()), 1.0, rtol=1e-12, atol=1e-12)
assert meta.get("dc_frac", meta.get("dc", 0.0)) < 1e-3
ok("FFT spectrum metrics")

# Bell-pair entropy
from metrics_extra import schmidt_entropy
psi = np.array([1/np.sqrt(2),0,0,1/np.sqrt(2)], dtype=complex)
S = schmidt_entropy(psi, n_qubits=2, cut=1)
assert abs(S - 1.0) < 1e-9
ok("Schmidt entropy = 1 bit")

# Trig series constant term
from series_encoding import _qte_maclaurin_coeffs
c = _qte_maclaurin_coeffs("sin(x)^2", n_terms=6, radius=4.0, m=0)
assert abs(float(np.real(c[0])) - 0.5) < 1e-9
ok("Fourier a0/2 = 0.5 for sin^2")

# Lorentz invariance
from physics.lorentz import preserves_minkowski
assert preserves_minkowski(beta=0.3) is True
ok("Minkowski metric preserved (beta=0.3)")

print("\n[ALL SMOKES PASSED]")
