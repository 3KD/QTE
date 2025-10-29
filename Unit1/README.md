# UNIT 1 — CORE THESIS & DOLLARHIDE TRANSFORM (COMPLETE PACK)
# QTE / Dollarhide / QTI Curriculum
# Status: Authoritative spec for Unit 1. This file is meant to drop directly into source control.
# Path target:
#   /Users/erik/Documents/QTExpanded/program5_branch_series/Unit1/README.md
#
# This file defines:
#   - The conceptual thesis (QTI, Dollarhide Transform)
#   - Math formalism and invariants
#   - Label grammar and metadata schema
#   - Implementation/code structure
#   - CLI experiment suite (sim + IBM hooks)
#   - JSON artifact schemas
#   - Test plan + acceptance thresholds
#   - Repo layout for Unit1
#   - Deployment script pattern


================================================================================
1. OBJECTIVES & OUTCOMES
================================================================================

Unit 1 is where we lock the worldview and the rules.

This unit does four essential things:

(1) Define the "Dollarhide Transform":
    mathematical object  →  finite complex vector  →  normalized statevector
    that we can load into a quantum state. This state is the "fingerprint."

(2) Define QTI (Quantum Transcendental Information):
    the idea that we can study structure/identity/similarity of math objects
    (constants, functions, sequences, etc.) by examining their quantum fingerprints
    and the geometry/entropy/symmetry of those fingerprints.

(3) Lock down conventions that EVERYTHING else in the project will use:
    - how we normalize vectors,
    - little-endian bit ordering,
    - QFT sign convention,
    - how we attach metadata,
    - what an experiment “pass” looks like.

(4) Set up a runnable surface:
    - CLI workflows to generate states locally and on hardware (IBM),
    - JSON artifact shapes,
    - test harness fragments,
    - file layout + git push plan.

By the end of this unit:
- We know how to go from "Maclaurin[sin(x)]" to a concrete, normalized vector,
  to |ψ> that lives on n qubits, to JSON that records what we did.
- We know how to compare two fingerprints for "similarity."
- We know how to sanity check and certify all that with tests and entropy metrics.
- We have a standard place in the repo where all this lives and gets committed.


================================================================================
2. CORE CONCEPTS
================================================================================

2.1 The Dollarhide Transform (high level)

We want a pipeline:

    mathematical object  O
        └──> generate a finite complex vector a ∈ ℂ^N
              (e.g. first N Maclaurin coefficients, or sampled function values)
              NOTE: this is not yet normalized.
        └──> normalize that vector to unit ℓ2 norm
              â = a / ||a||₂  (now ||â||₂ = 1)
        └──> interpret â as amplitudes of a quantum state
              |ψ_O> = Σ_{k=0}^{N-1} â_k |k>

That mapping O ↦ |ψ_O> is the "Dollarhide Transform."  
It produces what we will call the fingerprint of O.

This is the founding object of the whole curriculum.  
Everything else (spectral analysis, entanglement, crypto scramblers, chaos,
atlas clustering, etc.) operates on these |ψ> fingerprints.

We are NOT claiming this is uniquely "the" way. We are saying:
- we define it, we make it reproducible, we lock it in,
- everything downstream assumes it's the standard.


2.2 QTI (Quantum Transcendental Information)

"QTI" is our name for:
- encoding math objects into finite normed amplitude vectors,
- loading those as quantum states,
- and then studying their structure using quantum-native or hybrid
  (classical+quantum) diagnostics.

Examples of diagnostics:
- entropy of measurement distributions in incompatible bases,
- spectral features under QFT/FrFT/etc,
- mutual information between registers,
- pairwise similarity in an atlas,
- cryptographic indistinguishability after keyed mixing,
- chaos/scrambling profiles (spectral form factor K(t)),
- etc.

In other words:
QTI treats math objects as physical wavefunctions and then treats physics-
style observables on them as signals about the math itself.


2.3 Known-Answer Benchmarking / Function Atlas

We will build a library of named "known answers" (π, e, ζ(3), J0, Li_s(z), etc).
Each of these is turned into |ψ>. Those become reference fingerprints.

