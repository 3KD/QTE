import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import Diagonal, HGate
from tools.qft_module import qft

def hilbert_transform(n:int)->QuantumCircuit:
    """Hilbert transform via QFT-domain -i*sgn(ω) phase."""
    N=2**n; omega=np.arange(N)-N//2; phase = -np.pi/2 * np.sign(omega)
    qc = QuantumCircuit(n, name="Hilbert")
    qc.compose(qft(n), inplace=True)
    qc.append(Diagonal(np.exp(1j*phase)), range(n))
    qc.compose(qft(n, inverse=True), inplace=True)
    return qc

def walsh_hadamard(n:int)->QuantumCircuit:
    """Walsh–Hadamard (layer of H gates)."""
    qc = QuantumCircuit(n, name="WalshHadamard")
    for q in range(n):
        qc.append(HGate(), [q])
    return qc
