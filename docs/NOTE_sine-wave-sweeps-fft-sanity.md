    # Sine-wave sweeps / FFT sanity

    **Status**
    - [ ] Drafted
    - [ ] Linked in Master
    - [ ] Code referenced
    - [ ] Tests added

    ## Summary
    _Fill in a 2–4 sentence summary here._

    ## Code pointers
    - `smoke_test.py:3` — from harmonic_analysis import compute_fft_spectrum_from_amplitudes
- `smoke_test.py:14` — # 2) FFT (classical)
- `smoke_test.py:16` — power, freqs, mets = compute_fft_spectrum_from_amplitudes(amps, remove_dc=True, window="hann", pad_len=128)
- `smoke_test.py:17` — print("FFT metrics:", {k: round(v, 3) if isinstance(v, float) else v for k, v in mets.items()})
- `cli_runner.py:13` — compute_fft_spectrum_from_amplitudes,
- `cli_runner.py:30` — parser.add_argument("--pad-len", type=int, default=128, help="Zero-pad length for FFT/QFT spectrum")
- `cli_runner.py:31` — parser.add_argument("--plot", action="store_true", help="Plot FFT spectrum")
- `cli_runner.py:67` — # Optional FFT spectrum
- `cli_runner.py:70` — power, freqs, mets = compute_fft_spectrum_from_amplitudes(
- `cli_runner.py:76` — plt.title(f"{label} FFT — {args.method or '-'} / {args.phase}  (DC={mets['dc_frac']:.3f}, H={mets['entropy_bits']:.3f} bits)")
- `series_encoding.py:550` — # Spectral metrics (FFT)
- `series_encoding.py:554` — """Shannon entropy (bits) of normalized FFT power spectrum (exclude zeros)."""
- `series_encoding.py:556` — X = np.fft.fft(x)
- `series_encoding.py:566` — """Spectral flatness (geometric mean / arithmetic mean) of FFT power."""
- `series_encoding.py:568` — P = np.abs(np.fft.fft(x))**2 + eps
- `series_encoding.py:689` — G=np.fft.fft(fz)/M
- `series_encoding.py:1021` — vals = _np.fft.ifft(vals)
- `series_encoding.py:1445` — G = _npl.fft.fft(fz)/M
- `series_encoding.py:1894` — # --- QTE hotfix (append-only): set trigonometric Fourier constant term (a0/2) exactly ---
- `series_encoding.py:1904` — sets coeffs[0] to the *trigonometric average* a0/2 computed exactly:
- `series_encoding.py:1905` — a0/2 = (1/(2π)) ∫_{-π}^{π} f(x) dx
- `series_encoding.py:1906` — This makes sin^2(x) yield 0.5 for the constant term, matching the test.
- `series_encoding.py:1918` — c0_exact = sp.integrate(f, (x, -sp.pi, sp.pi)) / (2*sp.pi)  # a0/2
- `series_encoding.py:1925` — # --- QTE hotfix v2 (append-only): robust a0/2 computation for Fourier constant term ---
- `series_encoding.py:1937` — sets coeffs[0] to the trigonometric constant term a0/2 over [-π, π]:
- `series_encoding.py:1938` — a0/2 = (1/(2π)) ∫_{-π}^{π} f(x) dx
- `QTEGUI.py:42` — def _fft_from_gui(amplitudes, **kw):
- `QTEGUI.py:43` — """GUI-safe wrapper around harmonic_analysis.compute_fft_spectrum_from_amplitudes.
- `QTEGUI.py:54` — out = _ha.compute_fft_spectrum_from_amplitudes(amplitudes, **kw)
- `QTEGUI.py:89` — raise TypeError("Unexpected FFT output from harmonic_analysis")
- `QTEGUI.py:93` — def _fft_from_gui(amplitudes, **kw):
- `QTEGUI.py:94` — """GUI-safe wrapper around harmonic_analysis.compute_fft_spectrum_from_amplitudes.
- `QTEGUI.py:96` — # [_fft_from_gui] lazy import fallback
- `QTEGUI.py:114` — out = _ha.compute_fft_spectrum_from_amplitudes(amplitudes, **kw)
- `QTEGUI.py:154` — raise TypeError("Unexpected FFT output from harmonic_analysis")
- `QTEGUI.py:157` — def _fft_from_gui(amplitudes, **kw):
- `QTEGUI.py:158` — """GUI-safe wrapper around harmonic_analysis.compute_fft_spectrum_from_amplitudes.
- `QTEGUI.py:176` — fn = getattr(_ha, "compute_fft_spectrum_from_amplitudes", None)
- `QTEGUI.py:178` — raise RuntimeError("harmonic_analysis.compute_fft_spectrum_from_amplitudes missing")
- `QTEGUI.py:233` — raise TypeError("Unexpected FFT output from harmonic_analysis")
- `QTEGUI.py:234` — # [_fft_from_gui] compat v2
- `metrics_extra.py:6` — X = np.fft.fft(np.asarray(x))
- `metrics_extra.py:14` — X = np.fft.fft(np.asarray(x))
- `QTEGUI_Lite.py:137` — F = np.fft.fft(a) / math.sqrt(a.size)
- `QTEGUI_Lite.py:140` — P = np.abs(np.fft.fft(a))**2
- `paper_batch.py:6` — from harmonic_analysis import compute_fft_spectrum_from_amplitudes
- `paper_batch.py:38` — P, F, M = compute_fft_spectrum_from_amplitudes(a, remove_dc=True, window="hann", pad_len=512)
- `paper_batch.py:41` — plt.title(f"{lab} {mode.upper()} FFT  (DC={M['dc_frac']:.3f}, H={M['entropy_bits']:.3f} bits)")
- `harmonic_analysis.py:2` — Simple FFT/invariant utilities used by QTEGUI.
- `harmonic_analysis.py:4` — compute_fft_spectrum_from_amplitudes(amplitudes, *, sample_rate=1.0)
- `harmonic_analysis.py:7` — - 'X': complex FFT spectrum (two-sided)
- `harmonic_analysis.py:35` — def compute_fft_spectrum_from_amplitudes(amplitudes, *, sample_rate: float = 1.0):
- `harmonic_analysis.py:44` — X = np.fft.fft(x)
- `harmonic_analysis.py:47` — freq = np.fft.fftfreq(n, d=1.0/float(sample_rate))
- `sweep_polylog.py:4` — # ... inside your sweep loop, after you create a Statevector `sv` ...
- `sweep_polylog.py:34` — extra={"sweep":"polylog", "trial": sweep_idx},
- `qte_metrics.py:12` — from harmonic_analysis import compute_fft_spectrum_from_amplitudes
- `qte_metrics.py:27` — power, freqs, mets = compute_fft_spectrum_from_amplitudes(
- `qte_metrics.py:117` — # 2) FFT power
- `qte_metrics.py:118` — power, freqs, mets = compute_fft_spectrum_from_amplitudes(
- … (+67 more)

    ## Test pointers
    - `tests/test_fft_invariants.py:2` — from harmonic_analysis import compute_fft_spectrum_from_amplitudes
- `tests/test_fft_invariants.py:9` — out = compute_fft_spectrum_from_amplitudes(x, sample_rate=1.0)
- `tests/test_series_trig.py:22` — # sin^2(x) = (1 - cos(2x))/2 so constant term should be 0.5
- `tests/test_qtegui_fft_wrapper.py:7` — out = m._fft_from_gui(vec, remove_dc=True, window="hann", pad_len=8)

    ## Notes from curation
    - elif basis upper x qft fourier
- extra sweep polylog trial sweep idx
- hotfix append only set trigonometric fourier constant term a0 2 e
- hotfix v2 append only robust a0 2 computation fourier constant
- inside your sweep loop after you create statevector
- makes sin 2 x yield 0 5 constant term matching test
- sin maclaurin coeff

    ---
    Back to: [Master](QTEGUI_MASTER.md)
