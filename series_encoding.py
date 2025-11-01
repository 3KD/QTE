import numpy as np
from typing import Tuple, Optional

def _parse_label(label: str) -> Tuple[str, str]:
    s = label.strip()
    mode = None
    low = s.lower()
    if low.endswith(" egf"):
        mode = "egf"; s = s[:-4].rstrip()
    elif low.endswith(" terms"):
        mode = "terms"; s = s[:-6].rstrip()
    return s, (mode or "terms")

def _series_terms_sin(dim: int) -> np.ndarray:
    # sin: n = 1,3,5,...  c_{n+2} = - c_n / ((n+1)(n+2)), c_1 = 1
    a = np.zeros(dim, dtype=np.complex128)
    if dim <= 1: return a
    n, c = 1, 1.0
    while n < dim:
        a[n] = c
        # next odd: n+2
        c = -c / ((n + 1) * (n + 2))
        n += 2
    return a

def _series_terms_cos(dim: int) -> np.ndarray:
    # cos: n = 0,2,4,...  c_{n+2} = - c_n / ((n+1)(n+2)), c_0 = 1
    a = np.zeros(dim, dtype=np.complex128)
    if dim <= 0: return a
    n, c = 0, 1.0
    while n < dim:
        a[n] = c
        c = -c / ((n + 1) * (n + 2))
        n += 2
    return a

def _series_egf_sin(dim: int) -> np.ndarray:
    # EGF multiplies terms by n!: for sin this yields (-1)^k at odd n = 2k+1
    a = np.zeros(dim, dtype=np.complex128)
    for n in range(1, dim, 2):
        k = (n - 1) // 2
        a[n] = -1.0 if (k & 1) else 1.0
    return a

def _series_egf_cos(dim: int) -> np.ndarray:
    # EGF for cos: (-1)^k at even n = 2k
    a = np.zeros(dim, dtype=np.complex128)
    for n in range(0, dim, 2):
        k = n // 2
        a[n] = -1.0 if (k & 1) else 1.0
    return a

def _build_raw(base: str, dim: int, mode: str) -> np.ndarray:
    nm = base.strip().lower()
    if nm in {"maclaurin[sin(x)]", "maclaurin[sin]"}:
        return _series_terms_sin(dim) if mode == "terms" else _series_egf_sin(dim)
    if nm in {"maclaurin[cos(x)]", "maclaurin[cos]"}:
        return _series_terms_cos(dim) if mode == "terms" else _series_egf_cos(dim)
    raise ValueError(f"unknown series label: {base}")

def _l2_normalize(x: np.ndarray) -> np.ndarray:
    nrm = float(np.vdot(x, x).real)
    if nrm == 0.0:
        return x.astype(np.complex128)
    return (x / (nrm ** 0.5)).astype(np.complex128)

def get_series_amplitudes(label: str, dim: int, amp_mode: Optional[str] = None, normalize: bool = True) -> np.ndarray:
    base, label_mode = _parse_label(label)
    mode = (amp_mode or label_mode).lower()
    if mode not in {"terms", "egf"}:
        raise ValueError(f"amp_mode must be terms|egf, got {mode}")
    if dim <= 0:
        raise ValueError("dim must be positive")
    v = _build_raw(base, dim, mode)
    return _l2_normalize(v) if normalize else v

def build_state(label: str, nq: int, mode: Optional[str] = None):
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
