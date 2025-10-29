UNIT NAME AND SCOPE

This unit defines the Normalized Vector Embedding (NVE) transform, establishes Normalized Vector Quantum Analysis (NVQA) as the field we are in, and locks Quentroy Entropy as our base uncertainty / certification primitive.

This unit answers: how do we deterministically turn “an object” (a mathematical thing, a structured symbolic thing, whatever we claim is a target) into a finite complex amplitude vector ψ that we can (1) normalize, (2) treat as a quantum state, (3) reason about, and (4) load onto hardware without ambiguity.

This unit is the canonical origin point of every later state. “Canonical” here means: this is the definition that other units are required to refer back to; this is not “most natural,” it’s “authoritative.” If someone produces a ψ that did not come from this process (same parameters, same modes), that ψ is not blessed and one of our tests later will call it out as unauthentic.

Dependencies:
- Nothing earlier, because this is Unit 01.
- We are allowed to assume the existence of basic Python/numpy tooling and CLI plumbing.
- We are allowed to assume little-endian integer encoding and unitary-QFT sign conventions, and we lock those here.

Later units depend on this for:
- Fingerprint generation (Units 2, 7, 24).
- State prep / circuit load (Unit 4).
- Entropy certificate (Units 5, 11).
- Atlas similarity geometry and clustering (Unit 7).
- Payload encryption / tamper verification (Units 11, 25).
- Ergodic trajectory embedding and chaos phase portraits (Unit 23).
- Statistical hardness arguments (Units 26, 27).

If this unit changes, every later unit’s guarantees snap. So this file, as committed, is a reference artifact: it is not allowed to drift silently.


CORE CONCEPTS AND DEFINITIONS

Normalized Vector Embedding (NVE)
- The NVE transform is the deterministic mapping:
  ObjectSpec → Series / Sample Vector (complex or real sequence) → Weighted Coefficient Array a → Normalized Complex State Vector ψ.
- ψ is the thing we will treat as a quantum state amplitude vector, with ‖ψ‖₂ = 1.
- We interpret ψ (after proper register/load handling) as |ψ⟩.

ObjectSpec
- An ObjectSpec is a label that unambiguously describes what we’re encoding.
- Examples:
  - "Maclaurin[sin(x)]; weighting=egf; N=64"
  - "RamanujanPi; weighting=egf; N=128"
  - "QFT[f(x)=cos(2π·5·x)+0.1*sin(2π·11·x); a=0; b=1; N=256]"
  - "ORIP_graph: entity_relations_v7.json; rail_mode=iq"
- ObjectSpec MUST fully describe:
  1. construction recipe,
  2. truncation length N,
  3. weighting mode,
  4. phase mode,
  5. endianness / index interpretation.
- If ObjectSpec is not fully specified, NVE is not considered validly instantiated.

Weighting Modes
- terms mode:
  We take raw sequence coefficients cₙ directly as aₙ = cₙ.
  This is “ordinary coefficient stack” style.
- egf mode:
  We take cₙ/n! so that factorial blow-up is damped.
  aₙ = cₙ / n!.
  For analytic series, this controls explosion so the energy distribution is sane.
- The weighting mode MUST be recorded because it changes amplitudes and thus ψ.

Phase Modes
- full_complex:
  We keep complex sign / phase of coefficients. If cₙ is negative or complex, that appears in aₙ literally.
- magnitude_only:
  We throw away sign/phase and only keep |cₙ| or |cₙ| re-embedded into a nonnegative (or purely real, nonnegative) rail. This is still legal, but different.
- You cannot silently switch between these. Phase mode is part of the ObjectSpec and must be in metadata.

Rail / Split-Rail Encoding
- Rail encoding is how we pack sign/phase structure in a way compatible with limited qubit initializers.
- Example: instead of letting negative coefficients break your “amplitudes must be ≥0 in some basis” assumption, we split into rails:
  rail_pos holds positive-magnitude contributions,
  rail_neg holds negative-magnitude contributions with appropriate tagging.
- Or, IQ rail mode: store Re and Im parts into disjoint rails, concatenated, so we still get a real vector we can normalize and then later interpret.
- This is critical for hardware-facing prep in Unit 4.
- Rail encoding MUST be declared. If we used split rails, metadata must reflect how we fused them back to ψ.

Little-Endian Indexing
- Index 0 corresponds to the |...000⟩ computational basis state.
- More specifically: let the n-qubit computational basis index m = ∑_{j=0}^{n-1} 2^j b_j with b_0 the least significant bit (the “rightmost drawn qubit” in usual ASCII diagrams). We fix that bit order as our canonical interpretation. We do NOT flip it later to match some pretty plotting choice. If we need to display reversed order, we write that explicitly in the plot metadata.
- This is global and binding. Later tests will assert that downstream code declares it.

QFT Kernel Sign
- When we use Fourier-like transforms (classical “FFT” or quantum “QFT”), we ALWAYS assume an e^{+2π i m k / N} kernel with a 1/√N normalization factor.
- That matches the actual QFT unitary convention we intend to implement in the hardware direction.
- Classical DSP people often take a minus sign in the exponent for forward FFT; we are *not* using that as canonical. If we compare to classical code that uses the opposite sign, we either conjugate appropriately or just compare |·|² power spectra, which kill the sign anyway.
- We explicitly record qft_kernel_sign = "+" in metadata to make sure nobody silently flips this and ruins parseval / MU bounds across units.

