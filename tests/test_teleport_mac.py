
from qe_crypto import derive_subkeys
from qe_crypto import mac_bell_bits, verify_mac

def test_mac_over_bell_bits_roundtrip():
    master_key = b"K"*32
    nonce = b"N"*12
    _, _, Kc = derive_subkeys(master_key, nonce)
    bell_bits = b"\x01\x00\x01\x01"  # pretend 8 bits packed into bytes
    tag = mac_bell_bits(Kc, nonce, bell_bits, tag_len=16)
    assert verify_mac(Kc, nonce, bell_bits, tag)
    assert not verify_mac(Kc, nonce, bell_bits+b"\x00", tag)
