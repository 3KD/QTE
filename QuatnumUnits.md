# Quantum Series Encoding (QSE) — Definitive Curriculum (Units 1–5)

> This canvas is the authoritative, paper-style spec for Units **1–5**. Numbering is fixed and will not change. Each unit follows the same sections: **Overview → Definitions & Math → Implementation Pointers (code) → CLI Experiments (Sim & IBM) → Tests → Expected Results & Artifacts → Notes**.

---

## Unit 1 — Core Thesis & Foundational Concepts

### Overview

Establish **Quantum Transcendental Information (QTI)** and the **Dollarhide Transform** ((\TransformD)) that maps mathematical objects (constants / functions) to normalized complex vectors (“fingerprints”) that can be loaded into quantum states. Define the **Known-Answer Benchmarking** philosophy and the **Function Atlas** idea (similarity geometry across objects).

### Definitions & Math

* **Transform chain**: (\text{Object} \Rightarrow \text{Series/Signal} \Rightarrow \mathbf{a} \in \mathbb{C}^N \Rightarrow \tilde{\mathbf{a}}=\mathbf{a}/|\mathbf{a}|_2).
* **EGF weighting** (optional): coefficients (c_n \mapsto c_n/n!) to temper growth: (a_n= c_n) (terms mode) or (a_n = c_n/n!) (EGF mode).
* **Phase modes**: `sign` (preserve signs in phases) vs `abs` (magnitudes only).
* **Similarity**: cosine similarity (\cos\theta = \langle \tilde{\mathbf{a}}, \tilde{\mathbf{b}}\rangle).
* **Benchmarking**: load states with known truths (e.g., π) → evaluate hardware via fidelity/entropy.

### Implementation Pointers (code)

* `series_encoding.py`: object-to-vector pipelines; label parser (`Maclaurin[...]`, `QFT[...]`).
* `sbrv_precision.py`: SBRV stacked-precision decomposition.
* `sign_split_register.py`: dual-rail sign/IQ encodings.
* `series_preserving.py`: vector normalization, padding, LCU helpers.

### CLI Experiments (Sim & IBM)

* **Sim, π vector** (Maclaurin/EGF): save `.npy` and normalized `.json` metadata.
* **IBM sanity**: minimal state-load + Z/X measurement via `tools/run_on_ibm_torino.py` (n small, shots 4k). Output to `docs/results/`.

### Tests

* Normalization: (|\tilde{\mathbf{a}}|_2=1).
* Label parser equivalence (`Maclaurin[sin^2]` vs direct sampler).
* Similarity symmetry & bounds.

### Expected Results & Artifacts

* `.npy` vectors + `.json` descriptors; similarity matrices for Function Atlas seeds.

### Notes

* Fix **bit ordering** convention (LSB/MSB) for later units; document in metadata.

---

## Unit 2 — Classical Engine: Mathematical Object Library

### Overview

Provide curated generators for constants and special functions; robust Maclaurin via contour-FFT; direct sampling via `QFT[...]` labels.

### Definitions & Math

* **Constants**: π (Leibniz, Machin, Ramanujan, Chudnovsky), e, ln2, ζ(k), γ, ϕ, Catalan, Liouville, Champernowne C10, etc.
* **Special functions**: Bessel (J_n(x)), Polylog (\operatorname{Li}_s(z)).
* **Contour Maclaurin**: (c_n = \frac{1}{2\pi i}\oint \frac{f(z)}{z^{n+1}},dz) computed via FFT on a circle (|z|=r).
* **Sampling `QFT[...]`**: grid (x_k=a+k\Delta), (\Delta=(b-a)/N); produce (f(x_k)) vector.

### Implementation Pointers (code)

* `series_encoding.py`: `_qte_maclaurin_coeffs`, generators for constants/functions, `QFT[...]` sampler.
* `experiments/chsh_angles_phi_pi4.json` etc. (example inputs).
* `physics/lorentz.py` (aux math utilities present here for later use).

### CLI Experiments (Sim)

* Generate π via multiple methods; compare coefficient tails and EGF vs terms.
* Produce Bessel and Polylog coefficient vectors at fixed parameters.

### Tests

* Cross-method π consistency (value bits across methods within tolerance).
* Bessel recurrence checks; polylog differentiation identity on truncated ranges.
* Sampler vs analytic values at grid points.

### Expected Results & Artifacts

* Library index (`docs/results/object_index.json`) with method + truncation metadata.
* Plots of coefficient magnitudes (log-scale) showing EGF stabilization.

### Notes

* Record truncation N, radius r for Maclaurin; embed in metadata for reproducibility.

---

## Unit 3 — Classical Engine: Vector Engine & Algebra

### Overview

Algebra on fingerprints with norm and phase discipline; precision scaffolding.

### Definitions & Math

* **LCU**: (\alpha\tilde{\mathbf{a}} + \beta\tilde{\mathbf{b}}), renormalize.
* **Hadamard product**: ( (\mathbf{a}\odot\mathbf{b})_n=a_n b_n ).
* **Cauchy product (OGF)**: ((\mathbf{a}*\mathbf{b})*n=\sum*{k=0}^n a_k b_{n-k}).
* **EGF binomial product**: ( (\mathbf{a}\star\mathbf{b})*n=\sum*{k=0}^n \binom{n}{k} a_k b_{n-k} ).
* **Dirichlet convolution** (number-theoretic sequences): ((a\ast_D b)(n)=\sum_{d|n} a(d)b(n/d)).
* **SBRV precision**: (\mathbf{a}=\mathbf{a}^{(0)}+\sum_j \mathbf{r}^{(j)}) with decreasing ranges.

### Implementation Pointers (code)

* `series_preserving.py`: `lcu_combine`, `hadamard_product`, `cauchy_product`, `egf_product`, `dirichlet_convolution`.
* `sbrv_precision.py`: `sbrv_decompose`, `sbrv_reconstruct`.
* `sign_split_register.py`: `encode_srd_iq`, `encode_srd_ancilla`.

### CLI Experiments (Sim)

* Multiply generating functions via Cauchy/EGF and verify first K coefficients vs analytic product.
* Precision study: reconstruct from SBRV stacks and compare (\ell_2) error.

### Tests

* Algebraic identities (associativity/commutativity where applicable).
* Parseval after normalization.
* SBRV reconstruction within target (\epsilon).

### Expected Results & Artifacts

* JSON diff reports of coefficient-wise errors; plots of error vs stack depth.

### Notes

* Keep track of **amp_mode** and **phase_mode** across operations to avoid silent drift.

---

## Unit 4 — Quantum Engine: State Preparation & Core Algorithms

### Overview

Compile fingerprints into circuits; provide core algorithms: **QFT/ST-QFT**, **PEA**, **Digit QROM**, **Periodic states**.

### Definitions & Math

* **State init**: `qc.initialize(ψ)` loads (|\psi\rangle). Parseval ensures (\sum |a_k|^2=1).
* **QFT** on (n) qubits: (|x\rangle \mapsto \frac{1}{\sqrt{2^n}}\sum_y e^{2\pi i xy/2^n}|y\rangle).
* **PEA**: for (U|\phi\rangle=e^{2\pi i\lambda}|\phi\rangle), estimate (\lambda) via controlled-(U^{2^k})+inverse QFT.
* **Periodic state** (|\psi_{p/q}\rangle) with phase (e^{2\pi i p n/q}) shows QFT peaks at multiples of (2^n/q).
* **Digit QROM** encodes base-(b) digits into a register via table-lookup unitaries.

### Implementation Pointers (code)

* `quantum_embedding.py`: `generate_series_encoding`, `qft`, `st_qft`, `value_phase_estimation_circuit`, `digit_qrom_circuit`, `periodic_phase_state`.
* `tools/qft_module.py`: helper patterns for QFT family.

### CLI Experiments

* **QFT peaks**: periodic state with (q=8) → sharp peaks in frequency register.
* **PEA sanity**: diagonal unitary with known phase polynomial → recover bits of (\lambda).
* **QROM**: load digits of π (base 10/2) and verify via measurement histograms.

### Tests

* `tests/test_qft_parseval.py`: QFT unitary; norm preserved.
* `tests/test_pea_known_phase.py`: synthetic phase recovered to (k) bits.
* `tests/test_qrom_digit_consistency.py`: retrieved digits match source for first L positions.

### Expected Results & Artifacts

* Counts JSON for QFT peaks; PEA bitstring histograms; QROM correctness tables.

### Notes

* Track **endian** convention consistently between classical index and qubit order.

---

## Unit 5 — Analysis Suite: State Characterization

### Overview

Non-destructive characterization: amplitudes, basis probabilities, entropies, tomography, and **Entropy Certificates** for verification.

### Definitions & Math

* **Measurement distributions** (P_Z) and (P_X) (via H⊗n then Z).
* **Shannon entropy** (H(P)=-\sum p\log_2 p).
* **Maassen–Uffink** (QFT conjugates): (H_Z+H_X \ge n).
* **Tomography fidelity** (F(\rho,|\psi\rangle)=\langle\psi|\rho|\psi\rangle).
* **Certificate** (\mathcal{C}={H_Z, H_{QFT}, H_{\min}, \text{flatness}, ...}).

### Implementation Pointers (code)

* `QTEGUI.py.bak-neut`: *Amplitudes*, *Basis States*, *Measure*, *Tomography*, *Entropy* tabs.
* `entropy_lab.py`: `entropy_certificate_pack/verify`.
* `tools/leakage_meter.py`: leakage/randomness proxies.

### CLI Experiments (Sim & IBM)

* **Sim**: compute (H_Z), (H_{QFT}) for several fingerprints; verify MU bound numerically.
* **IBM**: run small-n states on `ibm_torino` (shots 4k) → compare empirical (H_Z) and (H_X) to ideal; attach certificate.

### Tests

* `tests/test_maassen_uffink_bound_z_qft.py`: bound holds within sampling error.
* `tests/test_tomography_fidelity_threshold.py`: > target fidelity on simulator for test states.
* `tests/test_entropy_certificate_pack_verify.py`: pack→verify stable on untouched states; detects tamper.

### Expected Results & Artifacts

* Plots of (P_Z), (P_X); CSV/JSON of entropies; certificate bundle files in `docs/results/`.

### Notes

* For hardware noise, report **confidence intervals** for entropies (bootstrap over shots).


awesome — lowest unfinished is Unit 7: Analysis Suite — The “Function Atlas.”
Here’s a tight, paper-ready unit (concept → math → code refs → CLI/IBM tests → expected results). You can paste this straight into your doc/canvas.

Unit 7 — Analysis Suite: The “Function Atlas”
7.1 Purpose & Scope

Build a geometric “atlas” of mathematical objects encoded as QTE statevectors, so related objects cluster together and families trace smooth manifolds under parameter sweeps. This unit defines metrics, reductions, clustering, and hardware-aware variants to quantify similarity and structure.

7.2 Concepts (What)

Fingerprint space. Each object → complex vector 
a∈CN
a∈C
N
 (Maclaurin/EGF/terms or QFT[...] sampling). States use 
