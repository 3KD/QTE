<!-- BEGIN: ABSTRACT_FROZEN -->

# Stand-Alone Quantum Encryption via Maclaurin-Structured Unitaries (teleportation-compatible)

## Abstract (drop-in)

We define a private-key quantum encryption scheme for amplitude-encoded payloads that uses a secret, per-message **Maclaurin-structured unitary** \(U_{K,\nu}\) and **standard quantum teleportation** for transport.  
**Security target** is computational **IND-CPA** with fresh nonces (approximate private channel): ciphertext ensembles are \(\varepsilon\)-close to maximally mixed to any QPT adversary without the key.  
We provide a spec, threat model, metrics, and a test plan (sim → chip → metro-link).

### Frozen claims (v0.1)

- **Correctness:** \(\mathrm{Dec}_{K,\nu}(\mathrm{Enc}_{K,\nu}(\rho))=\rho\) up to synthesis error \(\Delta\).
- **Security target (computational, nonce-based):** For any \(\rho_0,\rho_1\) and any QPT adversary \(A\):
  \[
  \Big|\Pr[A \text{ outputs } b]-\tfrac12\Big| \le \varepsilon + \mathrm{Adv}_{\mathrm{APRF}}(\kappa).
  \]
<!-- END: ABSTRACT_FROZEN -->

<!-- BEGIN: SECURITY_SCOPE -->

## Security scope & rules (Missing-but-Important included)

- **Line in the sand:** IND-CPA with fresh nonces; **no CCA**/decryption oracle; **no nonce reuse**.
- **Nonce handling:** 96–128-bit; uniqueness by **monotonic counter** ⟂ **RNG+ledger**; transmit in plaintext but **integrity-protected**.
- **Key schedule:** PQ-friendly KDF/PRF. Example: **HKDF-SHA3/SHAKE** for subkeys \((K_P,K_D,K_C)\). PRF/MAC via **KMAC256** or LWE-PRF.
- **Classical integrity:** MAC for teleportation bits (e.g., **KMAC256-128** tag on \([\nu,\ \text{Bell bits}]\)).
- **Accepted failure modes:** nonce collision ⇒ tomography risk; chosen-plaintext with reused \(\nu\) ⇒ break; hostile EPR source ⇒ corruption (not plaintext leak).
<!-- END: SECURITY_SCOPE -->

<!-- BEGIN: CONSTRUCTION_SPEC -->

## Construction specifics (pin down)

- **Phase map spec:** exact formula for \(\phi_k\) (Maclaurin-derived phase polynomial), coefficient bounds, modulo convention, precision \(t\) bits.
- **Round schedule:** count of H–D–H sandwiches, Feistel/sparse-Clifford rounds; connectivity assumptions.
- **Synthesis error budget:** bound \(\Delta\) from finite-precision phases; target \(\Delta \ll \varepsilon\).
- **Resource estimates:** depth / 2-qubit count vs \(n\); targets (SC/ion/photonic).
- **Qudit lift:** \(d\)-ary permutation/Clifford blocks; teleport bits \(= 2\log_2 d\).
<!-- END: CONSTRUCTION_SPEC -->

<!-- BEGIN: PROOF_SKELETON -->

## Proof skeleton (what you claim & must show)

- **Approx. private channel bound:** \(\|\mathbb{E}_\nu[U_{K,\nu}\rho U_{K,\nu}^\dagger] - I/2^n\|_1 \le \varepsilon\).
- **Hybrid PRF reduction:** PRF → random replacement ⇒ distinguisher reduces to PRF break.
- **Design proxy:** moment/Pauli-shadow closeness to a 1–2 design; leakage \(\varepsilon\) estimated empirically.
- **Correctness:** \(F(\rho, U^\dagger U \rho) \ge 1-\Delta\).
<!-- END: PROOF_SKELETON -->

<!-- BEGIN: METRICS_AND_OPS -->

## Metrics & governance (operational)

- **Frozen metrics:** \(\varepsilon\), \(F_{\min}\) (on-chip vs metro), sample sizes, stop rule.
- **Provenance stamp:** git SHA, metrics.version, backend ID, KDF salt (not \(K\)), \(\nu\), shots, date.
- **Guardrails already built:** metrics.version bump script (see `tools/bump_metrics_version.py`); ledger for nonce uniqueness.
<!-- END: METRICS_AND_OPS -->

<!-- BEGIN: EXPERIMENT_PLAN -->

## Experiment plan (explicit tasks)

- **Sim + single-chip teleport:** \(n \le 5\) with tomography.
- **Nonce-reuse ablation:** demonstrate break to document the rule.
- **Design-depth sweep:** leakage vs rounds curves.
- **Metro-link pilot:** authenticate Bell bits; measure \(F\) & leakage; include fallback if only on-chip is available.
<!-- END: EXPERIMENT_PLAN -->

<!-- BEGIN: SIDE_CHANNELS -->

## Side-channels & ops

- **Randomness quality:** CSPRNG/HW-TRNG for \(\nu\) and PRF seeds; test for repeats; logging without key exposure.
- **Timing/leakage notes:** constant circuit shape; constant-time compile; no plaintext-dependent gate pruning.
- **Key lifecycle:** storage, rotation cadence, erasure; proof of non-reuse.
- **Receiver policy:** reject on MAC fail; log nonces to prevent replay.
<!-- END: SIDE_CHANNELS -->

