# Theory Catalog: Spectral/QFT Framework (Living Document)
_Last updated: $(date -u +%FT%TZ)_

This catalog records **all** theoretically possible advantages your framework could enable, grouped by rigor. Each item includes: **Problem**, **Quantum claim**, **Classical baseline**, **Assumptions**, **Output type**, **Proof sketch**, **References/notes**.

## Legend
- ✅ **Provable now** (standard oracle models; implementable small-scale)
- 🟡 **Provable with extra assumptions** (e.g., QRAM, block-encodings, learnable U)
- 🔴 **Speculative** (open; risks hidden exponential costs e.g., state-prep)

---

## ✅ Exponential (query) advantage: Hidden period / eigenphase
**Problem.** Recover hidden period r (mod 2^K) or an eigenphase φ of a given unitary U.  
**Quantum.** Phase kickback + IQFT/QPE in poly(K, precision).  
**Classical.** Black-box lower bounds: exponential queries in K to find r / eigenphase.  
**Assumptions.** Standard oracle access (unitary implements the promise).  
**Output.** A few bits (r, or φ to m bits).  
**Sketch.** Your QPSK-indexer = diagonal phases → IQFT; QPE primitive is already present.

---

## ✅ Sampling hardness: IQP / diagonal-phase sandwiches
**Problem.** Sample from circuits: (H⊗n or QFT) → diagonal phases → inverse.  
**Quantum.** Low-depth execution; native in your stack.  
**Classical.** Believed hard to sample to small variation distance (PH-collapse consequences).  
**Assumptions.** Average-case hardness; anticoncentration.  
**Output.** Bitstring samples; certify via cross-entropy / heavy-output generation.

---

## 🟡 Sparse linear systems (HHL-family)
**Problem.** Prepare |x⟩ ∝ A^{-1} b for sparse, well-conditioned A given by oracle.  
**Quantum.** Poly(log N, κ, 1/ε) using block-encoding/LCU; measure observables of |x⟩.  
**Classical.** Poly(N) with N=2^n → exponential in n.  
**Assumptions.** Sparse oracles; access to b; tolerate observable-only readout.  
**Output.** Expectation values ⟨x|O|x⟩, not full vector.

---

## 🟡 Linear PDE evolution (spectral)
**Problem.** Evolve u_t = L u for local/sparse L; report observables.  
**Quantum.** Simulate e^{tL} (or e^{-itH}) poly in n,t,1/ε for sparse encodings.  
**Classical.** Grid size grows as N^d; exponential in d for fixed N.  
**Assumptions.** Block-encodings of L; observable outputs.

---

## 🟡 Koopman spectral decomposition (if U is given)
**Problem.** Given Koopman step U for dynamics, estimate spectrum/eigenfunctions.  
**Quantum.** QPE on U (poly in n, precision).  
**Classical.** Spectral analysis in 2^n space is exponential.  
**Assumptions.** Having/learning a good U-circuit is the hard part.

---

## 🟡 Amplitude / integral estimation (quadratic speedup)
**Problem.** Estimate integrals, overlaps, probabilities.  
**Quantum.** Amplitude estimation: O(1/ε) vs classical O(1/ε^2).  
**Assumptions.** State prep for integrand; controlled reflection or variants.

---

## 🔴 “High-dimensional function composition in poly(n)”
**Issue.** Composition becomes matrix multiply only after exponential state-prep; hidden costs dominate.  
**Path forward.** Restrict to oracle families (hidden shift/period), or sparse polynomial maps.

---

## 🔴 “Infinite-dimensional optimization in poly(n)”
**Issue.** Generic functional minimization needs oracle structure; measurement bottlenecks.  
**Path forward.** Specific observables via parameter-shift; expect poly, not exponential, wins.

---

## 🔴 “Quantum spectral clustering in O(log m)”
**Issue.** Requires QRAM/fast length-squared sampling.  
**Path forward.** Document as conditional result; otherwise total runtime isn’t log m.

---

## 🔴 “General functional integration/path integrals in poly(n)”
**Issue.** No general poly-time algorithm; special cases only; amplitude estimation is quadratic.

---

## Special-function / analytic directions
- **Bessel/Chebyshev bases.** Diagonalize linear ODE operators; faster overlap/integral estimation; IQP sampling with structured phases.  
- **Entropies.** Rényi-2 via SWAP test (two copies); Shannon via histogram or shadow estimation.  
- **Group actions.** Scaling S(λ)=e^{iαN}, fractional Fourier/phase-space rotations—compose with QPE and IQP sampling tests.

