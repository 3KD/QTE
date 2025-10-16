import math
import numpy as np

ETA = np.diag([-1.0, 1.0, 1.0, 1.0])  # Minkowski metric (-,+,+,+)

def boost_x(beta: float) -> np.ndarray:
    if not (-1.0 < beta < 1.0):
        raise ValueError("beta must be in (-1,1)")
    g = 1.0 / math.sqrt(1.0 - beta*beta)
    # Standard boost along +x
    L = np.array([
        [ g, -g*beta, 0.0, 0.0],
        [-g*beta,  g,   0.0, 0.0],
        [ 0.0,     0.0, 1.0, 0.0],
        [ 0.0,     0.0, 0.0, 1.0],
    ], dtype=float)
    return L

def preserves_minkowski(L: np.ndarray, atol=1e-10) -> bool:
    # Check L^T η L = η
    return np.allclose(L.T @ ETA @ L, ETA, atol=atol)
# --- QTE compatibility shim (append-only): allow preserves_minkowski(beta=...) ---
try:
    _preserves_minkowski_orig = preserves_minkowski  # type: ignore[name-defined]
    def preserves_minkowski(beta=None, *args, **kwargs):
        """Compatibility wrapper: accept preserves_minkowski(beta=...) or positional.
        Falls back to v/c kwargs if provided."""
        if beta is None:
            if 'beta' in kwargs:
                beta = kwargs['beta']
            elif args:
                beta = args[0]
            elif 'v' in kwargs and 'c' in kwargs and kwargs['c'] != 0:
                beta = kwargs['v'] / kwargs['c']
            else:
                raise TypeError("preserves_minkowski() requires beta (positional or keyword)")
        return _preserves_minkowski_orig(float(beta))
except Exception:
    # If original isn't present for some reason, define a minimal safe version.
    import numpy as _np
    def preserves_minkowski(beta=None, *args, **kwargs):
        if beta is None:
            if 'beta' in kwargs:
                beta = kwargs['beta']
            elif args:
                beta = args[0]
            elif 'v' in kwargs and 'c' in kwargs and kwargs['c'] != 0:
                beta = kwargs['v'] / kwargs['c']
            else:
                raise TypeError("preserves_minkowski() requires beta (positional or keyword)")
        b = float(beta)
        if abs(b) >= 1.0:
            return False
        g = 1.0 / _np.sqrt(1.0 - b*b)
        # Basic invariant check on a sample 4-vector (ct, x, 0, 0) with c=1
        t, x = 1.0, 0.25
        t2 = g*(t - b*x)
        x2 = g*(x - b*t)
        s  = t*t - x*x
        s2 = t2*t2 - x2*x2
        return abs(s - s2) < 1e-9

# --- QTE compat patch: preserves_minkowski accepts matrix or beta ---
def _qte_eta():
    import numpy as _np
    return _np.diag([1.0, -1.0, -1.0, -1.0])

try:
    _preserves_minkowski_orig  # type: ignore[name-defined]
except Exception:
    _preserves_minkowski_orig = None  # not present in older builds

def preserves_minkowski(arg=None, *args, **kwargs):
    """
    Accepts either:
      - a 4x4 Lorentz matrix L and checks L^T η L == η, or
      - a scalar beta (=v/c) and verifies invariance for the standard boost.
    Also accepts keyword beta=..., or (v=..., c=...) as a convenience.
    """
    import numpy as _np
    # Case 1: first arg looks like a matrix -> invariance check
    if hasattr(arg, "shape"):
        L = _np.asarray(arg, dtype=float)
        if L.shape != (4, 4):
            raise ValueError("Matrix must be 4x4 for Minkowski check")
        eta = _qte_eta()
        return _np.allclose(L.T @ eta @ L, eta, atol=1e-9)

    # Case 2: derive beta from inputs
    if arg is None:
        if "beta" in kwargs:
            arg = kwargs["beta"]
        elif "v" in kwargs and "c" in kwargs and kwargs["c"]:
            arg = kwargs["v"] / kwargs["c"]
        elif args:
            arg = args[0]
        else:
            raise TypeError("preserves_minkowski() requires a 4x4 matrix or beta")

    # If an original scalar-beta function exists, delegate
    if _preserves_minkowski_orig is not None:
        try:
            return bool(_preserves_minkowski_orig(float(arg)))
        except Exception:
            pass  # fall through to numeric check

    # Numeric fallback: construct boost and check L^T η L == η
    b = float(arg)
    if abs(b) >= 1.0:
        return False
    g = 1.0 / _np.sqrt(1.0 - b*b)
    L = _np.array([
        [ g, -g*b, 0.0, 0.0],
        [-g*b,  g,  0.0, 0.0],
        [ 0.0,  0.0, 1.0, 0.0],
        [ 0.0,  0.0, 0.0, 1.0],
    ], dtype=float)
    eta = _qte_eta()
    return _np.allclose(L.T @ eta @ L, eta, atol=1e-9)
