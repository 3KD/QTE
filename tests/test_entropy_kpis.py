import numpy as np
from qiskit.quantum_info import Statevector
from tools.entropy_metrics import entropy_kpis

def test_entropy_simple():
    n=2
    psi = Statevector.from_label('00')
    k = entropy_kpis(psi, basis="comp")
    assert k["H_shannon"] == 0.0
    assert k["H_min"] == 0.0
    # uniform superposition -> higher entropy
    v = np.ones(2**n)/np.sqrt(2**n)
    k2 = entropy_kpis(Statevector(v), basis="comp")
    assert k2["H_shannon"] > 0.9  # 2 qubits uniform H=2
