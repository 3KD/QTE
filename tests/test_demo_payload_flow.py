import os, sys, numpy as np
sys.path.insert(0, os.getcwd())
from tools.demo_payload_flow import int_to_basis_amplitudes, scramble_amplitudes, unscramble_amplitudes
from entropy_lab import entropy_certificate_pack, entropy_certificate_verify
def test_round_trip_cert_ok():
    n=6; d=1<<n; v=13
    a=int_to_basis_amplitudes(n,v)
    cert=entropy_certificate_pack(a)
    a_scr, params = scramble_amplitudes(a, b"key")
    a_back = unscramble_amplitudes(a_scr, params)
    ok, info = entropy_certificate_verify(a_back, cert, atol_bits=1e-9)
    assert ok, info
