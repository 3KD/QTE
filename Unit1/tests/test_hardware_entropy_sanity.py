import json
import math
import pytest
import os

def shannon_entropy_bits(prob_dict):
    total = 0.0
    for p in prob_dict.values():
        if p > 0:
            total += -p * math.log2(p)
    return total

def test_uniform_superposition_entropy_not_low():
    path = "Unit1/hardware/uniform4_counts.json"
    if not os.path.exists(path):
        pytest.skip("uniform4_counts.json not found yet; run hardware experiment first")

    with open(path) as f:
        obj = json.load(f)

    assert "probabilities" in obj
    assert obj.get("n_qubits", None) == 4

    H_est = shannon_entropy_bits(obj["probabilities"])
    # On 4 qubits, perfect is 4 bits.
    # We only demand >=3.0 so it's not catastrophically collapsed.
    assert H_est >= 3.0, f"entropy {H_est} too low; hardware run suspect"