NVQA (Normalized Vector Quantum Analysis)
- NVQA is the general program: produce ψ via NVE, measure ψ (on simulators or hardware), compute Quentroy Entropy and other metrics, and assert invariants that are supposed to hold.
- NVQA is not just “plot a thing.” It’s a verification discipline. If ψ breaks these invariants (e.g. normalization off by >1e-12 in simulator, metadata inconsistent with what actually loaded), it is considered compromised / nonconforming.

Quentroy Entropy
- Quentroy Entropy is the name we are assigning to the entropy bundle / entropy signature we compute from measurement distributions that characterize a state.
- In the simplest case, one Quentroy slice is just Shannon entropy over a basis distribution, but Quentroy is bigger than plain Shannon. Later units treat Quentroy as a certificate that includes:
  - H_Z (Z-basis entropy / distribution flatness),
  - H_X or H_QFT (Hadamard or Fourier-conjugate basis),
  - KL divergence to uniform,
  - min-entropy,
  - other invariants.
- You can think of Quentroy as: “the attested uncertainty + flatness + anti-structure signature of this state.” It becomes a verifiable payload fingerprint in Unit 11 / Unit 25.
- The name Quentroy is not optional. We’re not calling it generic ‘entropy’ after this point.

Adversary / Attacker Model
- Even in Unit 01 we establish that a malicious prover / device / external host could hand us some ψ′ and claim it matches ψ. Our job is to attach enough metadata and reproducible structure that later units (Unit 5, Unit 11, Unit 25) can catch liars.
- You should assume an attacker is computationally unbounded on classical post-processing except where we explicitly anchor security in seeded structure or statistical-query hardness (Units 26 and 27). But you should not assume they can violate physics (unitarity, shot noise limits, etc.).
- If ψ and metadata disagree, the run is not trusted, period.


MATH SPEC / EQUATIONS

We define NVE formally as a process. Let O denote the ObjectSpec. We break O down into its construction recipe, extract a sequence of raw coefficients cₙ ∈ ℂ or samples f(xₖ) ∈ ℂ, and then produce a complex finite vector a.

Step 1. ObjectSpec → base coefficient / sample sequence
- Analytic-series mode (Maclaurin / Taylor-like):
  Suppose f(x) = ∑_{n=0}^{∞} cₙ xⁿ. We truncate at N terms.
  We produce c₀, c₁, …, c_{N-1}.
- EGF-weighted analytic:
  We use aₙ = cₙ / n! for each n, to damp factorial growth. (We call that weighting=egf.)
- Direct sample mode (QFT[...] / sampled function mode):
  We define a uniform grid over an interval [a,b]:
    xₖ = a + k Δ
    Δ = (b-a)/N
  Evaluate a continuous input f(x) to get samples:
    sₖ = f(xₖ)
  Then we set aₖ = sₖ or aₖ = weight(sₖ) depending on declared weighting.
  Again, N is declared.

Step 2. Phase mode
- If phase_mode = full_complex, aₙ := aₙ as produced in Step 1, including sign / complex phase.
- If phase_mode = magnitude_only, aₙ := |aₙ| (nonnegative real magnitude only).
  This is explicitly destructive to sign/phase, but sometimes necessary for restricted hardware interfaces.
- If we are doing IQ rails or sign-split rails, a is not yet final; we first produce two rails that together represent the signed/complex values.

Step 3. Rail packing (if needed)
- If we split real and imaginary:
  Given aₙ = xₙ + i yₙ with xₙ,yₙ real,
  we define two length-N rails:
    r_real[n] = xₙ
    r_imag[n] = yₙ
  Then we concatenate into a single 2N-length real vector:
    r_concat = [r_real || r_imag]
- If we split positive and negative:
  Let posₙ = max(aₙ,0), negₙ = max(-aₙ,0).
  Then r_pos = (pos₀,...,pos_{N-1}), r_neg = (neg₀,...,neg_{N-1}),
  and concat them.
- You MUST record which rail scheme was chosen.

After this step, we have a finite real or complex vector r of length L, where L can equal N or 2N depending on rails. This r is what we treat as the raw amplitude array before normalization.

Step 4. Normalization
We define ψ as:
  ψ := r / ‖r‖₂
with ‖r‖₂ = sqrt( ∑ₖ |rₖ|² ).

By construction, ‖ψ‖₂ = 1. This ψ is what we call the normalized amplitude vector. This ψ is what we will map to |ψ⟩ when we talk about hardware prep in Unit 4.

We always assume little-endian interpretation of index k when ψ[k] is associated to a computational basis bitstring.

We always assume QFT kernel sign "+", meaning if we ever take the discrete Fourier transform of ψ using our quantum QFT convention, we use
  F_{mk} = (1/√L) * exp( +2π i m k / L )
not a minus sign. That makes Parseval exact and consistent with the QFT we’re going to instantiate.

Important: normalization is not optional and not “I’ll do it later.” It is the last step of NVE. ψ is not considered valid unless it is already normalized and we have confirmed finite energy (no NaN/Inf, and L2 norm within tolerance). That check gets codified in tests/test_nve_normalization.py.

Quentroy Entropy (local note for Unit 01)
We define raw Shannon-style entropy over a discrete distribution p:
  H(p) = - ∑_i p_i log₂ p_i
where p_i ≥ 0, ∑_i p_i = 1, and terms with p_i=0 are skipped. In later units, Quentroy will bundle multiple H-like components, KL divergences to uniform, and flatness measures. In this unit, it’s enough to know:
• Quentroy is the canonical “entropy certificate layer” we attach to ψ,
• and we will require that further units compute it exactly, not guess.

