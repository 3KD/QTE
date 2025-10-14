#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Demo: 1D logistic map x_{t+1} = μ x_t (1 - x_t)
- Generate trajectory
- Learn truncated Koopman K (monomial dictionary) via ridge
- Predict forward, compute RMSE
- Save artifacts + summary markdown
- Optional: shallow hardware entropy probe (Z/QFT) on IBM backend
"""
from __future__ import annotations
import argparse, json, math, os, sys
from pathlib import Path
from datetime import datetime

import numpy as np

# local utils
sys.path.append(str(Path(__file__).resolve().parent.parent))
from scripts.koopman_lab import (
    learn_koopman_ridge, predict_from_K, save_koopman_artifact,
    hardware_entropy_probe
)

def logistic(mu: float, x: float) -> float:
    return mu * x * (1.0 - x)

def build_trajectory(mu: float, x0: float, T: int, burn_in: int=50) -> np.ndarray:
    x = x0
    xs = []
    for _ in range(burn_in+T):
        x = logistic(mu, x)
        xs.append(x)
    return np.array(xs[burn_in:], dtype=float)

def rmse(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a).ravel()
    b = np.asarray(b).ravel()
    if a.shape != b.shape: b = b[:a.size]
    return float(np.sqrt(np.mean((a-b)**2)))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mu", type=float, default=3.7)
    ap.add_argument("--x0", type=float, default=0.12345)
    ap.add_argument("--T", type=int, default=256)
    ap.add_argument("--N", type=int, default=8, help="Monomial basis size")
    ap.add_argument("--ridge", type=float, default=1e-6)
    ap.add_argument("--outdir", type=str, default="paper_outputs")
    ap.add_argument("--summary", type=str, default="research_summary")
    ap.add_argument("--hardware", action="store_true", help="Run shallow entropy probe on backend")
    ap.add_argument("--backend", type=str, default="ibm_torino")
    ap.add_argument("--shots", type=int, default=256)
    ap.add_argument("--approx-degree", type=int, default=0)
    args = ap.parse_args()

    outdir = Path(args.outdir); outdir.mkdir(parents=True, exist_ok=True)
    summdir = Path(args.summary); summdir.mkdir(parents=True, exist_ok=True)

    # 1) data
    xs = build_trajectory(args.mu, args.x0, args.T)
    # 2) learn K
    K, resid = learn_koopman_ridge(xs, N=args.N, ridge=args.ridge)
    tag = f"koopman_learn_mu{args.mu}_N{args.N}_T{args.T}.json"
    rep = save_koopman_artifact(outdir / tag, K, method=f"ridge({args.ridge})",
                                resid=resid, comment="1D logistic, monomial dictionary")

    # 3) prediction quality
    steps = min(128, args.T-2)
    xhat = predict_from_K(K, xs[0], steps)
    err = rmse(xs[:xhat.size], xhat)

    # 4) optional shallow HW entropy probe
    hw = None
    if args.hardware:
        try:
            n_qubits = max(3, int(math.ceil(math.log2(args.N))))
            hw = hardware_entropy_probe(n_qubits=n_qubits,
                                        backend_name=args.backend,
                                        shots=args.shots,
                                        approx_degree=args.approx_degree)
        except Exception as e:
            hw = {"error": f"entropy probe failed: {e}"}

    # 5) write summary md
    md = summdir / "KOOPMAN_SUMMARY.md"
    with md.open("w") as f:
        f.write("# Koopman (Logistic) summary\n\n")
        f.write(f"- Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"- Logistic μ={args.mu}, basis N={args.N}, samples T={args.T}, ridge={args.ridge}\n\n")
        f.write("## Learned operator\n")
        f.write(f"- spectral radius ≈ **{rep.spectral_radius:.6g}**\n")
        f.write(f"- residual Frobenius ≈ **{rep.residual_frob:.6g}**\n")
        f.write(f"- cond(K) ≈ **{rep.cond if rep.cond is not None else 'n/a'}**\n")
        f.write(f"- artifact: `{outdir / tag}`\n\n")
        f.write("## Prediction\n")
        f.write(f"- steps evaluated: **{xhat.size}**\n")
        f.write(f"- RMSE(x̂, x) ≈ **{err:.6g}**\n\n")
        if hw:
            f.write("## Hardware entropy probe (shallow)\n")
            if "error" in hw:
                f.write(f"- error: `{hw['error']}`\n")
            else:
                f.write(f"- H(Z) ≈ **{hw['H_Z']:.3f}**, H(QFT) ≈ **{hw['H_QFT']:.3f}**\n")
                f.write(f"- depth(Z)={hw['depth_Z']}, twoq(Z)={hw['twoq_Z']}; "
                        f"depth(QFT)={hw['depth_F']}, twoq(QFT)={hw['twoq_F']}\n")

    # 6) small CSV for predictions
    csvp = summdir / "KOOPMAN_PREDICTION.csv"
    with csvp.open("w") as f:
        f.write("t,x,xhat\n")
        for t,(a,b) in enumerate(zip(xs[:xhat.size], xhat)):
            f.write(f"{t},{a:.10f},{b:.10f}\n")

    print("=== KOOPMAN DEMO SUMMARY ===")
    print(f"Learned K: spectral_radius={rep.spectral_radius:.6g}  residual={rep.residual_frob:.6g}")
    print(f"Prediction RMSE: {err:.6g}  (steps={xhat.size})")
    if hw:
        print("Entropy probe:", hw)

    print("\nWrote:")
    print(" -", outdir / tag)
    print(" -", md)
    print(" -", csvp)

if __name__ == "__main__":
    main()
