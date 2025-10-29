"""
Unit 01 enforcement: phase-mode distinction

Same ObjectSpec, but:
  phase_mode=full_complex
vs
  phase_mode=magnitude_only

Both MUST:
- normalize
- publish proper metadata
BUT MUST NOT:
- produce byte-identical ψ

If they collapse to the same ψ, we lost phase/sign information,
which kills our ability to attest encoded sign structure later.
"""
def test_phase_mode_distinct_vectors():
    assert True  # TODO: build both modes, assert not array_equal
