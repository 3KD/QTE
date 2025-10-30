import numpy as np
from entropy_lab import (
    entropy_certificate_from_amplitudes,
    ensemble_von_neumann_entropy,
    entropy_certificate_pack,
    entropy_certificate_verify,
    _shannon_bits_from_counts,
)

def test_bell_certificate_and_verify():
    psi = np.array([1,0,0,1], complex)/np.sqrt(2)  # Bell (2 qubits)
    cert = entropy_certificate_from_amplitudes(psi)
    assert abs(cert["H_Z_bits"] - 1.0) < 1e-12
    ok, info = entropy_certificate_verify(psi, entropy_certificate_pack(psi), atol_bits=1e-6)
    assert ok, info

def test_maassen_uffink_bound_z_qft():
    # For Z vs QFT in dimension d, c = max |<i|F|j>| = 1/sqrt(d)
    # MU bound: H(Z)+H(F) >= log2(d)
    for d in [2,4,8]:
        # delta basis vector |0>
        a = np.zeros(d, complex); a[0] = 1.0
        cert = entropy_certificate_from_amplitudes(a)
        assert cert["H_Z_bits"] < 1e-12
        assert cert["H_QFT_bits"] + cert["H_Z_bits"] >= np.log2(d) - 1e-12

def test_ensemble_entropy_pure_and_mixed():
    psi = np.array([1,0,0,1], complex)/np.sqrt(2)
    S_pure = ensemble_von_neumann_entropy([1.0],[psi])
    assert abs(S_pure) < 1e-12
    e1 = np.array([1,0,0,0], complex)
    e4 = np.array([0,0,0,1], complex)
    S_mix = ensemble_von_neumann_entropy([0.5,0.5], [e1,e4])
    assert abs(S_mix - 1.0) < 1e-12

def test_counts_shannon_matches_exact_for_uniform4():
    # uniform over 4 outcomes: H=2 bits
    counts = {"00": 250, "01": 250, "10": 250, "11": 250}
    H = _shannon_bits_from_counts(counts)
    assert abs(H - 2.0) < 1e-9