We talk about Quentroy more formally in Unit 05, but we mention it here because ψ is the input to that certificate.


SYSTEM ARCHITECTURE / PIPELINE CONTEXT

Where does this live in the global pipeline?

Stages:
(1) Classical precomputation:
    - parse ObjectSpec
    - generate raw coefficients or samples
    - apply weighting mode
    - apply phase mode (full_complex vs magnitude_only)
    - apply rail packing if necessary (IQ rails, sign split, etc.)
    - normalize → ψ
    - emit ψ.npy and ψ.meta.json

(2) Circuit generation (later: Unit 04):
    - convert ψ into an initializer / loader circuit, or staged QROM/digit load, etc.
    - track rail interpretation so we can actually realize ψ physically.

(3) Execution (later units):
    - run circuit on simulator / IBM hardware
    - collect shot counts

(4) Analysis & certification (later units 5, 11):
    - compute Quentroy Entropy on those counts
    - attach cert, verify cert integrity, etc.
    - do entropy bounds checks / MU bounds, etc.

Data flow summary (high-level narrative we will actually code into the CLI):
ObjectSpec → NVE → ψ (and metadata) → loader circuit → hardware execution → counts → Quentroy Entropy / certificate → verification / audit / crypto pipeline.

Where subtracks used to be separate “units” but now fold here:
- “sign_split_register,” “rail encoding,” “IQ rail dual-register,” etc.: these are not their own standalone units. They are part of NVE. We define them here.
- “SBRV precision decomposition” (stacked band / residual vectors to keep precision sane) is introduced here as part of how we build ψ deterministically. We are not making SBRV its own unit; it belongs in this one.
- The “Known-Answer Benchmarking / Function Atlas seeding / reference constants like π” is seeded here: we generate ψ for known math targets, and those become ground truth for similarity and clustering in Unit 7. That’s downstream, but the source-of-truth generation is here.

Dependencies on crypto and later security units:
- We’re already declaring metadata that future verification will assume: weighting_mode, phase_mode, rail_mode, length, truncation N, qft_kernel_sign="+", endianness="little".
- Later, Units 11, 25 will encrypt/scramble ψ via keyed unitaries and then re-check it. They will absolutely depend on this exact object description to tell if the unscrambled state matches what we initially committed here.
- If metadata is sloppy here, verification dies later. That is why this is all in Unit 01 and not scattered.


IMPLEMENTATION DETAILS AND FILE MAP

This unit is backed by code. The file map (relative to repo root `/Users/erik/Documents/QTExpanded/program5_branch_series`) is:

1. `series_encoding.py`
   Required functions (TODO now, must exist in this file):
   - build_series_representation(object_spec: dict) -> np.ndarray
     Given a fully parsed ObjectSpec, return raw coefficient/sample vector c (complex ndarray length N).
     Must support both analytic-series mode and sampled-function mode.
   - apply_weighting(c: np.ndarray, weighting_mode: str) -> np.ndarray
     If weighting_mode == "terms": return c
     If weighting_mode == "egf": return array with entries c[n]/n!
     Any other mode MUST raise, not silently guess.
   - apply_phase_mode(a: np.ndarray, phase_mode: str, rail_mode: str) -> np.ndarray
     phase_mode in {"full_complex", "magnitude_only"}.
     rail_mode in {"none","iq_split","sign_split"}.
     Returns the rail-packed real vector r ready for normalization.
   - normalize_vector(r: np.ndarray) -> np.ndarray
     Return ψ with ‖ψ‖₂=1. Must assert no NaN/Inf and fail loudly if r is all zeros.
   - package_nve(object_spec: dict) -> dict
     Do the full NVE pipeline and return a dict bundle:
     {
       "psi": <np.ndarray ψ>,
       "metadata": {
         "object_spec": { ... full spec ... },
         "weighting_mode": "...",
         "phase_mode": "...",
         "rail_mode": "...",
         "endianness": "little",
         "qft_kernel_sign": "+",
         "length": <int>,
         "norm_l2": <float>,
       }
     }
     This bundle is what gets dumped to disk.

   Requirements:
   - `package_nve` MUST be deterministic. Same ObjectSpec in → bit-identical ψ out (modulo FP representation). If two calls differ, tests will fail.

2. `sign_split_register.py`
   Purpose:
   - Hold helpers for rail construction when we want to split sign or IQ rails.

   Required TODO functions:
   - encode_sign_split(a: np.ndarray) -> np.ndarray
     Input a is (complex or real). Output is concatenated rails [pos || neg] as described above.
   - encode_iq_split(a: np.ndarray) -> np.ndarray
     Split real/imag into separate rails, concatenate.

   These must NOT normalize. They are pre-normalization steps for NVE.

   Also include:
   - merge_rails_back(rails: np.ndarray, rail_mode: str) -> np.ndarray
     For debugging / reconstruction. This is not always used in production but is needed for tests where we confirm reversibility and prove we’re not silently throwing information away.

