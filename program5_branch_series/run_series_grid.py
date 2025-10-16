# scripts/run_series_grid.py
# Quick local batch: build several series states (and algebra combos) and save with entanglement-aware filenames.

from __future__ import annotations
import itertools, os
from typing import Optional, List, Tuple
import numpy as np

from qiskit.quantum_info import Statevector
from series_preserving import series_vector, to_statevector, hadamard_product, cauchy_product, egf_product, dirichlet_convolution
from state_io import save_statevector

# ---- config ----
OUTDIR = "states"

CONSTS: List[Tuple[str, Optional[str]]] = [
    ("π", "Machin"),
    ("e", None),
    ("ζ(3)", None),
    ("ln(2)", None),
]

N_LIST = [2**6, 2**7]               # 64, 128
PHASES = ["sign"]                   # keep sign structure
AMPMODES = ["terms", "egf"]         # try both
OPS = ["none", "hadamard", "cauchy", "egf"]  # pick a few safe defaults

# ---- helpers ----

def make_label(A, B, N, phase, amp, op):
    aL, aM = A; btxt = ""
    if B is not None:
        bL, bM = B
        btxt = f" ⊗{amp} {bL}{f'({bM})' if bM else ''}"
    return f"ALG[{aL}{f'({aM})' if aM else ''}{btxt} | N={N} | phase={phase} | {op}]"

def build(A, B, N, phase, amp, op):
    aL, aM = A
    a = series_vector(aL, N, method=aM, amp_mode=amp, phase_mode=phase, normalize=False)
    if op == "none" or B is None:
        vec = a
    else:
        bL, bM = B
        b = series_vector(bL, N, method=bM, amp_mode=amp, phase_mode=phase, normalize=False)
        if op == "hadamard":
            vec = hadamard_product(a, b)
        elif op == "cauchy":
            vec = cauchy_product(a, b)
        elif op == "egf":
            vec = egf_product(a, b)
        elif op == "dirichlet":
            vec = dirichlet_convolution(a, b)
        else:
            raise ValueError(op)
    nrm = np.linalg.norm(vec)
    if nrm == 0:
        raise RuntimeError("zero vector")
    sv = to_statevector(vec / nrm)
    label = make_label(A, B, N, phase, amp, op)
    return label, sv

def main():
    os.makedirs(OUTDIR, exist_ok=True)
    # singles
    for (A), N, phase, amp in itertools.product(CONSTS, N_LIST, PHASES, AMPMODES):
        label, sv = build(A, None, N, phase, amp, "none")
        path = save_statevector(sv, label, directory=OUTDIR, extras={"family": "single"})
        print("saved:", path)

    # pairs with ops
    for A, B in itertools.combinations(CONSTS, 2):
        for N, phase, amp, op in itertools.product(N_LIST, PHASES, AMPMODES, OPS[1:]):
            label, sv = build(A, B, N, phase, amp, op)
            path = save_statevector(sv, label, directory=OUTDIR, extras={"family": "pair", "op": op})
            print("saved:", path)

if __name__ == "__main__":
    main()

