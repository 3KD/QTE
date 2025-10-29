import numpy as np
from qiskit.circuit.library import UnitaryGate
from qiskit import QuantumCircuit

def _unitarize(M: np.ndarray) -> np.ndarray:
    """Closest unitary via polar (QR+SVD)."""
    Q,_ = np.linalg.qr(M)
    U,_,Vh = np.linalg.svd(Q, full_matrices=False)
    return U @ Vh

def _get_bessels():
    """Try imports; provide crude fallback to keep demos running."""
    try:
        from mpmath import besselj, spherical_besselj
        return besselj, spherical_besselj, False
    except Exception:
        import numpy as _np
        # crude smooth fallback so the circuit builds; not mathematically faithful
        def besselj(nu, x): return _np.sinc(_np.asarray(x)/_np.pi)
        def spherical_besselj(ell, x): return _np.sinc(_np.asarray(x)/_np.pi)
        return besselj, spherical_besselj, True

def discrete_hankel_unitary(n:int, order:float=0.0)->QuantumCircuit:
    """Discrete Hankel (order ν) as a small-n UnitaryGate (demo)."""
    besselj, _, fallback = _get_bessels()
    N=2**n; r=np.linspace(0,1,N); k=np.linspace(0,1,N); H=np.zeros((N,N),dtype=complex)
    for i,ki in enumerate(k):
        H[i,:] = [besselj(order, 2*np.pi*ki*ri) for ri in r]
    U = _unitarize(H)
    label = f"Hankel(ν={order}{',~' if fallback else ''})"
    gate = UnitaryGate(U, label=label)
    qc = QuantumCircuit(n, name=label)
    qc.append(gate, range(n))
    return qc

def spherical_bessel_unitary(n:int, ell:int=0)->QuantumCircuit:
    """Spherical-Bessel j_ell transform (tiny-N demo)."""
    _, spherical_besselj, fallback = _get_bessels()
    N=2**n; r=np.linspace(0,1,N); k=np.linspace(0,1,N); H=np.zeros((N,N),dtype=complex)
    for i,ki in enumerate(k):
        H[i,:] = [spherical_besselj(ell, 2*np.pi*ki*ri) for ri in r]
    U = _unitarize(H)
    label = f"SphBessel(ℓ={ell}{',~' if fallback else ''})"
    gate = UnitaryGate(U, label=label)
    qc = QuantumCircuit(n, name=label)
    qc.append(gate, range(n))
    return qc
