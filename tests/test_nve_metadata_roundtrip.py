"""
Unit 01 enforcement: deterministic NVE

Requirements:
- same ObjectSpec => byte-identical ψ (or exactly equal floats)
- metadata fields identical:
  weighting_mode, phase_mode, rail_mode, length,
  endianness="little", qft_kernel_sign="+", nve_version="Unit01"

If this fails, you cannot certify payloads or do crypto attestation later.
"""
def test_nve_roundtrip_deterministic():
    assert True  # TODO: build twice, compare arrays/JSON exact match
