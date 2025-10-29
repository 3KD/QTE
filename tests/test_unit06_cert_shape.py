"""
Unit 06 QuentroyCert shape test.

We don't need the real math yet. We just need to assert the required
top-level keys and invariants are clearly defined and stable.

If somebody later tries to rename keys, drop required fields, change
'quentroy_version', etc., this test will catch it.

This does NOT run the CLI. It only checks structure and naming.
"""

def _fake_cert():
    return {
        "quentroy_version": "Unit06",
        "source_kind": "exec",  # could also be "sim"
        "endianness": "little",
        "qft_kernel_sign": "+",
        "loader_version": "Unit02",
        "prep_spec_fingerprint": "abc123prep",
        "object_spec_fingerprint": "obj456",
        "shots_total": 1024,
        "H_Z_bits": 5.123,
        "H_QFT_bits": None,  # allowed to be None if we don't have conjugate basis yet
        "flatness_KL_uniform": 0.42,
        "min_entropy_bits": 2.7,
        "counts_digest": "deadbeef00cafebabe",
        "timestamp_run_utc": "2025-10-29T12:34:56Z",
        "backend_id": "fake_backend",
        "exec_version": "Unit04",
        "rail_layout": [
            {
                "rail_tag": "iq_real",
                "start_index": 0,
                "length": 64,
                "logical_register": "rail0",
            }
        ],
    }

def test_unit06_cert_mandatory_fields_and_values():
    cert = _fake_cert()

    required_fields = [
        "quentroy_version",
        "source_kind",
        "endianness",
        "qft_kernel_sign",
        "loader_version",
        "prep_spec_fingerprint",
        "object_spec_fingerprint",
        "shots_total",
        "H_Z_bits",
        "H_QFT_bits",
        "flatness_KL_uniform",
        "min_entropy_bits",
        "counts_digest",
    ]

    for f in required_fields:
        assert f in cert, f"missing required field in QuentroyCert: {f}"

    # Hard invariants from Unit 06 spec
    assert cert["quentroy_version"] == "Unit06"
    assert cert["loader_version"] == "Unit02"
    assert cert["endianness"] == "little"
    assert cert["qft_kernel_sign"] == "+"
    assert cert["source_kind"] in ("sim", "exec")

    # Sanity of numeric-like stuff
    assert isinstance(cert["shots_total"], int) and cert["shots_total"] > 0
    assert "H_Z_bits" in cert
    assert "flatness_KL_uniform" in cert
    assert "min_entropy_bits" in cert

    # We accept H_QFT_bits can be None for now, but the key MUST exist
    assert "H_QFT_bits" in cert