∥a∥2=1
∥a∥
2
	​

=1.

Invariances. Global phase 
eiθ
e
iθ
 irrelevant; amplitude scaling removed by normalization; optional rail/sign-split encodes sign explicitly when needed.

Views. Compare in:

State space: complex inner product / fidelity on 
∣ψ⟩
∣ψ⟩.

Measurement space: Z-basis probs 
p=∣ψ∣2
p=∣ψ∣
2
; QFT-basis probs 
p~=∣QFT ψ∣2
p
~
	​

=∣QFTψ∣
2
.

Marginals: per-register distributions for multi-register states.

7.3 Mathematics (How)
7.3.1 Core similarity metrics

State fidelity: 
F(ψ,ϕ)=∣⟨ψ∣ϕ⟩∣2
F(ψ,ϕ)=∣⟨ψ∣ϕ⟩∣
2
. Phase-invariant and unitary-invariant.

Cosine similarity (complex):

Sc(a,b)=Re ⟨a,b⟩∥a∥2 ∥b∥2,⟨a,b⟩=∑nan‾bn.
S
c
	​

(a,b)=
∥a∥
2
	​

∥b∥
2
	​

Re⟨a,b⟩
	​

,⟨a,b⟩=
n
∑
	​

a
n
	​

	​

b
n
	​

.

Distribution distances (on 
p,p~
p,
p
~
	​

 or marginals):

Total variation: 
TV(p,q)=12∑i∣pi−qi∣
TV(p,q)=
2
1
	​

∑
i
	​

∣p
i
	​

−q
i
	​

∣.

Hellinger: 
H(p,q)=12∥p−q∥2
H(p,q)=
2

# Unit 6 — Spectral Analysis: Classical FFT vs. Quantum Fourier Transform (QFT)

**Objective.** Establish a rigorous bridge between classical spectral analysis (DFT/FFT) and quantum spectral analysis (QFT), then define testable experiments (sim & IBM hardware) that certify correctness, normalization, endianness, and uncertainty relations.

---

## 6.1 Concepts & Guarantees

* **Classical DFT/FFT (length N=2^n).** For a complex vector (x\in\mathbb{C}^N),
  [ X_k
  = \sum_{m=0}^{N-1} x_m, e^{-2\pi i mk/N},\qquad 0\le k<N. ]
  Parseval: (\sum_m |x_m|^2 = \tfrac1N \sum_k |X_k|^2).

* **Quantum Fourier Transform on n qubits (dimension d=2^n).**
  [ \mathrm{QFT}_d : |m\rangle \mapsto \frac{1}{\sqrt{d}} \sum_{k=0}^{d-1} e^{2\pi i mk/d},|k\rangle. ]
  For a state (|\psi\rangle=\sum_m a_m|m\rangle), the post-QFT state has amplitudes (\tilde a_k = \tfrac{1}{\sqrt{d}} \sum_m a_m e^{2\pi i mk/d}). The **QFT measurement distribution** is (p_k = |\tilde a_k|^2).

* **Link (FFT ↔ QFT).** If we take the classical vector of **amplitudes** (a) and apply FFT with a unitary normalization ((1/\sqrt{d})), then (|\mathrm{FFT}(a)|^2) equals the QFT measurement distribution (p), up to implementation choices (global phase, index/endianness, and sign in the kernel).

* **Entropic Uncertainty (Maassen–Uffink).** For (d=2^n), with (H_Z) the Shannon entropy of Z-basis measurement and (H_X) that of the QFT basis, (H_Z + H_X \ge \log_2 d = n) (base-2 logs). Equality holds for Fourier pairs like a computational basis state vs. uniform superposition.

* **Short-Time QFT (ST-QFT).** Windowed analysis: split the register into segment(s) or apply window functions before a local QFT to form a spectrogram analogue.

---

## 6.2 Math Details to Cite in Paper

1. **Normalizations.** We adopt the *unitary* DFT: (F_{km} = \tfrac{1}{\sqrt{d}} e^{2\pi i km/d}). Then (F) is unitary: (F^\dagger F = I), guaranteeing Parseval in the quantum sense: (|a|_2=|\tilde a|_2).
2. **Indexing & Endianness.** If the implementation uses little-endian qubit order, the integer map is (m=\sum_{j=0}^{n-1} 2^j b_j) with bit (b_0) the *least significant*. Our tests include a reversible bit-order map to compare spectra consistently.
3. **Kernel Sign.** We choose + sign in the QFT kernel ((e^{+2\pi i mk/d})); classical FFT often uses a minus sign in the forward transform. We reconcile via conjugation or by comparing power spectra only (magnitudes are sign-invariant).
4. **Windowing (Hann).** (w[m]=\tfrac12\left(1-\cos(2\pi m/(M-1))\right)). ST-QFT applies (w) to a block then QFT that block; spectrogram magnitude squared is blockwise (|F(w\odot a) |^2).

---

## 6.3 Code Map (QTE tree)

* **QFT Circuits**

  * `quantum_embedding.py`: `qft(n, swap_endian=True)`, `st_qft(...)` (short-time)
  * `tools/qft_module.py`: helpers for bit order, canonical QFT decomposition
* **Classical Spectral Tools**

  * `harmonic_analysis.py`: `power_spectrum(a, center=True, window='hann')`
  * `tools/lct_czt.py`: fractional/linear–chirp transforms (referenced but used in U9)
* **State Prep & Labels**

  * `series_encoding.py`: `generate_series_encoding(label=..., amp_mode=..., phase_mode=...)`
  * `periodic_phase_state(...)` (for discrete tones p/q)
* **GUI**

  * `QTEGUI.py*`: tabs **FFT Spectrum**, **QFT Spectrum**, **Amplitudes** (plotting & export)
* **Tests**

  * `tests/test_fft_invariants.py`: Parseval & energy localization
  * `tests/test_qft_parseval.py`: QFT unitary & (|a|=|\tilde a|)
  * `tests/test_maassen_uffink_bound_z_qft.py`: (H_Z+H_X\ge n)

---

## 6.4 CLI Experiments (Simulator)

### Exp. 6A — FFT↔QFT Consistency (Unitary DFT)

**Goal.** (|\mathrm{FFT}(a)|^2) matches QFT measurement distribution.

```bash
# Prepare an amplitude vector via label sampling (smooth tone with noise)
./qte_cli.py --nq 8 \
  --label "QFT[cos(2*pi*5*x) + 0.1*sin(2*pi*11*x); N=256; a=0; b=1]" \
  --dump states/tone.npy

# Classical spectrum (unitary FFT) and save JSON
./qte_cli_ext.py fft --load-state states/tone.npy \
  --unitary --center \
  --out-json docs/results/u6_exp6A_fft.json

# QFT spectrum (apply qft circuit then measure)
./qte_cli_ext.py qft --n 8 --load-state states/tone.npy \
  --shots 8192 \
  --out-json docs/results/u6_exp6A_qft.json

# Compare within tolerance (JS divergence / Earth-Mover)
./qte_cli_ext.py spec-compare \
  --fft-json docs/results/u6_exp6A_fft.json \
  --qft-json docs/results/u6_exp6A_qft.json \
  --metric js --tol 5e-2
```

**Acceptance.** `spec-compare` returns `ok: true`; peaks at k≈5 and 11 align (within aliasing tolerance).

### Exp. 6B — Entropic Uncertainty (Tight Instances)

**Goal.** Validate (H_Z+H_X\ge n) and near-equality for Fourier pairs.

```bash
# A: Z-basis delta (|0...0>) → uniform in X
./qte_cli_ext.py make --n 8 --basis-zero --dump states/delta.npy
./qte_cli_ext.py entropy --load-state states/delta.npy --basis Z
./qte_cli_ext.py qft --n 8 --load-state states/delta.npy --shots 8192 --dump states/delta_qft.npy
./qte_cli_ext.py entropy --load-state states/delta_qft.npy --basis Z > docs/results/u6_exp6B_delta.json

# B: Uniform in Z (H^{⊗n}|0>) → delta in X
./qte_cli_ext.py make --n 8 --uniform --dump states/uniform.npy
./qte_cli_ext.py entropy --load-state states/uniform.npy --basis Z
./qte_cli_ext.py qft --n 8 --load-state states/uniform.npy --shots 8192 --dump states/uniform_qft.npy
./qte_cli_ext.py entropy --load-state states/uniform_qft.npy --basis Z > docs/results/u6_exp6B_uniform.json
```

**Acceptance.** Both runs satisfy (H_Z+H_X\ge 8) within ±0.03 bits; pair A nearly saturates bound (~0 + 8), pair B similarly (~8 + 0).

### Exp. 6C — Short-Time QFT (Spectrogram)

**Goal.** Detect a piecewise-frequency signal via windowed QFT blocks.

```bash
# Construct a two-tone piecewise signal on 8 qubits (N=256)
./qte_cli.py --nq 8 --label "QFT[piecewise_cos(5;0:127) + piecewise_cos(13;128:255); N=256]" \
  --dump states/pw.npy

# ST-QFT with Hann window, block=32
./qte_cli_ext.py stqft --n 8 --load-state states/pw.npy \
  --block 32 --hop 16 --window hann \
  --out-json docs/results/u6_exp6C_stqft.json --plot docs/results/u6_exp6C_stqft.png
```

**Acceptance.** Spectrogram shows a horizontal band at k≈5 for the first half and at k≈13 for the second, with window leakage < −20 dB.

---

## 6.5 IBM Hardware Experiments (NISQ-safe)

> *Note.* Avoid `initialize` for large-N state prep; use states with shallow prep.

### Exp. 6H–1 — QFT of a Uniform Superposition

```bash
# Prepare H^{⊗n}|0> then apply exact QFT(n) and measure
./qte_cli_ext.py make --n 4 --uniform --dump states/h4.npy
./tools/run_on_ibm_torino.py --backend torino --n 4 --task qft \
  --load-state states/h4.npy --shots 8192 --out docs/results/u6_hardware_qft_uniform.json
```

**Prediction.** Post-QFT distribution sharply peaked at |0000⟩ (k=0) with fidelity ≥ 0.9 (device/noise dependent). Acceptance: peak ≥70% of counts; bit-ordering verified.

### Exp. 6H–2 — Periodic Phase State → Comb in QFT

```bash
# Build periodic phase state |ψ_p/q> (exact with low-depth phase rotations)
./qte_cli_ext.py periodic --n 5 --p 3 --q 32 --dump states/pps.npy
./tools/run_on_ibm_torino.py --backend torino --n 5 --task qft \
  --load-state states/pps.npy --shots 8192 --out docs/results/u6_hardware_qft_comb.json
```

**Prediction.** A comb with teeth separated by q/d; acceptance: KL divergence to ideal comb ≤ 0.2.

---

## 6.6 Result File Schemas (JSON)

```json
// docs/results/u6_exp6A_fft.json
{
  "signal": "states/tone.npy",
  "n": 8,
  "norm": "unitary",
  "center": true,
  "spectrum": [ {"k": 0, "power": 0.0012}, ... ]
}
```

