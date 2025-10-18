    # Spectrum metrics (DC, entropy bits, flatness)

    **Status**
    - [ ] Drafted
    - [ ] Linked in Master
    - [ ] Code referenced
    - [ ] Tests added

    ## Summary
    _Fill in a 2–4 sentence summary here._

    ## Code pointers
    - `smoke_test.py:3` — from harmonic_analysis import compute_fft_spectrum_from_amplitudes
- `smoke_test.py:16` — power, freqs, mets = compute_fft_spectrum_from_amplitudes(amps, remove_dc=True, window="hann", pad_len=128)
- `cli_runner.py:13` — compute_fft_spectrum_from_amplitudes,
- `cli_runner.py:53` — print(f"Preprocess metrics: DC={mets['dc_frac']:.3f}, H={mets['entropy_bits']:.3f} bits, len={mets['len']}")
- `cli_runner.py:70` — power, freqs, mets = compute_fft_spectrum_from_amplitudes(
- `cli_runner.py:71` — amps, remove_dc=True, window="hann", pad_len=args.pad_len
- `cli_runner.py:73` — print(f"\nFFT metrics: DC={mets['dc_frac']:.3f}, H={mets['entropy_bits']:.3f} bits, peak@{int(np.argmax(power))}")
- `cli_runner.py:76` — plt.title(f"{label} FFT — {args.method or '-'} / {args.phase}  (DC={mets['dc_frac']:.3f}, H={mets['entropy_bits']:.3f} bits)")
- `series_encoding.py:7` — # - spectral metrics: spectral_entropy_fft, spectral_flatness_fft
- `series_encoding.py:565` — def spectral_flatness_fft(vec: np.ndarray, eps: float = 1e-18) -> float:
- `series_encoding.py:566` — """Spectral flatness (geometric mean / arithmetic mean) of FFT power."""
- `series_encoding.py:636` — "spectral_flatness_fft": spectral_flatness_fft(v),
- `QTEGUI.py:42` — def _fft_from_gui(amplitudes, **kw):
- `QTEGUI.py:43` — """GUI-safe wrapper around harmonic_analysis.compute_fft_spectrum_from_amplitudes.
- `QTEGUI.py:44` — Returns a dict with keys: freq, X, P, dc, entropy_bits, entropy, flatness.
- `QTEGUI.py:54` — out = _ha.compute_fft_spectrum_from_amplitudes(amplitudes, **kw)
- `QTEGUI.py:61` — "dc": out.get("dc") if out.get("dc") is not None else (
- `QTEGUI.py:65` — "flatness": out.get("flatness"),
- `QTEGUI.py:72` — dc = meta.get("dc_frac", meta.get("dc", float(P[0] / S)))
- `QTEGUI.py:75` — "dc": dc,
- `QTEGUI.py:78` — "flatness": meta.get("flatness"),
- `QTEGUI.py:85` — "dc": float(P[0] / S),
- `QTEGUI.py:86` — "entropy_bits": None, "entropy": None, "flatness": None,
- `QTEGUI.py:93` — def _fft_from_gui(amplitudes, **kw):
- `QTEGUI.py:94` — """GUI-safe wrapper around harmonic_analysis.compute_fft_spectrum_from_amplitudes.
- `QTEGUI.py:95` — Returns a dict with keys: freq, X, P, dc, entropy_bits, entropy, flatness.
- `QTEGUI.py:96` — # [_fft_from_gui] lazy import fallback
- `QTEGUI.py:114` — out = _ha.compute_fft_spectrum_from_amplitudes(amplitudes, **kw)
- `QTEGUI.py:118` — if out.get("dc") is None and P is not None:
- `QTEGUI.py:120` — dc = float(P[0] / S)
- `QTEGUI.py:122` — dc = out.get("dc")
- `QTEGUI.py:127` — "dc": dc,
- `QTEGUI.py:130` — "flatness": out.get("flatness"),
- `QTEGUI.py:137` — dc = meta.get("dc_frac", meta.get("dc", float(P[0] / S)))
- `QTEGUI.py:140` — "dc": dc,
- `QTEGUI.py:143` — "flatness": meta.get("flatness"),
- `QTEGUI.py:150` — "dc": float(P[0] / S),
- `QTEGUI.py:151` — "entropy_bits": None, "entropy": None, "flatness": None,
- `QTEGUI.py:157` — def _fft_from_gui(amplitudes, **kw):
- `QTEGUI.py:158` — """GUI-safe wrapper around harmonic_analysis.compute_fft_spectrum_from_amplitudes.
- `QTEGUI.py:159` — Returns a dict with keys: freq, X, P, dc, entropy_bits, entropy, flatness.
- `QTEGUI.py:176` — fn = getattr(_ha, "compute_fft_spectrum_from_amplitudes", None)
- `QTEGUI.py:178` — raise RuntimeError("harmonic_analysis.compute_fft_spectrum_from_amplitudes missing")
- `QTEGUI.py:200` — dc = out.get("dc")
- `QTEGUI.py:201` — if dc is None and P is not None:
- `QTEGUI.py:203` — dc = float(P[0] / S)
- `QTEGUI.py:208` — "dc": dc,
- `QTEGUI.py:211` — "flatness": out.get("flatness"),
- `QTEGUI.py:218` — dc = (meta.get("dc_frac", meta.get("dc", float(P[0]/S)))
- `QTEGUI.py:222` — "dc": dc,
- `QTEGUI.py:225` — "flatness": (meta.get("flatness") if isinstance(meta, dict) else None),
- `QTEGUI.py:230` — return {"freq": freqs, "X": None, "P": P, "dc": float(P[0]/S),
- `QTEGUI.py:231` — "entropy_bits": None, "entropy": None, "flatness": None}
- `QTEGUI.py:234` — # [_fft_from_gui] compat v2
- `metrics_extra.py:13` — def spectral_flatness_fft(x: np.ndarray) -> float:
- `QTEGUI_Lite.py:121` — - spectrum(a) -> dict with power, flatness, H_z, H_qft
- `QTEGUI_Lite.py:143` — return {"H_Z_bits":Hz, "H_QFT_bits":Hf, "flatness":flat, "len":int(a.size)}
- `paper_batch.py:6` — from harmonic_analysis import compute_fft_spectrum_from_amplitudes
- `paper_batch.py:24` — w.writerow(["label","mode","nqubits","len","dc_frac","entropy_bits","peak_index"])
- `paper_batch.py:38` — P, F, M = compute_fft_spectrum_from_amplitudes(a, remove_dc=True, window="hann", pad_len=512)
- … (+74 more)

    ## Test pointers
    - `tests/test_fft_invariants.py:2` — from harmonic_analysis import compute_fft_spectrum_from_amplitudes
- `tests/test_fft_invariants.py:9` — out = compute_fft_spectrum_from_amplitudes(x, sample_rate=1.0)
- `tests/test_fft_invariants.py:14` — # DC of a mean-removed windowed cosine should be ~0
- `tests/test_fft_invariants.py:15` — assert out["dc"] < 1e-3
- `tests/test_qtegui_fft_wrapper.py:7` — out = m._fft_from_gui(vec, remove_dc=True, window="hann", pad_len=8)
- `tests/test_qtegui_fft_wrapper.py:9` — assert "freq" in out and "P" in out and "dc" in out

    ## Notes from curation
    - active state first fft qft measure amplitudes tomography basis all use active
- build qft spectrum
- entropy spectral entropy nats entropy bits bits
- k dc frac dc entropy entropy bits flatness
- qft spectrum series
- returns dict keys freq x p dc entropy bits entropy flatness
- shannon entropy bits amp 2
- shannon entropy bits normalized fft power spectrum exclude zeros
- spectral flatness

    ---
    Back to: [Master](QTEGUI_MASTER.md)
