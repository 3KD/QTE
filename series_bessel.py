# QTE add-on: Bessel J_ν Maclaurin coefficients (ν ≥ 0).
from __future__ import annotations
import math

def Jnu_maclaurin_coeff(n: int, nu: int) -> float:
    """
    Coefficient of x^n in:
      J_ν(x) = Σ_{m≥0} (-1)^m / (m! Γ(m+ν+1)) * (x/2)^{2m+ν}
    For integer ν ≥ 0: coefficient = 0 unless n ≥ ν AND (n-ν) even.
    Then m = (n-ν)//2 and coeff = (-1)^m / (m! Γ(m+ν+1)) * (1/2)^n.
    """
    if n < nu or ((n - nu) % 2):
        return 0.0
    m = (n - nu) // 2
    return ((-1.0)**m) / (math.factorial(m) * math.gamma(m + nu + 1)) * (0.5 ** n)

def J0_maclaurin_coeff(n: int) -> float:
    return Jnu_maclaurin_coeff(n, 0)

