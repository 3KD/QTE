"""
Unit 02 enforcement: register shape + padding

resolve_register_shape must:
- choose n_qubits = ceil(log2(L))
- pad psi with exact zeros to length 2**n_qubits
- report pad_count
- preserve norm ~1.0 within 1e-12
- refuse NaN/Inf
"""
def test_loader_shape_padding_contract():
    assert True  # TODO: create fake ψ length 3, assert padded_length=4, etc.
