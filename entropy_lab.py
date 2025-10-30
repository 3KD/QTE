import numpy as np

def _norm(psi: np.ndarray) -> np.ndarray:
    psi = np.asarray(psi, dtype=complex).reshape(-1)
    n = np.linalg.norm(psi)
    if n == 0: raise ValueError("zero vector")
    return psi / n

def qft_unitary(d: int) -> np.ndarray:
    k = np.arange(d).reshape(-1,1)
    l = np.arange(d).reshape(1,-1)
    omega = np.exp(2j*np.pi*k*l/d)
    return omega / np.sqrt(d)

def measure_distribution(psi: np.ndarray, basis: str = "Z") -> np.ndarray:
    """Return measurement distribution in basis 'Z' (computational) or 'QFT' (Fourier)."""
    psi = _norm(psi)
    d = psi.size
    if basis.upper() == "Z":
        amp = psi
    elif basis.upper() in ("X","QFT","FOURIER"):
        F = qft_unitary(d)
        amp = F @ psi
    else:
        raise ValueError("basis must be 'Z' or 'QFT'")
    p = np.abs(amp)**2
    return p / (p.sum() if p.sum()!=0 else 1.0)

def shannon_entropy_bits(p: np.ndarray) -> float:
    p = np.asarray(p, dtype=float)
    p = p[(p>0)]
    return float(-np.sum(p*np.log2(p))) if p.size else 0.0

def entropies_Z_X(psi: np.ndarray) -> tuple[float,float]:
    pZ = measure_distribution(psi, "Z")
    pX = measure_distribution(psi, "QFT")
    return shannon_entropy_bits(pZ), shannon_entropy_bits(pX)

def von_neumann_entropy_bits(rho: np.ndarray) -> float:
    """S(ρ) = -Tr ρ log2 ρ for a density matrix ρ."""
    w = np.linalg.eigvalsh((rho + rho.conj().T)/2.0).real
    w = w[(w>0)]
    return float(-np.sum(w*np.log2(w))) if w.size else 0.0

def ensemble_entropy(states: list[np.ndarray]) -> float:
    """Given pure states |ψ_i>, return S( (1/N) Σ |ψ_i><ψ_i| )."""
    if not states: return 0.0
    d = states[0].size
    rho = np.zeros((d,d), dtype=complex)
    for s in states:
        s = _norm(s)
        rho += np.outer(s, s.conj())
    rho /= len(states)
    return von_neumann_entropy_bits(rho)
# --- entropy helpers (safe to append) ------------------------------------------
from typing import Dict, Sequence
import numpy as np

def _shannon_bits(p_like) -> float:
    """Shannon entropy H(X) in bits for a probability vector."""
    p = np.asarray(p_like, dtype=float)
    if p.size == 0:
        return 0.0
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))

def entropy_certificate_from_amplitudes(a) -> Dict[str, float]:
    """Deterministic 'certificate' from amplitudes alone (no noise assumptions).
    Returns: {"H_Z_bits", "H_QFT_bits", "flatness"}.
    - H_Z_bits: Shannon entropy of Z-basis probabilities
    - H_QFT_bits: Shannon entropy of all-qubit QFT probabilities
    - flatness: spectral flatness (geometric mean / arithmetic mean) of |FFT(a)|^2
    """
    a = np.asarray(a, dtype=complex).reshape(-1)
    nrm = float(np.linalg.norm(a))
    a = a / (nrm if nrm != 0.0 else 1.0)

    # Z basis and QFT basis entropies
    pZ = np.abs(a) ** 2
    HZ = _shannon_bits(pZ)

    F = np.fft.fft(a) / np.sqrt(a.size)  # unitary-normalized FFT
    pX = np.abs(F) ** 2
    HX = _shannon_bits(pX)

    # Spectral flatness of raw two-sided power spectrum |FFT(a)|^2
    P = np.abs(np.fft.fft(a)) ** 2
    S = float(P.sum()) or 1.0
    Pn = P / S
    gm = float(np.exp(np.mean(np.log(Pn + 1e-15))))
    am = float(np.mean(Pn))
    flatness = gm / (am if am != 0.0 else 1.0)

    return {"H_Z_bits": HZ, "H_QFT_bits": HX, "flatness": flatness}