```json
// docs/results/u6_exp6A_qft.json
{
  "backend": "aer_simulator",
  "n": 8,
  "shots": 8192,
  "counts": {"00010101": 73, ...},
  "p": [ {"k": 0, "prob": 0.0011}, ... ],
  "endianness": "little"
}
```

```json
// docs/results/u6_exp6C_stqft.json
{
  "n": 8,
  "block": 32,
  "hop": 16,
  "window": "hann",
  "tiles": [ {"frame": 0, "k": 5, "power": 0.92}, ... ]
}
```

---

## 6.7 Troubleshooting & Pitfalls

* **Bit Reversal.** QFT implementations often include a final qubit-reversal swap. Our plotting tools reverse bits (if `swap_endian=True`) before indexing.
* **Kernel Sign & Global Phase.** Compare **powers** (magnitudes) to avoid sign-phase confusion.
* **Normalization Drift.** Ensure unitary FFT; otherwise rescale by (1/\sqrt{d}).
* **Window Leakage.** Hann reduces sidelobes; verify with a tone-at-bin vs off-bin test.
* **Hardware Depth.** Use low-depth prep (uniform, periodic-phase states) for NISQ runs.

---

## 6.8 What Goes Into the Paper

* Formal statement and proof sketch of the FFT↔QFT power-spectrum equivalence under unitary normalization.
* Empirical figures: (i) FFT vs QFT spectra overlay, (ii) uncertainty plots (H_Z, H_X), (iii) ST-QFT spectrogram, (iv) IBM hardware histograms with theoretical overlays.
* Repro appendix: CLI commands above and test references.

---

# Unit 7 — The “Function Atlas” (Stub)

> **To be filled next:** definition of metric space over fingerprints, cosine similarity matrix construction, PCA/t-SNE maps, clustering validity indices, and CLI for atlas export; plus IBM validation via QFT marginals.






# QTE Curriculum — Part B (Units 5–7) — Continuation

> This canvas continues the curriculum with **Unit 5** in full detail. Units 6–7 headers are stubbed and will be filled next so we keep ≤5 units per canvas.

---

# Unit 5 — Analysis Suite: State Characterization

## 5.1 Purpose & Scope

Provide rigorous, reproducible diagnostics of a prepared (n)-qubit state (|\psi\rangle) in the computational (Z) basis and in other analysis bases (e.g., (X) via Hadamard pre-rotations). Outputs include probability histograms, entropy metrics, marginals, and (optionally) full state tomography with fidelity to an ideal reference.

**Primary questions:**

* What probabilities (p_z(b)) over bitstrings (b\in{0,1}^n) does the state produce in the (Z) basis?
* How flat/structured are these distributions (Shannon entropy, min-entropy, KL divergence to uniform)?
* Do the entropies across incompatible bases obey the Maassen–Uffink bound?
* What is the state fidelity to an ideal target (via tomography on simulators/hardware)?

---

## 5.2 Mathematical Definitions

Let (p_Z(b) = |\langle b|\psi\rangle|^2). For the (X)-basis, implement a global Hadamard: (p_X(b) = |\langle b|H^{\otimes n}|\psi\rangle|^2).

* **Shannon entropy (bits):** (H(p) = -\sum_b p(b), \log_2 p(b)).
* **Min-entropy (bits):** (H_\min(p) = -\log_2 \max_b p(b)).
* **KL divergence to uniform:** (D_{\mathrm{KL}}(p,|,u) = \sum_b p(b) \log_2 \frac{p(b)}{1/2^n}).
* **Maassen–Uffink entropic uncertainty:** For complementary observables (e.g., (Z) and (X)),
  [ H_Z + H_X \ge n. ]
* **Tomographic fidelity:** (F(\rho, \sigma) = \left( \mathrm{Tr},\sqrt{\sqrt{\rho},\sigma,\sqrt{\rho}} \right)^2). For pure target (|\psi_\mathrm{ideal}\rangle): (F = \langle \psi_\mathrm{ideal}|\rho|\psi_\mathrm{ideal}\rangle).

---

## 5.3 Code Map (Files & Key Symbols)

**GUI / Orchestration**

* `QTEGUI.py.bak-neut`

  * **Measure tab**: renders (Z)-basis histograms, toggles for global-H ((X) basis), log magnitude, cumulative metrics.
  * **Tomography tab**: runs qiskit-experiments state tomography and reports fidelity.
  * **Marginals**: per-register and per-subsystem histograms; helper `_schmidt_entropy_bits(sv, cut)` for bipartite entropy.

**Metrics & Certificates**

* `entropy_lab.py`

  * `entropy_certificate_pack(statevec_or_counts, bases=("Z","X"), ...) -> dict`
    Computes (H_Z, H_X, H_\min), flatness, KL to uniform; packs into a portable JSON.
  * `entropy_certificate_verify(candidate, certificate, tol=...) -> bool`
    Recomputes metrics and checks deltas within tolerance.

**Helpers / Analysis**

* `harmonic_analysis.py`
  Classical FFT helpers (used by Unit 6 too) – windowing, centering, log-power.
* `quantum_embedding.py`

  * `generate_series_encoding(...) -> QuantumCircuit | np.ndarray`
    Produces ideal statevectors for known labels (used as ground-truth in tests/tomography).

**Tests (existing or to finalize here)**

* `tests/test_maassen_uffink_bound_z_qft.py` — asserts (H_Z + H_X \ge n) for representative states.
* `tests/test_bell_state_entropy_one.py` — verifies 1 ebit entanglement and entropy patterns for Bell states.
* `tests/test_fft_invariants.py` — Parseval/unitarity invariants (shared with Unit 6).

---

## 5.4 CLI Workflows (Local & Hardware)

> **Convention:** All CLI invocations write JSON artifacts to `docs/results/` with a deterministic filename so downstream steps can consume them.

### 5.4.1 Local (Simulator) — Z/X Entropies + Certificate

1. **Prepare an ideal statevector** (example: periodic phase state with period (q=16)):

```bash
./qte_cli.py --nq 4 \
  --label "periodic_phase_state[p=1,q=16]" \
  --dump states/pps_q16.npy
```

2. **Compute Z/X entropies and pack a certificate:**

```bash
./qte_cli_ext.py characterize \
  --load-state states/pps_q16.npy \
  --bases Z X \
  --out docs/results/unit5_pps_q16_entropy.json
```

**Output (schema excerpt):**

```json
{
  "n": 4,
  "bases": {
    "Z": {"H": 2.00, "Hmin": 1.00, "KL_to_uniform": 0.00},
    "X": {"H": 4.00, "Hmin": 4.00, "KL_to_uniform": 0.00}
  },
  "MU_sum_bits": 6.00,
  "MU_bound_bits": 4,
  "pass_MU": true
}
```

### 5.4.2 Local — Tomography vs. Ideal

```bash
./qte_cli_ext.py tomography \
  --load-state states/pps_q16.npy \
  --shots 4096 \
  --out docs/results/unit5_pps_q16_tomo.json
```

**Output keys:** `fidelity`, `trace_distance`, `basis_counts` (per measurement setting).

### 5.4.3 Hardware (IBM) — Z/X Histograms + Entropies

> Requires your IBM account saved and `tools/run_on_ibm_torino.py` configured. If your environment only supports SamplerV1-with-session, use the session fallback in that script.

1. **Build & transpile the target circuit** (example via `qte_cli_ext.py`):

```bash
./qte_cli_ext.py build \
  --nq 4 --label "periodic_phase_state[p=1,q=16]" \
  --out-circ tmp/pps_q16.qpy
```

2. **Run on hardware in Z-basis:**

```bash
python tools/run_on_ibm_torino.py \
  --backend torino --shots 4096 \
  --load-qpy tmp/pps_q16.qpy \
  --out docs/results/unit5_pps_q16_Z_hardware.json
```

3. **Run on hardware in X-basis** (global H added):

```bash
python tools/run_on_ibm_torino.py \
  --backend torino --shots 4096 --basis X \
  --load-qpy tmp/pps_q16.qpy \
  --out docs/results/unit5_pps_q16_X_hardware.json
```

4. **Post-compute entropies from hardware counts:**

```bash
./qte_cli_ext.py characterize \
  --load-counts docs/results/unit5_pps_q16_Z_hardware.json \
  --load-counts-X docs/results/unit5_pps_q16_X_hardware.json \
  --out docs/results/unit5_pps_q16_entropy_hw.json
```

---

## 5.5 Experiments & Acceptance Criteria

### E5.1 — Maassen–Uffink (Z vs. X) on Structured & Random States

* **Targets:** periodic phase state; random Haar state (simulator); Bell states.
* **Checks:** for each state, compute (H_Z, H_X, H_Z+H_X) and assert (H_Z+H_X \ge n).
* **Acceptance:** `pass_MU == true` for all; report margins ((H_Z+H_X) - n).
* **Test file:** `tests/test_maassen_uffink_bound_z_qft.py`.

### E5.2 — Tomographic Fidelity on Sim vs. Hardware

* **Target:** Bell state (|\Phi^+\rangle) and one structured QSE state.
* **Checks:** tomography fidelity to ideal.
* **Acceptance (typical):**

  * **Simulator:** (F \ge 0.98)
  * **Hardware (n≤4):** (F \ge 0.75) (Torino-like devices; adjust per backend calibration)
* **Test file:** `tests/test_bell_state_entropy_one.py` (plus `*_tomo.py` if separated).

### E5.3 — Certificate Stability (Z/X) Under Small Noise

* **Target:** same as E5.2 with added readout noise (sim or hardware).
* **Checks:** `entropy_certificate_pack` then remeasure; verify deltas within `tol`.
* **Acceptance:** `entropy_certificate_verify == true` with `tol` tuned (e.g., `ΔH ≤ 0.15` bits).
* **Test file:** `tests/test_entropy_certificate_stability.py` (new).

---

## 5.6 JSON Artifacts (Schemas)

**Characterization result** `unit5_*_entropy.json`:

```json
{
  "n": <int>,
  "backend": "simulator" | "ibm_torino" | "...",
  "bases": {
    "Z": {"H": <float>, "Hmin": <float>, "KL_to_uniform": <float>},
    "X": {"H": <float>, "Hmin": <float>, "KL_to_uniform": <float>}
  },
  "MU_sum_bits": <float>,
  "MU_bound_bits": <int>,
  "pass_MU": true,
  "counts": {"Z": {...}, "X": {...}}
}
```

**Tomography result** `unit5_*_tomo.json`:

```json
{
  "n": <int>,
  "fidelity": <float>,
  "trace_distance": <float>,
  "shots": <int>,
  "basis_counts": {
    "Z": {...}, "X": {...}, "Y": {...}
  }
}
```

---

## 5.7 Troubleshooting Notes (IBM Runtime)

* If `SamplerV2(backend=...)` is unavailable, construct **SamplerV1 with Session** or use the script’s fallback path. Ensure the script passes a backend/session to the primitive.
* If `backend.run(...)` is disallowed by your runtime version, use `Sampler` or `Estimator` primitives only.
* Shot counts for entropy estimation should be (\ge 4096) for stable metrics at (n\le4); increase with (n).

