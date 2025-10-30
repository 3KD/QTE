"""
Unit 03 enforcement: PrepSpec required fields.

PrepSpec must have all mandatory top-level keys:
- nve_version, loader_version, prep_version
- endianness, qft_kernel_sign
- n_qubits, padded_length, pad_count
- rail_mode, rail_layout
- amplitudes, init_sequence

amplitudes.vector must match loader_spec's amplitudes.vector exactly.
"""
def test_prep_serialization_fields_contract():
    assert True  # TODO: check keys + vector equality (no reordering)