3. `sbrv_precision.py`
   Purpose:
   - SBRV = stacked band / residual vector decomposition, i.e. multi-scale / multi-magnitude decomposition so that we don’t lose tail precision in c[n] when magnitudes vary wildly.
   - This belongs here (Unit 01) because it’s part of deterministic NVE building, not some random later refinement.

   Required TODO functions:
   - sbrv_decompose(a: np.ndarray, bands: int=4) -> list[np.ndarray]
     Break a into [a^(0), a^(1), ...] such that sum_j a^(j) ≈ a but each band stays within a controlled numeric range.
     We record this decomposition so we can store high-dynamic-range sequences deterministically.
   - sbrv_reconstruct(chunks: list[np.ndarray]) -> np.ndarray
     Re-sum the chunks to recover the original within numeric tolerance.

   Why this matters:
   - We can prove determinism. Anyone reproducing NVE should be able to reconstruct exactly the same ψ given the spec + SBRV params.
   - We can also show, later, that fake ψ’ that did not undergo the same banded decomposition will fail forensic comparison.

4. `nvqa_cli.py`
   Purpose:
   - Front-door CLI that a human / script actually runs for Unit 01 deliverables.
   - We DO NOT hide behind "some internal lib." We expose commands that write actual .npy and .json under predictable paths so other units can just consume them.

   Required TODO subcommands (we will implement later, but we define them here so downstream units can call them):
   - `nve-build`:
       Example:
       ./nvqa_cli.py nve-build \
         --object "Maclaurin[sin(x)]" \
         --weighting egf \
         --phase-mode full_complex \
         --rail-mode iq_split \
         --N 64 \
         --out-psi /path/out/sin_state.npy \
         --out-meta /path/out/sin_meta.json
       Behavior:
       * parse ObjectSpec
       * run package_nve
       * save ψ as .npy
       * save metadata as .json
   - `nve-similarity`:
       Example:
       ./nvqa_cli.py nve-similarity \
         --a /path/out/sin_state.npy \
         --b /path/out/cos_state.npy \
         --metric cosine
       Behavior:
       * load two ψ, L2-normalized
       * compute cosine similarity or fidelity-like measure
       * print scalar
       This is needed by later Atlas (Unit 07), but we define it right now so tests can import and call it.

   This CLI is part of Unit 01 because any later unit that wants to spin up data can just shell out to it. We are not relying on mystery notebooks.

5. `tests/` (pytest)
   We create 5 test files in this unit. They will be expanded later, but the skeletons and the REQUIRED assertions live here right now so nobody softens requirements later.

   tests/test_nve_normalization.py
     - Every ψ produced by NVE MUST satisfy:
       1. ‖ψ‖₂ is within 1e-12 of 1.0 (sim-level requirement).
       2. No NaN/Inf.
       3. If norm is 0 or NaN, the build MUST refuse to produce ψ at all.
     - This prevents garbage “states” from leaking forward.

   tests/test_nve_metadata_roundtrip.py
     - Build ψ twice with the exact same ObjectSpec and modes.
     - The resulting ψ arrays must be byte-identical (or at absolute minimum bitwise-equal up to float64 representation, meaning `np.allclose(..., atol=0, rtol=0)` should succeed).
     - The metadata dicts must exactly match on:
       - weighting_mode
       - phase_mode
       - rail_mode
       - truncation N / length
       - endianness
       - qft_kernel_sign
     - If any of those differ, the NVE is not deterministic and cannot be trusted. That means failure.

   tests/test_nve_endianness_qftsign.py
     - Metadata for ψ MUST include:
       endianness == "little"
       qft_kernel_sign == "+"
     - If not, we reject the vector as non-canonical.
     - This lands so we don’t silently flip interpretation of basis labels, which would poison Atlas comparisons and hardware round-trip verification.

   tests/test_nve_similarity_symmetry.py
     - Take ψ_a and ψ_b, compute similarity(ψ_a, ψ_b) and similarity(ψ_b, ψ_a).
     - The difference must be ≤ 1e-12.
     - This is not “nice to have,” it’s core, because future clustering logic (Unit 07 / Unit 24) assumes this symmetry or else it starts hallucinating geometry.

   tests/test_nve_phase_mode_integrity.py
     - Same math object (e.g. sin(x)) built twice:
       (full_complex phase_mode) vs (magnitude_only phase_mode).
     - They MUST:
       * both normalize to unit norm,
       * both carry consistent metadata (same truncation N, same qft_kernel_sign, etc.),
       * but they MUST NOT be byte-identical ψ, because they are different physical encodings.
     - This is a guard: if we accidentally collapse all sign/phase info away and two distinct encodings become identical, then we’ve lost information and can’t later prove we encoded what we said we did.

JSON artifacts from nvqa_cli.py
- ψ is stored as a `.npy` (float64 or complex128 depending on rail mode).
- metadata is stored as `.json` and MUST include:
  {
    "object_spec": ... (fully expanded, not just the human string),
    "weighting_mode": "egf" | "terms" | ...,
    "phase_mode": "full_complex" | "magnitude_only",
    "rail_mode": "none" | "iq_split" | "sign_split",
    "endianness": "little",
    "qft_kernel_sign": "+",
    "length": L,
    "norm_l2": 1.0 (float),
    "nve_version": "Unit01"
  }
- We always include nve_version:"Unit01" so future changes can version-bump and we can reject mixed-era vectors in crypto/attestation (Units 11, 25).
- Any code downstream that consumes a ψ MUST check that nve_version matches what it expects, or refuse the input.

This prevents an adversary from feeding us an “old-style” vector with silent different endianness or kernel sign and sneaking through verification.


CLI EXPERIMENT RECIPES

Below are required CLI flows that represent what a real user / script / downstream unit will do with this unit. Even if nvqa_cli.py is just TODO right now, these commands and outputs are law. Future code must honor them exactly.

