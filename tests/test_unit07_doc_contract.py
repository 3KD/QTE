"""
Unit07 documentation contract test.

Goal: enforce that Units/Unit07.md actually locks down:
- atlas_version="Unit07"
- deterministic similarity matrix + coords
- reference to nve-similarity, cosine metric, symmetry tolerance 1e-12
- required provenance fields (endianness, qft_kernel_sign, psi_fingerprint, semantic_hash, manifest)

This is pure string presence. We're not doing math here. We're freezing the spec.
"""

import pathlib

def test_unit07_doc_contract_strings_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    u7_doc = (root / "Units" / "Unit07.md").read_text()

    required_bits = [
        'atlas_version": "Unit07"',
        'nve_version": "Unit01"',
        'endianness": "little"',
        'qft_kernel_sign": "+"',
        'similarity_metric": "cosine"',
        'symmetry_tolerance": 1e-12',
        "psi_fingerprint",
        "semantic_hash",
        "manifest",
        'S":',
        "atlas_similarity_matrix.json",
        "atlas_layout.json",
        'embedding_algo": "FIXED_LINEAR_MAP_V1"',
        "coords",
        'x":',
        'y":',
        "nve-similarity",
        "similarity symmetry tolerance 1e-12",
        "atlas_version",
    ]

    missing = [bit for bit in required_bits if bit not in u7_doc]
    assert not missing, f"Unit07.md missing required contract tokens: {missing}"
