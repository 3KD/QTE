"""
qtegui_adapter.py — Thin, safe import surface for QTEGUI.
Re-exports stable symbols from quantum_embedding without heavy work at import-time.
"""
from typing import Optional, List, Tuple, Dict

try:
    from quantum_embedding import (
        qft_spectrum_from_series,
        index_qft_spectrum_circuit,
        run_circuit,
        simulate_statevector,
        generate_series_encoding,
        encode_entangled_constants,
        entangle_series_registers,
        entangle_series_multi,
        analyze_tensor_structure,
        perform_schmidt_decomposition,
        value_phase_estimation_circuit,
        periodic_phase_state,
        digit_qrom_circuit,
    )
except Exception as e:
    raise ImportError(
        "qtegui_adapter failed to import quantum_embedding; "
        "check optional qiskit-aer and local module paths."
    ) from e

__all__ = [
    "qft_spectrum_from_series",
    "index_qft_spectrum_circuit",
    "run_circuit",
    "simulate_statevector",
    "generate_series_encoding",
    "encode_entangled_constants",
    "entangle_series_registers",
    "entangle_series_multi",
    "analyze_tensor_structure",
    "perform_schmidt_decomposition",
    "value_phase_estimation_circuit",
    "periodic_phase_state",
    "digit_qrom_circuit",
]