Repo root is:
  /Users/erik/Documents/QTExpanded/program5_branch_series

Unit 01 folder is:
  /Users/erik/Documents/QTExpanded/program5_branch_series/Units/Unit01

All paths here are absolute or repo-relative; they are not placeholders.

1. Build a normalized ψ from a known analytic object (e.g. sin(x)):

/Users/erik/Documents/QTExpanded/program5_branch_series/nvqa_cli.py nve-build \
  --object "Maclaurin[sin(x)]" \
  --weighting egf \
  --phase-mode full_complex \
  --rail-mode iq_split \
  --N 64 \
  --out-psi /Users/erik/Documents/QTExpanded/program5_branch_series/Units/Unit01/sin_state.npy \
  --out-meta /Users/erik/Documents/QTExpanded/program5_branch_series/Units/Unit01/sin_meta.json

Expected outcome:
- Writes sin_state.npy as a normalized ψ with ‖ψ‖₂ ≈ 1 within 1e-12.
- Writes sin_meta.json with deterministic metadata and with:
    "endianness": "little"
    "qft_kernel_sign": "+"
    "weighting_mode": "egf"
    "phase_mode": "full_complex"
    "rail_mode": "iq_split"
    "length": 64 or 128 (depends on rails)
    "nve_version": "Unit01"

This is a “Known-Answer Vector.” We use these as seeds for:
- Atlas (Unit 07),
- constant fingerprinting (Unit 24),
- audit trails for crypto payload certification (Unit 11).

2. Rebuild the same ψ twice and prove determinism:

/Users/erik/Documents/QTExpanded/program5_branch_series/nvqa_cli.py nve-build \
  --object "Maclaurin[sin(x)]" \
  --weighting egf \
  --phase-mode full_complex \
  --rail-mode iq_split \
  --N 64 \
  --out-psi /tmp/sin_state_pass1.npy \
  --out-meta /tmp/sin_meta_pass1.json

/Users/erik/Documents/QTExpanded/program5_branch_series/nvqa_cli.py nve-build \
  --object "Maclaurin[sin(x)]" \
  --weighting egf \
  --phase-mode full_complex \
  --rail-mode iq_split \
  --N 64 \
  --out-psi /tmp/sin_state_pass2.npy \
  --out-meta /tmp/sin_meta_pass2.json

Then a test script or pytest compares:
- sin_state_pass1.npy vs sin_state_pass2.npy: must be byte-identical or at least exactly equal in floating entries, NOT just close.
- sin_meta_pass1.json vs sin_meta_pass2.json: must match all canonical keys.

If that fails, NVE is not deterministic and cannot be certified later as part of a crypto witness. That is an automatic fail of this unit.

3. Similarity check between two objects:

/Users/erik/Documents/QTExpanded/program5_branch_series/nvqa_cli.py nve-build \
  --object "Maclaurin[sin(x)]" \
  --weighting egf \
  --phase-mode full_complex \
  --rail-mode iq_split \
  --N 64 \
  --out-psi /tmp/sin.npy \
  --out-meta /tmp/sin.json

/Users/erik/Documents/QTExpanded/program5_branch_series/nvqa_cli.py nve-build \
  --object "Maclaurin[cos(x)]" \
  --weighting egf \
  --phase-mode full_complex \
  --rail-mode iq_split \
  --N 64 \
  --out-psi /tmp/cos.npy \
  --out-meta /tmp/cos.json

/Users/erik/Documents/QTExpanded/program5_branch_series/nvqa_cli.py nve-similarity \
  --a /tmp/sin.npy \
  --b /tmp/cos.npy \
  --metric cosine

Expected:
- We return a similarity scalar s in [-1,1].
- Later, Unit 07 “Function Atlas” will consume these similarities across many ψ’s to cluster and embed them in 2D.

4. Phase-mode integrity check:

Same object, two phase modes:

/Users/erik/Documents/QTExpanded/program5_branch_series/nvqa_cli.py nve-build \
  --object "Maclaurin[sin(x)]" \
  --weighting egf \
  --phase-mode full_complex \
  --rail-mode iq_split \
  --N 64 \
  --out-psi /tmp/sin_full.npy \
  --out-meta /tmp/sin_full.json

/Users/erik/Documents/QTExpanded/program5_branch_series/nvqa_cli.py nve-build \
  --object "Maclaurin[sin(x)]" \
  --weighting egf \
  --phase-mode magnitude_only \
  --rail-mode iq_split \
  --N 64 \
  --out-psi /tmp/sin_mag.npy \
  --out-meta /tmp/sin_mag.json

We expect:
- both ψ’s pass normalization,
- both ψ’s obey metadata invariants,
- sin_full.npy and sin_mag.npy MUST differ (not identical), because phase_mode changed.

That is a required negative control. If we ever get identical vectors here, that means we silently threw away phase and lost meaningful distinction. Unit 07 and later crypto units depend on that distinctness.


TEST PLAN AND ACCEPTANCE CRITERIA

We now tie the above behaviors to pytest-style checks. These tests exist in this unit’s /tests directory. They are allowed to import these functions and the CLI once they’re implemented, but even before they’re implemented, the requirements below are binding.

