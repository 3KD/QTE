# QTEGUI — minimal wrapper hosting QTEGUI_Lite tabs
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

# --- Tomography availability flag (safe) ---
try:
    from qiskit_experiments.library import StateTomography  # optional
except Exception:
    StateTomography = None
TOMO_OK = (StateTomography is not None)


# Transitional: pull tabs from QTEGUI_Lite if available
try:
    from QTEGUI_Lite import EntropyTab, SpectrumTab, PayloadTab
except Exception:
    EntropyTab = SpectrumTab = PayloadTab = None

class QTEGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quantum Transcendental Encoder (QTE)")
        self.geometry("1100x800")
        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True, padx=10, pady=10)
        # add tabs when present
        try:
            if EntropyTab is not None:
                nb.add(EntropyTab(nb), text="Entropy")
            if SpectrumTab is not None:
                nb.add(SpectrumTab(nb), text="Spectrum")
            if PayloadTab is not None:
                nb.add(PayloadTab(nb), text="Payload")
        except Exception as e:
            print("[WARN] Could not add Lite tabs:", e)

if __name__ == "__main__":
    app = QTEGUI()
    app.mainloop()


def _fft_from_gui(amplitudes, **kw):
    """GUI-safe wrapper around harmonic_analysis.compute_fft_spectrum_from_amplitudes.
    Returns a dict with keys: freq, X, P, dc, entropy_bits, entropy, flatness.
    """
    import numpy as _np
    try:
        _ha = harmonic_analysis
    except NameError:
        _ha = None
    if _ha is None:
        raise RuntimeError("harmonic_analysis not available")

    out = _ha.compute_fft_spectrum_from_amplitudes(amplitudes, **kw)

    if isinstance(out, dict):  # new-style API
        return {
            "freq": out.get("freq"),
            "X": out.get("X"),
            "P": out.get("P"),
            "dc": out.get("dc") if out.get("dc") is not None else (
                  float(out.get("P", [0])[0] / (float(_np.sum(out.get("P", [0]))) or 1.0)) if out.get("P") is not None else None),
            "entropy_bits": out.get("entropy_bits"),
            "entropy": out.get("entropy"),
            "flatness": out.get("flatness"),
        }

    if isinstance(out, tuple):  # backward-compat: (P,freqs,meta) or (P,freqs)
        if len(out) == 3:
            P, freqs, meta = out
            S = float(_np.sum(P)) or 1.0
            dc = meta.get("dc_frac", meta.get("dc", float(P[0] / S)))
            return {
                "freq": freqs, "X": None, "P": P,
                "dc": dc,
                "entropy_bits": meta.get("entropy_bits"),
                "entropy": meta.get("entropy"),
                "flatness": meta.get("flatness"),
            }
        if len(out) == 2:
            P, freqs = out
            S = float(_np.sum(P)) or 1.0
            return {
                "freq": freqs, "X": None, "P": P,
                "dc": float(P[0] / S),
                "entropy_bits": None, "entropy": None, "flatness": None,
            }

    raise TypeError("Unexpected FFT output from harmonic_analysis")



