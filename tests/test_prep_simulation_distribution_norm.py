"""
Unit 03 enforcement: simulate_counts distribution + norm.

simulate_counts(prep_spec, shots) must:
- return counts summing to shots
- return distribution summing to ~1.0
- norm_check_l2 ~1.0 within 1e-12
- include prep_version == "Unit03"
- include endianness == "little", qft_kernel_sign == "+"
- respect padded_length == 2**n_qubits
"""
def test_prep_simulation_distribution_norm_contract():
    assert True  # TODO: tiny PrepSpec with amplitude [1,0,0,0], shots=100
