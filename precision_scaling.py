# QTE add-on: simple fidelity/distortion bound for SBRV depth L.

def fidelity_upper_bound(d: int, L: int) -> float:
    """
    Rough analysis:
      ||Δ||_2 ≤ 2^{-(L+1)} sqrt(d)  ⇒  1 - F  ≲  O(2^{-2L} d).
    Returns an upper bound on 1 - fidelity (dimensionless).
    """
    return min(1.0, (2.0 ** (-(2 * (L + 1)))) * float(d))

