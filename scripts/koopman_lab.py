#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Koopman Lab v0 (self-contained)
- Learn truncated Koopman operator K (monomial dictionary) by ridge regression
- Simple prediction helper
- Optional hardware entropy probe (Z / QFT entropies) via Qiskit Sampler (robust decode)
Python 3.9+, Qiskit 2.2.x compatible.
"""
from __future__ import annotations
import json, math, cmath, os, sys
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple
from pathlib import Path

import numpy as np

# --------- Learning: truncated monomial dictionary in 1D ----------
def monomial_features(xs: np.ndarray, N: int) -> np.ndarray:
    """Return Φ (N x T) with rows [1, x, x^2, ... x^{N-1}] for samples xs (T,)"""
    xs = np.asarray(xs).reshape(1, -1)
    powers = np.arange(N).reshape(-1, 1)
    return np.power(xs, powers)  # (N, T)

def learn_koopman_ridge(xs: np.ndarray, N: int, ridge: float=1e-8) -> Tuple[np.ndarray, float]:
    """
    Learn K (N x N) s.t. Φ_{t+1} ≈ K Φ_t in least squares with Tikhonov λ=ridge.
    Returns (K, residual_frobenius)
    """
    x_t   = xs[:-1]
    x_tp1 = xs[1:]
    Phi_t   = monomial_features(x_t,   N)  # N x (T-1)
    Phi_tp1 = monomial_features(x_tp1, N)  # N x (T-1)

    # Ridge solution: K = Y X^T (X X^T + λI)^-1
    X = Phi_t
    Y = Phi_tp1
    XXt = X @ X.T
    lamI = ridge * np.eye(N)
    K = (Y @ X.T) @ np.linalg.pinv(XXt + lamI)

    resid = np.linalg.norm(Y - K @ X, ord='fro')
    return K, float(resid)

def spectral_info(K: np.ndarray) -> Tuple[np.ndarray, float, Optional[float]]:
    w = np.linalg.eigvals(K)
    rad = float(np.max(np.abs(w))) if w.size else 0.0
    cond = None
    try:
        s = np.linalg.svd(K, compute_uv=False)
        s = s[s>1e-15]
        if s.size:
            cond = float(np.max(s)/np.min(s))
    except Exception:
        cond = None
    return w, rad, cond

def predict_from_K(K: np.ndarray, x0: float, steps: int, clip: bool=True) -> np.ndarray:
    """
    Roll forward monomial vector under K. Use the first-order moment as x̂_t ≈ ⟨x⟩ ≈ φ_1.
    """
    N = K.shape[0]
    # monomial vector for scalar x: [1, x, x^2, ...]^T
    def phi_from_x(x: float) -> np.ndarray:
        return np.array([x**n for n in range(N)], dtype=float)
    phi = phi_from_x(x0)
    out = [x0]
    for _ in range(steps):
        phi = K @ phi
        xhat = phi[1] if len(phi) > 1 else 0.0
        if clip: xhat = max(min(xhat, 1.0), 0.0)
        out.append(float(xhat))
        # re-anchor phi around xhat to avoid divergence
        phi = phi_from_x(xhat)
    return np.array(out, dtype=float)

# --------- Optional hardware entropy probe (shallow) ----------
def shannon_H_from_counts(counts: Dict[str, int]) -> float:
    tot = sum(counts.values()) or 1
    H = 0.0
    for c in counts.values():
        p = c / tot
        if p>0: H -= p*math.log2(p)
    return H

def robust_decode_sampler_result(res, shots: int, width: int) -> Dict[str, int]:
    """Handle both quasi_dists and pub_results; return dict bitstring->count"""
    counts: Dict[str,int] = {}
    # SamplerV2-ish
    qd = getattr(res, "quasi_dists", None)
    if qd:
        for k,p in qd[0].items():
            b = format(k, f"0{width}b")
            counts[b] = counts.get(b,0) + int(round(float(p)*shots))
        return counts
    # Runtime pub_results path
    pub = getattr(res, "_pub_results", None)
    if pub and hasattr(pub, "__iter__"):
        try:
            d = pub[0].data
            # counts direct?
            c = getattr(d, "counts", None)
            if isinstance(c, dict) and c:
                return {str(k): int(v) for k,v in c.items()}
            # quasi_distribution?
            q = getattr(d, "quasi_dists", None) or getattr(d, "quasi_distribution", None)
            if q:
                q0 = q[0] if isinstance(q, list) else q
                for k,p in q0.items():
                    b = format(int(k), f"0{width}b")
                    counts[b] = counts.get(b,0)+int(round(float(p)*shots))
                return counts
        except Exception:
            pass
    # Last resort: empty
    return counts

def hardware_entropy_probe(n_qubits: int, backend_name: str, shots: int=256, approx_degree: int=0) -> Dict[str, float]:
    """
    Prepare |+>^n, apply per-qubit phase RZ(theta_j) with simple schedule,
    measure H_Z. Then append QFT (optionally approximate), measure H_QFT.
    """
    try:
        from qiskit import QuantumCircuit, transpile
        from qiskit.circuit.library import QFT
        from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
    except Exception as e:
        return {"error": f"Qiskit imports failed: {e}"}

    qc = QuantumCircuit(n_qubits)
    qc.h(range(n_qubits))
    # simple phase schedule: θ_j = 0.2 * 2^j  (keeps depth tiny)
    for j in range(n_qubits):
        qc.rz(0.2*(2**j), j)

    qcZ = qc.copy()
    qcZ.measure_all()

    qcF = qc.copy()
    qft = QFT(n_qubits, do_swaps=False, approximation_degree=max(0, int(approx_degree)))
    qcF.append(qft, range(n_qubits))
    qcF.measure_all()

    svc = QiskitRuntimeService()
    backend = svc.backend(backend_name)
    tqcZ = transpile(qcZ, backend=backend, optimization_level=1)
    tqcF = transpile(qcF, backend=backend, optimization_level=1)

    # Sampler with resilience fallback
    opts = {"default_shots": shots}
    try:
        sampler = Sampler(mode=backend, options={**opts, "resilience_level": 1})
    except Exception:
        sampler = Sampler(mode=backend, options=opts)

    resZ = sampler.run([tqcZ]).result()
    resF = sampler.run([tqcF]).result()
    w = len(tqcZ.clbits) or n_qubits
    cZ = robust_decode_sampler_result(resZ, shots, w)
    cF = robust_decode_sampler_result(resF, shots, w)
    return {
        "H_Z":  shannon_H_from_counts(cZ),
        "H_QFT":shannon_H_from_counts(cF),
        "depth_Z": int(tqcZ.depth()),
        "depth_F": int(tqcF.depth()),
        "twoq_Z":  int(sum(1 for ci in tqcZ.data if getattr(getattr(ci,'operation',ci),'num_qubits',0) >= 2)),
        "twoq_F":  int(sum(1 for ci in tqcF.data if getattr(getattr(ci,'operation',ci),'num_qubits',0) >= 2)),
    }

# --------- Artifact writers ----------
@dataclass
class KoopmanReport:
    N: int
    method: str
    spectral_radius: float
    residual_frob: float
    cond: Optional[float]
    eigenvalues: List[complex]

def save_koopman_artifact(path: Path, K: np.ndarray, method: str, resid: float, comment: str="") -> KoopmanReport:
    w, rad, cond = spectral_info(K)
    rep = KoopmanReport(
        N=K.shape[0],
        method=method,
        spectral_radius=float(rad),
        residual_frob=float(resid),
        cond=(None if cond is None else float(cond)),
        eigenvalues=[complex(z) for z in w]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump({
            "N": rep.N,
            "method": rep.method,
            "spectral_radius": rep.spectral_radius,
            "residual_frob": rep.residual_frob,
            "cond": rep.cond,
            "eigenvalues": [ [z.real, z.imag] for z in rep.eigenvalues ],
            "comment": comment
        }, f, indent=2)
    return rep

if __name__ == "__main__":
    print("Koopman Lab v0 utilities module. Use scripts/koopman_demo_logistic.py to run a demo.")
