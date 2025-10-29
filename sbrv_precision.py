"""sbrv_precision.py — Unit 01 SBRV (stacked band / residual vector) precision scaffolding.

We split large-dynamic-range coefficient vectors into multiple 'bands'
so we can store high and low magnitude parts deterministically.

sbrv_decompose(a, bands=4) -> list[np.ndarray]
sbrv_reconstruct(chunks)   -> np.ndarray

These MUST be deterministic: same input => same band decomposition.
Later units (24, transcendental constants; 27, SQ hardness) rely on this.
"""

# TODO: real implementations
def sbrv_decompose(a, bands=4):
    raise NotImplementedError("Unit01 TODO: sbrv_decompose")

def sbrv_reconstruct(chunks):
    raise NotImplementedError("Unit01 TODO: sbrv_reconstruct")