We can then:
- Compare new fingerprints to that atlas,
- Check reproducibility across hardware runs,
- Use known-answers as validation targets when we run on IBM hardware.

This is important because instead of "here's a random benchmark circuit that
does nothing meaningful" we have "here is π embedded in amplitude space, and
here is what Torino hardware did to it." That's auditable and publishable.


================================================================================
3. MATH FORMALISM
================================================================================

3.1 From Object to Vector

We define a function MakeVector(O, mode) that returns finite vector a ∈ ℂ^N.

Typical modes:

(A) Series / Maclaurin mode ("terms" mode):
    If f(x) = Σ_{n=0}^∞ c_n x^n,
    we take the first N coefficients:
        a_n = c_n    for n = 0..N-1

(B) EGF mode ("egf" mode):
    Exponential generating function weighting:
        a_n = c_n / n!
    This tames growth and stabilizes numeric range, especially for
    rapidly growing series.

(C) Sample/QFT mode ("QFT[...]"):
    For a function g(x) sampled on a uniform grid:
        x_k = a + k Δ, with k = 0..N-1, Δ = (b - a)/(N-1) or (b-a)/N
        a_k = g(x_k)
    Useful for things that aren't analytic at 0, or for arbitrary signals.

We also optionally separate sign/phase, but that comes later (see 3.4).


3.2 Normalization

We need unit ℓ2 norm for quantum amplitudes. Define:

    ||a||₂ = sqrt( Σ_k |a_k|² )

If ||a||₂ = 0 (degenerate pathological case), reject. Otherwise:

    â = a / ||a||₂

Now we assert Parseval-style normalization:
    Σ_k |â_k|² = 1

This â is what we actually load into a quantum state as amplitudes.


3.3 State Preparation Mapping

We map indices k = 0..N-1 to n-qubit computational basis states |k>:

    â_k ↦ amplitude of |k>

So the state is:
    |ψ> = Σ_{k=0}^{N-1} â_k |k>

Dimension N MUST be a power of two, N = 2^n, because we want to load
the amplitudes on exactly n qubits. For non-power-of-two truncations,
we pad with zeros to the next power of two.

Bit ordering convention:
- We use LITTLE-ENDIAN internally:
    integer index k = Σ_{j=0}^{n-1} (bit_j)*2^j
  where bit_0 is qubit 0 (LSB), bit_1 is qubit 1, etc.
- We write bitstrings in left-to-right "most significant bit first"
  when we print them in JSON counts, because that's how IBM / Qiskit
  typically display measurement results. We will document this mapping
  in metadata so there’s no ambiguity.


3.4 Phase / sign encoding and dual-rail (IQ / sign-split)

Amplitude can be complex. We support:
- Raw complex amplitude mode: â_k is complex.
- "ABS" magnitude-only mode: we discard phase, keep |â_k|.
- "SIGN-SPLIT" / IQ mode: we use two registers to capture sign or I/Q
  parts separately. For example:
    real part → main register
    sign bit or imag part → aux register

These alternate encodings show up when we want hardware that can't
faithfully load arbitrary complex phases, but we still want to retain
structure. In Unit 1, we define them but we don't force them yet.
Downstream units can call them explicitly.


3.5 Similarity metric between two fingerprints

Given two fingerprints |ψ_A>, |ψ_B>:

- Fidelity-style overlap:
      F(A,B) = |⟨ψ_A | ψ_B⟩|²
  This is invariant under a global phase of either state, range [0,1].

- Cosine similarity in coefficient space (for fast/atlas work):
      cosine(a,b) = Re(⟨â, b̂⟩) / (||â||₂ ||b̂||₂)
  where â,b̂ are normalized real-valued feature vectors (e.g. magnitudes).
  Used by later "Function Atlas" clustering.

In Unit 1, we lock the idea that fingerprints can be compared by fidelity,
and fidelity ∈ [0,1] is our canonical scalar similarity for "identity."


3.6 Entropy notation (preview; referenced by tests and certs)