---

# Unit 6 — Analysis Suite: Spectral Analysis (FFT & QFT)

> **Stub (to be filled next):** classical FFT flow (windowing, centering, Parseval); QFT circuit flow; cross-checks; CLI; tests.

# Unit 7 — Analysis Suite: The Function Atlas

> **Stub (to be filled next):** cosine similarity, PCA, clustering; marginal- and register-aware embeddings; CLI; tests.







# Unit 11 — Application: Payload & Entropy Certification (Verifiable Quantum Encryption)

## Concept & Goals

**Problem:** Privacy + verification for cloud quantum runs.
**Solution:** Encrypt payload state with a keyed, nonce’d unitary (U_{K,\nu}) and verify integrity with an **Entropy Certificate** computed on the unscrambled state.

**Workflow:**

1. Pack certificate on clean payload (|\psi_\text{payload}\rangle): (\text{Cert}*\text{in}=\text{Pack}(|\psi*\text{payload}\rangle)).
2. Scramble: (|\psi_\text{scrambled}\rangle=U_{K,\nu}|\psi_\text{payload}\rangle). Send to cloud.
3. Cloud applies computation: (|\psi_\text{scrambled}'\rangle = U_\text{compute}|\psi_\text{scrambled}\rangle).
4. Client unscrambles: (|\psi_\text{payload}'\rangle=U_{K,\nu}^\dagger|\psi_\text{scrambled}'\rangle).
5. Verify: (\text{Verify}(|\psi_\text{payload}'\rangle, \text{Cert}_\text{in}) \stackrel{?}{=} \text{True}).

## Formal Definitions

Let (p_Z) be the Z-basis outcome distribution, (p_F) be the distribution after QFT.

* **Shannon entropy:** (H(p)=-\sum_i p_i\log p_i).
* **Min-entropy:** (H_\min(p)=-\log\max_i p_i).
* **KL to uniform:** (D_{KL}(p\Vert u)=\sum_i p_i\log\frac{p_i}{1/d}), (d=2^n).
* **Flatness:** (\mathrm{flat}(p)=\frac{|p|_2^2-1/d}{1-1/d}\in[0,1]).

**Certificate vector (example):**
[ \mathcal{C} = { H(p_Z),; H(p_F),; H_\min(p_Z),; H_\min(p_F),; D_{KL}(p_Z\Vert u),; D_{KL}(p_F\Vert u),; \mathrm{flat}(p_Z),; \mathrm{flat}(p_F) }. ]

**Security hypothesis (IND-CPA-style):** Averaging the scrambled state over nonces
(\bar{\rho}=\mathbb{E}*\nu\big[ U*{K,\nu}|\psi\rangle\langle\psi|U_{K,\nu}^\dagger \big]) satisfies
( \tfrac12|\bar{\rho}-I/d|_1 \le \varepsilon ).

## Code References

* **Scrambler:** `qe_crypto/unitary_cipher.py` — `cipher_u(...)`, `phase_poly(...)`.
* **PRF:** `qe_crypto/primitives.py` — `prf_bits(...)`.
* **Entropy cert:** `entropy_lab.py` — `entropy_certificate_pack(...)`, `entropy_certificate_verify(...)`.
* **End-to-end demo:** `tools/demo_payload_flow.py`.
* **Support:** `qe_crypto/teleport_auth.py`, `qe_crypto/nonce_ledger.py`, `qe_crypto/phase_mix.py`.
* **Hardware runner (optional):** `tools/run_on_ibm_torino.py`.

## CLI Experiments

**A. Happy path (no tampering)**

```bash
./tools/demo_payload_flow.py --n 8 --payload-int 42 --key "my-key" --json
```

*Expected:* `"verify_ok": true`, all entropy deltas ~ 0 within tolerance.

**B. Tampered path**

```bash
./tools/demo_payload_flow.py --n 8 --payload-int 42 --key "my-key" --tamper --json
```

*Expected:* `"verify_ok": false`, noticeable increases in KL and |ΔH|.

**C. Hardware sanity (optional)**

```bash
# run a shallow cipher on torino (sessionless-capable Sampler build)
./tools/run_on_ibm_torino.py --backend torino --n 4 --rounds 2 --shots 4096 --basis X
```

*Expected:* Hardware noise inflates H(p_Z) and reduces peaks vs. simulator; certificate still verifies on unscramble.

## Tests & Acceptance

* `tests/test_demo_payload_flow.py` — happy vs. tamper paths (pass/fail).
* `tests/test_crypto_ind_cpa.py` — (\tfrac12|\bar{\rho}-I/d|_1\le\tau) (e.g., (\tau=0.2)).
* `tests/test_entropy_lab.py` — invariance of (\mathcal{C}) under `cipher_u` followed by inverse.

**Acceptance thresholds (suggested):**

* Happy path: all |Δ entropy| (< 0.05); verify_ok = true.
* Tamper path: at least one metric delta (> 0.15); verify_ok = false.

## Artifacts

* JSON run record with `backend`, `metrics`, `job_id`, output path.
* Certificate files (YAML/JSON) + corresponding state `.npy` snapshots.
* Plots: Z vs. QFT entropy bars; KL vs. uniform.

---

# Unit 12 — Vertical: Quantum Dynamics (Koopman & Chaos)

## Concept & Goals

Two complementary studies:

1. **Classical chaos via Koopman operator (EDMD)** on logistic map data.
2. **Quantum chaos** of your PRF-driven scrambler via the **Spectral Form Factor (SFF)**.

## Formal Pieces

**Koopman (EDMD):** For observable lift (\Phi(x)), learn (K) minimizing (|K\Phi(x_t)-\Phi(x_{t+1})|). Use SVD/pseudoinverse: (K = G^\dagger A) with (G=\sum \Phi(x_t)\Phi(x_t)^\top), (A=\sum \Phi(x_t)\Phi(x_{t+1})^\top).

**Spectral Form Factor:** For unitary (U), (K(t)=|\mathrm{Tr}(U^t)|^2). Chaotic systems (CUE-like) show **dip–ramp–plateau** after smoothing; integrable circuits do not.

## Code References

* **Koopman demo:** `scripts/koopman_demo_logistic.py`.
* **SFF / chaos tools:** `physics/kubo_otoc_sff.py` — `spectral_form_factor(...)`.
* **Chaotic unitary:** `qe_crypto/unitary_cipher.py` — `cipher_u(...)`.
* **CLI glue:** `qte_cli_ext.py` — `sff` subcommand.

## CLI Experiments

**A. Koopman fit (logistic map)**

```bash
python scripts/koopman_demo_logistic.py --N 2000 --lift poly3 --out docs/results/koopman_logistic.json
```

*Expected:* eigenvalues near unit circle; 1-step prediction MSE ≪ variance of series.

**B. SFF: integrable vs. chaotic**

```bash
# QFT (integrable-ish baseline)
./qte_cli_ext.py sff --src qft --n 6 --t 1
./qte_cli_ext.py sff --src qft --n 6 --t 2
...
# Cipher (chaotic)
./qte_cli_ext.py sff --src cipher --n 6 --rounds 5 --t 1
./qte_cli_ext.py sff --src cipher --n 6 --rounds 5 --t 2
...
```

*Expected:* QFT: spiky/irregular; Cipher: smoothed dip–ramp–plateau after modest averaging over random seeds.

**C. Hardware sanity (optional)**

```bash
./tools/run_on_ibm_torino.py --backend torino --n 5 --rounds 2 --shots 4096 --basis Z
```

*Expected:* Increasing rounds → higher Z/QFT entropies; qualitative scrambling trend survives noise.

## Tests & Acceptance

* `tests/test_koopman_edmd.py` — reconstruction error on held-out data below threshold (e.g., MSE < 0.02 after scaling).
* `tests/test_sff_cipher_vs_qft.py` — cipher’s smoothed K(t) exhibits monotone ramp region; QFT does not.

**Acceptance thresholds (suggested):**

* EDMD: stable spectrum; prediction R² > 0.8 on validation slice.
* SFF: after averaging over ≥16 PRF seeds, ramp slope > 0 for a window t∈[t₁,t₂]; plateau variance small.

## Artifacts

* Koopman JSON: basis, Gram/fit diagnostics, spectrum.
* SFF CSVs per t and seed; aggregated plot PNGs.
* Notebooks (optional) for figures included in paper.

## Notes

* SFF trace can be estimated with Hutchinson-style estimators for larger n if exact trace is infeasible.
* Noise mitigation (readout calibration) helps stabilize entropy/SFF qualitative trends on hardware.





# Unit 7 — The “Function Atlas” (Similarity, PCA & Clustering of Quantum Fingerprints)

## 7.1 Concept & Goal

We build a **geometric atlas** of your encoded objects (constants, series, functions) by turning each state (|\psi_i\rangle) into a feature vector and comparing them with mathematically principled similarities. The atlas lets you:

* quantify **similarity/dissimilarity** between fingerprints,
* visualize structure via **PCA/embeddings**, and
* discover **clusters** that reflect shared analytic structure (e.g., polylog vs. Bessel vs. trigonometric families).

This unit is purely analysis; it consumes saved fingerprints/states produced by Units 2–4.

---

## 7.2 Mathematics

### 7.2.1 Vectorizations

Let (x_i \in \mathbb{C}^{N}) be the amplitude vector of (|\psi_i\rangle).

Common feature maps:

* **Amplitude magnitudes**: (v_i = |x_i|) or (p_i = |x_i|^2) (probabilities).
* **Phase-aware split** (sign/IQ packing used in QTE): concatenate real/imag or sign-split rails to keep phase while remaining in (\mathbb{R}) for downstream linear algebra.

Normalize features to unit (\ell_2)-norm unless stated.

### 7.2.2 Similarities / Distances

* **Cosine similarity**: ( s_{ij}=\dfrac{\langle v_i, v_j\rangle}{|v_i|,|v_j|}\in[-1,1] ).
* **Jensen–Shannon distance** for probabilities (p_i, p_j):
  [
  \mathrm{JSD}(p_i,p_j)=\sqrt{\tfrac{1}{2}D_{\mathrm{KL}}(p_i\Vert m)+\tfrac{1}{2}D_{\mathrm{KL}}(p_j\Vert m)},\ \ m=\tfrac{1}{2}(p_i+p_j).
  ]
  (Well-defined, symmetric, metric.)
* **Fidelity** (optional physics metric): (F(\psi_i,\psi_j)=|\langle \psi_i|\psi_j\rangle|^2).

### 7.2.3 Embedding & Clustering

* **PCA**: compute covariance (C=\frac{1}{M-1}V^\top V), take top eigenpairs to map (v_i \mapsto y_i \in \mathbb{R}^2).
* **Spectral clustering** (optional): graph Laplacian from similarity matrix to separate nonlinearly separable families.

---

## 7.3 Implementation (Code Pointers)

* **State generation** (existing):

  * `series_encoding.py` — builds classical fingerprints and statevectors.
  * `quantum_embedding.py` — prepares circuits/initializes states.
* **New (lightweight, CLI-first analysis tool):**

  * `tools/function_atlas.py`

    * Loads `.npy` vectors or `.npz` bundles of states.
    * Computes cosine/JSD matrices, PCA embeddings.
    * Emits JSON/CSV/PNG artifacts (matrix, scatter).
* **Tests (new):**

  * `tests/test_function_atlas.py`

    * Validates metric properties (symmetry, ranges), PCA shape/variance, and sanity separations on toy families.

> If you prefer no new deps, PCA is implemented via `numpy.linalg.svd`; JSD uses only NumPy (with safe eps guards).

---

## 7.4 CLI Experiments (Reproducible & Paper-Ready)

### 7.4.1 Build a small atlas from known families

Create 6–10 exemplars per family; (N=2^n) with (n\in{8,10}).

```bash
# Trig family
python tools/paper_batch.py \
  --out states/trig/ --family trig --forms "sin,cos" --k 1:6 --nq 10 --mode amp-egf

# Bessel family (J0 at varied scale)
python tools/paper_batch.py \
  --out states/bessel/ --family bessel --orders "0" --scale 0.5:3.0:0.5 --nq 10 --mode amp-egf

# Polylog family Li_s(z) at varied s (or varied |z|)
python tools/paper_batch.py \
  --out states/polylog/ --family polylog --s 1.2,1.5,2.0,2.5 --z 0.5,0.7,0.9 --nq 10 --mode amp-egf
```

> If `tools/paper_batch.py` isn’t in the repo, you can generate the same sets with your existing `series_encoding.py` helper or GUI scripts; the atlas step only needs saved `.npy` vectors.

### 7.4.2 Compute similarities + PCA and export artifacts

```bash
# Cosine + JSD across all families
python tools/function_atlas.py matrix \
  --glob "states/*/*.npy" \
  --feature prob \
  --metrics cosine,jsd \
  --out-dir atlas/out

# PCA (2D) with cosine kernel; write JSON+PNG scatter
python tools/function_atlas.py pca \
  --glob "states/*/*.npy" \
  --feature prob \
  --metric cosine \
  --out atlas/out/pca_cosine.json \
  --plot atlas/out/pca_cosine.png

# Optional: spectral clustering (k=3 suggested for {trig, bessel, polylog})
python tools/function_atlas.py cluster \
  --matrix atlas/out/cosine_matrix.npy \
  --method spectral --k 3 \
  --out atlas/out/labels_spectral.json
```

---

## 7.5 Predicted / Interpretable Results

* **Cosine/JSD matrices**: near-block-diagonal structure (intra-family high similarity / low distance; inter-family low similarity / higher distance).
* **PCA scatter**: three visibly separated lobes (trig vs. Bessel vs. polylog). Within families, parameters (e.g., frequency (k), order/scale) trace smooth manifolds.
* **Clustering**: spectral (k=3) recovers families with high purity (>90%) on synthetic sets.

These provide objective evidence that QTE fingerprints respect analytic class structure.

---

## 7.6 Tests (PyTest)

```python
# tests/test_function_atlas.py

def test_cosine_range_and_symmetry(load_example_vectors):
    S = cosine_matrix(load_example_vectors)
    assert np.allclose(S, S.T, atol=1e-8)
    assert S.min() >= -1 - 1e-8 and S.max() <= 1 + 1e-8

def test_jsd_metric_properties(load_example_probs):
    D = jsd_matrix(load_example_probs)
    assert np.allclose(D, D.T, atol=1e-8)
    assert np.all(D.diagonal() < 1e-12)
    assert np.all(D >= -1e-12)  # nonnegativity

def test_pca_shapes_and_variance(load_example_vectors):
    Y, var = pca_2d(load_example_vectors)
    assert Y.shape[1] == 2
    assert var[0] >= var[1] >= 0

def test_family_separation_small_benchmark(example_dataset_labels):
    # Quick smoke: mean intra-family cosine > mean inter-family cosine
    S, labels = precomputed_cosine(), example_dataset_labels
    intra, inter = summarize_intra_inter(S, labels)
    assert intra.mean() > inter.mean()
```

---

## 7.7 IBM Option (Optional, for end-to-end realism)

You can **swap in hardware-sampled** distributions for one subset (e.g., some trig states) and re-run the atlas to measure robustness under noise:

```bash
# Prepare & run a few fingerprints on hardware (existing runner)
python tools/run_on_ibm_torino.py --backend torino --n 5 --rounds 1 --shots 4096 \
  --basis Z --out docs/results/trig_hardware_counts.json

# Convert counts → probability vectors, save alongside .npy set, then:
python tools/function_atlas.py matrix \
  --glob "states/trig/*.npy docs/results/trig_hardware/*.npy" \
  --feature prob --metrics cosine,jsd --out-dir atlas/out_hw
```

**Expectation:** hardware points remain in their family neighborhood with slight radial drift (noise increases JSD), quantitatively illustrating hardware impact while preserving global geometry.

---

## 7.8 Failure Modes & Diagnostics

* **Scale leakage**: differing vector norms bias cosine; always normalize.
* **Phase aliasing**: if you need phase sensitivity, use sign-split/IQ features and compare via real inner products.
* **Sparse vectors**: add (\epsilon) safeguards before (\log) in KL/JSD.
* **Mixed bases**: don’t mix Z-basis and transformed (QFT/Hankel) features in the same atlas unless explicitly intended.

---

## 7.9 Extensions

* **Kernelized PCA** with fidelity kernel (K_{ij}=|\langle\psi_i|\psi_j\rangle|^2).
* **t-SNE/UMAP** overlays for non-linear structure (purely offline).
* **Atlas over marginals**: compute similarities on per-register marginals to study subsystem structure.

---

### Minimal `tools/function_atlas.py` (skeleton signatures you can implement/expand)

* `load_vectors(glob, feature="prob"|"amp"|"iq") -> np.ndarray, labels`
* `cosine_matrix(V) -> np.ndarray`
* `jsd_matrix(P) -> np.ndarray`
* `pca_2d(V) -> (Y, var_explained)`
* `plot_scatter(Y, labels, out_png)`

(If you’d like, I can draft this file and the corresponding `tests/test_function_atlas.py` in the next step.)





Unit 7 — The “Function Atlas” (Similarity, PCA & Clustering of Quantum Fingerprints)
7.1 Concept & Goal

We build a geometric atlas of your encoded objects (constants, series, functions) by turning each state 
∣ψi⟩
∣ψ
i
	​

⟩ into a feature vector and comparing them with mathematically principled similarities. The atlas lets you:

quantify similarity/dissimilarity between fingerprints,

visualize structure via PCA/embeddings, and

discover clusters that reflect shared analytic structure (e.g., polylog vs. Bessel vs. trigonometric families).

This unit is purely analysis; it consumes saved fingerprints/states produced by Units 2–4.

7.2 Mathematics
7.2.1 Vectorizations

Let 
xi∈CN
x
i
	​

∈C
N
 be the amplitude vector of 
∣ψi⟩
∣ψ
i
	​

⟩.

Common feature maps:

Amplitude magnitudes: 
vi=∣xi∣
v
i
	​

=∣x
i
	​

∣ or 
pi=∣xi∣2
p
i
	​

=∣x
i
	​

∣
2
 (probabilities).

Phase-aware split (sign/IQ packing used in QTE): concatenate real/imag or sign-split rails to keep phase while remaining in 
R
R for downstream linear algebra.

Normalize features to unit 
ℓ2
ℓ
2
	​

-norm unless stated.

7.2.2 Similarities / Distances

Cosine similarity: 
sij=⟨vi,vj⟩∥vi∥ ∥vj∥∈[−1,1]
s
ij
	​

=
∥v
i
	​

∥∥v
j
	​

∥
⟨v
i
	​

,v
j
	​

⟩
	​

∈[−1,1].

Jensen–Shannon distance for probabilities 
pi,pj
p
i
	​

,p
j
	​

:

JSD(pi,pj)=12DKL(pi∥m)+12DKL(pj∥m),  m=12(pi+pj).
JSD(p
i
	​

,p
j
	​

)=
2
1
	​

D
KL
	​

(p
i
	​

∥m)+
2
1
	​

D
KL
	​

(p
j
	​

∥m)







# QTE Curriculum — Part B (Units 6–10)

> This canvas holds Units 6–10. We’ll append each unit in full detail as we finalize it. Unit 6 is included below in the agreed “testable unit” style.

---

## Unit 6 — Analysis Suite: Spectral Analysis (FFT & QFT)

### 1) Concept & Goal

**Objective.** Quantify spectral content of encoded states in *both* classical and quantum Fourier domains to validate correctness, diagnose leakage/aliasing, and build entropy-based certificates.

### 2) Mathematical Background

* **Classical FFT.** For a real/complex sequence (x_n), (X_k = \sum_{n=0}^{N-1} x_n e^{-2\pi i kn/N}). Parseval: (\sum_n |x_n|^2 = \tfrac{1}{N}\sum_k |X_k|^2).
* **Quantum QFT.** (\mathrm{QFT},|n\rangle = \tfrac{1}{\sqrt{N}}\sum_{k=0}^{N-1} e^{2\pi i nk/N}|k\rangle). Measurement in Z after QFT yields the **momentum-space** distribution.
* **Short-Time QFT.** Windowed/segmented QFT reveals nonstationary structure.
* **Uncertainty/entropic checks.** Maassen–Uffink bound on measurement entropies in conjugate bases serves as a sanity check.

### 3) Code References

* **FFT pipeline:** `tools/harmonic_analysis.py` (windowing, centering, Hann), `tests/test_fft_invariants.py`.
* **QFT circuits:** `tools/qft_module.py` (standard + ST-QFT), `quantum_embedding.py` (integration hooks).
* **Certificates:** `entropy_lab.py` (H_Z, H_QFT, flatness, KL).
* **GUI tabs:** FFT Spectrum, QFT Spectrum (in `QTEGUI.py.*`).

### 4) CLI Experiments

```bash
# A. Classical FFT vs Parseval
./qte_cli_ext.py fft --label "QFT[sin(2*pi*x); N=256; a=0; b=1]" --window hann --plot

# B. Quantum QFT spectrum (simulator)
./qte_cli_ext.py qft-spectrum --n 8 --label "QFT[sin(2*pi*x); N=256; a=0; b=1]" --shots 4096

# C. Short-Time QFT sweep
./qte_cli_ext.py stqft --n 8 --label "QFT[chirp(x); N=256; a=0; b=1]" --win 32 --hop 8 --plot
```

### 5) Predicted Results

* **FFT:** Energy conservation (Parseval) within numerical tolerance. Single-tone ⇒ sharp peaks at ±k.
* **QFT:** Peaks align with classical FFT locations; entropic bound satisfied (H_Z + H_QFT ≥ bound).
* **ST-QFT:** Chirp condenses at matching fractional angle/time tiles.

### 6) Tests

* `tests/test_qft_parseval.py` — asserts unitary QFT (norm preserved; simulated Parseval).
* `tests/test_fft_invariants.py` — windowing normalization, energy checks.
* `tests/test_maassen_uffink_bound_z_qft.py` — entropic uncertainty.

### 7) IBM Hardware (Torino) Runners

```bash
# Sessionless runner (counts + entropy metrics)
python tools/run_on_ibm_torino.py --backend torino --n 3 --rounds 0 \
  --shots 4096 --basis Z --out docs/results/qft_spectrum_torino.json
```

**Expected:** Broadened peaks vs simulator; entropy/KL drift quantified in output JSON.

---

## Unit 7 — Analysis Suite: Function Atlas (placeholder)

**To be inserted:** Similarity metrics, PCA/UMAP scatter, clustering of fingerprints; CLI and tests.

## Unit 8 — Analysis Suite: Entanglement & Multi‑Register Analysis

### 1) Concept & Goal

**Objective.** Create, visualize, and quantify multipartite entanglement for QSE states. Provide reproducible metrics (Schmidt entropies, mutual information, marginals) and small‑n hardware validations.

### 2) Mathematical Background

* **Bipartition & Schmidt decomposition.** For a pure state |psi> in H_A ⊗ H_B: |psi> = sum_i sqrt(lambda_i) |i_A>|i_B| with lambda_i ≥ 0, sum_i lambda_i = 1. Reduced states: rho_A = Tr_B |psi><psi|, rho_B = Tr_A |psi><psi|.
* **Entanglement entropy.** S(rho_A) = −Tr(rho_A log2 rho_A) = S(rho_B). Bell: S = 1 bit. Product: S = 0.
* **Mutual information (from Z‑basis counts).** I(A:B) = H(A)+H(B)−H(A,B), capturing classical correlations.
* **Marginals.** From counts p(z1…zn), sum over other bits to obtain per‑register marginals; compare against ideal reduced densities.

### 3) Code References

* **Entanglement builders:** `quantum_embedding.py` — `entangle_series_multi(...)` (chain/star/all_to_all); also `periodic_phase_state`, `qft` as structured sources.
* **Entropy utilities:** GUI helper `_schmidt_entropy_bits(sv, cut)` (Measure tab); `entropy_lab.py` for entropy packs (H_Z, H_QFT, flatness, KL) as consistency checks.
* **Register views:** Measure tab grid overlays & marginals (QTEGUI).
* **Tomography (small‑n):** Tomography tab (uses `qiskit_experiments`) to reconstruct rho and compute `state_fidelity`.
* **Tests already present:** `tests/test_bell_state_entropy_one.py` (Bell has S≈1 on 1|1 cut); `tests/test_maassen_uffink_bound_z_qft.py` (entropy bound). Placeholders below for GHZ/marginals.

### 4) CLI Experiments

```bash
# A) Bell state: build → entropies → marginals (simulator)
./qte_cli_ext.py entangle --kind bell --n 2 --shots 4096 --dump states/bell.npy
./qte_cli_ext.py schmidt --load-state states/bell.npy --cuts 1 --report
./qte_cli_ext.py marginals --load-state states/bell.npy --registers 0,1 --report

# B) GHZ(3): bipartition entropies & classical mutual information
./qte_cli_ext.py entangle --kind ghz --n 3 --shots 4096 --dump states/ghz3.npy
./qte_cli_ext.py schmidt --load-state states/ghz3.npy --cuts 1,2 --report
./qte_cli_ext.py mutual-info --load-state states/ghz3.npy --registers 0:2 --report

# C) Multi‑register from function labels + topology
./qte_cli_ext.py entangle --labels "Maclaurin[sin(x)]" "Maclaurin[J0(x)]" \
  --topology star --nq 4 --shots 4096 --dump states/multi_star.npy
./qte_cli_ext.py schmidt --load-state states/multi_star.npy --cuts 1,2,3 --report

# D) Entanglement growth under cipher U (light‑cone proxy)
./qte_cli_ext.py scramble --cipher-rounds 1 --n 8 --out states/t1.npy
./qte_cli_ext.py scramble --cipher-rounds 2 --n 8 --out states/t2.npy
./qte_cli_ext.py scramble --cipher-rounds 3 --n 8 --out states/t3.npy
./qte_cli_ext.py schmidt-scan --pattern 1..7 --load-states states/t1.npy states/t2.npy states/t3.npy --plot
```

*Notes.* `schmidt` computes S(rho_A) for each specified cut; `schmidt-scan` sweeps contiguous cuts; `mutual-info` and `marginals` operate on shot counts.

### 5) Predicted Results

* **Bell (n=2).** Schmidt entropy on 1|1: S ≈ 1.00 ± 0.02 (sim); per‑qubit marginals uniform; strong I(A:B).
* **GHZ (n=3).** Across 1|2 or 2|1: S ≈ 1. Any single‑qubit reduced density ≈ I/2. Z‑basis shows perfect classical correlations; QFT‑basis distinguishes from W.
* **Function‑entangled registers.** Entropy reflects label similarity; star topology central qubit shows highest entropy.
* **Cipher growth.** Entropy front increases with rounds (light‑cone‑like pattern in `schmidt-scan`).

### 6) Tests

* `tests/test_bell_state_entropy_one.py` — assert S_{1|1}(Bell) in [0.9, 1.1].
* `tests/test_ghz_entropies.py` (add) — assert S_{1|2} = S_{2|1} = 1 within tolerance.
* `tests/test_marginals_consistency.py` (add) — GHZ single‑qubit marginals ≈ uniform; mutual information high.
* `tests/test_lightcone_entropy_growth.py` (add) — monotone increase of boundary entropies with cipher rounds.

### 7) IBM Hardware (Torino) Runners

```bash
# 2‑qubit Bell on hardware: counts + optional tomography fidelity
./qte_cli_ext.py entangle --kind bell --n 2 --backend torino --shots 8192 \
  --result docs/results/bell_torino_counts.json

# Optional tomography (if CLI hook is enabled) or use the GUI Tomography tab
./qte_cli_ext.py tomography --kind bell --n 2 --backend torino --shots 8192 \
  --result docs/results/bell_torino_tomo.json
```

**Expected:** Fidelity vs ideal ≥ 0.9 after transpilation/mitigation; Schmidt entropy from reconstructed rho ≈ 1 within error bars.

## Unit 9 — Quantum Engine: Advanced QSP Transform Library (placeholder)

**To be inserted:** FrFT/LCT, CZT, Hankel/Bessel, Hilbert/Wavelet/NTT, DCT/DST; unitary blocks and validations.

## Unit 10 — Analysis Suite: Hierarchical Analysis (Chunks) (placeholder)

**To be inserted:** Chunking, merge statistics, spectra stacking; CLI and tests.




# QTE Master Curriculum — Canonical Units (9–16)

> Stable numbering continued.

---

## Unit 9 — Spectral Analysis: Classical FFT vs Quantum QFT

**Scope.** Side‑by‑side spectra; windowing, centering, Hann; Parseval checks.
**Key ideas.** Classical pipeline (FFT) vs circuit QFT counts.
**Equations.** Parseval: `∑|x_n|^2 = (1/N)∑|X_k|^2`.
**Core code.** `harmonic_analysis.py`, `tools/qft_module.py`.
**Primary tests.** `tests/test_qft_parseval.py`, `tests/test_fft_invariants.py`.
**CLI.** `qte_cli_ext.py qft --state state.npy --shots 4096`.

---

## Unit 10 — Transform Library I: FrFT / LCT / Chirp‑Z

**Scope.** Fractional Fourier, Linear Canonical, and CZT unitaries.
**Key ideas.** Time–frequency rotation; nonuniform spectral zoom.
**Core code.** `tools/lct_czt.py::{frac_fourier, linear_canonical_unitary, chirp_z}`.
**Primary tests.** `tests/test_frft_rotation_identity.py`, `tests/test_czt_consistency.py`.
**CLI.** `qte_cli_ext.py lct --mode frft --alpha 0.5 --state s.npy`.

---

## Unit 11 — Transform Library II: Hankel & Spherical Bessel

**Scope.** Radial/Fourier analogues for 2D/3D symmetry.
**Key ideas.** Bessel kernel; radial momentum readout.
**Core code.** `tools/hankel_bessel.py::{discrete_hankel_unitary, spherical_bessel_unitary}`.
**Primary tests.** `tests/test_hankel_orthogonality.py`, `tests/test_spherical_bessel_unitarity.py`.
**CLI.** `qte_cli_ext.py hankel --order 0 --state ring.npy`.

---

## Unit 12 — Transform Library III: Hilbert / Wavelet / NTT / Walsh–DCT–DST

**Scope.** Analytic signal, wavelet skims, NTT for exact arithmetic, cosine/sine bases.
**Core code.** `tools/hilbert_wavelet_ntt.py::{hilbert_transform, wavelet_pass, ntt}`, `tools/dct_dst.py::{dct2_unitary, dst2_unitary}`, `tools/walsh.py::walsh_hadamard`.
**Primary tests.** `tests/test_hilbert_analytic_signal.py`, `tests/test_dct_energy_compaction.py`.
**CLI.** `qte_cli_ext.py dct --state cosine.npy`.

---

## Unit 13 — Crypto Primitives: PRF / Subkeys / MAC

**Scope.** SHAKE‑based PRF; HKDF‑like derives; Bell‑pair MAC.
**Core code.** `qe_crypto/primitives.py::{prf_bits, derive_subkeys, mac_bell_bits}`.
**Primary tests.** `tests/test_mac_bell_bits.py`, `tests/test_prf_distribution.py`.
**CLI.** `qte_cli_ext.py mac --msg 0xBEEF --key k.hex`.

---

## Unit 14 — Unitary Cipher & Leakage Meter

**Scope.** SPN‑like mixing: H/S/QFT + keyed diagonal; leakage measurement.
**Core code.** `qe_crypto/unitary_cipher.py::{cipher_u, phase_poly}`, `tools/leakage_meter.py`.
**Primary tests.** `tests/test_cipher_leakage.py`, `tests/test_phase_mix_balance.py`.
**CLI.** `qte_cli_ext.py cipher --n 6 --rounds 4 --key key.hex`.

---

## Unit 15 — IND‑CPA Metric & Shadow Distinguishers

**Scope.** Average over nonces, trace distance to maximally mixed; shadow score.
**Equations.** `td = ½‖ρ̄ − I/d‖_1`.
**Core code.** `qe_crypto/phase_mix.py::{avg_state_over_nonces, trace_distance_to_maxmix}`, `entropy_lab.py::{shadow_score_from_rho, leakage_score_from_state}`.
**Primary tests.** `tests/test_crypto_ind_cpa.py`, `tests/test_shadow_distinguisher.py`.
**CLI.** `tools/run_ind_cpa.py --n 4 --rounds 2 --samples 192`.

---

## Unit 16 — Chaos Diagnostics: OTOC / Spectral Form Factor

**Scope.** Scrambling signatures; dip–ramp–plateau.
**Equations.** `K(t)=|Tr(U^t)|^2`.
**Core code.** `physics/kubo_otoc_sff.py::spectral_form_factor`.
**Primary tests.** `tests/test_sff_baselines.py`.
**CLI.** `qte_cli_ext.py sff --src cipher --n 8 --rounds 5 --t 1..20`.

---

## Unit 4 — Vector Algebra (Series-Preserving Products) — Detailed

**Purpose.** Operate on Dollarhide fingerprints in ways that preserve their series semantics and admit predictable quantum behavior after loading as amplitudes. *This replaces the brief Unit 4 stub above.*

**Concept.** Let `a = (a₀,…,a_{N−1})`, `b = (b₀,…,b_{N−1})`. We provide linear combination (LCU) and four bilinear products aligned to ordinary, exponential, and number‑theoretic generating functions.

**Mathematics.**

* **LCU (linear combination).** `c = α a + β b`.
* **Hadamard (termwise).** `(a ⊙ b)_n = a_n b_n`.
* **Cauchy (OGF convolution).** `(a ⋆_C b)_n = ∑_{k=0}^n a_k b_{n−k}`.
* **EGF (binomial convolution).** `(a ⋆_E b)_n = ∑_{k=0}^n \binom{n}{k} a_k b_{n−k}`.
* **Dirichlet convolution.** For 1‑indexed sequences: `(a ⋆_D b)(n) = ∑_{d|n} a(d) b(n/d)`; we map indices `{1..N}` ↔ `{0..N−1}` when stored.

**Properties.**

* All are bilinear; Hadamard, Cauchy, EGF are commutative & associative on finite pads; Dirichlet is commutative if both inputs are multiplicative.
* Norm bounds: `‖a ⊙ b‖₂ ≤ ‖a‖₂ ‖b‖₂`; Young‑type bounds for convolutions. After normalization, `|ψ⟩ = c/‖c‖` remains a valid statevector.

**Implementation in repo.**

* `series_preserving.py`

  * `lcu_combine(a, b, alpha=1.0, beta=1.0)`
  * `hadamard_product(a, b)`
  * `cauchy_product(a, b)`
  * `egf_product(a, b)`
  * `dirichlet_convolution(a, b, index_mode="one_based")`

**Unit tests.**

* `tests/test_series_algebra.py`

  * Validates algebraic identities (commutativity/associativity where applicable).
  * Parseval‑style consistency on load: FFT energy conserved up to normalization.
  * Edge cases: unequal lengths (zero‑pad), NaNs/Infs rejected.

**Local CLI experiments.**

```bash
# Build two fingerprints (EGF‑weighted Maclaurin)
qte_cli.py --nq 8 --label "Maclaurin[sin(x)] egf"   --dump sin_egf.npy
qte_cli.py --nq 8 --label "Maclaurin[cos(x)] egf"   --dump cos_egf.npy

# Algebra: Cauchy vs Hadamard
qte_cli_ext.py algebra --op cauchy   --a sin_egf.npy --b cos_egf.npy --out conv.npy
qte_cli_ext.py algebra --op hadamard --a sin_egf.npy --b cos_egf.npy --out had.npy

# Load to quantum and compare QFT spectra
qte_cli_ext.py qft --state conv.npy --shots 4096 --out conv_counts.json
qte_cli_ext.py qft --state had.npy  --shots 4096 --out had_counts.json
```

**Expected.** `had` yields a sparser Z‑basis amplitude footprint; `conv` exhibits broadened spectral support. Energies match simulation within tolerance.

**IBM Runtime hook (optional).**

```bash
# Send the Cauchy‑combined state to hardware (Torino)
qte_cli_ext.py build --state conv.npy --out conv_circ.qpy
tools/run_on_ibm_torino.py --backend torino --n 8 --rounds 0 --shots 4096 \
  --basis Z --load conv_circ.qpy --out docs/results/unit4_conv_hw.json
```

**Validation.** Compare hardware counts to Aer via KL divergence / entropy deltas; assert within noise envelope recorded in `tests/test_series_algebra.py::test_hw_tolerance`.



# QTE Curriculum — Master Index (Canvases & Unit Status)

**Note:** I cannot read or open canvases after creating them. This index is my working map so you can verify quickly. If an item is wrong, tell me and I will correct it immediately.

---

## Canvas Plan (≤5 units per canvas)

* **Canvas A — Detailed Units 1–5**
  Units: 1) Core Thesis & Foundational Concepts
  2) Classical Engine — Mathematical Object Library
  3) Classical Engine — Vector Engine & Algebra
  4) Quantum Engine — State Prep & Core Algorithms
  5) Analysis Suite — State Characterization