def ensemble_von_neumann_entropy(weights: Sequence[float], statevecs: Sequence[Sequence[complex]]) -> float:
    """Von Neumann entropy S(ρ) of an ensemble ρ = Σ w_k |ψ_k⟩⟨ψ_k|.
    `weights`: non-negative, will be normalized
    `statevecs`: list of same-dimension complex vectors
    """
    p = np.asarray(weights, dtype=float).reshape(-1)
    if p.size == 0 or len(statevecs) == 0:
        return 0.0
    p = p / (float(p.sum()) or 1.0)

    vecs = [np.asarray(v, dtype=complex).reshape(-1) for v in statevecs]
    d = vecs[0].size
    if any(v.size != d for v in vecs):
        raise ValueError("All state vectors in the ensemble must have equal length")

    rho = np.zeros((d, d), dtype=complex)
    for w, v in zip(p, vecs):
        nrm = float(np.linalg.norm(v))
        v = v / (nrm if nrm != 0.0 else 1.0)
        rho += w * np.outer(v, v.conj())

    # Hermitize numerically and compute eigenvalues
    rho = (rho + rho.conj().T) / 2.0
    ev = np.linalg.eigvalsh(rho).real
    ev = ev[ev > 0]
    return float(-np.sum(ev * np.log2(ev))) if ev.size else 0.0
# --- end append ----------------------------------------------------------------------
# --- entropy helpers (safe to append) ------------------------------------------
from typing import Dict, Sequence
import numpy as np

def _shannon_bits(p_like) -> float:
    """Shannon entropy H(X) in bits for a probability vector."""
    p = np.asarray(p_like, dtype=float)
    if p.size == 0:
        return 0.0
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))

def entropy_certificate_from_amplitudes(a) -> Dict[str, float]:
    """Deterministic 'certificate' from amplitudes alone (no noise assumptions).
    Returns: {"H_Z_bits", "H_QFT_bits", "flatness"}.
    - H_Z_bits: Shannon entropy of Z-basis probabilities
    - H_QFT_bits: Shannon entropy of all-qubit QFT probabilities
    - flatness: spectral flatness (geometric mean / arithmetic mean) of |FFT(a)|^2
    """
    a = np.asarray(a, dtype=complex).reshape(-1)
    nrm = float(np.linalg.norm(a))
    a = a / (nrm if nrm != 0.0 else 1.0)

    # Z basis and QFT basis entropies
    pZ = np.abs(a) ** 2
    HZ = _shannon_bits(pZ)

    F = np.fft.fft(a) / np.sqrt(a.size)  # unitary-normalized FFT
    pX = np.abs(F) ** 2
    HX = _shannon_bits(pX)

    # Spectral flatness of raw two-sided power spectrum |FFT(a)|^2
    P = np.abs(np.fft.fft(a)) ** 2
    S = float(P.sum()) or 1.0
    Pn = P / S
    gm = float(np.exp(np.mean(np.log(Pn + 1e-15))))
    am = float(np.mean(Pn))
    flatness = gm / (am if am != 0.0 else 1.0)

    return {"H_Z_bits": HZ, "H_QFT_bits": HX, "flatness": flatness}

def ensemble_von_neumann_entropy(weights: Sequence[float], statevecs: Sequence[Sequence[complex]]) -> float:
    """Von Neumann entropy S(ρ) of an ensemble ρ = Σ w_k |ψ_k⟩⟨ψ_k|.
    `weights`: non-negative, will be normalized
    `statevecs`: list of same-dimension complex vectors
    """
    p = np.asarray(weights, dtype=float).reshape(-1)
    if p.size == 0 or len(statevecs) == 0:
        return 0.0
    p = p / (float(p.sum()) or 1.0)

    vecs = [np.asarray(v, dtype=complex).reshape(-1) for v in statevecs]
    d = vecs[0].size
    if any(v.size != d for v in vecs):
        raise ValueError("All state vectors in the ensemble must have equal length")

    rho = np.zeros((d, d), dtype=complex)
    for w, v in zip(p, vecs):
        nrm = float(np.linalg.norm(v))
        v = v / (nrm if nrm != 0.0 else 1.0)
        rho += w * np.outer(v, v.conj())

    # Hermitize numerically and compute eigenvalues
    rho = (rho + rho.conj().T) / 2.0
    ev = np.linalg.eigvalsh(rho).real
    ev = ev[ev > 0]
    return float(-np.sum(ev * np.log2(ev))) if ev.size else 0.0
# --- end append ----------------------------------------------------------------------



# === QTE: entropy helpers & robust certificates (append-only) ===
def _shannon_bits(p_like):
    import numpy as np
    p = np.asarray(p_like, dtype=float)
    if p.size == 0:
        return 0.0
    p = p[p > 0]
    H = -np.sum(p * np.log2(p)) if p.size else 0.0
    return float(max(H, 0.0))  # clamp tiny negatives

def _min_entropy_bits(p_like):
    """H_∞(X) = -log2 max_x p(x)."""
    import numpy as np
    p = np.asarray(p_like, dtype=float)
    m = float(np.max(p)) if p.size else 1.0
    return float(-np.log2(m if m > 0.0 else 1.0))

