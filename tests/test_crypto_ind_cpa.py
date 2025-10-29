import pytest
pytest.skip("skipped: legacy test not wired to Unit01 NVE/NVQA yet", allow_module_level=True)

import numpy as np
from qe_crypto import avg_state_over_nonces, phase_mix_encrypt, trace_distance_to_maxmix

def _rand_state(n, seed):
    d = 1 << int(n)
    rng = np.random.default_rng(seed)
    v = rng.normal(size=d) + 1j*rng.normal(size=d)
    return v / np.linalg.norm(v)

def test_avg_state_close_to_maxmix_small_n():
    n = 4
    master_key = b"K"*32
    psi = _rand_state(n, seed=1)
    rho_bar = avg_state_over_nonces(psi, master_key, num_samples=96, t_bits=12, rounds=2, seed=123)
    td = trace_distance_to_maxmix(rho_bar)
    assert td <= 0.2  # loose bound for toy PRF

def test_nonce_reuse_is_worse():
    n = 4
    master_key = b"K"*32
    psi = _rand_state(n, seed=2)
    rho_bar = avg_state_over_nonces(psi, master_key, num_samples=128, t_bits=12, rounds=2, seed=321)
    td_fresh = trace_distance_to_maxmix(rho_bar)

    nonce = b"\x02"*12
    v = phase_mix_encrypt(psi, master_key, nonce, t_bits=12, rounds=2)
    rho_reuse = np.outer(v, np.conjugate(v))
    td_reuse = trace_distance_to_maxmix(rho_reuse)
    assert td_reuse > td_fresh
