# series_preserving.py
# Utilities to build sign/phase-preserving series vectors, run algebra on them,
# and probe phase structure via simple Hadamard-test observables.
#
# No backend use; all-numpy. Meant to be imported by GUI or scripts.

from __future__ import annotations
from typing import Optional, Tuple, Iterable, List, Dict
import numpy as np

try:
    # QTE modules
    from series_encoding import get_series_amplitudes
    from qiskit.quantum_info import Statevector
except Exception as e:  # type: ignore
    get_series_amplitudes = None
    Statevector = None  # type: ignore


# ---------------------------
# Core series → vector
# ---------------------------

def series_vector(
    label: str,
    N: int,
    *,
    method: Optional[str] = None,
    amp_mode: str = "terms",       # "terms" or "egf"
    phase_mode: str = "sign",      # "sign" or "abs" (or extended phases if your series supports it)
    normalize: bool = False,
) -> np.ndarray:
    """
    Return a complex vector v[0:N] representing the first N coefficients (or EGF-scaled coefficients),
    with sign/phase encoded as chosen by `phase_mode`. If normalize=True, rescale to ||v||=1.
    """
    if get_series_amplitudes is None:
        raise RuntimeError("series_encoding.get_series_amplitudes is not available in this environment.")
    arr = np.asarray(
        get_series_amplitudes(
            label, N,
            method=method,
            phase_mode=phase_mode,
            normalize=False,             # <-- important: algebra in raw space first, normalize at the end
            amp_mode=("egf" if amp_mode.lower().startswith("egf") else "terms"),
        ),
        dtype=np.complex128,
    )
    if normalize:
        nrm = np.linalg.norm(arr)
        if nrm == 0:
            return arr
        arr = arr / nrm
    return arr


def to_statevector(vec: np.ndarray):
    """Wrap a normalized vector as a qiskit Statevector if available; else return the numpy array."""
    nrm = float(np.linalg.norm(vec))
    if nrm == 0:
        raise ValueError("Zero vector cannot be promoted to a state.")
    if abs(nrm - 1.0) > 1e-12:
        vec = vec / nrm
    if Statevector is None:
        return vec
    return Statevector(vec)


# ---------------------------
# Algebra on series arrays
# ---------------------------