Let p_Z be the Z-basis measurement distribution of |ψ>:
    p_Z(b) = |⟨b | ψ⟩|²
Then Shannon entropy in bits is:
    H_Z = - Σ_b p_Z(b) log₂ p_Z(b)

Let X basis be applying a global Hadamard H^{⊗n} before measuring in Z.
Then:
    p_X(b) = |⟨b | H^{⊗n} | ψ⟩|²
    H_X = - Σ_b p_X(b) log₂ p_X(b)

Maassen-Uffink entropic uncertainty bound:
    H_Z + H_X ≥ n
We'll validate that later — it's one of our sanity checks.


================================================================================
4. LABEL GRAMMAR & METADATA
================================================================================

We need a reproducible way to say "please build a vector from sin(x)'s Maclaurin
series, up to N=256 terms, in EGF mode" without hardcoding by hand every time.

We solve that with a structured label grammar.

4.1 Object Labels (examples)

- "Maclaurin[sin(x)]"
    → generate c_n for sin(x) around x=0 via Maclaurin.
      a_n = c_n in "terms" mode by default.

- "Maclaurin[sin(x)^2] egf"
    → Maclaurin expansion of sin(x)^2,
      then a_n = c_n / n! (EGF weighting).

- "QFT[cos(2*pi*5*x) + 0.1*sin(2*pi*11*x); N=256; a=0; b=1]"
    → sample the real function cos(2π·5·x)+0.1 sin(2π·11·x)
      over x in [0,1] with N=256 points.
      a_k = f(x_k).

- "periodic_phase_state[p=3,q=32]"
    → build a phase e^{2πi * p * n / q} across computational basis |n>,
      truncated/padded to the required N.

Later units will add:
- "BesselJ0[x0=...]" ,
- "Polylog[s=2,z=0.5]" ,
- etc.

4.2 Arguments / Modifiers

Tokens we standardize NOW:
- "egf"      → EGF weighting (divide by n!)
- "terms"    → plain series coefficients (default if omitted)
- "abs"      → discard phase, use |a_n|
- "iq"       → keep real & imag rails separately (later)
- "N=..."    → truncation length for series
- "nq=..."   → explicitly request number of qubits
               If N < 2^nq, we zero-pad.
               If N > 2^nq, it's an error (must choose bigger nq).

Locking these tokens now means tests can enforce them.


4.3 Metadata schema

Any time we generate a fingerprint vector and/or quantum state, we ALSO emit
a metadata JSON describing:

{
  "label": "Maclaurin[sin(x)] egf",
  "source": {
    "type": "maclaurin",
    "function": "sin(x)",
    "mode": "egf",                // "terms", "egf", "sample", "periodic_phase_state"
    "truncation_N": 256,
    "n_qubits": 8,
    "padding": "zero-pad-to-256",
    "amp_mode": "complex",        // "complex" | "abs" | "iq-split"
    "phase_mode": "keep-phase"
  },
  "conventions": {
    "endianness": "little-endian index<->qubit map",
    "bitstring_display": "msb-left in output counts",
    "qft_kernel_sign": "+",
    "fft_normalization": "unitary (1/sqrt(N))"
  },
  "norm_check": {
    "l2_norm_raw": 12.345,
    "l2_norm_normalized": 0.9999999998
  },
  "similarity_hint": {
    "atlas_family": "trig",
    "expected_neighbors": ["Maclaurin[cos(x)] egf"]
  },
  "timestamp_utc": "2025-10-29T04:00:00Z"
}

Acceptance rule:
ANY experiment that writes a .npy state OR hardware counts must also emit
metadata of this shape and store it in docs/results/ or Unit1/metadata/.


================================================================================
5. IMPLEMENTATION SURFACE (FILES / FUNCTIONS / TOOLS THIS UNIT RELIES ON)
================================================================================

Some of these already exist. This is the spec for what they are supposed to do.

5.1 series_encoding.py
- Responsibility:
  - Parse label strings like "Maclaurin[sin(x)] egf".
  - Generate finite vector a (np.ndarray complex length N).
  - Apply "terms" vs "egf".
  - Handle "QFT[...]" sampling labels.
  - Zero-pad to next power-of-two if needed.
  - Return both the raw vector and source metadata.