* **Canvas B — Detailed Units 6–10**
  Units: 6) Spectral Analysis (FFT & QFT)
  7) “Function Atlas” (Similarity & Clustering)
  8) Entanglement & Multi‑Register Analysis
  9) Advanced QSP Transform Library
  10) Hierarchical Analysis (Chunks)

* **Canvas C — Detailed Units 11–15**
  Units: 11) Application — Payload & Entropy Certification
  12) Vertical — Quantum Dynamics (Koopman & Chaos)
  13) Vertical — Quantum Cryptography & Security
  14) Validation Framework
  15) Quasiparticles & Dispersion (QPE)

* **Canvas D — Detailed Units 16–20 (Extensions)**
  Units: 16) Quantum Amplitude Estimation (QAE)
  17) Quantum Kernel / QML Feature Maps
  18) PDE / HHL & Spectral Methods
  19) Radial Transforms (Hankel, Spherical Bessel) Applications
  20) Black‑Hole‑Style Scrambling & SFF (extended)

---

## Unit Status Ledger (Working Truth Table)

Legend: ✅ detailed | 🟨 draft/partial | ⭕ planned | 🔎 verification by you requested (canvas presence)

### Part 1 — Foundations

1. **Core Thesis & Foundational Concepts** — ✅ 🔎
2. **Classical Engine — Mathematical Object Library** — ✅ 🔎
3. **Classical Engine — Vector Engine & Algebra** — 🟨 🔎 (you noted Unit 3 visibility issue; I will re‑embed if missing)
4. **Quantum Engine — State Prep & Core Algorithms** — ✅ 🔎

