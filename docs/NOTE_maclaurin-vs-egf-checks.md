    # Maclaurin vs EGF checks

    **Status**
    - [ ] Drafted
    - [ ] Linked in Master
    - [ ] Code referenced
    - [ ] Tests added

    ## Summary
    _Fill in a 2–4 sentence summary here._

    ## Code pointers
    - `cli_runner.py:28` — parser.add_argument("--method", type=str, default=None, help="Series method (π: Ramanujan|Machin)")
- `cli_runner.py:29` — parser.add_argument("--phase", type=str, default="sign", choices=["sign", "abs"], help="Phase mode for signed series")
- `tests_qte.py:7` — v = se.get_series_amplitudes("J0", 32, amp_mode="egf", normalize=True)
- `tests_qte.py:28` — v = se.get_series_amplitudes("Maclaurin[log(1+x); auto_r; real_coeffs]", 16,
- `series_encoding.py:1` — # series_encoding.py — unified, drop-in QTE series utilities
- `series_encoding.py:2` — # - get_series_amplitudes(label, dim, method=None, phase_mode="sign", normalize=True, amp_mode="egf"|"terms")
- `series_encoding.py:57` — """Li_s(z) = Σ_{n≥1} z^n / n^s. Direct series with simple guards."""
- `series_encoding.py:89` — # Constants (values) used by EGF mode
- `series_encoding.py:270` — if s.upper().startswith('J0'):
- `series_encoding.py:285` — if s.upper().startswith("J0"):
- `series_encoding.py:317` — # Maclaurin TERMS generators
- `series_encoding.py:421` — "J0": _terms_J0, "J_0": _terms_J0,
- `series_encoding.py:443` — amp_mode: str = "egf",       # "egf" | "terms"
- `series_encoding.py:447` — - EGF:     t_{n+1} = t_n * x / (n+1), complex-safe (x = compute_series_value(label))
- `series_encoding.py:448` — - TERMS:   if generator exists -> raw terms; else EGF-like fallback (complex-safe)
- `series_encoding.py:476` — # fallback to EGF-like if no TERMS generator
- `series_encoding.py:484` — # EGF mode
- `series_encoding.py:642` — ### QTE Maclaurin generic ###
- `series_encoding.py:646` — def _qte_is_maclaurin_label(lbl):
- `series_encoding.py:648` — return t.startswith("maclaurin[") or t.startswith("maclaurin(")
- `series_encoding.py:651` — if t.lower().startswith("maclaurin["):
- `series_encoding.py:682` — def _qte_maclaurin_coeffs(expr, n_terms, radius=0.6, m=None):
- `series_encoding.py:698` — if _qte_is_maclaurin_label(label):
- `series_encoding.py:700` — n=int(dim); coeffs=_qte_maclaurin_coeffs(expr, n_terms=n, radius=float(r))
- `series_encoding.py:717` — if _qte_is_maclaurin_label(label):
- `series_encoding.py:774` — raise ValueError("polylog requires |z| < 1 for this series")
- `series_encoding.py:806` — if L.startswith("J0") and str(amp_mode).lower() == "egf":
- `series_encoding.py:902` — # === QTE EXT: J0 EGF safe path + rail helpers ===
- `series_encoding.py:905` — def _qte_j0_vector(dim, egf=False, phase_mode="sign", normalize=True):
- `series_encoding.py:913` — if egf:
- `series_encoding.py:934` — if s.startswith("J0") and str(amp_mode).lower() == "egf":
- `series_encoding.py:935` — return _qte_j0_vector(dim, egf=True, phase_mode=phase_mode, normalize=normalize)
- `series_encoding.py:940` — # Add: rail split (extra sign qubit), strict EGF weighting, QFT[...] amplitudes, Euler-accelerated polylog
- `series_encoding.py:981` — # --- Strict EGF weighting (1/k!) with lgamma to avoid overflow) ---
- `series_encoding.py:1049` — # Delegate for the base vector (no EGF weighting yet)
- `series_encoding.py:1061` — # Apply strict EGF weighting if requested
- `series_encoding.py:1062` — if str(amp_mode).lower() == "egf":
- `series_encoding.py:1143` — # Idempotent wrapper: safe EGF for J0 + label-level [rail] post-processing
- `series_encoding.py:1191` — def _QTE_j0_terms_vector(n):
- `series_encoding.py:1192` — # J0(x) series coefficients placed at even indices (odds zero).
- `series_encoding.py:1214` — _base = _qte_bessel_terms_vector(_n, _dim_base)
- `series_encoding.py:1215` — if str(amp_mode).lower() == 'egf':
- `series_encoding.py:1258` — # Safe J0 path for both 'terms' and 'egf' to avoid factorial overflow
- `series_encoding.py:1259` — if s.upper().startswith("J0"):
- `series_encoding.py:1260` — v = _QTE_j0_terms_vector(dim)
- `series_encoding.py:1292` — # Bessel J_n (series + value), Maclaurin auto_r + real_coeffs, known Li constants.
- `series_encoding.py:1322` — # z in (-1,0); alternating series with Kahan summation
- `series_encoding.py:1378` — # -------- Maclaurin niceties (auto_r, real_coeffs) --------
- `series_encoding.py:1398` — if t.lower().startswith("maclaurin["):
- `series_encoding.py:1426` — def _qte_maclaurin_coeffs(expr, n_terms, radius=0.6, m=None):
- `series_encoding.py:1452` — # ------------- Bessel J_n -----------------------
- `series_encoding.py:1453` — def _qte_bessel_Jn_terms(n, N):
- `series_encoding.py:1466` — def _qte_bessel_Jn_value(n, x=1.0, terms=256, tol=1e-16):
- `series_encoding.py:1502` — def _qte_bessel_terms_vector(n, dim):
- `series_encoding.py:1503` — """Return first `dim` Maclaurin coefficients of J_n(x)."""
- `series_encoding.py:1524` — # --- QTE: Bessel J_n value support (idempotent) ---
- `series_encoding.py:1541` — def _QTE_bessel_Jn_value(n, x, terms=2000):
- `series_encoding.py:1542` — # Stable series: J_n(x) = sum_{k>=0} (-1)^k / (k! Γ(k+n+1)) * (x/2)^{2k+n}
- `series_encoding.py:1578` — return _QTE_bessel_Jn_value(_n, _x, terms=max(terms or 256, 256))
- `series_encoding.py:1580` — # --- end QTE: Bessel J_n value support ---
- … (+130 more)

    ## Test pointers
    - `tests_qte.py:7` — v = se.get_series_amplitudes("J0", 32, amp_mode="egf", normalize=True)
- `tests_qte.py:28` — v = se.get_series_amplitudes("Maclaurin[log(1+x); auto_r; real_coeffs]", 16,
- `qte_smoke.py:7` — # J0 terms working & real
- `qte_smoke.py:9` — v = np.asarray(get_series_amplitudes("J0", d, amp_mode="terms", normalize=False))
- `qte_smoke.py:10` — print("J0 len:", len(v), "dtype:", v.dtype, "first8:", v.real[:8].tolist())
- `qte_smoke.py:26` — coeffs = get_series_amplitudes("J0", 2**nq, amp_mode="terms", normalize=False).real
- `tests/test_series_trig.py:4` — from series_encoding import _qte_maclaurin_coeffs  # internal but OK for tests
- `tests/test_series_trig.py:15` — coeffs = _qte_maclaurin_coeffs("sin(x)", n_terms=N, radius=4.0, m=0)
- `tests/test_series_trig.py:23` — coeffs = _qte_maclaurin_coeffs("sin(x)^2", n_terms=6, radius=4.0, m=0)

    ## Notes from curation
    - add bessel j maclaurin coefficients 0
- add fixed maclaurin coefficient erf x
- add rail split extra sign qubit strict egf weighting qft amplitudes
- bessel j n series value maclaurin auto r real coeffs known li constant
- if t lower startswith maclaurin
- maclaurin generic
- maclaurin niceties auto r real coeffs
- maclaurin terms generators
- mode str egf terms periodic pea qrom etc
- modes egf terms periodic p q value phase pea digit qrom
- return t startswith maclaurin t startswith maclaurin
- returns coefficient x n maclaurin series nonzero only odd n
- sin maclaurin coeff

    ---
    Back to: [Master](QTEGUI_MASTER.md)
