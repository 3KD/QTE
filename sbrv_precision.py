# QTE add-on: Stacked Binary Residual Vectors (SBRV).
from __future__ import annotations
import numpy as np
from typing import List, Tuple, Dict

def quantize_msb(a: np.ndarray, step: float = 1.0) -> np.ndarray:
    """
    Coarse quantizer capturing MSB-scale structure.
    If your 'a' is not roughly in units of 'step', pre-scale a first.
    """
    a = np.asarray(a, dtype=float)
    return np.round(a / step) * step

def build_sbrv(a: np.ndarray, L: int, step: float = 1.0
               ) -> Tuple[np.ndarray, List[np.ndarray], Dict]:
    """
    Build SBRV:
      a = a0 + Σ_{ell=1..L} 2^{-ell} r^(ell), with r^(ell) ∈ {-1,0,1}^d.
    Returns (a0, stack, meta). If 'a' is complex, run on real/imag separately.
    """
    a = np.asarray(a, dtype=float)
    a0 = quantize_msb(a, step=step)
    res = a - a0
    stack: List[np.ndarray] = []
    meta = {"levels": []}
    for ell in range(1, L + 1):
        r = np.clip(np.round(res * (2**ell)), -1, 1).astype(int)
        stack.append(r)
        res = res - (r / (2**ell))
        meta["levels"].append({
            "level": ell,
            "scale": float(2**(-ell)),
            "l2":    float(np.linalg.norm(r))
        })
    return a0, stack, meta

def reconstruct_sbrv(a0: np.ndarray, stack: List[np.ndarray], L: int) -> np.ndarray:
    """
    Reconstruct (to level L) and L2-normalize.
    """
    aL = np.asarray(a0, dtype=float).copy()
    for ell, r in enumerate(stack[:L], 1):
        aL = aL + (r / (2**ell))
    n = float(np.linalg.norm(aL))
    return aL / n if n > 0 else aL


