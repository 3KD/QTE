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
