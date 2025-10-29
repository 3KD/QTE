import numpy as np
import pytest

def fidelity(a, b):
    # naive fidelity helper for test: |<a|b>|^2
    inner = np.vdot(a, b)
    return float(abs(inner)**2)

def test_fidelity_range_and_identity():
    # dummy identical states: normalized
    v = np.array([1,1,0,0], dtype=complex)
    v = v / np.linalg.norm(v)
    f = fidelity(v, v)
    assert 0.0 <= f <= 1.0
    assert f > 0.999999

def test_fidelity_not_trivial_for_diff_objects():
    v1 = np.array([1,1,0,0], dtype=complex)
    v2 = np.array([1,0,1,0], dtype=complex)
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    f = fidelity(v1, v2)
    assert 0.0 <= f <= 1.0
    # they shouldn't be identical
    assert f < 0.999999
