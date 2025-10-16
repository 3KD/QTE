"""
Simple FFT/invariant utilities used by QTEGUI.

compute_fft_spectrum_from_amplitudes(amplitudes, *, sample_rate=1.0)
returns a dict with:
  - 'freq': np.ndarray of frequencies (Hz, two-sided)
  - 'X': complex FFT spectrum (two-sided)
  - 'P': power spectrum |X|^2 normalized to sum=1
  - 'dc': float, DC share (P[0]/sum(P))
  - 'flatness': spectral flatness (geom/arith mean)
  - 'entropy': spectral entropy (nats) and 'entropy_bits' (bits)

No SciPy required; purely NumPy.
"""
from __future__ import annotations
import numpy as np

def _normalize_power(p: np.ndarray) -> np.ndarray:
    s = float(np.sum(p).real)
    return p / (s if s != 0.0 else 1.0)

def _spectral_flatness(P: np.ndarray) -> float:
    P = np.asarray(P, dtype=float) + 1e-15
    gm = float(np.exp(np.mean(np.log(P))))
    am = float(np.mean(P))
    return gm / am

def _spectral_entropy(P: np.ndarray) -> tuple[float, float]:
    Pn = _normalize_power(P)
    with np.errstate(divide='ignore', invalid='ignore'):
        H = -float(np.sum(Pn * np.log(Pn + 1e-15)))
        Hb = -float(np.sum(Pn * np.log2(Pn + 1e-15)))
    return H, Hb

def compute_fft_spectrum_from_amplitudes(amplitudes, *, sample_rate: float = 1.0):
    x = np.asarray(amplitudes, dtype=complex).reshape(-1)
    n = x.size
    if n == 0:
        raise ValueError("amplitudes must be non-empty")
    # center + Hann to be consistent with other metrics in repo
    x = x - np.mean(x)
    if n > 1:
        x = x * np.hanning(n)
    X = np.fft.fft(x)
    P = np.abs(X)**2
    Pn = _normalize_power(P)
    freq = np.fft.fftfreq(n, d=1.0/float(sample_rate))

    dc = float(Pn[0])
    flat = _spectral_flatness(P)
    H, Hb = _spectral_entropy(P)

    return {
        "freq": freq,
        "X": X,
        "P": Pn,
        "dc": dc,
        "flatness": flat,
        "entropy": H,
        "entropy_bits": Hb,
    }
