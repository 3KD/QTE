import numpy as np
from qiskit.circuit.library import UnitaryGate
from qiskit import QuantumCircuit

def _unitary_from_orth(M: np.ndarray, label:str)->QuantumCircuit:
    # Ensure square, near-orthonormal
    U = M.astype(complex)
    # Make perfectly unitary via polar decomposition (closest unitary)
    Q,_ = np.linalg.qr(U)
    Uu,_,Vh = np.linalg.svd(Q, full_matrices=False)
    Uu = Uu @ Vh
    gate = UnitaryGate(Uu, label=label)
    n = int(np.log2(U.shape[0]))
    qc = QuantumCircuit(n, name=label)
    qc.append(gate, range(n))
    return qc

def dct2_unitary(n:int)->QuantumCircuit:
    """DCT-II orthogonal matrix (size N=2^n), wrapped as a unitary. Small-N demo."""
    N = 2**n
    k = np.arange(N)[:,None]
    nidx = np.arange(N)[None,:]
    M = np.sqrt(2.0/N)*np.cos(np.pi*(nidx+0.5)*k/N)
    M[0,:] /= np.sqrt(2.0)  # orthonormal DCT-II scaling
    return _unitary_from_orth(M, f"DCT2(N={N})")

def dst2_unitary(n:int)->QuantumCircuit:
    """DST-II orthogonal matrix (size N=2^n), wrapped as a unitary. Small-N demo."""
    N = 2**n
    k = np.arange(1,N+1)[:,None]
    nidx = np.arange(N)[None,:]
    M = np.sqrt(2.0/(N+1))*np.sin(np.pi*(nidx+1)*k/(N+1))
    return _unitary_from_orth(M, f"DST2(N={N})")
