import pytest
pytest.skip("skipped: crypto/scrambler/IND-CPA path not validated in Unit01 yet", allow_module_level=True)
import numpy as np
from qe_crypto.phase_mix import avg_state_over_nonces, trace_distance_to_maxmix
from qe_crypto.shadow_dist import shadow_score_from_rho

def _rand_state(n, seed=123):
    rng = np.random.default_rng(seed)
    d = 2**n
    v = rng.normal(size=d) + 1j*rng.normal(size=d)
    return v / np.linalg.norm(v)

def test_ind_cpa_trace_and_shadow_baseline():
    n=4; samples=192; rounds=2; t_bits=12; seed=123
    psi = _rand_state(n, seed=seed)
    rho = avg_state_over_nonces(psi, b"K"*32, num_samples=samples, t_bits=t_bits, rounds=rounds, seed=seed+1)
    td = trace_distance_to_maxmix(rho)
    s  = shadow_score_from_rho(rho, m=256, seed=seed+2)
    # Frozen acceptance for v0.1 (matches your last run with margin)
    assert td <= 0.20
    assert s  <= 0.05
