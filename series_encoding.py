import math
import numpy as np
from typing import Tuple, Optional

def _parse_label(label: str) -> Tuple[str, str]:
    s = label.strip()
    mode = None
    low = s.lower()
    if low.endswith(" egf"):
        mode = "egf"
        s = s[:-4].rstrip()
    elif low.endswith(" terms"):
        mode = "terms"
        s = s[:-6].rstrip()
    return s, (mode or "terms")

def _maclaurin_coeff(name: str, n: int) -> float:
    nm = name.strip().lower()
    if nm in {"maclaurin[sin(x)]", "maclaurin[sin]"}:
        if n % 2 == 0:
            return 0.0
        k = (n - 1) // 2
        return ((-1.0) ** k) / math.factorial(n)
    if nm in {"maclaurin[cos(x)]", "maclaurin[cos]"}:
        if n % 2 == 1:
            return 0.0
        k = n // 2
        return ((-1.0) ** k) / math.factorial(n)
    raise ValueError(f"unknown series label: {name}")

def _series_terms(name: str, dim: int) -> np.ndarray:
    a = np.zeros(dim, dtype=np.complex128)
    for n in range(dim):
        a[n] = _maclaurin_coeff(name, n)
    return a

def _series_egf(name: str, dim: int) -> np.ndarray:
    a = np.zeros(dim, dtype=np.complex128)
    for n in range(dim):
        c = _maclaurin_coeff(name, n)
        if c != 0.0:
            a[n] = c * math.factorial(n)
    return a

def _l2_normalize(x: np.ndarray) -> np.ndarray:
    nrm = float(np.linalg.norm(x))
    if nrm == 0.0:
        return x
    return (x / nrm).astype(np.complex128)

def get_series_amplitudes(label: str, dim: int, amp_mode: Optional[str] = None, normalize: bool = True) -> np.ndarray:
    base, label_mode = _parse_label(label)
    mode = (amp_mode or label_mode).lower()
    if mode not in {"terms", "egf"}:
        raise ValueError(f"amp_mode must be terms|egf, got {mode}")
    if dim <= 0:
        raise ValueError("dim must be positive")
    if (dim & (dim - 1)) != 0:
        pass
    if mode == "terms":
        v = _series_terms(base, dim)
    else:
        v = _series_egf(base, dim)
    return _l2_normalize(v) if normalize else v

def build_state(label: str, nq: int, mode: Optional[str] = None) -> Tuple[np.ndarray, dict]:
    dim = 1 << int(nq)
    vec = get_series_amplitudes(label, dim, amp_mode=mode, normalize=True)
    meta = {
        "label": label,
        "mode": (mode or _parse_label(label)[1]),
        "nq": int(nq),
        "dim": dim,
        "endianness": "little",
        "norm_l2": float(np.vdot(vec, vec).real),
    }
    return vec, meta
