# QTE add-on: simple rail masks & carriers.
from __future__ import annotations
import numpy as np

def even_odd_masks(d: int):
    idx = np.arange(d)
    return (idx % 2 == 0), (idx % 2 == 1)

def block_masks(d: int, blocks: int):
    blocks = max(1, int(blocks))
    size = max(1, d // blocks)
    return [((np.arange(d) // size) == b) for b in range(blocks)]

def carriers(d: int, ks: list[int]) -> np.ndarray:
    """
    OFDM-style carriers r_k(i) = exp(2π i k i / d) as (d x len(ks)) matrix.
    """
    i = np.arange(d)[:, None]
    return np.exp(2j * np.pi * i * (np.asarray(ks)[None, :]) / d)

