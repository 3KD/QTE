# QTE add-on: Dual-rail (ancilla-tag) composition spec.
from __future__ import annotations
import numpy as np
from typing import Union, Dict, Any

def compose_dual_rail(psiA: np.ndarray,
                      psiB: np.ndarray,
                      U: Union[str, None] = "I",
                      alpha: complex = 1/np.sqrt(2),
                      beta:  complex = 1/np.sqrt(2)) -> Dict[str, Any]:
    """
    Return a minimal, backend-agnostic spec for an ancilla-tagged superposition:
      |Ψ⟩ = α|0⟩⊗|ψA⟩ + β|1⟩⊗U†|ψB⟩
    U can be "I", "QFT", "DHT:nu=0", or a symbolic tag you resolve later.
    """
    return {
        "alpha": complex(alpha),
        "beta":  complex(beta),
        "railA": np.asarray(psiA),
        "railB": np.asarray(psiB),
        "U":     U,
    }

def decompose_dual_rail(spec: Dict[str, Any]):
    """Inverse helper: (psiA, psiB, U, alpha, beta)."""
    return spec["railA"], spec["railB"], spec["U"], spec["alpha"], spec["beta"]


