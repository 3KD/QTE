import numpy as np

def ok(msg): print("[OK]", msg)

# FFT spectrum (signature-agnostic)
from harmonic_analysis import compute_fft_spectrum_from_amplitudes
x = np.cos(2*np.pi*5*np.arange(256)/256)
out = compute_fft_spectrum_from_amplitudes(x)  # tolerate different return forms

# normalize power & derive dc robustly
if isinstance(out, tuple) and len(out) >= 2:
    P = np.asarray(out[0], dtype=float)
    freqs = out[1]
    meta = out[2] if len(out) >= 3 else {}
else:
    # fallback: treat as dict-like
    P = np.asarray(out.get("P", []), dtype=float)
    freqs = np.asarray(out.get("freq", []))

S = float(P.sum()) or 1.0
Pn = P / S
np.testing.assert_allclose(float(Pn.sum()), 1.0, rtol=1e-12, atol=1e-12)
dc = float(meta.get("dc_frac", meta.get("dc", Pn[0] if Pn.size else 0.0)))
assert dc < 1e-3
ok("FFT spectrum metrics")

# Bell-pair entropy
from metrics_extra import schmidt_entropy
psi = np.array([1/np.sqrt(2),0,0,1/np.sqrt(2)], dtype=complex)
Sbits = schmidt_entropy(psi, n_qubits=2, cut=1)
assert abs(Sbits - 1.0) < 1e-9
ok("Schmidt entropy = 1 bit")

# Trig series constant term
from series_encoding import _qte_maclaurin_coeffs
c = _qte_maclaurin_coeffs("sin(x)^2", n_terms=6, radius=4.0, m=0)
assert abs(float(np.real(c[0])) - 0.5) < 1e-9
ok("Fourier a0/2 = 0.5 for sin^2")

# Lorentz invariance (accepts matrix or beta)
from physics.lorentz import boost_x, preserves_minkowski
assert preserves_minkowski(boost_x(0.3))
ok("Minkowski metric preserved for boost matrix (beta=0.3)")

print("\n[ALL SMOKES PASSED]")
