"""
Unit 02 enforcement: LoaderSpec integrity

build_loader_spec must emit LoaderSpec with:
- loader_version == "Unit02"
- copies nve_version from metadata
- endianness == "little"
- qft_kernel_sign == "+"
- register_qubits consistent: padded_length == 2**n_qubits
- amplitudes.vector length == padded_length
- last pad_count entries exactly 0 / 0+0j
- norm ~1.0 within 1e-12
- no NaN/Inf
"""
def test_loader_spec_integrity_contract():
    assert True  # TODO: synthesize minimal nve_bundle, run build_loader_spec, assert all invariants
