import numpy as np

_I = np.array([[1,0],[0,1]], dtype=complex)
_X = np.array([[0,1],[1,0]], dtype=complex)
_Y = np.array([[0,-1j],[1j,0]], dtype=complex)
_Z = np.array([[1,0],[0,-1]], dtype=complex)
_PAULI = {'I': _I, 'X': _X, 'Y': _Y, 'Z': _Z}

def _rand_pauli_string(n, rng):
    """Draw a random n-qubit Pauli string (avoid all-Identity)."""
    alphabet = ['I','X','Y','Z']
    while True:
        s = ''.join(rng.choice(alphabet) for _ in range(n))
        if any(ch in s for ch in ('X','Y','Z')):
            return s

def _pauli_matrix(s: str):
    M = np.array([[1]], dtype=complex)
    for ch in s:
        M = np.kron(M, _PAULI[ch])
    return M

def shadow_score_from_rho(rho, m: int = 128, seed: int = 0) -> float:
    """
    Score ~ sqrt( E_P [ (Tr(rho P))^2 ] ) over random nontrivial Paulis P.
    For maximally mixed rho, score ~ 0. Lower is better (more "randomized").
    """
    rho = np.asarray(rho, dtype=complex)
    n = int(np.log2(rho.shape[0]))
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(int(m)):
        s = _rand_pauli_string(n, rng)
        P = _pauli_matrix(s)
        exp = np.trace(rho @ P)
        vals.append((exp.real**2 + exp.imag**2))
    return float(np.sqrt(np.mean(vals)))
