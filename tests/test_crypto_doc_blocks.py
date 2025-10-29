from pathlib import Path

def test_crypto_doc_blocks_present():
    p = Path("docs") / "QE_STANDALONE_TELEPORTATION.md"
    s = p.read_text(encoding="utf-8")
    for tag in (
        "ABSTRACT_FROZEN","SECURITY_SCOPE","CONSTRUCTION_SPEC","PROOF_SKELETON",
        "METRICS_AND_OPS","EXPERIMENT_PLAN","SIDE_CHANNELS","POSITIONING",
        "QUDITS_ADDENDUM","REFERENCES","LAST_MILE_BUNDLE","COMPLIANCE_GAPS"
    ):
        assert f"BEGIN: {tag}" in s and f"END: {tag}" in s