### Part 2 — Basic Analysis

5. **Analysis Suite — State Characterization** — 🟨 🔎 (believe we drafted; ready to deepen)
6. **Spectral Analysis (FFT & QFT)** — 🟨 🔎

### Part 3 — Advanced Analysis & Applications

7. **“Function Atlas” (Similarity & Clustering)** — 🟨 🔎
8. **Entanglement & Multi‑Register Analysis** — 🟨 🔎
9. **Advanced QSP Transform Library** — ⭕
10. **Hierarchical Analysis (Chunks)** — ⭕

### Part 4 — Research Verticals & Validation

11. **Application — Payload & Entropy Certification** — 🟨 🔎
12. **Vertical — Quantum Dynamics (Koopman & Chaos)** — 🟨 🔎
13. **Vertical — Quantum Cryptography & Security** — ✅ 🔎 (LaTeX unit written)
14. **Validation Framework** — 🟨 🔎
15. **Quasiparticles & Dispersion (QPE)** — 🟨 🔎

### Part 5 — Extension Tracks

16. **Quantum Amplitude Estimation (QAE)** — ⭕
17. **Quantum Kernel / QML Feature Maps** — ⭕
18. **PDE / HHL & Spectral Methods** — ⭕
19. **Radial Transform Applications** — ⭕
20. **Black‑Hole‑Style Scrambling & SFF (extended)** — ⭕

