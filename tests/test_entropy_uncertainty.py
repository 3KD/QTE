import numpy as np
from entropy_lab import entropies_Z_X, ensemble_entropy, _norm

def random_state(d: int) -> np.ndarray:
    z = np.random.normal(size=d) + 1j*np.random.normal(size=d)
    return _norm(z)

def test_entropic_uncertainty_MUB():
    # For Z & QFT (MUB) in dimension d=2^n: H_Z + H_X >= log2 d
    d = 16
    psi = random_state(d)
    HZ, HX = entropies_Z_X(psi)
    assert (HZ + HX) >= np.log2(d) - 1e-9

def test_ensemble_entropy_two_orthogonal_states_is_1bit():
    e0 = np.array([1,0,0,0], dtype=complex)
    e1 = np.array([0,1,0,0], dtype=complex)
    S = ensemble_entropy([e0, e1])
    assert abs(S - 1.0) < 1e-9
