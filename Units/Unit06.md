# Unit 06 — Quentroy Entropy Certification / Attestation Layer

## UNIT NAME AND SCOPE

This unit defines how we turn raw shot data from execution (simulated or hardware) into a Quentroy certificate ("QuentroyCert"), and it locks what that certificate MUST contain, how it is versioned, and how it is tied back to the exact ψ and loader layout that were claimed.

We are not "doing statistics." We are creating an auditable object.

This unit answers:
- We ran something (or simulated it). How do we prove what state that was, how uncertain it looked, and whether that matches the thing we SAID we loaded?

We will NOT rename your terms:
- NVE      = Normalized Vector Embedding (Unit 01)
- NVQA     = Normalized Vector Quantum Analysis (global field name)
- Quentroy Entropy = the entropy / flatness / anti-structure witness we attach
- LoaderSpec  = semantic rail layout (Unit 02)
- PrepSpec    = concrete init recipe (Unit 03)
- ExecSpec    = requested hardware execution (Unit 04)
- RunReceipt  = what the backend actually said happened (Unit 04)
- QuentroyCert = the signed/attestable summary of uncertainty & match (THIS UNIT)

We lock that the QuentroyCert object is versioned with `"quentroy_version": "Unit06"`. That literal string MUST appear in output and in nvqa_cli.py so that future tests can grep for it and so a verifier can instantly reject older or spoofed formats.

This unit does NOT introduce any new naming you didn't authorize. We just structure Quentroy so later crypto units (11, 25) can authenticate payloads.

## POSITION IN THE PIPELINE

By Unit 04 we've done:
1. Build ψ from an ObjectSpec via NVE (Unit 01).
2. Generate LoaderSpec so we know which amplitude chunk maps to which register / rail (Unit 02).
3. Generate PrepSpec and (for sim) produce counts (Unit 03).
4. Generate ExecSpec, actually run hardware, then capture RunReceipt with shot counts, backend ID, timestamps, etc. (Unit 04).

Unit 06 consumes either:
- (PrepSpec, sim_counts) from nve-run-sim (Unit 03 path), OR
- (ExecSpec, RunReceipt) from nve-run-exec (Unit 04 path),

and emits:
- QuentroyCert, a JSON object which becomes the audit artifact and security anchor for later tamper checks.

In English: Unit 06 is where "I ran this" turns into "Here's a cert that proves how it behaved statistically and what that maps back to."

This QuentroyCert is the THING downstream. Everything in Units 11 / 25 / 27 points back to this.

## QUENTROY ENTROPY: WHAT WE'RE MEASURING

We are *not* calling this "Shannon entropy" or "some distribution stats". We are calling it Quentroy Entropy, full stop, because that is what you said it is called.

Internally, Quentroy Entropy bundles:
- H_Z: the entropy of the observed Z-basis measurement distribution (shot histogram of computational basis bitstrings under the frozen little-endian basis convention).
- H_QFT or H_X: entropy of a conjugate-basis measurement distribution, typically after applying a Fourier-like or Hadamard-like transform that we promised to respect sign `+` in the exponent for. (We insist on qft_kernel_sign="+" everywhere.)
- KL_to_uniform: how "flat" the distribution looks vs uniform. This kills structured cheating where someone gives you a fake "random-looking" state that is actually super peaky.
- min_entropy_estimate: worst-case single-outcome surprise (a lower bound on unpredictability).
- bias / flatness diagnostics that tell us if rails are lopsided or if certain qubits are frozen.

For Unit 06 we don't nail down exact math for all components, but we DO hard-lock the field names and the required presence of H_Z. We also lock that metadata like endianness and qft_kernel_sign flow into QuentroyCert so you can prove the QuentroyCert matches the exact conventions we said we were using upstream.

If anybody shows up later with a QuentroyCert that doesn't carry endianness="little" and qft_kernel_sign="+", we reject it as nonconforming.

## WHAT COUNTS AS INPUT

Unit 06 takes *measurement evidence*. That evidence can come from either:
- SIM path (nve-run-sim from Unit 03): where we have
  - PrepSpec (an object that says how ψ would be loaded),
  - sim_counts (fake but structurally correct shot counts).
- EXEC path (nve-run-exec from Unit 04): where we have
  - ExecSpec (the requested hardware run, including loader_version, exec_version, backend, shots),
  - RunReceipt (actual device-reported counts_Z, maybe counts_aux, timing, etc.).

Unit 06 doesn't generate ψ. ψ was frozen in Unit 01.
Unit 06 doesn't generate LoaderSpec. That's Unit 02.
Unit 06 doesn't deal with routing or hardware coupling maps or that garbage. That's handled before.
Unit 06 just notarizes: "You said you ran THIS. Here is what actually came out. Here's Quentroy on it."

## QUENTROY CERTIFICATE STRUCTURE (QuentroyCert)

We define QuentroyCert as a JSON object that MUST contain at least the following keys. If any required key is missing, the cert is invalid.

Required top-level keys:
- "quentroy_version": "Unit06"
  - THIS IS FIXED. If someone hands you "Unit07" or "v1" or whatever nonsense, reject.
- "source_kind": "sim" or "exec"
  - "sim" means derived from nve-run-sim (Unit 03).
  - "exec" means derived from nve-run-exec (Unit 04).
