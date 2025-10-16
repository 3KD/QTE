# QTE add-on: Sign-Split Registers (SRD) + I/Q packing
from __future__ import annotations
import numpy as np

def sign_split(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Elementwise decompose a real sequence a into nonnegative rails p, n such that a = p - n."""
    a = np.asarray(a, dtype=float)
    p = np.maximum(a, 0.0)
    n = np.maximum(-a, 0.0)
    return p, n

def _l2_norm(v: np.ndarray) -> float:
    return float(np.linalg.norm(v))

def _norm_or_zero(v: np.ndarray) -> np.ndarray:
    n = _l2_norm(v)
    return v / n if n > 0 else v

def encode_srd_ancilla(a: np.ndarray,
                       alpha: complex = 1/np.sqrt(2),
                       beta:  complex = 1/np.sqrt(2)
                       ) -> tuple[np.ndarray, np.ndarray, complex, complex]:
    """
    Phase-insensitive SRD (ancilla-tag) spec:
      |Ψ⟩ = α |0⟩ ⊗ |ψ+⟩  +  β |1⟩ ⊗ |ψ-⟩
    Returns (psi_plus, psi_minus, alpha, beta), rails normalized in L2.
    """
    p, n = sign_split(a)
    return _norm_or_zero(p), _norm_or_zero(n), complex(alpha), complex(beta)

def encode_srd_iq(a: np.ndarray) -> np.ndarray:
    """
    Phase-aware SRD (I/Q) packing: c = p + i n  with a = p - n.
    Returns a normalized complex amplitude vector (L2 = 1).
    """
    p, n = sign_split(a)
    c = p + 1j * n
    return _norm_or_zero(c)

def decode_srd_iq(real_part: np.ndarray, imag_part: np.ndarray) -> np.ndarray:
    """Given phase-aware estimates of Re(c), Im(c): reconstruct a = p - n."""
    return np.asarray(real_part, dtype=float) - np.asarray(imag_part, dtype=float)