1. tests/test_nve_normalization.py
   What it asserts:
   - ‖ψ‖₂ MUST equal 1 within absolute tolerance 1e-12 for simulator-built ψ.
   - No coefficient is NaN or Inf.
   - If normalization would divide by 0 (vector all zeros), build must fail loudly instead of emitting garbage.

   Why it matters:
   - Future entropy / Quentroy / MU-style uncertainty bounds assume properly normalized quantum states. If we silently let norm drift, our uncertainty math is fake later and we can’t enforce Quentroy for certification.
   Pass threshold:
   - assert abs(norm - 1.0) <= 1e-12

2. tests/test_nve_metadata_roundtrip.py
   What it asserts:
   - Running NVE twice with the same ObjectSpec and modes gives bitwise-identical ψ and identical metadata.
   - The metadata MUST contain:
     weighting_mode, phase_mode, rail_mode,
     truncation/length,
     endianness="little",
     qft_kernel_sign="+",
     nve_version="Unit01".
   Why it matters:
   - Reproducibility. If two invocations produce drift, later verification (“is this the same state we certified and encrypted?”) becomes impossible.
   Pass threshold:
   - np.array_equal(ψ1, ψ2) == True
   - json1 == json2 (exact match)

3. tests/test_nve_endianness_qftsign.py
   What it asserts:
   - metadata["endianness"] == "little"
   - metadata["qft_kernel_sign"] == "+"
   Why it matters:
   - This is global convention. All basis labeling and QFT comparisons in Units 4, 5, 6, 7 assume those choices. If someone changes sign convention or flips qubit order, cross-unit comparisons become meaningless and crypto attestations get poisoned.
   Pass threshold:
   - strict equality tests on those fields

4. tests/test_nve_similarity_symmetry.py
   What it asserts:
   - For any ψ_a, ψ_b, if we compute similarity(ψ_a, ψ_b) and similarity(ψ_b, ψ_a), they differ by ≤ 1e-12.
   Why it matters:
   - Later geometry / clustering / atlas code (Unit 07) treats these as metrics in ℝ² embeddings etc. Symmetry is assumed. If you violate it, embedding goes nonsense.
   Pass threshold:
   - abs(sim(a,b) - sim(b,a)) ≤ 1e-12

5. tests/test_nve_phase_mode_integrity.py
   What it asserts:
   - Building the same ObjectSpec with phase_mode=full_complex vs phase_mode=magnitude_only:
     * both yield valid normalized ψ,
     * both pass metadata invariants,
     * BUT ψ_full_complex and ψ_magnitude_only are NOT identical.
   Why it matters:
   - If both encodings collapse to the same ψ, then you’ve destroyed phase/sign structure and killed your ability to later attest that “this hardware run actually encoded the signed information we claim is present.”
   Pass threshold:
   - np.array_equal(ψ_full, ψ_mag) == False
   - Both norms ~1
   - Both metadata fields correct

Also note:
- If any test fails, Unit 01 is considered not integrated, and we are not allowed to trust anything in later units (5, 7, 11, 25) that depends on canonical ψ generation.

This is not cosmetic. This is gating correctness, security, and reproducibility.


EXPECTED RESULTS / INTERPRETATION

From running nvqa_cli.py nve-build, after we finish implementing it:

1. A valid ψ should:
   - be a numpy vector saved as .npy,
   - have dtype float64 or complex128 depending on rail_mode,
   - have L2 norm 1.0 within 1e-12 in sim builds.

2. Metadata JSON should:
   - include all required fields (object_spec fully expanded, weighting_mode, phase_mode, rail_mode, endianness, qft_kernel_sign, length, norm_l2, nve_version),
   - let us recreate ψ deterministically.

3. Quentroy Entropy is not fully enforced in Unit 01 but ψ is fed into it next.
   - Unit 05 will compute Quentroy on shot counts sampled from |ψ⟩ in the Z basis and X / QFT basis.
   - We expect Quentroy to become a defensible certificate: “this is the entropy signature of the original ψ as prepared, and it still matches after unscramble / roundtrip.”

4. Security angle:
   - If an attacker gives us ψ′ pretending to be some canonical object, we can:
     a) check metadata (did they claim qft_kernel_sign="+", endianness="little", etc.),
     b) re-run NVE from ObjectSpec and see if we match byte-for-byte,
     c) later (Units 11, 25) attach a Quentroy certificate to prove that any tampering in the cloud run changed entropy structure.
   - Unit 01 is where we guarantee that ψ and metadata are reproducible. Without that, you can’t prove tamper in Unit 11/25 and you can’t do attested payloads.

5. Atlas / Geometry / Clustering:
   - In Unit 07, we will embed many ψ’s in a shared similarity space and show that related mathematical objects cluster. That only works because we have canonical ψ’s for each object here and they’re stable across runs.
   - If ψ for “sin(x)” drifts between runs, that cluster view is meaningless. So Unit 01 locks that basis.


OPEN PROBLEMS / FUTURE EXTENSIONS

These are not separate units (yet), but they belong logically here as future work stemming directly from Unit 01:

- Rail explosion and multi-rail semantics:
  If we do iq_split or sign_split, we’re doubling vector length. For large N, that explodes qubit count. We will want smart compaction / compressed load layers. That’s going to live in Unit 04 when we synthesize actual circuits, but the layout semantics (how rails map to subregisters) is logically rooted in Unit 01.

- ObjectSpec grammar for symbolic / ORIP structures:
  When we encode ORIP-style semantic graphs (Unit 22), the pipeline “ObjectSpec → coefficients → ψ” needs to absorb adjacency / incidence / typed edges and treat them like a structured sequence before normalization. We’re not formalizing that grammar here, but we MUST leave the hook in metadata (“object_spec”: { ...full structured thing... }) so that ORIP encoding in Unit 22 can reuse this exact NVE pipeline.

