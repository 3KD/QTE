# qte_metrics.py
from __future__ import annotations
import os, math, json, time
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional

import numpy as np
import matplotlib.pyplot as plt

from qiskit.quantum_info import Statevector
from quantum_embedding import generate_series_encoding
from harmonic_analysis import compute_fft_spectrum_from_amplitudes

# ---------- core metrics ----------

def amplitude_entropy(vec: np.ndarray) -> float:
    """Shannon entropy (bits) of |amp|^2."""
    p = np.abs(vec) ** 2
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))

def spectral_metrics(vec: np.ndarray, pad_len: int = 256) -> Dict[str, float | int]:
    """
    Use your existing harmonic_analysis helper for consistency.
    Returns DC fraction, spectral entropy, top-1 index and fraction.
    """
    power, freqs, mets = compute_fft_spectrum_from_amplitudes(
        vec, remove_dc=True, window="hann", pad_len=pad_len
    )
    S = float(np.sum(power)) or 1.0
    top_idx = int(freqs[int(np.argmax(power))])
    top_frac = float(np.max(power) / S)
    return {
        "spec_dc": float(mets.get("dc_frac", 0.0)),
        "spec_entropy": float(mets.get("entropy_bits", 0.0)),
        "spec_top_idx": top_idx,
        "spec_top_frac": top_frac,
    }

def safe_label_method(label: str, method: Optional[str]) -> str:
    return f"{label}[{method}]" if (method and "(" not in label) else label

# ---------- state/metrics pipeline ----------

@dataclass
class SeriesSpec:
    label: str                 # e.g. "Li(2,0.5)" or "π"
    method: Optional[str]      # e.g. "Machin" for π, else None
    mode: str                  # "EGF" | "Terms"
    phase_mode: str            # "sign" | "abs"
    n_qubits: int
    pad_len: int = 256

@dataclass
class SeriesMetrics:
    label: str
    method: Optional[str]
    mode: str
    phase_mode: str
    n_qubits: int
    dim: int
    amp_entropy: float
    spec_dc: float
    spec_entropy: float
    spec_top_idx: int
    spec_top_frac: float
    wall_ms: int

def prepare_state(spec: SeriesSpec) -> Statevector:
    sv = generate_series_encoding(
        spec.label,
        n_qubits=spec.n_qubits,
        method=spec.method,
        phase_mode=spec.phase_mode,
        amp_mode=("egf" if spec.mode == "EGF" else "terms"),
    )
    return sv

def compute_metrics(spec: SeriesSpec, sv: Statevector) -> SeriesMetrics:
    t0 = time.time()
    vec = np.asarray(sv.data, dtype=np.complex128)
    aH = amplitude_entropy(vec)
    sm = spectral_metrics(vec, pad_len=spec.pad_len)
    dt = int(round((time.time() - t0) * 1000))
    return SeriesMetrics(
        label=spec.label,
        method=spec.method,
        mode=spec.mode,
        phase_mode=spec.phase_mode,
        n_qubits=spec.n_qubits,
        dim=len(vec),
        amp_entropy=aH,
        spec_dc=float(sm["spec_dc"]),
        spec_entropy=float(sm["spec_entropy"]),
        spec_top_idx=int(sm["spec_top_idx"]),
        spec_top_frac=float(sm["spec_top_frac"]),
        wall_ms=dt,
    )

# ---------- plotting helpers (optional) ----------

def save_plots(outdir: str, base: str, sv: Statevector, pad_len: int = 256) -> None:
    os.makedirs(outdir, exist_ok=True)
    vec = np.asarray(sv.data, dtype=np.complex128)
    probs = np.abs(vec) ** 2

    # 1) amplitude spectrum
    fig1, ax1 = plt.subplots(figsize=(8, 3))
    ax1.bar(range(len(probs)), probs)
    ax1.set_title("|amp|^2")
    ax1.set_xlabel("Index")
    ax1.set_ylabel("Prob")
    fig1.tight_layout()
    fig1.savefig(os.path.join(outdir, f"{base}__amps.png"), dpi=150)
    plt.close(fig1)

    # 2) FFT power
    power, freqs, mets = compute_fft_spectrum_from_amplitudes(
        vec, remove_dc=True, window="hann", pad_len=pad_len
    )
    fig2, ax2 = plt.subplots(figsize=(8, 3))
    ax2.plot(freqs, power, marker="o")
    ax2.set_title(f"FFT (DC={mets['dc_frac']:.3f}, H={mets['entropy_bits']:.3f} bits)")
    ax2.set_xlabel("Frequency index")
    ax2.set_ylabel("Power")
    ax2.grid(True, alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(os.path.join(outdir, f"{base}__fft.png"), dpi=150)
    plt.close(fig2)

