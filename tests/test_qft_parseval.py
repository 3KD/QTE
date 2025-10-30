import numpy as np
from qiskit.quantum_info import Statevector
from tools.qft_module import qft

def test_qft_parseval():
    n=3
    vec = np.random.randn(2**n) + 1j*np.random.randn(2**n)
    vec = vec/np.linalg.norm(vec)
    psi = Statevector(vec)
    out = psi.evolve(qft(n))
    assert abs(np.linalg.norm(out.data) - 1.0) < 1e-8
