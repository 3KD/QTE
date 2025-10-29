"""
qe_crypto shim for pre-push pytest.

Real crypto logic (phase_mix_encrypt, derive_subkeys, avg_state_over_nonces,
trace_distance_to_maxmix, etc.) will live in later units
(IND-CPA witness, QDR rails, etc.).

Right now we only provide stubs so imports in legacy tests don't crash.
All stubs raise NotImplementedError at runtime so we never get silent lies.
"""

def avg_state_over_nonces(*args, **kwargs):
    raise NotImplementedError("stub avg_state_over_nonces (Unit11/15 real)")

def phase_mix_encrypt(*args, **kwargs):
    raise NotImplementedError("stub phase_mix_encrypt (Unit11/25 real)")

def trace_distance_to_maxmix(*args, **kwargs):
    raise NotImplementedError("stub trace_distance_to_maxmix (Unit15 real)")

def derive_subkeys(*args, **kwargs):
    raise NotImplementedError("stub derive_subkeys (Unit25 real)")
