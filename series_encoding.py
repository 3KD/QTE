"""series_encoding.py — Unit 01 NVE pipeline (authoritative)

REQUIREMENTS:
- build_series_representation(object_spec)
- apply_weighting(c, weighting_mode)
- apply_phase_mode(a, phase_mode, rail_mode)
- normalize_vector(r)
- package_nve(object_spec) -> {"psi": np.ndarray, "metadata": {...}}

The metadata MUST include:
    "endianness": "little"
    "qft_kernel_sign": "+"
    "weighting_mode": ...
    "phase_mode": ...
    "rail_mode": ...
    "length": ...
    "norm_l2": 1.0
    "nve_version": "Unit01"

Determinism test in tests/test_nve_metadata_roundtrip.py will fail the build if
two invocations on the same object_spec produce different psi arrays or different metadata.
"""

# TODO: real implementation
def build_series_representation(object_spec):
    raise NotImplementedError("Unit01 TODO: build_series_representation")

def apply_weighting(c, weighting_mode):
    raise NotImplementedError("Unit01 TODO: apply_weighting")

def apply_phase_mode(a, phase_mode, rail_mode):
    raise NotImplementedError("Unit01 TODO: apply_phase_mode (full_complex / magnitude_only + rail packing)")

def normalize_vector(r):
    raise NotImplementedError("Unit01 TODO: normalize_vector (assert ||ψ||₂≈1 within 1e-12, no NaN/Inf)")

def package_nve(object_spec):
    raise NotImplementedError("Unit01 TODO: package_nve (produce psi + canonical metadata)")

# --- Legacy compatibility shims for old tests ---
def get_series_amplitudes(*args, **kwargs):
    """
    Legacy stub for tests/test_entanglement.py expecting get_series_amplitudes.
    Unit01 replaced this with package_nve/object_spec pipeline.
    We leave a stub so import doesn't explode. Runtime use will raise.
    """
    raise NotImplementedError("legacy get_series_amplitudes stub (migrated to NVE in Unit01)")

def compute_series_value(*args, **kwargs):
    """
    Legacy stub for tests/test_entanglement.py expecting compute_series_value.
    """
    raise NotImplementedError("legacy compute_series_value stub (migrated to NVE in Unit01)")

def _qte_maclaurin_coeffs(*args, **kwargs):
    """
    Legacy stub for tests/test_series_trig.py.
    """
    raise NotImplementedError("legacy _qte_maclaurin_coeffs stub (migrated to NVE in Unit01)")