def entropy_certificate_from_amplitudes(a):
    import numpy as np
    a = np.asarray(a, dtype=complex).reshape(-1)
    nrm = float(np.linalg.norm(a))
    a = a / (nrm if nrm != 0.0 else 1.0)

    # Z basis
    pZ  = np.abs(a)**2
    HZ  = _shannon_bits(pZ)
    HZinf = _min_entropy_bits(pZ)

    # QFT/"momentum" basis (unitary, normalized)
    F   = np.fft.fft(a) / np.sqrt(a.size)
    pQ  = np.abs(F)**2
    HQ  = _shannon_bits(pQ)
    HQinf = _min_entropy_bits(pQ)

    # spectral flatness on two-sided FFT power (normalized)
    P = np.abs(np.fft.fft(a))**2
    S = float(P.sum()) or 1.0
    Pn = P / S
    gm = float(np.exp(np.mean(np.log(Pn + 1e-15))))
    am = float(np.mean(Pn))
    flat = gm / (am if am != 0.0 else 1.0)

    return {
        "H_Z_bits": HZ, "Hmin_Z_bits": HZinf,
        "H_QFT_bits": HQ, "Hmin_QFT_bits": HQinf,
        "flatness": flat,
    }

def ensemble_von_neumann_entropy(probabilities, statevecs):
    import numpy as np
    p = np.asarray(probabilities, dtype=float).reshape(-1)
    p = p / (float(p.sum()) or 1.0)
    vecs = [np.asarray(v, dtype=complex).reshape(-1) for v in statevecs]
    d = vecs[0].size if vecs else 0
    if d == 0:
        return 0.0
    if any(v.size != d for v in vecs):
        raise ValueError("All state vectors in the ensemble must have equal length")

    rho = np.zeros((d, d), dtype=complex)
    for w, v in zip(p, vecs):
        nrm = float(np.linalg.norm(v))
        v = v / (nrm if nrm != 0.0 else 1.0)
        rho += w * np.outer(v, v.conj())

    # Hermitize & guard eigenspectrum
    rho = (rho + rho.conj().T) / 2.0
    ev = np.linalg.eigvalsh(rho).real
    ev = np.clip(ev, 0.0, 1.0)
    ev = ev[ev > 0]
    H = float(-np.sum(ev * np.log2(ev))) if ev.size else 0.0
    return max(H, 0.0)



# === QTE: certificate pack/verify + count-based estimators (append-only) ===
def _shannon_bits_from_counts(counts, n_shots=None):
    """counts: dict[str|int]->int or array-like; returns H2 in bits."""
    import numpy as np
    if isinstance(counts, dict):
        n = float(sum(int(v) for v in counts.values())) or 1.0
        p = np.array([v/n for v in counts.values()], dtype=float)
    else:
        arr = np.asarray(counts, dtype=float).reshape(-1)
        n = float(arr.sum()) or 1.0
        p = arr / n
    p = p[p > 0]
    return float(-np.sum(p*np.log2(p))) if p.size else 0.0

def entropy_certificate_pack(a):
    """
    Deterministic certificate computed from amplitudes (dimension-agnostic).
    Returns a dict you can serialize and send alongside the quantum message.
    """
    import numpy as np
    from entropy_lab import entropy_certificate_from_amplitudes
    a = np.asarray(a, dtype=complex).reshape(-1)
    d = a.size
    cert = entropy_certificate_from_amplitudes(a)
    cert.update({
        "d": int(d),
        "basis_pair": "Z/QFT",
        "version": 1,
    })
    return cert

def entropy_certificate_verify(a, cert, *, atol_bits=0.05):
    """
    Recompute certificate on receiver side and compare within tolerance (bits).
    Returns (ok, details_dict_with_deltas).
    """
    import numpy as np
    from entropy_lab import entropy_certificate_from_amplitudes
    a = np.asarray(a, dtype=complex).reshape(-1)
    got = entropy_certificate_from_amplitudes(a)
    deltas = {}
    keys = ["H_Z_bits","Hmin_Z_bits","H_QFT_bits","Hmin_QFT_bits","flatness"]
    ok = True
    for k in keys:
        if k in cert and k in got:
            dv = float(got[k] - cert[k])
            deltas[k] = dv
            if k.startswith("H") and abs(dv) > float(atol_bits):
                ok = False
    # dimension sanity
    if int(cert.get("d", a.size)) != int(a.size):
        ok = False
        deltas["d_mismatch"] = (int(cert.get("d")), int(a.size))
    return ok, {"recomputed": got, "deltas": deltas}