def hadamard_product(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Termwise product: c_n = a_n * b_n."""
    if len(a) != len(b):
        raise ValueError("Hadamard product requires same length arrays.")
    return np.asarray(a) * np.asarray(b)

def cauchy_product(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """OGF Cauchy product: c_n = sum_{k=0}^n a_k b_{n-k}."""
    a = np.asarray(a); b = np.asarray(b)
    N = min(len(a), len(b))
    c = np.zeros(N, dtype=np.complex128)
    for n in range(N):
        kmax = n
        c[n] = np.dot(a[:kmax+1], b[n-kmax:n+1][::-1])
    return c

def egf_product(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """EGF product: c_n = sum_{k=0}^n C(n,k) a_k b_{n-k}."""
    from math import comb
    a = np.asarray(a); b = np.asarray(b)
    N = min(len(a), len(b))
    c = np.zeros(N, dtype=np.complex128)
    for n in range(N):
        s = 0.0+0.0j
        for k in range(n+1):
            s += comb(n, k) * a[k] * b[n-k]
        c[n] = s
    return c

def dirichlet_convolution(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """
    Dirichlet convolution on indices starting at 1:
      c(n) = sum_{d|n} a(d) b(n/d)
    We ignore index 0; c[0]=0 by convention.
    """
    a = np.asarray(a); b = np.asarray(b)
    N = min(len(a), len(b))
    c = np.zeros(N, dtype=np.complex128)
    for n in range(1, N):
        s = 0.0+0.0j
        d = 1
        while d*d <= n:
            if n % d == 0:
                s += a[d] * b[n//d]
                if d*d != n:
                    s += a[n//d] * b[d]
            d += 1
        c[n] = s
    return c

def lcu_combine(vectors: Iterable[np.ndarray], coeffs: Iterable[complex], *, normalize_out: bool = True) -> np.ndarray:
    """
    Linear Combination of Unitaries (here: just linear combination of vectors).
    Returns v = sum_i coeffs[i] * vectors[i]; optionally normalizes.
    """
    vecs = [np.asarray(v, dtype=np.complex128) for v in vectors]
    cs = np.asarray(list(coeffs), dtype=np.complex128)
    if len(vecs) != len(cs):
        raise ValueError("vectors and coeffs must have the same length.")
    N = len(vecs[0])
    if any(len(v) != N for v in vecs):
        raise ValueError("All vectors must have the same length.")
    out = np.zeros(N, dtype=np.complex128)
    for c, v in zip(cs, vecs):
        out += c * v
    if normalize_out:
        nrm = np.linalg.norm(out)
        if nrm != 0:
            out = out / nrm
    return out


# ---------------------------
# Phase / sign witnesses (Hadamard-test style, diagonal ±1 masks)
# ---------------------------

def make_diag_mask(mask: str, N: int) -> np.ndarray:
    """
    Build a ±1 diagonal mask in array form.
      - 'parity' : (-1)^{popcount(index)}
      - 'lsb'    : (-1)^{index & 1}
      - 'msb'    : (-1)^{(index >> (n-1)) & 1}
      - 0/1 bitstring like '1010' : repeat over indices
    """
    diag = np.ones(N, dtype=float)
    m = mask.strip().lower()
    n = max(1, int(np.log2(N)))
    if m == "parity":
        for i in range(N):
            if bin(i).count("1") % 2 == 1:
                diag[i] = -1.0
    elif m == "lsb":
        for i in range(N):
            if i & 1:
                diag[i] = -1.0
    elif m == "msb":
        bit = 1 << (n - 1)
        for i in range(N):
            if i & bit:
                diag[i] = -1.0
    elif set(m) <= {"0", "1"} and len(m) >= 1:
        pat = np.array([1.0 if ch == "1" else -1.0 for ch in m], dtype=float)
        L = len(pat)
        for i in range(N):
            diag[i] = pat[i % L]
    else:
        raise ValueError("Unknown mask. Use 'parity', 'lsb', 'msb', or a 0/1 pattern like 1010.")
    return diag

def hadamard_test_expectation(vec: np.ndarray, mask: str = "parity") -> float:
    """
    Analytic expectation value of a diagonal ±1 observable D for state |ψ⟩ with amplitudes vec:
      ⟨D⟩ = Σ_i (±1)_i * |ψ_i|^2
    """
    v = np.asarray(vec, dtype=np.complex128)
    N = len(v)
    diag = make_diag_mask(mask, N)
    p = np.abs(v)**2
    return float(np.dot(diag, p))


# ---------------------------
# High-level helpers
# ---------------------------

def build_series_state(
    A: Tuple[str, Optional[str]],
    B: Optional[Tuple[str, Optional[str]]] = None,
    *,
    N: int,
    amp_mode: str = "terms",
    phase_mode: str = "sign",
    op: str = "none",  # "none", "add", "sub", "hadamard", "cauchy", "egf", "dirichlet"
):
    """
    Compose a state from one or two series sources, with a chosen algebraic operation.
    Returns (label, Statevector-or-ndarray, norm_before_normalize).
    """
    a_lab, a_meth = A
    a = series_vector(a_lab, N, method=a_meth, amp_mode=amp_mode, phase_mode=phase_mode, normalize=False)

    if op == "none" or B is None:
        c = a
        op_txt = ""
    else:
        b_lab, b_meth = B
        b = series_vector(b_lab, N, method=b_meth, amp_mode=amp_mode, phase_mode=phase_mode, normalize=False)
        if op == "add":
            c = a + b
        elif op == "sub":
            c = a - b
        elif op == "hadamard":
            c = hadamard_product(a, b)
        elif op == "cauchy":
            c = cauchy_product(a, b)
        elif op == "egf":
            c = egf_product(a, b)
        elif op == "dirichlet":
            c = dirichlet_convolution(a, b)
        else:
            raise ValueError(f"Unknown op: {op}")
        op_txt = f" | {op}"

    nrm = float(np.linalg.norm(c))
    if nrm == 0.0:
        raise ValueError("Resulting vector is all zeros.")
    sv = to_statevector(c / nrm)
    label = f"ALG[{a_lab}{f'({a_meth})' if a_meth else ''}{f' ⊗{amp_mode} ' + B[0] + (f'({B[1]})' if B[1] else '') if B else ''} | N={N} | phase={phase_mode}{op_txt}]"
    return label, sv, nrm

