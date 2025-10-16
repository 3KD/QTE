import math
import numpy as np

from series_encoding import _qte_maclaurin_coeffs  # internal but OK for tests

def sin_maclaurin_coeff(k: int) -> float:
    # sin(x) = Σ_{m>=0} (-1)^m x^{2m+1} / (2m+1)!
    if k % 2 == 0:
        return 0.0
    m = (k - 1) // 2
    return ((-1.0)**m) / math.factorial(2*m + 1)

def test_sin_maclaurin_first_15_terms():
    N = 15
    coeffs = _qte_maclaurin_coeffs("sin(x)", n_terms=N, radius=4.0, m=0)
    assert len(coeffs) >= N
    for k in range(N):
        ref = sin_maclaurin_coeff(k)
        assert abs(coeffs[k] - ref) < 1e-12, f"k={k} got {coeffs[k]} ref {ref}"

def test_sin_squared_series_consistency():
    # sin^2(x) = (1 - cos(2x))/2 so constant term should be 0.5
    coeffs = _qte_maclaurin_coeffs("sin(x)^2", n_terms=6, radius=4.0, m=0)
    assert abs(coeffs[0] - 0.5) < 1e-12
