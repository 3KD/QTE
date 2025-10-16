# QTE add-on: fixed Maclaurin coefficient for erf(x).
from __future__ import annotations
import math

def erf_coefficient(n: int) -> float:
    """
    erf(x) = (2/√π) Σ_{m≥0} (-1)^m x^{2m+1} / (m!(2m+1))
    Returns the coefficient of x^n in the Maclaurin series (nonzero only for odd n).
    """
    if n % 2 == 0:
        return 0.0
    m = (n - 1) // 2
    return (2.0 / math.sqrt(math.pi)) * ((-1.0)**m) / (math.factorial(m) * (2*m + 1))

