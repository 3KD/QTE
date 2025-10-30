
import hashlib, hmac

def mac_bell_bits(Kc, nonce, bell_bits, tag_len=16):
    """KMAC-like tag using SHAKE256 over (Kc || "KMAC" || nonce || bell_bits)."""
    x = hashlib.shake_256()
    x.update(Kc); x.update(b"KMAC"); x.update(nonce); x.update(bell_bits)
    return x.digest(int(tag_len))

def verify_mac(Kc, nonce, bell_bits, tag):
    calc = mac_bell_bits(Kc, nonce, bell_bits, tag_len=len(tag))
    return hmac.compare_digest(calc, tag)
