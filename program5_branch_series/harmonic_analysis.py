# harmonic_analysis.py
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, Sequence, Optional

# ------------- Core FFT tools -------------

def power_spectrum(x: Sequence[complex]) -> Tuple[np.ndarray, np.ndarray]:
    x = np.asarray(x, dtype=complex)
    X = np.fft.fft(x)
    P = np.abs(X) ** 2
    freqs = np.fft.fftfreq(len(x))
    return P, freqs

def spectral_entropy(power: np.ndarray) -> float:
    p = power / (power.sum() if power.sum() != 0 else 1.0)
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))

def spectrum_metrics(power: np.ndarray) -> Dict[str, float]:
    P = power
    S = P.sum()
    if S == 0:
        return {"dc_frac": 0.0, "entropy_bits": 0.0, "centroid": 0.0, "peak_idx": 0.0, "peak_power": 0.0}
    dc = float(P[0] / S)
    H = spectral_entropy(P)
    idx = np.arange(len(P))
    centroid = float((idx * P).sum() / S)
    peak_idx = int(np.argmax(P))
    peak_power = float(P[peak_idx] / S)
    return {"dc_frac": dc, "entropy_bits": H, "centroid": centroid, "peak_idx": peak_idx, "peak_power": peak_power}

def kl_divergence(p: np.ndarray, q: np.ndarray, eps: float = 1e-12) -> float:
    P = p / (p.sum() + eps)
    Q = q / (q.sum() + eps)
    P = np.clip(P, eps, 1.0)
    Q = np.clip(Q, eps, 1.0)
    return float(np.sum(P * np.log2(P / Q)))

# ------------- Preprocessing -------------

def _hann_window(n: int) -> np.ndarray:
    if n <= 1:
        return np.ones(n)
    return np.hanning(n)

def preprocess_amplitudes(
    amplitudes: Sequence[complex],
    *,
    remove_dc: bool = True,
    window: str = "hann",
    pad_len: Optional[int] = 128,
    use_magnitude_if_complex: bool = True,
) -> np.ndarray:
    x = np.asarray(amplitudes, dtype=complex)
    xr = x.real if (np.allclose(x.imag, 0.0) or not use_magnitude_if_complex) else np.abs(x)

    if remove_dc:
        xr = xr - np.mean(xr)

    if window == "hann":
        xr = xr * _hann_window(len(xr))

    if pad_len and pad_len > len(xr):
        xr = np.pad(xr, (0, pad_len - len(xr)), mode="constant")

    # L2 normalize so it can be used for state prep if needed
    nrm = np.linalg.norm(xr)
    if nrm != 0:
        xr = xr / nrm
    return xr.astype(complex)

# ------------- One-stop spectrum -------------

def compute_fft_spectrum_from_amplitudes(
    amplitudes: Sequence[complex],
    *,
    remove_dc: bool = True,
    window: str = "hann",
    pad_len: int = 128,
) -> Tuple[np.ndarray, np.ndarray, Dict[str, float]]:
    proc = preprocess_amplitudes(amplitudes, remove_dc=remove_dc, window=window, pad_len=pad_len)
    power, freqs = power_spectrum(proc)
    mets = spectrum_metrics(power)
    return power, freqs, mets

# ------------- Plotting -------------

def plot_spectrum(power: np.ndarray, freqs: np.ndarray, title: str = "Spectrum"):
    plt.figure(figsize=(10, 4))
    plt.plot(freqs, power, marker="o")
    plt.title(title)
    plt.xlabel("Frequency Index")
    plt.ylabel("Power")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# === QTE override (amplitude-FFT) ===
def compute_fft_spectrum_from_amplitudes(amps, *, remove_dc=False, window=None, pad_len=None):
    import numpy as _np
    x = _np.asarray(amps, dtype=_np.complex128).reshape(-1)
    N = x.size
    if N == 0:
        return _np.zeros(0), _np.zeros(0), {'len': 0, 'dc_frac': 0.0, 'entropy_bits': 0.0}

    if remove_dc:
        x = x - _np.mean(x)
    if window == "hann":
        x = x * _np.hanning(N)

    M = int(pad_len) if (pad_len and int(pad_len) > 0) else N
    X = _np.fft.fft(x, n=M)
    P = _np.abs(X)**2
    S = float(P.sum()) if P.size else 1.0
    dc = float(P[0]/S) if S > 0 else 0.0
    p = P/S if S > 0 else P
    p = p[p > 0]
    H = float(-_np.sum(p * _np.log2(p))) if p.size else 0.0
    return P, _np.arange(M), {'len': N, 'dc_frac': dc, 'entropy_bits': H}
