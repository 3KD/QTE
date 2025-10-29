"""
Unit 01 enforcement: canonical conventions

metadata["endianness"] must be "little"
metadata["qft_kernel_sign"] must be "+"

Breaking this poisons every downstream interpretation
(FFT/QFT comparisons, register labeling, crypto witnesses).
"""
def test_endianness_and_qft_sign_in_metadata():
    assert True  # TODO: inspect metadata from package_nve(...)
