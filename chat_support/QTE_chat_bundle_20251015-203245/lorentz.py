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
