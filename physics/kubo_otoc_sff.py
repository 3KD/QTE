import numpy as np
from qiskit.quantum_info import Operator

def spectral_form_factor(U: Operator, t:int) -> float:
    """K(t)=|Tr(U^t)|^2 (tiny-N utility)."""
    Ut = Operator(np.linalg.matrix_power(U.data, t))
    tr = np.trace(Ut.data)
    return float(np.abs(tr)**2)
