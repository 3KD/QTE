# Results — Current Snapshot

_This section summarizes all logged findings to date (see `research_summary/results_index.csv` and `RESULTS_SUMMARY.md`)._

## Key findings at a glance
- **Ramsey (1-qubit):** visibility **0.752**, R² **0.990** (17 points, 256 shots).  
- **CHSH:** **no violation**; S values **−0.016** and **−0.109** at 256 shots.  
- **QPSK indexer:** best **p\*** **0.246** at **K=8 (M=256)** with 512 shots; at **K=7** with **depth≈232** and **two-qubit≈82**, **p\*** drops to **0.0195**.

> **p\*** denotes the highest single-bitstring probability from the measured distribution.

---

## 1) Ramsey (single-qubit coherence)
**Artifact:** `paper_outputs/ramsey_ibm_torino_256s.json` (+ fit JSON)

- Fit: \( p_0(\phi) = c + a \cos(2\phi + \psi) \)  
  \(c\approx0.516,\; a\approx-0.376,\; \psi\approx-3.107\)  
  Visibility \(V\approx 2|a|\approx 0.752\), \(R^2\approx 0.990\).
- **Interpretation:** Single-qubit phase coherence and contrast are strong on this backend for modest depth; this is the ceiling our multi-qubit circuits must live under.

---

## 2) CHSH (Bell test)
**Artifacts:**  
- `paper_outputs/chsh2_ibm_torino_256s.json` → \(S\approx -0.016\).  
- `paper_outputs/chsh_ibm_torino_256s.json` → \(S\approx -0.109\).

Angles (for the first):  
- E(ab): A=0, B=π/4; E(ab′): A=0, B=−π/4;  
- E(a′b): A=π/2, B=π/4; E(a′b′): A=π/2, B=−π/4.

**Interpretation:** No violation (S≪2). With current mapping/depth and no mitigation, entangling + readout errors dominate. Use as a “noisy two-qubit” baseline.

---

## 3) QPSK / K-bit indexer (IQFT decode)
**Artifacts:** 11 total across K=5…10; representative entries:

- **Best observed:** `qpsk_ibm_torino_M256_sym145_8b_512s_*` → **p\*** ≈ **0.246** at **K=8** (512 shots).  
- **With transpile stats:** `qpsk_ibm_torino_M128_sym73_7b_512s_d3libb03qtks738cedmg.json` → **depth≈232**, **two-qubit≈82**, **p\*** ≈ **0.0195**.

**Interpretation:** p\* collapses with **two-qubit gate count and depth**. The K=8 success suggests layout/seed luck matters; many earlier runs didn’t record p\*, depth, or twoq — backfilling will enable a proper correlation plot \(p^* \) vs. two-qubit count.

---

## Inventory & provenance
- **Total artifacts:** 20 (Ramsey 1, CHSH 2, QPSK 11, Other 6).  
- **Best Ramsey visibility:** ~**0.752** (`ramsey_ibm_torino_256s.json`).  
- **Best QPSK p\* (so far):** **0.2461** at **K=8, M=256** (`...d3ksg203qtks738borl0.json`).  
- Additional PNG figures detected at repo root (8).

---

## What this means
1. **Ceiling is fine; bottleneck is entangling depth.**  
   The Ramsey result shows the hardware can maintain high contrast for 1-qubit phases. As soon as we lean on 2-qubit gates (CHSH; IQFT ladders), fidelity becomes depth-limited.

2. **Transpile/layout are first-order controls.**  
   A 2× change in two-qubit count often swamps everything else. Seeds, approximate IQFT, and chain length should be treated as knobs, not constants.

---

## Next steps (actionable)
1. **Backfill QPSK metadata offline** (no runs needed): re-transpile each saved circuit to log **depth** and **two-qubit** for every artifact; regenerate `results_index.csv`; plot \(p^*\) vs two-qubit count and vs depth.
2. **Reduce two-qubit exposure:** try **approximate IQFT** (degree 2–3), enforce **short chains** in initial layout, and **seed-sweep** to minimize CZ/CX count.
3. **Lightweight mitigation:** enable readout mitigation (and resilience options where supported) to see if we can lift p\* without changing topology.
4. **Revisit CHSH on a strong pair:** pick the best-coupled edge, prune to a minimal-depth implementation, and check if S can exceed 2 under mitigation.

---

## Reproducibility pointers
- Summaries: `research_summary/RESULTS_SUMMARY.md` and `research_summary/latest.json`.
- Full index: `research_summary/results_index.csv` (with file, backend, shots, and metrics).
- Scripts: `scripts/` (QPSK runner, Sampler decoder, two-qubit counter).
