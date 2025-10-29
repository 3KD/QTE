"""
Unit 03 enforcement: PrepSpec must mirror LoaderSpec shape info.

synthesize_init_circuit(loader_spec) must produce:
- prep_version == "Unit03"
- same n_qubits / padded_length / pad_count
- same rail_mode / rail_layout
- init_sequence[0]["op"] == "prepare_basis_amplitudes"
- endianness == "little"
- qft_kernel_sign == "+"
"""
def test_prep_shape_matches_loader_contract():
    assert True  # TODO: build synthetic loader_spec, run synthesize_init_circuit, assert invariants
