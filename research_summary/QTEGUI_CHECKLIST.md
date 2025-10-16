# QTEGUI Checklist (2025-10-16)

**Scope:** sanity coverage for GUI-backed computational blocks.

- [x] FFT invariants via `harmonic_analysis.compute_fft_spectrum_from_amplitudes`
- [x] Entanglement metrics: `metrics_extra.schmidt_entropy` (bits)
- [x] Schmidt decomposition outputs `(rhoA, rhoB, rhoAB)` (NumPy)
- [x] Trig series: `_qte_maclaurin_coeffs` constant term (a0/2) exact/numeric
- [x] Lorentz: `boost_x` & `preserves_minkowski` (matrix or beta)
- [ ] QPSK metrics postlog tools (`scripts/postlog_qpsk.py`) — hook into GUI
- [ ] CHSH angles (experiments/chsh_angles_phi_pi4.json) — GUI runner
- [ ] Value Phase Estimation wiring in GUI
- [ ] Dataset/Results index: ensure `research_summary/results_index.csv` updates
- [ ] Error surfacing in GUI (toast/log pane) on import/exec failures