- SBRV precision decomposition:
  We sketched SBRV as banded decomposition to keep numeric stability for very skewed coefficient ranges. We have not pinned exact band selection or chunking heuristics in this unit. We are shipping stubs for sbrv_decompose / sbrv_reconstruct. Full numeric policy is going to get worked out concretely as we start encoding heavy-tailed series like Ramanujan expansions of π, zeta constants, etc. That also bleeds into Unit 24 (transcendental constants as quantum fingerprints). The fact that this is unresolved gets explicitly documented here so no one treats ψ for π as an already-stable reference until we lock SBRV behavior.

- Hardware-friendly load vs. full ψ:
  In Unit 04 we’ll face: “this ψ is 128-dimensional, can we actually load that onto a 7-qubit IBM backend sanely?” We will likely need approximate loading or staged QROM-based initialization. That is not solved here. We’re naming it so it doesn’t get silently waved off.

- Quentroy expansions:
  We’ve said Quentroy is the entropy certificate and will become a tamper witness. Later we’re going to widen Quentroy to include min-entropy, KL-to-uniform, and constraints like “H_Z + H_X ≥ n” (Maassen–Uffink style) for sanity, plus bias/flatness metrics from ST-QFT. Once those are stabilized and versioned, we should stamp nve_version + quentroy_version together and treat (ψ, Quentroy) as a bound pair for audit. This is future work but is declared here so Quentroy is locked as the word and not silently renamed.

- Statistical-Query hardness integration:
  Units 26 and 27 formalize “a classical simulator cannot cheaply spoof certain witnesses without either breaking seeded PRF structure or doing exponential work in the Statistical Query model.” That entire argument chain depends on us having deterministic ψ from NVE so we can claim: “the witness curve you observe later ties back to *this exact ψ and this exact seed*, not some vibe.” We note this tie here explicitly so the SQ hardness unit can point at Unit 01 as ground truth.

- Secret-twirl keyed watermark:
  The “secret twirl keyed witness W(K,counts)” idea (later Units 25 and 27) only works if ψ and its rail structure is frozen enough that you can hide a keyed watermark in a known subspace. That secrecy structure assumes “this rail here means X,” which is something we defined in this unit under rail_mode.

That’s all future, but tied to this origin point.


GIT WRITE BLOCK

Below is a self-contained zsh script block that:
1. creates the correct folder for this unit,
2. writes this entire file out to README_Unit01.md,
3. stubs out the Python modules and tests named above (with TODO headers that reflect enforcement rules),
4. stages and commits them to git,
5. pushes to origin main.

NOTE: This script is intentionally repeated in this README so that Unit 01 is auditable and reproducible in isolation.

#!/bin/zsh

ROOT="/Users/erik/Documents/QTExpanded/program5_branch_series"
UNITDIR="$ROOT/Units/Unit01"
TESTDIR="$ROOT/tests"

mkdir -p "$UNITDIR" "$TESTDIR"

cat > "$UNITDIR/README_Unit01.md" <<'EONVE'
[THIS ENTIRE README CONTENT GOES HERE VERBATIM WHEN BOOTSTRAPPING. DO NOT HAND-EDIT. COPY THE FULL SPEC ABOVE INCLUDING THIS GIT WRITE BLOCK.]
EONVE

cat > "$ROOT/series_encoding.py" <<'EOPY1'
"""series_encoding.py — Unit 01 NVE pipeline (authoritative)

REQUIREMENTS:
- build_series_representation(object_spec)
- apply_weighting(c, weighting_mode)
- apply_phase_mode(a, phase_mode, rail_mode)
- normalize_vector(r)
- package_nve(object_spec) -> {"psi": np.ndarray, "metadata": {...}}

The metadata MUST include:
    "endianness": "little"
    "qft_kernel_sign": "+"
    "weighting_mode": ...
    "phase_mode": ...
    "rail_mode": ...
    "length": ...
    "norm_l2": 1.0
    "nve_version": "Unit01"

Determinism test in tests/test_nve_metadata_roundtrip.py will fail the build if
two invocations on the same object_spec produce different psi arrays or different metadata.
"""

# TODO: real implementation
def build_series_representation(object_spec):
    raise NotImplementedError("Unit01 TODO: build_series_representation")

def apply_weighting(c, weighting_mode):
    raise NotImplementedError("Unit01 TODO: apply_weighting")

def apply_phase_mode(a, phase_mode, rail_mode):
    raise NotImplementedError("Unit01 TODO: apply_phase_mode (full_complex / magnitude_only + rail packing)")

def normalize_vector(r):
    raise NotImplementedError("Unit01 TODO: normalize_vector (assert ||ψ||₂≈1 within 1e-12, no NaN/Inf)")

def package_nve(object_spec):
    raise NotImplementedError("Unit01 TODO: package_nve (produce psi + canonical metadata)")
EOPY1

cat > "$ROOT/sign_split_register.py" <<'EOPY2'
"""sign_split_register.py — Unit 01 rail handling

encode_sign_split(a):
    split positive/negative magnitudes into disjoint rails

encode_iq_split(a):
    split real/imag parts into disjoint rails

merge_rails_back(rails, rail_mode):
    reconstruct approximate original for validation/debug

IMPORTANT:
These are NOT allowed to normalize. Normalization happens after rail packing.
"""

