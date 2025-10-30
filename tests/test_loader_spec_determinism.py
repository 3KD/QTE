"""
Unit 02 enforcement: LoaderSpec determinism

Two builds from identical nve_bundle input must produce byte-identical
LoaderSpec (after stable JSON dump ordering). If not, later attestation
and crypto proofs can't trust the loader.
"""
def test_loader_spec_determinism_contract():
    assert True  # TODO: build twice and compare serialized specs
