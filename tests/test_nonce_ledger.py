def test_nonce_ledger_enforces_uniqueness(tmp_path):
    from tools.nonce_ledger import NonceLedger
    f = tmp_path / "nonces.json"
    L = NonceLedger(f)
    assert L.record("abc123") is True
    assert L.record("abc123") is False
    assert L.has("abc123") is True
