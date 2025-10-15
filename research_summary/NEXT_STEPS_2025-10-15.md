# NEXT STEPS — 2025-10-15

## Snapshot (from RESULTS_SUMMARY.md)
- Ramsey (ibm_torino, 256 shots): visibility 0.752, R²=0.990 (fit).
- CHSH (ibm_torino, 256 shots): S = −0.109 / −0.016 (no violation).
- QPSK: only one run with p* logged (0.0195 @ M=128,K=7,512 shots). Many rows missing p_star/depth/twoq.

## Immediate TODO (metrics/plumbing)
- [ ] Ensure **all** QPSK paths compute & write: `p_star`, `depth`, `twoq`.
- [ ] Standardize Ramsey JSON: include `timestamp`, unify `points`→`ramsey_points` in CSV writer.
- [ ] CHSH: pin angle schedule to the `chsh2` set and record it every run.

## Reruns to queue
- [ ] **Ramsey sweep**: phases=9 (0..2π), shots=4096 → `paper_outputs/ramsey_ibm_torino_4096s.json` (+fit).
- [ ] **CHSH fixed angles**: |Φ⁺⟩ and |Ψ⁺⟩, shots=8192 → `paper_outputs/chsh_ibm_torino_8192s.json`, record angles.
- [ ] **QPSK leaderboard**:
      - M=128, K=7, shots=2048
      - M=256, K=8, shots=2048
      Ensure p* is logged for each.

## Commands (templates)
### Ramsey
PYTHONPATH=. python scripts/ramsey_pi_sweep.py --backend ibm_torino --shots 4096 --npts 9 --span 6.283185307179586

### CHSH (fixed angles from chsh2 file)
PYTHONPATH=. python scripts/chsh_run.py --backend ibm_torino --shots 8192 --state bell_phi_plus --angles "+0,+pi/4; +0,-pi/4; +pi/2,+pi/4; +pi/2,-pi/4"

### QPSK (indexer)
PYTHONPATH=. python scripts/qpsk_end2end.py --backend ibm_torino --shots 2048 --K 7 --M 128 --symbol 73
PYTHONPATH=. python scripts/qpsk_end2end.py --backend ibm_torino --shots 2048 --K 8 --M 256 --symbol 145

## Packaging
- [ ] Update `RESULTS_SUMMARY.md` and regenerate `latest.json`.
- [ ] Tag: `results-2025-10-15-sweep1`
- [ ] Push artifacts.
