from dataclasses import dataclass
from typing import Optional, List
import numpy as np
import json
from pathlib import Path

# ---------- Basis utilities ----------
def phi_vec(x: float, N: int) -> np.ndarray:
    """Monomial feature vector [1, x, x^2, ..., x^{N-1}]^T (float64)."""
    v = np.empty(N, dtype=np.float64)
    v[0] = 1.0
    for n in range(1, N):
        v[n] = v[n-1]*x
    return v

# ---------- Analytic K from power series of F ----------
def poly_truncate(p: np.ndarray, N: int) -> np.ndarray:
    """Keep coefficients up to degree N-1."""
    out = np.zeros(N, dtype=np.float64)
    out[:min(N, len(p))] = p[:min(N, len(p))]
    return out

def poly_conv(a: np.ndarray, b: np.ndarray, N: int) -> np.ndarray:
    """Cauchy convolution (polynomial multiply), truncated to degree < N."""
    out = np.zeros(N, dtype=np.float64)
    da, db = len(a), len(b)
    for i in range(min(da, N)):
        ai = a[i]
        if ai == 0.0:
            continue
        jmax = min(db, N - i)
        out[i:i+jmax] += ai * b[:jmax]
    return out

def poly_pow_trunc(p: np.ndarray, n: int, N: int) -> np.ndarray:
    """Compute (p(x))^n truncated to degree < N by repeated squaring."""
    if n == 0:
        e = np.zeros(N, dtype=np.float64); e[0] = 1.0
        return e
    base = poly_truncate(p, N)
    result = np.zeros(N, dtype=np.float64); result[0] = 1.0
    m = n
    while m > 0:
        if (m & 1) == 1:
            result = poly_conv(result, base, N)
        base = poly_conv(base, base, N)
        m >>= 1
    return result

def koopman_from_series(F_coeffs: np.ndarray, N: int) -> np.ndarray:
    """
    Build K with columns K[:, n] = coeffs of (F(x))^n up to degree N-1.
    F_coeffs[k] = coefficient of x^k in F(x). Length may be < N.
    """
    F = poly_truncate(F_coeffs, N)
    K = np.zeros((N, N), dtype=np.float64)
    for n in range(N):
        K[:, n] = poly_pow_trunc(F, n, N)
    return K

# ---------- Data-driven K from (x_t, x_{t+1}) pairs ----------
def learn_koopman_from_pairs(pairs, N: int, ridge: float = 1e-8):
    """
    pairs: iterable of (x_t, x_{t+1}) floats
    Returns K_hat (N x N), fit residual ||G' - K_hat G||_F, and cond(A) of normal matrix.
    """
    xs = np.array([p[0] for p in pairs], dtype=np.float64)
    ys = np.array([p[1] for p in pairs], dtype=np.float64)
    G  = np.stack([phi_vec(float(x), N) for x in xs], axis=1)   # N x T
    Gp = np.stack([phi_vec(float(y), N) for y in ys], axis=1)   # N x T
    GGt = G @ G.T
    A = GGt + ridge * np.eye(N, dtype=np.float64)
    K_hat = (Gp @ G.T) @ np.linalg.solve(A, np.eye(N, dtype=np.float64))
    resid = float(np.linalg.norm(Gp - K_hat @ G, ord='fro'))
    condA = float(np.linalg.cond(A))
    return K_hat, resid, condA

# ---------- Diagnostics & reporting ----------
@dataclass
class KoopmanReport:
    N: int
    method: str
    spectrum: List[dict]           # list of {"re":..., "im":...}
    spectral_radius: float
    residual_frob: float
    cond: Optional[float] = None
    comment: Optional[str] = None

def spectrum_info(K: np.ndarray):
    w = np.linalg.eigvals(K)
    rad = float(np.max(np.abs(w))) if len(w) else 0.0
    return w, rad

def _serialize_eigs(eigs) -> List[dict]:
    out = []
    for z in eigs:
        z = complex(z)
        out.append({"re": float(z.real), "im": float(z.imag)})
    return out

def save_report(path: Path, K: np.ndarray, method: str, resid=None, cond=None, comment=None):
    w, rad = spectrum_info(K)
    rep = KoopmanReport(
        N=int(K.shape[0]),
        method=str(method),
        spectrum=_serialize_eigs(w),
        spectral_radius=float(rad),
        residual_frob=float(resid) if resid is not None else 0.0,
        cond=float(cond) if cond is not None else None,
        comment=str(comment) if comment is not None else None
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(rep.__dict__, f, indent=2)
    return rep

def pretty_block(K: np.ndarray, m: int = 6) -> str:
    m = min(m, K.shape[0])
    lines = []
    for i in range(m):
        lines.append(" ".join(f"{K[i,j]:9.5f}" for j in range(m)))
    return "\n".join(lines)
