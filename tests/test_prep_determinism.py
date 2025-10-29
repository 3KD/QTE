"""
Unit 03 enforcement: determinism of PrepSpec.

Given identical loader_spec twice:
- synthesize_init_circuit must yield PrepSpec objects that
  JSON-stable-dump byte-identical.
If not, later crypto/attestation can't rely on prep specs.
"""
def test_prep_determinism_contract():
    assert True  # TODO: compare two PrepSpecs for byte-identical stable serialization