---

## Breadcrumbs & Versioning

* **This index:** v1.0 — created now.
* On each detailed canvas I will add a tiny header:

  * `QTE Units X–Y — vX.Y — YYYY‑MM‑DD — Units listed here`
  * I’ll update this index every time I add or change a unit.

---

## Next Concrete Steps (proposed)

1. Add headers to the existing canvases you see in your sidebar (for fast visual confirmation).
2. If Canvas A (Units 1–5) is missing Unit 3, I’ll re‑embed it there and mark ✅ here.
3. Continue detailing from the **lowest unfinished unit** (currently Unit 5), keeping ≤5 units per canvas.



# QTE Curriculum — Units 7–10 (Final, Testable)

> House style: **Overview → Definitions & Math → Implementation Pointers (code) → CLI Experiments (Sim & IBM where applicable) → Tests → Expected Results & Artifacts → Notes**.

---

## Unit 7 — Analysis Suite: The “Function Atlas”

### Overview

Build a geometric atlas of encoded objects (constants, series, functions) by converting each state’s amplitudes into feature vectors, comparing with principled similarities, and visualizing with low-dimensional embeddings. The atlas reveals families and parameter sweeps as coherent structures.

### Definitions & Math

* Feature maps from amplitude vector (x\in\mathbb{C}^N):

  * **prob**: (p=\lvert x\rvert^2\in\mathbb{R}^N,\ \sum p_i=1)
  * **amp**: (v=\lvert x\rvert \in\mathbb{R}^N) (scale-invariant after (\ell_2) normalization)
  * **iq**: (u=[\Re x;\Im x]\in\mathbb{R}^{2N}) (phase-aware)
* Similarities/distances:

  * **Cosine**: (s(a,b)=\frac{\langle a,b\rangle}{|a|_2|b|_2})
  * **Fidelity** (state): (F(\psi,\phi)=|\langle\psi|\phi\rangle|^2)
  * **Jensen–Shannon distance** (prob.): (\mathrm{JSD}(p,q)=\sqrt{\tfrac12 D_{\mathrm{KL}}(p|m)+\tfrac12 D_{\mathrm{KL}}(q|m)}), (m=(p+q)/2)
* Embeddings:

  * **PCA/SVD** on centered features (V\rightarrow Y\in\mathbb{R}^{M\times 2})
  * **Spectral clustering** on similarity graph (optional)

### Implementation Pointers (code)

* `series_encoding.py` — produce/snapshot vectors (terms/EGF, phase modes).
* `quantum_embedding.py` — optional circuits for hardware-sampled variants.
* **New** `tools/function_atlas.py`:

  * `load_vectors(glob, feature)`
  * `cosine_matrix(V)`, `jsd_matrix(P)`
  * `pca_2d(V) -> (Y, var)`
  * `cluster_spectral(S, k)`
  * `save_matrix/plot_scatter(...)`
* **New** `tests/test_function_atlas.py` (see Tests).

### CLI Experiments (Sim & optional IBM)

```bash
# Build example sets (any saved .npy vectors are fine)
python tools/function_atlas.py matrix \
  --glob "states/*/*.npy" \
  --feature prob --metrics cosine,jsd \
  --out-dir atlas/out

python tools/function_atlas.py pca \
  --glob "states/*/*.npy" \
  --feature prob --metric cosine \
  --out atlas/out/pca_cosine.json \
  --plot atlas/out/pca_cosine.png

# Optional clustering
python tools/function_atlas.py cluster \
  --matrix atlas/out/cosine_matrix.npy --k 3 \
  --out atlas/out/labels.json

# Optional: include hardware-sampled distributions for robustness
# (convert counts→prob and save .npy next to the set, then re-run matrix/pca)
```