def _fft_from_gui(amplitudes, **kw):
    """GUI-safe wrapper around harmonic_analysis.compute_fft_spectrum_from_amplitudes.
    Returns a dict with keys: freq, X, P, dc, entropy_bits, entropy, flatness.
    # [_fft_from_gui] lazy import fallback
    """
    import numpy as _np
    # try the module-level optional import first
    try:
        _ha = harmonic_analysis
    except NameError:
        _ha = None
    # lazily import if absent (test env may have the module even if optional import was skipped)
    if _ha is None:
        try:
            import importlib as _imp
            _ha = _imp.import_module("harmonic_analysis")
        except Exception:
            _ha = None
    if _ha is None:
        raise RuntimeError("harmonic_analysis not available")

    out = _ha.compute_fft_spectrum_from_amplitudes(amplitudes, **kw)

    if isinstance(out, dict):  # new-style API
        P = out.get("P")
        if out.get("dc") is None and P is not None:
            S = float(_np.sum(P)) or 1.0
            dc = float(P[0] / S)
        else:
            dc = out.get("dc")
        return {
            "freq": out.get("freq"),
            "X": out.get("X"),
            "P": P,
            "dc": dc,
            "entropy_bits": out.get("entropy_bits"),
            "entropy": out.get("entropy"),
            "flatness": out.get("flatness"),
        }

    if isinstance(out, tuple):  # backward compat: (P,freqs,meta) or (P,freqs)
        if len(out) == 3:
            P, freqs, meta = out
            S = float(_np.sum(P)) or 1.0
            dc = meta.get("dc_frac", meta.get("dc", float(P[0] / S)))
            return {
                "freq": freqs, "X": None, "P": P,
                "dc": dc,
                "entropy_bits": meta.get("entropy_bits"),
                "entropy": meta.get("entropy"),
                "flatness": meta.get("flatness"),
            }
        if len(out) == 2:
            P, freqs = out
            S = float(_np.sum(P)) or 1.0
            return {
                "freq": freqs, "X": None, "P": P,
                "dc": float(P[0] / S),
                "entropy_bits": None, "entropy": None, "flatness": None,
            }

    raise TypeError("Unexpected FFT output from harmonic_analysis")


def _fft_from_gui(amplitudes, **kw):
    """GUI-safe wrapper around harmonic_analysis.compute_fft_spectrum_from_amplitudes.
    Returns a dict with keys: freq, X, P, dc, entropy_bits, entropy, flatness.
    """
    import numpy as _np, inspect as _ins
    # resolve module
    try:
        _ha = harmonic_analysis
    except NameError:
        _ha = None
    if _ha is None:
        try:
            import importlib as _imp
            _ha = _imp.import_module("harmonic_analysis")
        except Exception:
            _ha = None
    if _ha is None:
        raise RuntimeError("harmonic_analysis not available")

    fn = getattr(_ha, "compute_fft_spectrum_from_amplitudes", None)
    if not callable(fn):
        raise RuntimeError("harmonic_analysis.compute_fft_spectrum_from_amplitudes missing")

    # attempt 1: call as-is
    try:
        out = fn(amplitudes, **kw)
    except TypeError:
        # attempt 2: filter kwargs to accepted params (and alias pad_len->padlen if needed)
        try:
            sig = _ins.signature(fn)
            params = sig.parameters
            alias = dict(kw)
            if "pad_len" in alias and "pad_len" not in params and "padlen" in params:
                alias["padlen"] = alias.pop("pad_len")
            filtered = {k: v for k, v in alias.items() if k in params}
            out = fn(amplitudes, **filtered)
        except Exception:
            # attempt 3: bare call
            out = fn(amplitudes)

    # normalize to dict (support old and new APIs)
    if isinstance(out, dict):
        P = out.get("P")
        dc = out.get("dc")
        if dc is None and P is not None:
            S = float(_np.sum(P)) or 1.0
            dc = float(P[0] / S)
        return {
            "freq": out.get("freq"),
            "X": out.get("X"),
            "P": P,
            "dc": dc,
            "entropy_bits": out.get("entropy_bits"),
            "entropy": out.get("entropy"),
            "flatness": out.get("flatness"),
        }

    if isinstance(out, tuple):
        if len(out) == 3:
            P, freqs, meta = out
            S = float(_np.sum(P)) or 1.0
            dc = (meta.get("dc_frac", meta.get("dc", float(P[0]/S))) 
                  if isinstance(meta, dict) else float(P[0]/S))
            return {
                "freq": freqs, "X": None, "P": P,
                "dc": dc,
                "entropy_bits": (meta.get("entropy_bits") if isinstance(meta, dict) else None),
                "entropy": (meta.get("entropy") if isinstance(meta, dict) else None),
                "flatness": (meta.get("flatness") if isinstance(meta, dict) else None),
            }
        if len(out) == 2:
            P, freqs = out
            S = float(_np.sum(P)) or 1.0
            return {"freq": freqs, "X": None, "P": P, "dc": float(P[0]/S),
                    "entropy_bits": None, "entropy": None, "flatness": None}

    raise TypeError("Unexpected FFT output from harmonic_analysis")
# [_fft_from_gui] compat v2