- Key functions you must expose in practice:
    generate_series_vector(label: str,
                           N: int|None,
                           n_qubits: int|None,
                           amp_mode: str="complex")
        -> (np.ndarray a, dict meta)

    normalize_vector(a: np.ndarray)
        -> (np.ndarray â, dict norm_info)

    build_state_metadata(label: str,
                         meta: dict,
                         norm_info: dict,
                         conventions: dict)
        -> dict full_metadata


5.2 sbrv_precision.py  (SBRV = stacked bit-range vector)
- Goal: store giant-dynamic-range data as stackable slices.
- In Unit 1 we just acknowledge it exists for precision control.
- Later units will lean on it.


5.3 sign_split_register.py
- Goal: support alt encodings like amp_mode="abs" or IQ rail splits.
- Mentioned here so we don't pretend phase-accurate load is always easy.


5.4 series_preserving.py
- Goal: algebra on fingerprints (LCU, Hadamard product, Cauchy/EGF conv).
- This is technically Unit 3 material, but Unit 1 references it philosophically:
  fingerprints aren't just static blobs, you can combine them predictably.


5.5 quantum_embedding.py
- Goal:
  - Given normalized â (length 2^n), either:
      (A) produce a QuantumCircuit that prepares |ψ> on n qubits
          (when feasible for that amplitude family),
      (B) or just treat â as the simulator ground truth statevector.
  - Provide reference structured states like periodic_phase_state(p,q,n_qubits).

- Key call shapes:
    build_state_circuit(normalized_vec, backend_constraints) -> QuantumCircuit
    save_statevector(normalized_vec, path)
    periodic_phase_state(p, q, n_qubits) -> np.ndarray


5.6 QTEGUI.py / QTEGUI.py.bak-neut
- This is your GUI "lab bench":
  - "Amplitude" tab: shows raw amplitudes â_k.
  - "Measure" tab: simulates Z-basis measurement / histograms.
  - "Entropy" tab: computes H_Z, H_X.
  - "Tomography" tab: reconstructs density matrix and fidelity.
- We reference it so it's clear that the math here = what's shown in GUI.
- CLI shouldn't *depend* on GUI runtime, but results should agree.


5.7 tools/run_on_ibm_torino.py
- Goal:
  - Send a shallow circuit (like uniform superposition or periodic_phase_state)
    to IBM hardware (e.g. backend "ibm_torino"),
  - collect measurement counts,
  - emit docs/results/<name>_counts.json with metadata.
- Must support flags:
    --backend torino
    --shots 4096
    --basis Z (or X = apply global H before measure)
    --load-qpy tmp/<circuit>.qpy
    --out docs/results/<file>.json


================================================================================
6. CLI WORKFLOWS / EXPERIMENT RECIPES
================================================================================

We'll define 3 baseline Experiments for Unit 1: U1-A, U1-B, U1-C.

----------------------------------------
6.1 Experiment U1-A: Generate a fingerprint for π
----------------------------------------

Goal:
- Build a normalized amplitude vector for π (or some canonical constant),
  emit metadata JSON, and save both locally.

Example command flow (simulator):

    ./qte_cli.py \
      --nq 8 \
      --label "Maclaurin[pi_constant]" \
      --mode terms \
      --dump states/pi_terms.npy \
      --meta Unit1/metadata/pi_terms_meta.json

Meaning:
- generate_series_vector("Maclaurin[pi_constant]", mode="terms", N auto or N=256)
- normalize_vector(...)
- write states/pi_terms.npy  (â)
- write Unit1/metadata/pi_terms_meta.json

Acceptance for U1-A:
- The produced vector has ℓ2 norm ~ 1.0 within 1e-12.
- The metadata file exists, includes n_qubits and truncation length, and
  includes endianness + qft_kernel_sign + fft_normalization.


----------------------------------------
6.2 Experiment U1-B: Compare two fingerprints (similarity / fidelity)
----------------------------------------

