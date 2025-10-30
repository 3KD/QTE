import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import Diagonal
from tools.qft_module import qft

def _diag(phi):  # phi in radians
    return Diagonal(np.exp(1j*phi))

def frac_fourier(n:int, alpha:float)->QuantumCircuit:
    """
    Fractional Fourier transform (small-n prototype) via chirp–QFT–chirp–QFT†–chirp.
    alpha in [0,1] (0=id, 1=QFT up to phases).
    """
    N=2**n; theta=alpha*np.pi/2; k=np.arange(N); c=2*np.pi/N
    quad_t=((k-N/2.0)**2)*np.tan(theta/2.0)*c
    quad_f=-((k-N/2.0)**2)*np.sin(theta)*c
    qc=QuantumCircuit(n, name=f"FrFT({alpha:.3f})")
    qc.append(_diag(quad_t), range(n))
    qc.compose(qft(n), inplace=True)
    qc.append(_diag(quad_f), range(n))
    qc.compose(qft(n, inverse=True), inplace=True)
    qc.append(_diag(quad_t), range(n))
    return qc

def chirp_z(n:int, k0:float, dk:float)->QuantumCircuit:
    """Chirp-Z zoom (Bluestein-style) prototype."""
    N=2**n; k=np.arange(N); c=np.pi*dk/N
    phi_t=c*(k**2); phi_f=-c*((k-k0)**2)
    qc=QuantumCircuit(n, name=f"CZT(k0={k0:.2f})")
    qc.append(Diagonal(np.exp(1j*phi_t)), range(n))
    qc.compose(qft(n), inplace=True)
    qc.append(Diagonal(np.exp(1j*phi_f)), range(n))
    qc.compose(qft(n, inverse=True), inplace=True)
    qc.append(Diagonal(np.exp(1j*phi_t)), range(n))
    return qc
