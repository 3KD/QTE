# Experiment Playbook (Paste-ready recipes)
_Last updated: $(date -u +%FT%TZ)_

> Use these to generate artifacts that support each theoretical claim.

## 1) QPSK/IQFT (period/phase proxy)
- Vary (K,M,symbol), collect p*, depth, twoq.
Example:
\`\`\`bash
PYTHONPATH="$(pwd)" python scripts/qpsk_end2end.py --send \
  --backend ibm_torino --M 128 --K 7 --symbol 73 --shots 512
\`\`\`

## 2) IQP sandwich sampling
- Build diagonal phases from analytic series; wrap with H⊗n (or QFT/IQFT).
- Log cross-entropy vs uniform/product baselines.

## 3) QPE on scale operator
- Implement U(α)=e^{iαN} with per-qubit phases (binary-weighted).
- Run inverse-QFT readout; sweep α, shots.

## 4) Sparse-linear toy (HHL-lite)
- Encode tiny tridiagonal A; prepare |b⟩; measure ⟨O⟩.
- Compare to classical solve; store error bars.

## 5) Amplitude/integral estimation
- Use two-copy SWAP (Rényi-2) or overlap circuits.
- Compare convergence vs classical Monte Carlo.

## 6) Koopman (when U exists)
- Learned or analytic U; QPE; log eigenphases; stability checks.

All runs: ensure artifacts land under `paper_outputs/` and index updates in `research_summary/results_index.csv`.

