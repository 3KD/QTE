# Verification Matrix: Theory → Measurable Proxy
_Last updated: $(date -u +%FT%TZ)_

Map each theory item to what we can verify on NISQ today (with your QTE stack).

| Theory item | Proxy experiment (now) | Statistic to log | Pass criterion |
|---|---|---|---|
| Hidden period / eigenphase | QPSK indexer + IQFT for known symbol/phase | argmax bitstring hit rate p* vs K; depth, twoq | p* above noise model; scaling trend |
| IQP sampling hardness | (H⊗n) → diagonal phases → (H⊗n) | XEB / HOG; TV distance to product baseline | Positive XEB; significant HOG |
| QPE on scale operator | U = e^{iαN}; phase bits via inverse QFT | bit-wise success vs shots; effect of approx-degree | Accuracy improves with shots; robust to noise |
| Sparse linear solver toy | Tridiag A via block-encoding (small n) | Observable ⟨x|O|x⟩ error vs classical | Error within ε at feasible depth |
| Amplitude estimation | Overlap / integral of prepared series | RMSE vs classical Monte-Carlo at equal budget | ~quadratic fewer shots for same error |
| Koopman spectrum (when U ready) | Learned/analytic U on small n | Phase histogram; stability vs time-step | Consistent eigenphases; reproducible |

All experiments should write JSON artifacts and update `results_index.csv`.

