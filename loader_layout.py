"""
loader_layout.py — Unit 02 (State Loader Construction / Hardware-Ready Register Layout)

This module consumes the output bundle from Unit 01 (package_nve),
and produces a deterministic LoaderSpec dict that downstream units
(03/04/05/11/etc.) will treat as the contract for how ψ maps onto qubits.

All functions MUST raise loudly if invariants are violated.
No silent repair is allowed.
"""

import numpy as np

def resolve_register_shape(psi: np.ndarray):
    """
    Input:
        psi : np.ndarray
            normalized state vector from Unit 01 (‖psi‖₂ ≈ 1, length L).
    Output:
        dict with:
        {
          "psi_padded": np.ndarray length D,
          "original_length": L,
          "padded_length": D,
          "pad_count": D-L,
          "n_qubits": n
        }

    Rules:
    - n is smallest int with 2**n >= L
    - D = 2**n
    - psi_padded is psi followed by exact zeros (0.0 or 0.0+0.0j) to length D
    - must assert:
        abs(||psi||₂ - 1.0) <= 1e-12
        abs(||psi_padded||₂ - 1.0) <= 1e-12
      and no NaN/Inf anywhere
    """
    raise NotImplementedError("Unit02 TODO: resolve_register_shape")

def derive_rail_layout(psi_padded: np.ndarray, rail_mode: str):
    """
    Input:
        psi_padded : np.ndarray length D
        rail_mode  : 'none' | 'iq_split' | 'sign_split'

    Output:
        rail_layout dict, matching Unit 02 spec:
        - kind: "single" | "iq_split" | "sign_split"
        - ranges for each rail

    Must NOT reorder amplitudes, only annotate index ranges.
    Must assert even split for iq_split/sign_split.
    """
    raise NotImplementedError("Unit02 TODO: derive_rail_layout")

def build_loader_spec(nve_bundle: dict):
    """
    Input:
        nve_bundle from Unit 01 package_nve():
        {
          "psi": np.ndarray,
          "metadata": {
             "object_spec": {...},
             "weighting_mode": "...",
             "phase_mode": "...",
             "rail_mode": "...",
             "endianness": "little",
             "qft_kernel_sign": "+",
             "length": L,
             "norm_l2": 1.0,
             "nve_version": "Unit01"
          }
        }

    Output:
        LoaderSpec dict:
        {
          "nve_version": <from metadata>,
          "loader_version": "Unit02",
          "endianness": "little",
          "qft_kernel_sign": "+",

          "object_spec": {...copy...},

          "rail_mode": <rail_mode>,
          "rail_layout": { ... },

          "register_qubits": {
             "n_qubits": n,
             "original_length": L,
             "padded_length": D,
             "pad_count": D-L
          },

          "amplitudes": {
             "vector": [... list form ...],
             "dtype": "float64" | "complex128"
          }
        }

    Must:
    - call resolve_register_shape
    - call derive_rail_layout
    - assert endianness == "little"
    - assert qft_kernel_sign == "+"
    - assert ||psi_padded||₂ ~ 1.0 within 1e-12
    - assert no NaN/Inf
    - produce deterministic ordering suitable for stable JSON dump
    """
    raise NotImplementedError("Unit02 TODO: build_loader_spec")

def loader_spec_to_json(spec: dict, path: str):
    """
    Serialize LoaderSpec to disk at 'path' as JSON with stable key ordering.

    Must refuse to write if:
    - spec['loader_version'] != "Unit02"
    - spec['endianness'] != "little"
    - spec['qft_kernel_sign'] != "+"
    - any amplitude NaN/Inf
    - ||vector||₂ deviates from 1.0 by >1e-12
    """
    raise NotImplementedError("Unit02 TODO: loader_spec_to_json")
