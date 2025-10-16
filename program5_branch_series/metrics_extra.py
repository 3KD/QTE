# QTE add-on: extra metrics (descriptive diagnostics).
from __future__ import annotations
import numpy as np

def spectral_entropy_fft(x: np.ndarray) -> float:
    X = np.fft.fft(np.asarray(x))
    p = np.abs(X) ** 2
    s = float(p.sum()) or 1.0
    p = p / s
    with np.errstate(divide='ignore', invalid='ignore'):
        return float(-(p * np.log(p + 1e-15)).sum())

def spectral_flatness_fft(x: np.ndarray) -> float:
    X = np.fft.fft(np.asarray(x))
    p = np.abs(X) ** 2 + 1e-15
    gm = float(np.exp(np.mean(np.log(p))))
    am = float(np.mean(p))
    return gm / am

def phase_coherence(c: np.ndarray) -> float:
    c = np.asarray(c, dtype=complex)
    mags = np.abs(c)
    nz = mags > 0
    phases = np.zeros_like(c, dtype=complex)
    phases[nz] = c[nz] / mags[nz]
    return float(np.abs(phases.mean()))

def schmidt_entropy(psi: np.ndarray, n_qubits: int, cut: int) -> float:
    """
    Von Neumann entropy across bipartition (pure state).
    'psi' is a 2^n complex vector; 'cut' is #qubits in subsystem A.
    """
    psi = np.asarray(psi, dtype=complex)
    A = psi.reshape((2**cut, 2**(n_qubits - cut)))
    s = np.linalg.svd(A, compute_uv=False)
    lam2 = (s ** 2)
    lam2 = lam2 / (float(lam2.sum()) or 1.0)
    with np.errstate(divide='ignore', invalid='ignore'):
        return float(-(lam2 * np.log(lam2 + 1e-15)).sum())

def qfi_pure_state(psi: np.ndarray, H: np.ndarray) -> float:
    """
    F_Q = 4(⟨H^2⟩ - ⟨H⟩^2) for a pure state.
    H should be a Hermitian operator in the same Hilbert space.
    """
    psi = np.asarray(psi, dtype=complex)
    H = np.asarray(H, dtype=complex)
    bra = psi.conj()
    expH  = float(bra @ (H @ psi))
    expH2 = float(bra @ (H @ (H @ psi)))
    return 4.0 * (expH2 - expH**2)

# Optional Hankel-domain entropy (needs SciPy). Safe to ignore if not installed.
def spectral_entropy_hankel(x: np.ndarray, nu: int = 0) -> float:
    try:
        from scipy.special import jv, jn_zeros
    except Exception as e:
        raise ImportError("SciPy required for Hankel-domain entropy") from e
    x = np.asarray(x, dtype=float)
    d = len(x)
    zeros = jn_zeros(nu, d)
    r = np.linspace(0.0, 1.0, d, endpoint=True)
    H = np.zeros((d, d), dtype=float)
    for k in range(d):
        J = jv(nu, zeros[k] * r)
        H[:, k] = r * J
    H = H / (np.linalg.norm(H, axis=0, keepdims=True) + 1e-15)
    X = H.T @ x
    p = np.abs(X) ** 2
    p = p / (float(p.sum()) or 1.0)
    with np.errstate(divide='ignore', invalid='ignore'):
        return float(-(p * np.log(p + 1e-15)).sum())