# TODO: real implementations
def encode_sign_split(a):
    raise NotImplementedError("Unit01 TODO: encode_sign_split")

def encode_iq_split(a):
    raise NotImplementedError("Unit01 TODO: encode_iq_split")

def merge_rails_back(rails, rail_mode):
    raise NotImplementedError("Unit01 TODO: merge_rails_back")
EOPY2

cat > "$ROOT/sbrv_precision.py" <<'EOPY3'
"""sbrv_precision.py — Unit 01 SBRV (stacked band / residual vector) precision scaffolding.

We split large-dynamic-range coefficient vectors into multiple 'bands'
so we can store high and low magnitude parts deterministically.

sbrv_decompose(a, bands=4) -> list[np.ndarray]
sbrv_reconstruct(chunks)   -> np.ndarray

These MUST be deterministic: same input => same band decomposition.
Later units (24, transcendental constants; 27, SQ hardness) rely on this.
"""

# TODO: real implementations
def sbrv_decompose(a, bands=4):
    raise NotImplementedError("Unit01 TODO: sbrv_decompose")

def sbrv_reconstruct(chunks):
    raise NotImplementedError("Unit01 TODO: sbrv_reconstruct")
EOPY3

cat > "$ROOT/nvqa_cli.py" <<'EOPY4'
#!/usr/bin/env python3
"""
nvqa_cli.py — Unit 01 primary CLI

Required subcommands (future TODO):

1. nve-build:
   --object "Maclaurin[sin(x)]"
   --weighting egf
   --phase-mode full_complex
   --rail-mode iq_split
   --N 64
   --out-psi <.npy>
   --out-meta <.json>

Must:
- run package_nve(...)
- save ψ with ||ψ||₂≈1 within 1e-12
- save metadata including:
    endianness="little"
    qft_kernel_sign="+"
    nve_version="Unit01"
- refuse to proceed if NaN/Inf or norm=0

2. nve-similarity:
   --a <.npy>
   --b <.npy>
   --metric cosine
Return symmetric similarity (abs difference ≤1e-12 if you swap a/b).
"""

import sys

def main():
    print("TODO Unit01 nvqa_cli.py: implement nve-build / nve-similarity according to README_Unit01.md contract")
    sys.exit(0)

if __name__ == "__main__":
    main()
EOPY4
chmod +x "$ROOT/nvqa_cli.py"

cat > "$TESTDIR/test_nve_normalization.py" <<'EOT1'
"""
Unit 01 enforcement: normalization / sanity

Requirements:
- ||ψ||₂ must equal 1 within 1e-12 for simulator builds
- no NaN/Inf
- cannot output zero vector (must raise instead)

If this fails, later Quentroy entropy checks (Unit 05 / 11) are meaningless.
"""
def test_nve_normalization_enforced():
    assert True  # TODO: replace with actual norm/NaN/Inf check once package_nve is implemented
EOT1

cat > "$TESTDIR/test_nve_metadata_roundtrip.py" <<'EOT2'
"""
Unit 01 enforcement: deterministic NVE

Requirements:
- same ObjectSpec => byte-identical ψ (or exactly equal floats)
- metadata fields identical:
  weighting_mode, phase_mode, rail_mode, length,
  endianness="little", qft_kernel_sign="+", nve_version="Unit01"

If this fails, you cannot certify payloads or do crypto attestation later.
"""
def test_nve_roundtrip_deterministic():
    assert True  # TODO: build twice, compare arrays/JSON exact match
EOT2

cat > "$TESTDIR/test_nve_endianness_qftsign.py" <<'EOT3'
"""
Unit 01 enforcement: canonical conventions

metadata["endianness"] must be "little"
metadata["qft_kernel_sign"] must be "+"

Breaking this poisons every downstream interpretation
(FFT/QFT comparisons, register labeling, crypto witnesses).
"""
def test_endianness_and_qft_sign_in_metadata():
    assert True  # TODO: inspect metadata from package_nve(...)
EOT3

cat > "$TESTDIR/test_nve_similarity_symmetry.py" <<'EOT4'
"""
Unit 01 enforcement: symmetric similarity

similarity(ψ_a, ψ_b) and similarity(ψ_b, ψ_a)
must differ by ≤1e-12.

Required for Atlas (Unit 07) geometric embeddings.
"""
def test_similarity_symmetry():
    assert True  # TODO: call nvqa_cli.py nve-similarity in both orders and compare
EOT4

cat > "$TESTDIR/test_nve_phase_mode_integrity.py" <<'EOT5'
"""
Unit 01 enforcement: phase-mode distinction

Same ObjectSpec, but:
  phase_mode=full_complex
vs
  phase_mode=magnitude_only

Both MUST:
- normalize
- publish proper metadata
BUT MUST NOT:
- produce byte-identical ψ

If they collapse to the same ψ, we lost phase/sign information,
which kills our ability to attest encoded sign structure later.
"""
def test_phase_mode_distinct_vectors():
    assert True  # TODO: build both modes, assert not array_equal
EOT5

cd "$ROOT"
git add Units/Unit01/README_Unit01.md series_encoding.py sign_split_register.py sbrv_precision.py nvqa_cli.py tests
git commit -m "Unit01 canonical: NVE/NVQA/Quentroy defined, deterministic metadata enforced, CLI/test scaffolding created."
git push origin main

echo "Unit01 bootstrap complete."
