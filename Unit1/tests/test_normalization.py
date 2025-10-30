import numpy as np
import pytest
# Eventually import real functions:
# from series_encoding import generate_series_vector, normalize_vector

def test_normalize_vector_unit_norm():
    # placeholder demo vector (non-zero)
    a = np.array([1.0, 2.0, 3.0, 4.0], dtype=complex)
    norm = np.linalg.norm(a)
    ahat = a / norm
    assert abs(np.linalg.norm(ahat) - 1.0) < 1e-9
    assert np.isfinite(ahat).all()

def test_zero_vector_rejected():
    a = np.zeros(16, dtype=complex)
    # TODO: replace with actual normalize_vector once implemented
    assert np.linalg.norm(a) == 0.0
    # with pytest.raises(ValueError):
    #     normalize_vector(a)
