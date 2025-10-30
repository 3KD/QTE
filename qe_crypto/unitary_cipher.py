import numpy as np, hashlib
from qiskit import QuantumCircuit
from qiskit.circuit.library import Diagonal
from tools.qft_module import qft

def phase_poly(n:int, key:bytes, nonce:bytes, t_bits:int=12)->np.ndarray:
    """Keyed per-index phases φ_k (toy PRF). Swap with KMAC/Shake in production."""
    N=2**n; phi=np.zeros(N)
    seed = hashlib.sha3_256(key+nonce).digest()
    rng = int.from_bytes(seed, "big")
    for k in range(N):
        rng = (1103515245*rng + 12345) & ((1<<64)-1)
        phi[k] = 2*np.pi * ((rng & ((1<<t_bits)-1)) / (1<<t_bits))
    return phi

def cipher_u(n:int, key:bytes, nonce:bytes, rounds:int=3)->QuantumCircuit:
    """
    U_{K,ν} = P · QFT† · D_φ(key,nonce) · QFT · C   (toy P,C for now).
    """
    qc = QuantumCircuit(n, name="Cipher-U")
    for r in range(rounds):
        # C: shallow scrambler
        for q in range(n):
            qc.h(q); qc.s(q)
        # QFT sandwich with keyed diagonal
        qc.compose(qft(n), inplace=True)
        phi = phase_poly(n, key, nonce+bytes([r & 0xFF]))
        qc.append(Diagonal(np.exp(1j*phi)), range(n))
        qc.compose(qft(n, inverse=True), inplace=True)
        # P: simple bit-reversal as placeholder
        for i in range(n//2):
            qc.swap(i, n-1-i)
    return qc
