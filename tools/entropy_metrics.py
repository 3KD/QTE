import numpy as np
from typing import Dict, Tuple, Optional
from qiskit.quantum_info import Statevector
from tools.qft_module import qft

def _probs_from_state(psi: Statevector, basis: str="comp") -> np.ndarray:
    """Return measurement probabilities in chosen basis: 'comp' or 'qft'."""
    if basis == "comp":
        return np.abs(psi.data)**2
    elif basis == "qft":
        n = psi.num_qubits
        psi_f = psi.evolve(qft(n))
        return np.abs(psi_f.data)**2
    else:
        raise ValueError("basis must be 'comp' or 'qft'")

def shannon_entropy(p: np.ndarray) -> float:
    p = np.asarray(p, dtype=float)
    p = p[p>0]
    return float(-np.sum(p*np.log2(p)))

def renyi2_entropy(p: np.ndarray) -> Tuple[float, float]:
    s2 = float(np.sum(np.asarray(p, dtype=float)**2))
    if s2 <= 0: return float('inf'), float('inf')
    H2 = -np.log2(s2)
    PR = 2.0**H2
    return float(H2), float(PR)

def min_entropy(p: np.ndarray) -> float:
    return float(-np.log2(float(np.max(p)) if len(p) else 1.0))

def rel_entropy_to_uniform(p: np.ndarray) -> float:
    D = len(p)
    return float(np.log2(D) - shannon_entropy(p))

def entropy_kpis(psi: Statevector, basis: str="comp") -> Dict[str, float]:
    p = _probs_from_state(psi, basis=basis)
    H = shannon_entropy(p)
    H2, PR = renyi2_entropy(p)
    Hinf = min_entropy(p)
    Dgap = rel_entropy_to_uniform(p)
    return {"H_shannon": H, "H2": H2, "PR": PR, "H_min": Hinf, "D_to_uniform": Dgap}
