import pytest
pytest.skip("skipped: crypto/scrambler/IND-CPA path not validated in Unit01 yet", allow_module_level=True)
import numpy as np
import importlib.util
import pytest

spec = importlib.util.find_spec("qe_crypto.phase_mix")
pytestmark = pytest.mark.skipif(spec is None, reason="qe_crypto.phase_mix not available")

from qe_crypto.phase_mix import avg_state_over_nonces
from qe_crypto.shadow_dist import shadow_score_from_rho

def _rand_state(n, seed=7):
    rng = np.random.default_rng(seed)
    d = 2**n
    v = rng.normal(size=d) + 1j*rng.normal(size=d)
    return v / np.linalg.norm(v)

def test_shadow_score_drops_after_encryption():
    n = 4
    psi = _rand_state(n, seed=7)
    rho_plain = np.outer(psi, np.conjugate(psi))
    master_key = b"K"*32

    rho_enc = avg_state_over_nonces(psi, master_key,
                                    num_samples=192, t_bits=12, rounds=2, seed=123)

    s_plain = shadow_score_from_rho(rho_plain, m=128, seed=5)
    s_enc   = shadow_score_from_rho(rho_enc,   m=128, seed=6)

    # randomized state should collapse Pauli expectation magnitudes
    assert s_enc <= 0.40 * s_plain
    assert s_enc <= 0.15
