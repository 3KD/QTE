import numpy as np

def ok(msg): print("[OK]", msg)

def _coerce_spectrum(out):
    """Return (P, freqs, meta_dict) from various function signatures."""
    meta = {}
    # dict-like output
    if isinstance(out, dict):
        P = np.asarray(out.get("P", []), dtype=float)
        freqs = np.asarray(out.get("freq", np.arange(P.size)), dtype=float)
        for k in ("dc_frac","dc","entropy","entropy_bits","flatness"):
            if k in out: meta[k] = out[k]
        return P, freqs, meta
    # tuple-like output
    if isinstance(out, tuple):
        if len(out) == 3:
            P, freqs, md = out
            return np.asarray(P, float), np.asarray(freqs, float), (md if isinstance(md, dict) else {})
        if len(out) == 2:
            P, freqs = out
            return np.asarray(P, float), np.asarray(freqs, float), {}
        if len(out) == 1:
            P = out[0]
            P = np.asarray(P, float)
            return P, np.arange(P.size, dtype=float), {}
    # fallback: assume it's an array-ish power spectrum
    P = np.asarray(out, float) if np.ndim(out) else np.asarray([float(out)], float)
    return P, np.arange(P.size, dtype=float), {}

# FFT spectrum (signature-agnostic)
from harmonic_analysis import compute_fft_spectrum_from_amplitudes

x = np.cos(2*np.pi*5*np.arange(256)/256)
out = compute_fft_spectrum_from_amplitudes(x)
P, freqs, meta = _coerce_spectrum(out)

# normalize and DC check
S = float(P.sum()) or 1.0
Pn = P / S
np.testing.assert_allclose(float(Pn.sum()), 1.0, rtol=1e-12, atol=1e-12)
dc = float(meta["dc_frac"]) if "dc_frac" in meta else float(meta["dc"]) if "dc" in meta else (float(Pn[0]) if Pn.size else 0.0)
assert abs(dc) < 1e-3
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
