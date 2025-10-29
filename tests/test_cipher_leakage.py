import pytest
pytest.skip("skipped: crypto/scrambler/IND-CPA path not validated in Unit01 yet", allow_module_level=True)
from qiskit.quantum_info import Statevector
from qe_crypto.unitary_cipher import cipher_u
from tools.leakage_meter import leakage_score_from_state

def test_leakage_monotone():
    n=3; key=b'k'*32; nonce=b'n'*16
    psi = Statevector.from_label('0'*n)
    scores=[]
    for r in range(0,4):
        U = cipher_u(n,key,nonce,rounds=r)
        out = psi.evolve(U)
        scores.append(leakage_score_from_state(out, paulis=64))
    # allow tiny numerical jitter
    for i in range(len(scores)-1):
        assert scores[i+1] <= scores[i] + 1e-6