- "endianness": "little"
  - required or reject.
- "qft_kernel_sign": "+"
  - required or reject.
- "loader_version": "Unit02"
  - required or reject. This binds the QuentroyCert back to the LoaderSpec semantics (split rails, IQ rails, etc.).
- "prep_spec_fingerprint": "<digest or stable fingerprint of PrepSpec or ExecSpec>"
  - this is what ties QuentroyCert to the exact loading configuration and not some random other run.
- "object_spec_fingerprint": "<digest of the ObjectSpec that created ψ in Unit 01>"
  - this lets you tell which conceptual object this cert is about.
- "shots_total": <int>
  - total number of samples observed.
- "H_Z_bits": <float>
  - Quentroy Entropy component for Z-basis histogram.
- "H_QFT_bits": <float>  (or "H_X_bits" depending which conjugate basis we use)
  - Quentroy Entropy component for conjugate-basis histogram.
  - We are allowed to emit null/None for now IF we don't have conjugate counts yet,
    but the field MUST exist.
- "flatness_KL_uniform": <float>
  - KL divergence of observed distribution from uniform.
- "min_entropy_bits": <float>
  - self-explanatory: the min-entropy estimate from highest-probability outcome.
- "counts_digest": "<digest of actual counts table>"
  - We do NOT include the entire raw histogram in the core cert if that's huge.
    We just hash/digest it here. Raw counts live in RunReceipt / sim_result.json.
    This makes QuentroyCert small and portable.

Optional-but-encouraged:
- "timestamp_run_utc": "<ISO8601 or epoch string>"
  - from RunReceipt if available.
- "backend_id": "<backend name>"
  - from RunReceipt if source_kind == "exec".
- "exec_version": "Unit04"
  - only for "exec". Locks to Unit 04 ExecSpec contract.
- "rail_layout": [ ... objects ... ]
  - same shape as LoaderSpec["rail_layout"], so you can audit rail packing.
  - we *highly* recommend copying it in so cert review doesn't have to fish
    across 3 JSON files to know which slice of ψ meant what.

The point is: QuentroyCert is what an auditor / verifier / downstream crypto unit actually holds up and says "prove that matches what you claimed." So it MUST embed enough structure to link to ψ, LoaderSpec, and the measured distribution you claim came from ψ.

## CLI SURFACE (THIS UNIT LOCKS IT)

We are extending nvqa_cli.py with one more subcommand that downstream tests are now going to require textually present:

Subcommand:
    nve-quentroy-cert   (belongs to Unit 06)

Flags:
    --source-kind {sim,exec}
    --in-spec   <prep_spec.json OR exec_spec.json>
    --in-counts <sim_result.json OR run_receipt.json>
    --out-cert  <quentroy_cert.json>

Behavior contract:
    - Read PrepSpec+sim_counts (if --source-kind sim) or ExecSpec+RunReceipt (if --source-kind exec).
    - Compute Quentroy Entropy metrics, at least H_Z_bits.
    - Assemble QuentroyCert JSON with all required top-level keys listed above.
    - Force:
        "quentroy_version": "Unit06"
        "endianness": "little"
        "qft_kernel_sign": "+"
        "loader_version": "Unit02"
      into the output. If any of those are missing or different, that's a FAIL.
    - Write QuentroyCert to --out-cert.

We are not required (in this unit) to define how to compute KL, min-entropy, etc. numerically. We ARE required to output keys with numeric placeholders or 0.0 or null if not available. The existence and naming of these keys is the contract.

## TEST REQUIREMENTS LOCKED BY THIS UNIT

New tests (Unit 06) will enforce the following:

1. test_unit06_contract_cli.py
   - opens nvqa_cli.py
   - requires it to literally contain:
        "nve-quentroy-cert"
        "--out-cert"
        "quentroy_version=\"Unit06\""
        "loader_version=\"Unit02\""
        "endianness=\"little\""
        "qft_kernel_sign=\"+\""
   - This guarantees the CLI surface and invariants didn't quietly mutate.

2. test_unit06_cert_shape.py
   - constructs a fake QuentroyCert dict inline (not by running anything yet)
   - asserts the dict has all required top-level keys exactly as listed.
   - asserts quentroy_version == "Unit06"
   - asserts loader_version == "Unit02"
   - asserts endianness == "little"
   - asserts qft_kernel_sign == "+"
   - asserts source_kind in {"sim","exec"}
   - asserts we exposed H_Z_bits, flatness_KL_uniform, min_entropy_bits, etc.

If any of those fail in the future, you broke Unit 06.

## WHY THIS UNIT EXISTS

- Without QuentroyCert, anyone can claim "I ran ψ" and show you any random histogram.
  You'd have zero leverage to push back.

- With QuentroyCert:
  * We bind shot data to ObjectSpec (via object_spec_fingerprint).
  * We bind it to LoaderSpec (via loader_version="Unit02" and rail_layout).
  * We bind it to ExecSpec/PrepSpec fingerprints.
  * We show statistical structure (Quentroy) that SHOULD match ψ if ψ was correctly loaded and run.
    If later you get a hardware run that produces a cert way off from baseline,
    you know it's bogus or tampered.

- QuentroyCert is the input to crypto-tamper-proofing later (Units 11, 25).
  Without this unit stabilized, those units can't claim security.

End of Unit 06 spec.