Goal:
- Take two normalized fingerprints (e.g. sin(x) and cos(x)), compute fidelity.

Example command:

    ./qte_cli_ext.py similarity \
      --state-a states/sin_egf.npy \
      --state-b states/cos_egf.npy \
      --metric fidelity \
      --out docs/results/sin_cos_similarity.json

Expected output:

{
  "metric": "fidelity",
  "value": 0.7421,
  "state_a": "states/sin_egf.npy",
  "state_b": "states/cos_egf.npy"
}

Acceptance for U1-B:
- "value" ∈ [0,1].
- "metric": "fidelity" or something equivalent.
- Deterministic for same inputs.
- This becomes input to later "Function Atlas" clustering in Unit 7.


----------------------------------------
6.3 Experiment U1-C: Hardware sanity shot (IBM backend)
----------------------------------------

Goal:
- Prove end-to-end pipeline: build a shallow state, run on IBM hardware,
  capture counts + entropy + metadata, store it.

We'll start with uniform superposition |ψ> = H^{⊗n}|0...0>, n=4.
This is simple and robust.

Step 1. Build the "uniform superposition" circuit locally:

    ./qte_cli_ext.py make \
      --nq 4 \
      --uniform \
      --out-circ tmp/uniform4.qpy \
      --meta Unit1/metadata/uniform4_meta.json

This:
- builds a circuit H on each of 4 qubits,
- serializes that circuit to tmp/uniform4.qpy,
- emits metadata documenting n_qubits, bit ordering, etc.

Step 2. Send to hardware:

    python tools/run_on_ibm_torino.py \
      --backend torino \
      --shots 4096 \
      --basis Z \
      --load-qpy tmp/uniform4.qpy \
      --out Unit1/hardware/uniform4_counts.json

The runner script:
- executes/submits job,
- collects raw counts,
- normalizes to probabilities,
- estimates entropy H_Z,
- appends conventions (endianness, etc.).

Expected output shape (more in Section 7).

Acceptance for U1-C:
- For n=4, we expect ~uniform distribution over 16 bitstrings.
- Shannon entropy H_Z in hardware output should be ≥ 3.0 bits
  (4 bits is perfect, 0 is catastrophic).
- The metadata in uniform4_counts.json repeats our conventions:
  endianness, qft_kernel_sign="+", etc.

This experiment proves "label → circuit → hardware → JSON" is now a pipeline,
not just theory.


================================================================================
7. JSON ARTIFACT SCHEMAS
================================================================================

Everything that comes out of these pipelines MUST serialize in predictable ways,
because later units parse them.

7.1 State generation metadata (local sim)

File: Unit1/metadata/pi_terms_meta.json
Shape:
{
  "label": "Maclaurin[pi_constant] terms",
  "n_qubits": 8,
  "N_trunc": 256,
  "amp_mode": "complex",         // "complex" | "abs" | "iq-split"
  "phase_mode": "keep-phase",
  "endianness": "little-endian index<->qubit map",
  "bitstring_display": "msb-left in JSON counts",
  "qft_kernel_sign": "+",
  "fft_normalization": "unitary (1/sqrt(N))",
  "norm_info": {
      "l2_norm_raw": 12.345,
      "l2_norm_after": 0.9999999998
  },
  "timestamp_utc": "2025-10-29T04:00:00Z"
}

Required keys:
- label
- n_qubits
- N_trunc
- amp_mode
- norm_info.l2_norm_after ≈ 1.0
- endianness / bitstring_display / qft_kernel_sign / fft_normalization
- timestamp_utc


7.2 Similarity result

File: docs/results/sin_cos_similarity.json
Shape:
{
  "metric": "fidelity",
  "value": 0.7421,
  "state_a": "states/sin_egf.npy",
  "state_b": "states/cos_egf.npy"
}

Required:
- metric string
- numeric "value" in [0,1]
- references to both state paths


7.3 Hardware counts + metadata

