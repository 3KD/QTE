# QTE Status Board — 2025-10-15

## Experiments (hardware)
- [x] Ramsey (ibm_torino, 256 shots): visibility 0.752, R²=0.990
- [x] CHSH (ibm_torino, 256 shots): S = −0.109 / −0.016 (no violation)
- [ ] CHSH (fixed angles, ≥8192 shots): queued
- [~] QPSK leaderboard (M=128,K=7; M=256,K=8): results exist, metrics incomplete

## Metrics & Logging
- [ ] Standardize post-run logging for **p_star**, **depth**, **twoq**, **timestamp**
- [ ] Backfill missing QPSK p_star into `results_index.csv` (script added)

## Tests
- [x] Maclaurin syntax / Bessel / Polylog core (existing)
- [x] sin Maclaurin coefficients (new)
- [x] Entanglement invariants (Bell vs product) (new)
- [x] Lorentz boost preserves Minkowski metric (new)
- [ ] CHSH pipeline unit/integration test (runner to add)

## Near-term Objectives (Q4 2025)
- [ ] CHSH runner (`scripts/chsh_run.py`) with angles file + CSV logging
- [ ] Unified “repro pack” CLI (artifact + plots + metrics + gate counts)
- [ ] Hardware reruns: Ramsey sweep (4096 shots), CHSH (8192 shots), QPSK (2048 shots)
