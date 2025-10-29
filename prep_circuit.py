"""
prep_circuit.py — Unit 03 (Circuit Prep Spec and Simulation Harness)

This module:
- turns a LoaderSpec (Unit 02) into a PrepSpec (this unit),
- simulates shot counts from that PrepSpec,
- chains Unit 01 -> Unit 02 -> Unit 03 for convenience.

All functions MUST raise loudly if invariants are violated.
No silent mutation, no silent reordering, no silent metadata fixing.
"""

import numpy as np

def synthesize_init_circuit(loader_spec: dict) -> dict:
    """
    Input:
        loader_spec: dict from Unit 02 build_loader_spec()
        Required loader_spec fields used here:
          loader_version == "Unit02"
          endianness == "little"
          qft_kernel_sign == "+"
          rail_mode
          rail_layout
          register_qubits.{n_qubits, padded_length, pad_count}
          amplitudes.{vector, dtype}
          nve_version (carried through)
    Output:
        PrepSpec dict (Unit 03 contract), with fields:
          nve_version
          loader_version
          prep_version == "Unit03"
          endianness == "little"
          qft_kernel_sign == "+"
          n_qubits
          padded_length
          pad_count
          rail_mode
          rail_layout
          amplitudes { vector, dtype }
          init_sequence [ { "op": "prepare_basis_amplitudes",
                             "target_register": "full",
                             "amplitude_source": "amplitudes.vector",
                             "endianness": "little" } ]

    Must assert:
    - loader_spec["endianness"] == "little"
    - loader_spec["qft_kernel_sign"] == "+"
    - loader_spec["loader_version"] == "Unit02"
    - padded_length == 2**n_qubits
    - amplitudes.vector length == padded_length
    - L2 norm of amplitudes.vector ~ 1.0 within 1e-12
    - no NaN/Inf in amplitudes.vector
    - deterministic: same loader_spec in -> byte-identical PrepSpec after stable json dump
    """
    raise NotImplementedError("Unit03 TODO: synthesize_init_circuit")

def simulate_counts(prep_spec: dict, shots: int) -> dict:
    """
    Input:
        prep_spec: PrepSpec dict from synthesize_init_circuit()
        shots: int > 0
    Output:
        SimResult dict:
        {
          "prep_version": "Unit03",
          "n_qubits": <int>,
          "shots": <int>,
          "rail_mode": <str>,
          "counts": { "0": int, "1": int, ... },
          "distribution": { "0": float, "1": float, ... },
          "norm_check_l2": <float>,
          "endianness": "little",
          "qft_kernel_sign": "+"
        }

    Must assert:
    - prep_spec["prep_version"] == "Unit03"
    - prep_spec["endianness"] == "little"
    - prep_spec["qft_kernel_sign"] == "+"
    - shots > 0
    - amplitudes length == padded_length == 2**n_qubits
    - sum(|amp[i]|^2) ~ 1.0 within 1e-12
    - no NaN/Inf

    Sampling:
    - build ideal probs p[i] = |amp[i]|^2
    - multinomial-draw 'shots' samples
    - populate counts and distribution accordingly
    - norm_check_l2 should still be ~1.0
    """
    raise NotImplementedError("Unit03 TODO: simulate_counts")

def prep_run_bundle(nve_bundle: dict, shots: int) -> dict:
    """
    Chained convenience:
    - call build_loader_spec(nve_bundle) from Unit 02
    - call synthesize_init_circuit(...) from this unit
    - call simulate_counts(..., shots) from this unit

    Return dict:
    {
      "nve_version": ...,
      "loader_version": ...,
      "prep_version": "Unit03",
      "shots": shots,
      "prep_spec": <PrepSpec>,
      "sim_result": <SimResult>
    }

    Must raise on any contract violation in the chain.
    """
    raise NotImplementedError("Unit03 TODO: prep_run_bundle")
