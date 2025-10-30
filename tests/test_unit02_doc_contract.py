"""
Unit 02 documentation contract test.

We assert the spec doc Units/Unit02.md contains all the required lock phrases.
This makes the doc itself part of the enforcement boundary.

If anyone deletes or "softens" a guarantee in Unit02.md,
this test will fail and pre-push should block the commit.
"""

import pathlib

def test_unit02_doc_contract_phrases_exist():
    unit02_path = pathlib.Path(__file__).resolve().parents[1] / "Units" / "Unit02.md"
    doc = unit02_path.read_text()

    required_phrases = [
        "LoaderSpec",
        "rail_layout",
        "endianness\": \"little\"",
        "qft_kernel_sign\": \"+\"",
        "loader_version\": \"Unit02\"",
        "build_loader_spec",
        "loader_spec_to_json",
        "validate_loader_spec",
        "deterministic",
        "same input → identical JSON",
        "len(rail_layout)",
        "semantic_hash",
    ]

    missing = [phrase for phrase in required_phrases if phrase not in doc]
    assert not missing, f"Unit02.md missing required phrases: {missing}"
