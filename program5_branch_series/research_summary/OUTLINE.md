# Working Title
Quantum Telemetry Experiments: Coherence, Entanglement, and QPSK Indexing on IBM Hardware

## Abstract
_TODO: 120–150 words summarizing goals, methods (Ramsey, CHSH, QPSK indexer), and the headline results: Ramsey visibility ~0.75; CHSH not violated; QPSK p* strongly limited by two-qubit depth._

## 1. Introduction
- Motivation: simple-to-complex pipeline (single-qubit coherence → two-qubit entanglement → K-bit phase indexing).
- Research questions:
  1) What coherence/contrast can we rely on for 1-qubit phases?  
  2) Do shallow Bell circuits on this backend clear CHSH > 2?  
  3) How does QPSK indexer fidelity scale with K and with two-qubit gate count/depth?

## 2. Methods
### 2.1 Hardware & SDK
- Backend: `ibm_torino` (IBM Quantum).  
- Stack: Qiskit 2.2.1, qiskit-ibm-runtime 0.42.0 (published-results Sampler shape).  
- Shots: primarily 128–512.

### 2.2 Circuit families
- Ramsey: H–Rz(2φ)–H with phase sweep (17 points, π/8 steps).
- CHSH: standard settings; angles logged per-term.
- QPSK indexer: K-phase encode followed by IQFT(K) and computational-basis measurement. Optional approximate IQFT.

### 2.3 Execution & result decoding
- Sampler V2; robust decoder for published results (SamplerPubResult → DataBin) with fallback.
- Depth and two-qubit gate count printed post-transpile; optional seed sweep.

### 2.4 Metrics
- Ramsey: cosine fit (c, a, ψ), visibility V≈2|a|, R².  
- CHSH: S = E(a,b)+E(a,b′)+E(a′,b)−E(a′,b′).  
- QPSK: p* = max bitstring probability; report depth & two-qubit gates.

## 3. Results
### 3.1 Ramsey (single-qubit coherence)
- Visibility ~0.752; R² ~0.990 (17 points, 256 shots).

### 3.2 CHSH (Bell test)
- S in [−0.109, −0.016] at 256 shots; no violation.

### 3.3 QPSK / Indexer
- Best observed p*: 0.246 at K=8 (M=256), 512 shots.
- Example at K=7 (M=128): depth ~232, two-qubit ~82 → p* ~0.0195.

## 4. Discussion
- Single-qubit phases are healthy; two-qubit depth is main limiter for multi-bit indexing.
- Sensitivity to layout/seed; mitigation and approximate IQFT are promising levers.

## 5. Limitations
- Many early QPSK artifacts lack p*/depth/twoq; backfill by re-transpile (offline).
- No readout mitigation/advanced resilience in these logs (where unsupported).

## 6. Future Work
- Backfill metadata; correlate p* vs two-qubit count.  
- Try approximate IQFT degrees 2–3; enforce short qubit chains; seed sweeps.  
- Revisit CHSH with optimized pair + mitigation.

## 7. Reproducibility
- Artifacts indexed in `research_summary/results_index.csv`; human summary in `RESULTS_SUMMARY.md`.
- Runner scripts in `scripts/`; Sampler decoder and two-qubit counter included.

### Appendix A — Artifact inventory (pointer)
See `research_summary/results_index.csv` (20 JSON artifacts: Ramsey 1, CHSH 2, QPSK 11, Other 6).

### Appendix B — QPSK transpile stats (pointer)
Depth/two-qubit counts recorded in artifacts where available; backfill planned.
