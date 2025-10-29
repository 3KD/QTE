from __future__ import annotations
import hashlib, hmac

def _hkdf_sha3(key: bytes, salt: bytes, info: bytes, out_len: int) -> bytes:
    """Tiny HKDF using SHA3-256 (good enough for our test scaffolding)."""
    if salt is None:
        salt = b"\x00"*32
    prk = hmac.new(salt, key, hashlib.sha3_256).digest()
    okm, t, counter = b"", b"", 1
    while len(okm) < out_len:
        t = hmac.new(prk, t + info + bytes([counter]), hashlib.sha3_256).digest()
        okm += t
        counter += 1
    return okm[:out_len]

def derive_subkeys(master_key: bytes, nonce: bytes) -> tuple[bytes, bytes, bytes]:
    """Derive (Kp, Kd, Kc) from master key + nonce."""
    okm = _hkdf_sha3(master_key, nonce, b"QTE|subkeys", 96)
    return okm[0:32], okm[32:64], okm[64:96]

def prf_bits(key: bytes, nonce: bytes, nbits: int, domain: bytes = b"QTE|PRF") -> bytes:
    """
    Domain-separated SHAKE-256 XOF as a PRF.
    Returns ceil(nbits/8) bytes; mask the last byte if you need exact bit count.
    """
    nbytes = (nbits + 7) // 8
    xof = hashlib.shake_256(domain + b"|" + key + b"|" + nonce)
    return xof.digest(nbytes)

def mac_bell_bits(Kc: bytes, nonce: bytes, bell_bytes: bytes, tag_len: int = 16) -> bytes:
    """HMAC(SHA3-256) over (nonce || bell_bytes), truncated to tag_len."""
    tag = hmac.new(Kc, nonce + bell_bytes, hashlib.sha3_256).digest()
    return tag[:tag_len]

def verify_mac(Kc: bytes, nonce: bytes, bell_bytes: bytes, tag: bytes, tag_len: int = 16) -> bool:
    good = mac_bell_bits(Kc, nonce, bell_bytes, tag_len=tag_len)
    if len(good) != len(tag):
        return False
    acc = 0
    for a, b in zip(good, tag):
        acc |= (a ^ b)
    return acc == 0


def prf_shake256(key: bytes, nonce: bytes, nbits: int, domain: bytes = b"QTE|PRF"):
    """Back-compat alias for SHAKE-256 XOF PRF; returns ceil(nbits/8) bytes."""
    return prf_bits(key, nonce, nbits, domain=domain)

__all__ = ['derive_subkeys','prf_bits','prf_shake256','mac_bell_bits','verify_mac']


def prf_bits(key: bytes, nonce: bytes, counter: int, t_bits: int) -> int:
    """
    Deterministic PRF -> integer in [0, 2**t_bits).
    Domain sep: b"PRFv1|"+key+"|"+nonce+"|"+counter_be (8 bytes, big-endian).
    """
    import hashlib
    if not isinstance(key, (bytes, bytearray)) or not isinstance(nonce, (bytes, bytearray)):
        raise TypeError("key and nonce must be bytes")
    if not isinstance(counter, int):
        raise TypeError("counter must be int")
    if t_bits <= 0 or t_bits > 256:
        raise ValueError("t_bits out of range (1..256)")

    ctr_be = counter.to_bytes(8, 'big', signed=False)
    xof = hashlib.shake_256(b"PRFv1|" + bytes(key) + b"|" + bytes(nonce) + b"|" + ctr_be)
    nbytes = (t_bits + 7) // 8
    raw = xof.digest(nbytes)
    val = int.from_bytes(raw, 'big') & ((1 << t_bits) - 1)
    return val

