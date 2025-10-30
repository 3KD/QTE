import numpy as np
from .primitives import prf_shake256, derive_subkeys

def _phase_for_index(Kp, nonce, idx, round_no, t_bits):
    msg = nonce + idx.to_bytes(8, "big") + round_no.to_bytes(2, "big")
    need = max(2, (t_bits + 7)//8)
    raw = prf_shake256(Kp, msg, outlen=need)
    val = int.from_bytes(raw, "big") & ((1 << t_bits) - 1)
    return (2.0 * np.pi) * (val / float(1 << t_bits))

def _fwht(v):
    """Walsh–Hadamard transform (size must be a power of 2)."""
    v = np.asarray(v, dtype=np.complex128).copy()
    n = int(v.shape[0])
    h = 1
    while h < n:
        for i in range(0, n, h*2):
            a = v[i:i+h].copy()
            b = v[i+h:i+2*h].copy()
            v[i:i+h]       = a + b
            v[i+h:i+2*h]   = a - b
        h *= 2
    return v / np.sqrt(n)

def phase_mix_encrypt(psi, key, nonce, t_bits=12, rounds=2):
    """Apply keyed, nonce-scoped random-diagonal + mixing (FWHT) rounds.

    Each round: v <- H * diag(e^{i phi}) * v
    This turns the diagonal-phase family into a simple RDC-like mixer,
    which empirically drives E_nu[ |U_{K,nu} psi><...| ] closer to I/d.
    """
    psi = np.asarray(psi, dtype=np.complex128)
    d = int(psi.shape[0])
    Kp, _, _ = derive_subkeys(key, nonce)
    v = psi.copy()
    for r in range(int(rounds)):
        phase = np.fromiter((_phase_for_index(Kp, nonce, i, r, int(t_bits)) for i in range(d)),
                            dtype=np.float64, count=d)
        v = v * np.exp(1j * phase)
        v = _fwht(v)
    return v

def avg_state_over_nonces(psi, key, num_samples=128, t_bits=12, rounds=2, seed=1234):
    """Monte Carlo average of encrypted states over fresh nonces. Returns rho_bar."""
    rng = np.random.default_rng(seed)
    d = int(np.asarray(psi).shape[0])
    rho = np.zeros((d, d), dtype=np.complex128)
    for _ in range(int(num_samples)):
        nonce = rng.bytes(12)  # 96-bit nonce
        v = phase_mix_encrypt(psi, key, nonce, t_bits=int(t_bits), rounds=int(rounds))
        rho += np.outer(v, np.conjugate(v))
    rho /= float(num_samples)
    return rho

def trace_distance_to_maxmix(rho):
    """Return 1/2 * ||rho - I/d||_1 for Hermitian rho."""
    d = int(rho.shape[0])
    diff = rho - np.eye(d, dtype=np.complex128)/float(d)
    vals = np.linalg.eigvalsh(diff)
    return 0.5 * float(np.sum(np.abs(vals)))
