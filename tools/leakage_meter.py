import numpy as np
from qiskit.quantum_info import Pauli, Statevector

def leakage_score_from_state(state: Statevector, paulis:int=256) -> float:
    """
    Estimate leakage proxy: sqrt( average_P (Tr(P ρ))^2 ) over random non-identity Paulis.
    """
    n = state.num_qubits
    rho = np.outer(state.data, np.conj(state.data))
    S=0.0; cnt=0
    for _ in range(paulis):
        label = ''.join(np.random.choice(list('IXYZ'), size=n))
        if set(label)=={'I'}: continue
        P = Pauli(label).to_matrix()
        val = float(np.trace(P @ rho).real)
        S += val*val; cnt += 1
    if cnt==0: return 0.0
    return float(np.sqrt(S/cnt))