### Tests

* `test_cosine_range_and_symmetry` — symmetric, ([-1,1]) bounded
* `test_jsd_metric_properties` — symmetry, nonnegativity, zeros on diagonal
* `test_pca_shapes_and_variance` — (Y\in\mathbb{R}^{M\times 2}), monotone variance
* `test_family_separation_small_benchmark` — mean intra-family cosine > mean inter-family cosine

### Expected Results & Artifacts

* `atlas/out/cosine_matrix.npy`, `atlas/out/jsd_matrix.npy`
* `atlas/out/pca_cosine.{json,png}`, `atlas/out/labels.json` (if clustered)
* Qualitative: near block-diagonal similarity; PCA lobes per family; smooth parameter curves within families.

### Notes

* Normalize features before cosine; add (\epsilon) for JSD logs.
* Keep one feature type per run (don’t mix `prob` with `iq` in a single matrix).

---

## Unit 8 — Analysis Suite: Entanglement & Multi-Register Structure

### Overview

Quantify multipartite structure of QSE states: Schmidt entropies across cuts, classical mutual information from counts, per-register marginals, and (small-n) tomography fidelity.

### Definitions & Math

* **Schmidt entropy** (pure (|\psi\rangle) on bipartition (A|B)): (S(\rho_A)= -\mathrm{Tr}(\rho_A \log_2 \rho_A)), (\rho_A=\mathrm{Tr}_B(|\psi\rangle\langle\psi|))
* **Classical mutual information** (from Z-basis counts):
  (I(A!:!B)=H(A)+H(B)-H(A,B))
* **GHZ/Bell references**: Bell: (S_{1|1}=1). GHZ(*n): (S*{1|n-1}=1).

### Implementation Pointers (code)

* `quantum_embedding.py` — builders:

  * `bell_state()`, `ghz_state(n)`, `periodic_phase_state(...)`
  * `entangle_series_multi(labels, topology=...)` (chain|star|all)
* **New** `qte_cli_ext.py` subcommands:

  * `entangle --kind bell|ghz|labels ... --dump <state.npy>`
  * `schmidt --load-state <npy> --cuts 1,2,... --report`
  * `schmidt-scan --pattern "1..(n-1)" --plot`
  * `marginals --load-state <npy> --registers 0,1,... --report`
  * `mutual-info --load-counts <json> --registers 0:2 --report`
* `entropy_lab.py` — reuse entropy helpers; add `schmidt_from_statevec(...)`

### CLI Experiments (Sim & IBM)

```bash
# Bell (n=2) — sim
./qte_cli_ext.py entangle --kind bell --n 2 --dump states/bell.npy
./qte_cli_ext.py schmidt --load-state states/bell.npy --cuts 1 --report
./qte_cli_ext.py marginals --load-state states/bell.npy --registers 0,1 --report

# GHZ (n=3) — sim
./qte_cli_ext.py entangle --kind ghz --n 3 --dump states/ghz3.npy
./qte_cli_ext.py schmidt --load-state states/ghz3.npy --cuts 1,2 --report
./qte_cli_ext.py mutual-info --load-state states/ghz3.npy --registers 0:2 --report

# Structured QSE state — sim
./qte_cli_ext.py entangle --labels "Maclaurin[sin(x)]" "Maclaurin[J0(x)]" \
  --topology star --nq 4 --dump states/multi_star.npy
./qte_cli_ext.py schmidt --load-state states/multi_star.npy --cuts 1,2,3 --report

# Optional hardware Bell (torino)
python tools/run_on_ibm_torino.py --backend torino --n 2 --shots 8192 \
  --basis Z --task bell --out docs/results/bell_torino_counts.json
```

### Tests

* `tests/test_bell_state_entropy_one.py` — (S_{1|1}\in[0.9,1.1]) (sim)
* `tests/test_ghz_entropies.py` — (S_{1|2}=S_{2|1}\approx 1) (sim)
* `tests/test_marginals_consistency.py` — GHZ single-qubit marginals ~ uniform
* `tests/test_mutual_info_high_for_ghz.py` — high (I(A:B)) in Z counts
* (Optional) tomography smoke test n≤3 with fidelity threshold

### Expected Results & Artifacts

* JSON `schmidt` reports (per cut), marginal histograms, mutual-info tables; optional tomography JSON with fidelity.
* Bell sim: (S\approx1). GHZ sim: (S\approx1) on 1|2 cut; high classical Z-correlations.

### Notes

* Use little-endian register order consistently in cut definitions.
* For counts-based MI on hardware, show bootstrapped (95%) CIs.

---

## Unit 9 — Quantum Transform Library I (FrFT / LCT / CZT)

### Overview

Provide unitary spectral transforms beyond QFT: Fractional Fourier (time–frequency rotation), Linear Canonical Transform (abc-d family), and Chirp-Z (zoom/spiral contour). Expose them as compile-time unitaries for small (n) and classical references for validation.

### Definitions & Math

* **Unitary DFT (size (N=2^n))**: (F_{km}=N^{-1/2}e^{2\pi i km/N})
* **FrFT (angle (\alpha))**: rotation in time–frequency plane; discrete unitary (U_\alpha) with
  (U_\alpha U_\beta \approx U_{\alpha+\beta}), (U_0=I), (U_1=F)
* **LCT with matrix (\begin{pmatrix}A&B\C&D\end{pmatrix}), (AD-BC=1)**: generalizes FrFT; discrete unitary (U_{A,B;C,D})
* **CZT**: evaluates (X_k=\sum_m x_m A^{-m}W^{mk}) along spiral; implement unitarily via Bluestein mapping where feasible; classical reference always provided

### Implementation Pointers (code)

* **New** `tools/lct_czt.py`

  * `frac_fourier_unitary(n, alpha)`  (returns (2^n\times2^n) ndarray)
  * `linear_canonical_unitary(n, A,B,C,D)` (unitary ndarray)
  * `chirp_z_reference(x, A, W, M)` (classical)
* `quantum_embedding.py`

  * `apply_unitary_statevec(x, U) -> x'`
  * (optional) circuit synthesis stubs for very small (n) (depth-aware)
* `harmonic_analysis.py` — energy/Parseval checks

### CLI Experiments (Sim)

```bash
# FrFT rotation identities
./qte_cli_ext.py frft --n 8 --alpha 0.5 --state states/signal.npy --out states/frft_05.npy
./qte_cli_ext.py frft --n 8 --alpha 0.5 --state states/frft_05.npy --out states/frft_10.npy
# Compare to FFT (alpha=1)
./qte_cli_ext.py compare --a states/frft_10.npy --b states/fft_1.npy --metric l2 --tol 1e-6

# LCT unit test case (A=cosθ, B=sinθ, C=−sinθ, D=cosθ)
./qte_cli_ext.py lct --n 8 --theta 0.3 --state states/signal.npy --out states/lct_theta.npy

# CZT zoom around a band (classical reference)
./qte_cli_ext.py czt --load-state states/signal.npy --A 1.0 --W "exp(-2j*pi/256)" --M 128 \
  --out docs/results/czt_band.json
```

### Tests

* `tests/test_frft_rotation_identity.py`

  * (U_\alpha U_\beta \approx U_{\alpha+\beta}), (| \cdot |_2) error (<10^{-6}) (sim)
* `tests/test_lct_unitarity.py`

  * (|U^\dagger U-I|_2 < 10^{-9})
* `tests/test_czt_consistency.py`

  * CZT equals FFT at matching parameters; known tones recovered at expected indices

### Expected Results & Artifacts

* Saved transformed statevectors (`.npy`), CZT JSON spectra, comparison reports with max error and norms.
* Plots (optional) of magnitude spectra before/after transforms.

### Notes

* All transforms use **unitary normalization**; verify Parseval after each transform.
* Circuit synthesis for FrFT/LCT is optional and only for tiny (n) to keep depth low.

---

## Unit 10 — Analysis Suite: Hierarchical Chunking & Aggregation

### Overview

Analyze long vectors/states by chunking into overlapping blocks with windows, computing per-chunk features (spectra, entropy), and aggregating into hierarchical summaries. Useful for nonstationary fingerprints and “local similarity” maps.

### Definitions & Math

* **Chunking**: block length (B=2^m), hop (H) (default (H=B/2))
* **Windowing** (w[m]) (Hann by default)
* Per-chunk feature (f_t) from chunk (x_{t}\odot w) (e.g., entropy, spectral centroid)
* **Aggregation**: mean/var over time; piecewise statistics; heatmaps (time×frequency or time×register)

### Implementation Pointers (code)

* **New** `tools/chunks.py`

  * `chunk_view(x, B, H, window='hann') -> array[T, B]`
  * `features_per_chunk(chunks, kind=['entropy','power','centroid']) -> dict`
  * `reconstruct_overlap_add(chunks, B, H, window) -> x'`
* `harmonic_analysis.py` — reuse Hann and unitary FFT for per-chunk spectra
* `entropy_lab.py` — chunkwise (H_Z) (if operating on counts) or Shannon of (|x|^2)

### CLI Experiments (Sim)

```bash
# Split → analyze → merge (sanity)
./qte_cli_ext.py chunks split --load-state states/long.npy --B 64 --H 32 \
  --window hann --out tmp/chunks.npz

./qte_cli_ext.py chunks analyze --chunks tmp/chunks.npz \
  --features entropy,power,centroid \
  --out docs/results/chunk_features.json --plot docs/results/chunk_heatmap.png

./qte_cli_ext.py chunks merge --chunks tmp/chunks.npz --window hann \
  --out states/long_recon.npy

# Acceptance: reconstruction error small; statistics stable
./qte_cli_ext.py compare --a states/long.npy --b states/long_recon.npy --metric l2 --tol 1e-8
```

### Tests

* `tests/test_chunk_reconstruction.py` — overlap-add reconstruction (|x-x'|_2<10^{-8})
* `tests/test_chunk_feature_shapes.py` — expected shapes/keys for features
* `tests/test_chunk_energy_accounting.py` — window compensation yields conserved energy (within tol)

### Expected Results & Artifacts

* `tmp/chunks.npz` (window, B, H, T, chunks)
* `docs/results/chunk_features.json` (per-chunk metrics) + optional heatmap PNG
* Reconstruction `.npy` + comparison JSON

### Notes

* Keep (B) power-of-two for FFT; document window normalization so energy is conserved.
* For register-wise chunking, expose a `--by-register` flag to chunk each qubit register’s marginal separately.

---

## Global Conventions (Units 7–10)

* **Normalization**: unitary FFT/QFT; vectors are (\ell_2)-normalized before similarity/entropy.
* **Endianness**: little-endian for bit→index mapping; QFT sign (+).
* **Tolerances (defaults)**: l2 compare (1e{-6})–(1e{-8}) (sim), entropy deltas on hardware ≤0.15 bits for n≤4 unless specified.
* **Artifacts**: JSON schemas include `n`, `feature`, `params`, and deterministic seeds where applicable.