File: Unit1/hardware/uniform4_counts.json
Shape:
{
  "backend": "ibm_torino",
  "shots": 4096,
  "basis": "Z",
  "n_qubits": 4,
  "counts": {
      "0000": 263,
      "0001": 255,
      "0010": 260,
      "0011": 254,
      "...":  "...",
      "1111": 244
  },
  "probabilities": {
      "0000": 0.0642,
      "0001": 0.0622,
      "0010": 0.0635,
      "0011": 0.0620,
      "...":  "...",
      "1111": 0.0596
  },
  "entropy_bits": {
      "H_Z": 3.78,
      "H_min": 2.83
  },
  "endianness": "little-endian internal index to qubits",
  "bitstring_display": "msb-left in this JSON",
  "qft_kernel_sign": "+",
  "fft_normalization": "unitary (1/sqrt(N))",
  "timestamp_utc": "2025-10-29T04:15:00Z",
  "job_id": "ibm-job-abc123"
}

Required:
- backend, shots, n_qubits, basis
- counts{} and probabilities{}
- entropy_bits{} with at least H_Z
- conventions (endianness, qft_kernel_sign, etc.)
- timestamp_utc

Acceptance:
- entropy_bits.H_Z present
- n_qubits matches circuit
- counts keys match measured bitstrings


================================================================================
8. TEST PLAN & ACCEPTANCE CRITERIA
================================================================================

These pytest-style tests enforce the contract of Unit 1.  
They will live in /Unit1/tests/ (and pytest can discover them there).

8.1 tests/test_normalization.py

Goal:
- Ensures that any vector our pipeline normalizes actually has ||â||₂ ≈ 1,
  and zero vectors are rejected.

Pseudo-outline:

    def test_normalize_vector_unit_norm():
        a, meta = generate_series_vector("Maclaurin[sin(x)] egf",
                                         N=256, n_qubits=8)
        ahat, norm_info = normalize_vector(a)
        assert abs(np.linalg.norm(ahat) - 1.0) < 1e-9
        assert np.isfinite(ahat).all()

    def test_zero_vector_rejected():
        a = np.zeros(16, dtype=complex)
        with pytest.raises(ValueError):
            normalize_vector(a)

Acceptance:
- pass => we can trust amplitudes we feed into quantum circuits.


8.2 tests/test_metadata_schema.py

Goal:
- After building a state + metadata, ensure required keys are present.

Pseudo-outline:

    def test_metadata_has_required_fields():
        with open("Unit1/metadata/pi_terms_meta.json") as f:
            obj = json.load(f)

        required_top = ["label","n_qubits","N_trunc","amp_mode"]
        for r in required_top:
            assert r in obj

        assert "norm_info" in obj
        assert "endianness" in obj
        assert "qft_kernel_sign" in obj
        assert "fft_normalization" in obj

Acceptance:
- We never silently "forget" to log conventions.


8.3 tests/test_similarity_fidelity_range.py

Goal:
- Fidelity stays in [0,1]; identical states get ~1.

Pseudo-outline:

    def test_fidelity_range_and_identity():
        ahat = load("states/cos_egf.npy")
        bhat = load("states/cos_egf.npy")
        f = fidelity(ahat,bhat)
        assert 0.0 <= f <= 1.0
        assert f > 0.999999

    def test_fidelity_not_trivial_for_diff_objects():
        ahat = load("states/sin_egf.npy")
        bhat = load("states/cos_egf.npy")
        f = fidelity(ahat,bhat)
        assert 0.0 <= f <= 1.0
        assert f < 0.999999

Acceptance:
- fidelity is implemented correctly and is discriminative.


8.4 tests/test_hardware_entropy_sanity.py  (optional but strongly encouraged)

Goal:
- If we ran the uniform superposition circuit on hardware (U1-C),
  confirm the entropy wasn't catastrophically low.

Pseudo-outline:

    def test_uniform_superposition_entropy_not_low():
        with open("Unit1/hardware/uniform4_counts.json") as f:
            obj = json.load(f)

        H_Z = obj["entropy_bits"]["H_Z"]
        n   = obj["n_qubits"]
        assert n == 4
        assert H_Z >= 3.0  # out of ideal 4 bits

