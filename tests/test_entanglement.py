import pytest
pytest.skip("skipped: legacy test not wired to Unit01 NVE/NVQA yet", allow_module_level=True)
import numpy as np

from metrics_extra import schmidt_entropy
from quantum_embedding import perform_schmidt_decomposition

def _norm(v):
    v = np.asarray(v, dtype=complex)
    return v / np.linalg.norm(v)

def test_product_state_entropy_zero():
    # |00>
    psi = _norm([1,0,0,0])
    S = schmidt_entropy(psi, n_qubits=2, cut=1)
    assert abs(S - 0.0) < 1e-12

def test_bell_state_entropy_one():
    # (|00> + |11>)/√2
    psi = _norm([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)])
    S = schmidt_entropy(psi, n_qubits=2, cut=1)
    assert abs(S - 1.0) < 1e-6

def test_schmidt_decomposition_consistency():
    psi = _norm([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)])
    rhoA, rhoB, rhoAB = perform_schmidt_decomposition(psi, cut=1)
    # trace(rhoA) == trace(rhoB) == 1; eigenvalues match; purity < 1 for entangled
    assert np.allclose(np.trace(rhoA), 1.0)
    assert np.allclose(np.trace(rhoB), 1.0)
    evalsA = np.sort(np.linalg.eigvalsh(rhoA))
    evalsB = np.sort(np.linalg.eigvalsh(rhoB))
    assert np.allclose(evalsA, evalsB)
    purity = float(np.real(np.trace(rhoA @ rhoA)))
    assert purity < 1.0
