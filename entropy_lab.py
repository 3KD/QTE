import numpy as np

def _norm(psi: np.ndarray) -> np.ndarray:
    psi = np.asarray(psi, dtype=complex).reshape(-1)
    n = np.linalg.norm(psi)
    if n == 0: raise ValueError("zero vector")
    return psi / n

def qft_unitary(d: int) -> np.ndarray:
    k = np.arange(d).reshape(-1,1)
    l = np.arange(d).reshape(1,-1)
    omega = np.exp(2j*np.pi*k*l/d)
    return omega / np.sqrt(d)

def measure_distribution(psi: np.ndarray, basis: str = "Z") -> np.ndarray:
    """Return measurement distribution in basis 'Z' (computational) or 'QFT' (Fourier)."""
    psi = _norm(psi)
    d = psi.size
    if basis.upper() == "Z":
        amp = psi
    elif basis.upper() in ("X","QFT","FOURIER"):
        F = qft_unitary(d)
        amp = F @ psi
    else:
        raise ValueError("basis must be 'Z' or 'QFT'")
    p = np.abs(amp)**2
    return p / (p.sum() if p.sum()!=0 else 1.0)

def shannon_entropy_bits(p: np.ndarray) -> float:
    p = np.asarray(p, dtype=float)
    p = p[(p>0)]
    return float(-np.sum(p*np.log2(p))) if p.size else 0.0

def entropies_Z_X(psi: np.ndarray) -> tuple[float,float]:
    pZ = measure_distribution(psi, "Z")
    pX = measure_distribution(psi, "QFT")
    return shannon_entropy_bits(pZ), shannon_entropy_bits(pX)

def von_neumann_entropy_bits(rho: np.ndarray) -> float:
    """S(ρ) = -Tr ρ log2 ρ for a density matrix ρ."""
    w = np.linalg.eigvalsh((rho + rho.conj().T)/2.0).real
    w = w[(w>0)]
    return float(-np.sum(w*np.log2(w))) if w.size else 0.0

def ensemble_entropy(states: list[np.ndarray]) -> float:
    """Given pure states |ψ_i>, return S( (1/N) Σ |ψ_i><ψ_i| )."""
    if not states: return 0.0
    d = states[0].size
    rho = np.zeros((d,d), dtype=complex)
    for s in states:
        s = _norm(s)
        rho += np.outer(s, s.conj())
    rho /= len(states)
    return von_neumann_entropy_bits(rho)