<!-- BEGIN: POSITIONING -->

## Positioning vs baselines

- **What you are / not:** stand-alone, nonce-keyed, computational encryption (not perfect secrecy like QOTP; different key-rate trade).
- **Comparators:** QOTP (2n bits, perfect), \(\varepsilon\)-private channels (key \(\approx n+O(\log(1/\varepsilon))\)), data-locking (fragile).
- **Why this point:** pragmatic key/depth/metric balance for near-term devices.
<!-- END: POSITIONING -->

<!-- BEGIN: QUDITS_ADDENDUM -->

## Qudits addendum (already prepped)

| \(d\) | \(\log_2 d\) | Teleport bits \(=2\log_2 d\) |
|---:|---:|---:|
| 2 | 1 | 2 |
| 3 | ~1.585 | ~3.17 (→ 4 with padding) |
| 4 | 2 | 4 |
<!-- END: QUDITS_ADDENDUM -->

<!-- BEGIN: REFERENCES -->

## References (anchor the claims)

Private/approx. private channels; authentication ⇒ encryption; superdense coding; teleportation; high-\(d\) QKD/superdense demos.  
(Add canonical arXiv DOIs/IDs in your bibliography section.)
<!-- END: REFERENCES -->

<!-- BEGIN: LAST_MILE_BUNDLE -->

## Last-mile bundle (consolidated)

**Crypto primitives pinned:** PRF/MAC = **KMAC256**, KDF = **HKDF-SHA3/SHAKE** (derive \(K_P,K_D,K_C\)).  
**Nonce policy:** 96–128-bit; uniqueness via **counter** ⟂ **RNG+ledger**; collision handling.  
**Threat-model table:**

| Attacker power                              | Allowed?     | Notes / Mitigation |
|---|---|---|
| Ciphertext-only                             | Yes          | IND-CPA with fresh \(\nu\). |
| Known-plaintext                             | Yes          | Same bound as IND-CPA target. |
| Chosen-plaintext with **nonce reuse**       | **No**       | Catastrophic ⇒ enforce ledger; reuse ablation test. |
| Decryption oracle (CCA)                     | Out of scope | Not claimed; excluded. |
| Malicious EPR source                        | Not prevented| Corruption risk; MAC Bell bits; provenance. |

**Proof skeleton pointers:** (i) \(\varepsilon\)-randomization via phase-mixing moments; (ii) hybrid PRF→random; (iii) \(\Delta \ll \varepsilon\).  
**Operational guardrails:** metrics.version freeze; provenance stamp; reject on MAC fail; log nonces.  
**Baseline comparators:** QOTP; \(\varepsilon\)-private channels; data-locking.  
**Qudit target choice:** pick \(d\in\{2,3,4\}\); teleport bits \(=2\log_2 d\).  
**Side-channel notes:** constant circuit shape; constant-time compile; no plaintext-dependent pruning.  
**Key lifecycle:** storage, rotation, revocation, incident response; proof of non-reuse.  
**Export/IP line:** publish vs patent search; EAR/ITAR concerns.

### Mini to-do (actionable)

- [ ] Lock primitives (PRF=KMAC256, KDF=HKDF-SHA3, MAC=KMAC256-128).
- [ ] Pick \(\varepsilon\) and \(F_{\min}\) (e.g., \(\varepsilon=2^{-20}\) lab; \(F_{\min}=0.99\) on-chip, 0.90 metro).
- [ ] Choose \(d\) and rounds for v0.1; depth estimate.
- [ ] Add **Nonce Ledger** (file/KV) to enforce uniqueness.
- [ ] Prepare IND test harness (Pauli-shadow distinguisher) + nonce-reuse ablation.

### Vendor outreach (paste-ready)

**Subject:** Pilot: nonce-keyed quantum encryption + teleportation (metrics frozen)  
**Body:** We propose an end-to-end demo of a nonce-keyed quantum encryption unitary \(U_{K,\nu}\) on \(n=3\text{–}5\) qubits, transported via standard teleportation with authenticated Bell bits.  
**Acceptance metrics (frozen):** fidelity \(F \ge 0.99\) on-chip (\(\ge 0.90\) over metro), leakage proxy \(\varepsilon \le 2^{-20}\) by Pauli-shadow test, **no nonce reuse**.  
**What we need:** scheduled access (single-chip + optional metro hop), connectivity map, classical side-channel hooks.  
**Artifacts:** circuits (JSON), MAC’d Bell outcomes, provenance stamps (git SHA, metrics.version, nonce).
<!-- END: LAST_MILE_BUNDLE -->

<!-- BEGIN: COMPLIANCE_GAPS -->

## Compliance & gaps (tracking)

- Primitives locked (KMAC/HKDF-SHA3): ☐
- Nonce ledger wired into pipeline: ☐
- IND harness + reuse ablation: ☐
- Metrics/version + provenance stamped into runs: ☐
- Vendor outreach brief finalized: ☐
<!-- END: COMPLIANCE_GAPS -->

