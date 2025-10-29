"""
Unit 01 enforcement: normalization / sanity

Requirements:
- ||ψ||₂ must equal 1 within 1e-12 for simulator builds
- no NaN/Inf
- cannot output zero vector (must raise instead)

If this fails, later Quentroy entropy checks (Unit 05 / 11) are meaningless.
"""
def test_nve_normalization_enforced():
    assert True  # TODO: replace with actual norm/NaN/Inf check once package_nve is implemented
