import numpy as np
from series_encoding import (
    get_series_amplitudes, qte_extras_encode, qte_extras_metrics,
    encode_srd_iq, decode_srd_iq, build_sbrv, reconstruct_sbrv
)

# J0 terms working & real
d = 16
v = np.asarray(get_series_amplitudes("J0", d, amp_mode="terms", normalize=False))
print("J0 len:", len(v), "dtype:", v.dtype, "first8:", v.real[:8].tolist())

# SRD/IQ round-trip (norm-invariant)
a = np.linspace(-1, 1, 32)
c = encode_srd_iq(a)
art = decode_srd_iq(c.real, c.imag)
print("SRD/IQ ok:", np.allclose(a/np.linalg.norm(a), art/np.linalg.norm(art), atol=1e-6))

# SBRV improves with level
a0, stack, _ = build_sbrv(a, L=3)
a1 = reconstruct_sbrv(a0, stack, 1)
a3 = reconstruct_sbrv(a0, stack, 3)
print("SBRV improves:", np.linalg.norm(a3-a) <= np.linalg.norm(a1-a))

# Holistic encode + metrics
nq = 5
coeffs = get_series_amplitudes("J0", 2**nq, amp_mode="terms", normalize=False).real
res = qte_extras_encode(coeffs, n_qubits=nq, srd_mode="iq", sbrv_levels=2)
m = qte_extras_metrics(res["state"], n_qubits=nq, cut=2)
print("metrics keys:", sorted(m.keys()))