Acceptance:
- Hardware plumbing not totally cooked.


================================================================================
9. REPO LAYOUT (POST-UNIT-1)
================================================================================

We are standardizing where stuff goes so later units can assume it.

After Unit 1 is committed and pushed, we expect this minimal structure:

/Users/erik/Documents/QTExpanded/program5_branch_series/
    Unit1/
        README.md                       <-- THIS FILE
        examples/
            pi_terms.npy
            sin_egf.npy
            cos_egf.npy
        metadata/
            pi_terms_meta.json
            sin_egf_meta.json
            cos_egf_meta.json
            uniform4_meta.json
        hardware/
            uniform4_counts.json
        tests/
            test_normalization.py
            test_metadata_schema.py
            test_similarity_fidelity_range.py
            test_hardware_entropy_sanity.py
    series_encoding.py
    sbrv_precision.py
    sign_split_register.py
    series_preserving.py
    quantum_embedding.py
    tools/
        run_on_ibm_torino.py
        function_atlas.py             (used heavily later, declared now)
        qft_module.py                 (QFT circuits, used in later units)
    qte_cli.py
    qte_cli_ext.py
    docs/
        results/
            (JSON run artifacts like sin_cos_similarity.json)
    tmp/
        (transient .qpy, .npy scratch)
    .gitignore
    .git (repo initialized, remote origin already set, branch = main)

NOTES:
- tests/ under Unit1/ must be pytest-discoverable
  (pytest can be pointed at the repo root or Unit1/tests).
- docs/results/ is global, downstream units will reuse it.
- hardware/ keeps the on-device counts snapshots tied to this unit.
- metadata/ keeps provenance blobs tied to generated states in this unit.

The point: later units assume this discipline already exists.


================================================================================
10. ACCEPTANCE CHECKLIST FOR UNIT 1
================================================================================

You consider Unit 1 "done / frozen" when ALL of this is true:

[REQ-1] You can take a label like "Maclaurin[sin(x)] egf" and via CLI produce:
        - a normalized statevector .npy (length 2^n),
        - a metadata JSON in Unit1/metadata/,
        - with ||â||₂ ≈ 1 and no NaNs.

[REQ-2] You can run the similarity CLI comparing two .npy states and get a JSON
        with fidelity ∈ [0,1].

[REQ-3] You can build a trivial low-depth state (uniform superposition H^{⊗4}),
        send it to IBM hardware via tools/run_on_ibm_torino.py,
        and get back a counts+entropy JSON in Unit1/hardware/
        with H_Z ≥ 3.0 bits.

[REQ-4] You have tests in Unit1/tests/ that:
        - assert normalization,
        - assert metadata schema keys,
        - assert fidelity correctness,
        - assert hardware entropy sanity (if hardware run exists).

[REQ-5] You have this README.md, sample metadata, placeholder tests, etc.
        committed under:
        /Users/erik/Documents/QTExpanded/program5_branch_series/Unit1/

From this point forward:
- every later unit (2,3,4,…) is allowed to assume the above is available.
- we do NOT re-argue endianness, normalization, qft_kernel_sign, etc.
  Those are locked here.


================================================================================
11. HOW TO UPDATE + PUSH THIS UNIT IN PRACTICE
================================================================================

The intended workflow is:
1. Edit /Users/erik/Documents/QTExpanded/program5_branch_series/Unit1/README.md
   directly in VS Code (this file).
2. Generate states and metadata using qte_cli, drop them in Unit1/examples/
   and Unit1/metadata/.
3. Run hardware, drop the counts JSON in Unit1/hardware/.
4. Run pytest on Unit1/tests/.
5. git add + git commit + git push.

To make your life easier, we also prepared an automated scaffold step
(see the zsh script that created this file). That scaffold:
- mkdirs the needed directories,
- writes README.md,
- writes placeholder tests and placeholder metadata/hardware JSONs,
- stages/commits/pushes to origin main.

After scaffold succeeds once, you will be editing the real files directly.


# END OF UNIT 1 README
