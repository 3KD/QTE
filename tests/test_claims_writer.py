def test_claims_writer_generates_file(tmp_path):
    from tools import write_claims
    out = tmp_path / "claims.md"
    meta = write_claims.write(path=str(out), eps="2^-10", fmin_chip="0.98", fmin_metro="0.90")
    assert out.exists()
    s = out.read_text(encoding="utf-8")
    assert "metrics.version" in s
    assert meta["epsilon_target"] == "2^-10"
