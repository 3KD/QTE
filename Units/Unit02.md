UNIT 02 — LOADER SPEC AND SEMANTIC RAIL ALIGNMENT
=================================================

SCOPE
-----

Unit 02 defines how a normalized ψ from Unit 01 (Normalized Vector Embedding / NVE) is assigned a physical / logical load layout so later hardware and simulators know exactly what each amplitude means and where it lives.

In plain terms:
- Unit 01 gives us ψ plus metadata (phase_mode, rail_mode, etc).
- Unit 02 turns that ψ into a LoaderSpec object that freezes:
  - rail ordering,
  - subregister mapping,
  - bit significance (endianness),
  - QFT kernel sign convention,
  - and a deterministic semantic hash.

After this unit:
- There is NO ambiguity about “which amplitude is which rail / qubit / slot.”
- Anyone downstream (Unit 03 simulation, Unit 04 execution on backend, Unit 05 Quentroy Entropy attestation) must consume LoaderSpec, not improvise.

We do not say “canonical” and we do not let anyone substitute their own layout silently. LoaderSpec is the reference layout. If LoaderSpec changes, it is a version bump and old LoaderSpec is considered incompatible.


MOTIVATION
----------

Why we need this:

1. Rail mode from Unit 01 (iq_split, sign_split, etc.) explodes a logical object into rails. If we don't pin which slice of ψ corresponds to which semantic component, hardware prep in Unit 04 and entropy witness / Quentroy Entropy in Unit 05 are meaningless.

2. We must freeze index meaning:
   - Computational basis ordering is LITTLE-ENDIAN. That means basis index k maps to bitstring where the least significant bit is the physically “rightmost drawn” qubit.
   - We commit that here. Anyone who flips that later is wrong.
   - This matters for attribution of counts, parsing QFT basis transforms, and proving identity of a prepared state.

3. We must freeze transform sign:
   - qft_kernel_sign = "+"
   - That means our QFT-like kernel is exp(+2π i m k / N) / √N.
   - Classical FFT libraries often use a minus sign. We are NOT using the minus sign as default. If you want to compare, conjugate or take |·|² manually. That’s on you.
   - This sign choice affects how we interpret entropy in Fourier-like bases and must match across all units.

4. We must emit a deterministic loader spec file that future tooling can diff byte-for-byte.
   - If two LoaderSpecs differ for “the same ψ input + same params,” everything downstream (attestation, similarity atlas, crypto watermark embedding, etc.) loses the ability to trust that a given ψ is THE ψ.


REQUIRED ARTIFACT: LoaderSpec
-----------------------------

LoaderSpec is a dict/JSON with ALL of these fields, no exceptions:

- "object_spec": dict
    The full structured ObjectSpec that produced ψ in Unit 01. Must include:
    - construction recipe
    - truncation N
    - weighting_mode
    - phase_mode
    - rail_mode
    - endianness
    - qft_kernel_sign="+"
    This cannot be just a human string. It must be a structured dump of whatever Unit 01's package_nve() used.

- "rail_layout": list
    Deterministic, ordered description of how ψ is mapped onto logical rails / subregisters / qubit slots.
    Each entry MUST include:
      {
        "index": <int>,          # position in ψ
        "rail_tag": <str>,       # e.g. "I", "Q", "POS", "NEG", "MAIN", etc.
        "subregister": <str>,    # e.g. "R0", "R1", "Z0", etc.
        "bit_index_le": <int>    # the little-endian bit index that would host this slot in computation basis labeling
      }
    "rail_layout" MUST be length == len(ψ). No gaps. No padding that isn't represented. No silent compression.

- "endianness": "little"
    Always literally "little". This MUST match Unit 01 and MUST be explicit here again.

- "qft_kernel_sign": "+"
    Always literally "+". This MUST match Unit 01 and MUST be explicit here again.

- "loader_version": "Unit02"
    Literal string "Unit02".
    This is how later units verify that whoever produced this LoaderSpec was actually following Unit 02 rules and not improvising.

- "semantic_hash": "<hex string>"
    A deterministic digest computed from everything in the LoaderSpec EXCEPT the semantic_hash field itself.
    Rule:
      semantic_hash = SHA256(
         json.dumps(spec_without_semantic_hash, sort_keys=True, separators=(',',':')).encode('utf-8')
      ).hexdigest()
    You MUST sort keys in the JSON before hashing, and you MUST use compact separators (",", ":") so it's reproducible cross-platform.

- "length": <int>
    Length of ψ (post-rail expansion). Same as len(rail_layout).

If ANY of these keys is missing, LoaderSpec is invalid.
If "endianness" != "little" or "qft_kernel_sign" != "+", LoaderSpec is invalid.
If "loader_version" != "Unit02", LoaderSpec is invalid.
If length != len(rail_layout), LoaderSpec is invalid.
If semantic_hash does not match recompute(rule above), LoaderSpec is invalid.


FUNCTION CONTRACTS (loader_layout.py)
-------------------------------------

Unit 02 introduces loader_layout.py. That file MUST exist and MUST define:

1. build_loader_spec(object_spec: dict, psi, nve_metadata: dict) -> dict
   - object_spec: the exact structured ObjectSpec from Unit 01 (NOT a lossy human summary).
   - psi: the normalized ψ vector from Unit 01 (NumPy array or list of floats/complex that we just got).
   - nve_metadata: the metadata dict returned alongside ψ from Unit 01 package_nve().

   What it MUST do:
   - Validate nve_metadata["endianness"] == "little".
   - Validate nve_metadata["qft_kernel_sign"] == "+".
   - Get rail_mode from nve_metadata (like "iq_split", "sign_split", "none").
   - Construct rail_layout deterministically. Deterministic here means:
       same object_spec + same ψ always yields byte-identical rail_layout ordering.
     How you label "subregister" and "rail_tag" MUST be fixed by rail_mode rules:
       - iq_split example:
         first half of ψ => I rail values, tag rail_tag="I", subregister="I"
         second half of ψ => Q rail values, tag rail_tag="Q", subregister="Q"
       - sign_split example:
         first half => POS rail, rail_tag="POS", subregister="POS"
         second half => NEG rail, rail_tag="NEG", subregister="NEG"
       - none:
         single rail, rail_tag="MAIN", subregister="MAIN"
     For each index k in ψ, assign:
       index = k
       bit_index_le = k  (for now 1:1; we reserve more complicated mapping for Unit 04 routing, but here it's identity)
       Note: bit_index_le MUST correspond to little-endian interpretation of basis states. No reversal.

   - Build spec dict with all required keys except semantic_hash.
   - Compute semantic_hash per rule.
   - Insert semantic_hash.
   - Return resulting dict.

   build_loader_spec MUST raise (not silently continue) if:
   - ψ is empty,
   - len(ψ) != claimed "length",
   - rail_mode is unknown,
   - rail_mode implies 2N structure but ψ length is not divisible correctly,
   - nve_metadata disagrees with endianness/little or qft_kernel_sign/+.

2. loader_spec_to_json(spec: dict, path: str) -> None
   - Recompute semantic_hash using the rule above and assert it matches spec["semantic_hash"].
   - Write the JSON to disk at `path`, using:
       json.dumps(spec, sort_keys=True, separators=(',',':'))
     EXACTLY those separators. EXACTLY sort_keys=True.
   - File must be UTF-8, no BOM.
   - If semantic_hash mismatch, raise and refuse to write.

   Why:
   - deterministic serialization. If two machines build the same LoaderSpec, `diff` on the resulting .json must say identical.

3. validate_loader_spec(spec: dict) -> None
   - Assert required keys exist.
   - Assert:
       spec["endianness"] == "little"
       spec["qft_kernel_sign"] == "+"
       spec["loader_version"] == "Unit02"
   - Assert:
       isinstance(spec["rail_layout"], list)
       len(spec["rail_layout"]) == spec["length"] == len({entry["index"] for entry in rail_layout})
         i.e. complete coverage, no missing slots, no duplicates.
   - Recompute semantic_hash and assert exact match.

   On ANY failure: raise. DO NOT "fix" or "autocorrect" or "guess". This is security critical.

These functions MUST be pure and deterministic. No RNG. No clock time. No host-dependent ordering.
If environment differences change spec output bytes, that's a violation of Unit 02.


CLI EXTENSION (nvqa_cli.py)
---------------------------

nvqa_cli.py already exists (from Unit 01). It MUST, by the end of Unit 02, grow a subcommand:

Subcommand name:
    nve-loader-spec

Flags (all required unless noted):
    --object "<ObjectSpec>"
    --weighting <weighting_mode>
    --phase-mode <phase_mode>
    --rail-mode <rail_mode>
    --N <int>
    --out-spec <path/to/spec.json>

Behavior contract:
1. Parse args into an ObjectSpec dict. ObjectSpec dict MUST include:
   {
     "recipe": "...",
     "weighting_mode": "...",
     "phase_mode": "...",
     "rail_mode": "...",
     "N": <int>,
     "endianness": "little",
     "qft_kernel_sign": "+"
   }
   The CLI is not allowed to leave those implicit.

2. Call Unit 01 pipeline (package_nve) to get:
   - psi (normalized, ||psi||₂ = 1 within 1e-12, no NaN/Inf, nonzero),
   - nve_metadata (must include endianness="little", qft_kernel_sign="+", rail_mode, etc.).

3. Call loader_layout.build_loader_spec(object_spec, psi, nve_metadata).

4. Call loader_layout.loader_spec_to_json(spec, out_path).

5. Exit 0 only if:
   - spec["loader_version"] == "Unit02"
   - spec["endianness"] == "little"
   - spec["qft_kernel_sign"] == "+"
   - spec["length"] == len(spec["rail_layout"])
   - semantic_hash validated and stable

If any of those fails, exit nonzero and print an error. DO NOT silently "fix" rails; DO NOT silently renumber.

The CLI string "nve-loader-spec" MUST literally appear in nvqa_cli.py source. The string "loader_version=\"Unit02\"" MUST literally appear too. The tests below check this.


WHY UNIT 02 IS LIFE OR DEATH FOR LATER UNITS
--------------------------------------------

- Unit 03 (simulation / PrepSpec): assumes LoaderSpec exists and is valid and TRUSTED. Unit 03 produces simulated shot counts based on ψ loaded according to LoaderSpec.

- Unit 04 (on-hardware execution / ExecSpec): assumes LoaderSpec is the truth when actually allocating rails / qubits. If LoaderSpec lies or drifts, the backend run is unauditable.

- Unit 05 (Quentroy Entropy certification): computes Quentroy Entropy for a run and binds it to the LoaderSpec + ψ identity. If LoaderSpec shifts rails, Quentroy certificates become meaningless, and tamper-proofing dies.

- Payload watermarking later (attestation / crypto units): expects LoaderSpec to be versioned and reproducible so we can say "this prepared state matches THIS ψ, not some edited ψ'".

- Atlas / similarity geometry units (later ones): depend on ψ being reproducible (Unit 01) AND mapped consistently to subspaces (Unit 02). If either drifts, function atlas is garbage.

Basically: Unit 01 said "this is ψ". Unit 02 says "this is how ψ sits in memory / rails / qubits / subregisters EVERY TIME". If either moves, the rest of the stack cannot prove identity, cannot detect tampering, cannot certify entropy, and cannot compare states between runs.


TEST CONTRACTS (THESE TESTS ARE REAL ENFORCERS)
-----------------------------------------------

These tests run under pytest on developer machines and in pre-push. They are designed to fail LOUD if anyone weakens guarantees.

Test file: tests/test_unit02_contract_cli.py

What it enforces:
- nvqa_cli.py MUST contain:
  - the literal string "nve-loader-spec"
  - the literal flag string "--out-spec"
  - the literal string "loader_version=\"Unit02\""
- This proves that the CLI surface is in place and that loader_version lock is acknowledged in code.

Test file: tests/test_unit02_doc_contract.py

What it enforces:
- Units/Unit02.md MUST mention all of these phrases:
  - "LoaderSpec"
  - "rail_layout"
  - "endianness\": \"little\""  (note: the exact literal with quotes appears below)
  - "qft_kernel_sign\": \"+\""
  - "loader_version\": \"Unit02\""
  - "build_loader_spec"
  - "loader_spec_to_json"
  - "validate_loader_spec"
  - "deterministic"
  - "same input → identical JSON"
  - "len(rail_layout)"
  - "semantic_hash"
- This prevents silent watering-down of the spec. If someone edits Unit02.md and rips out requirements, tests break immediately.

NOTE: We purposely test for literal text matches, because that catches anyone trying to "reinterpret" endianness or remove deterministic guarantees without us noticing.


SECURITY / ADVERSARY MODEL REITERATION
--------------------------------------

Every future proof-of-integrity and Quentroy Entropy certificate assumes:
- ψ generation (Unit 01) was deterministic and recorded.
- LoaderSpec (Unit 02) captured rail layout, endianness, QFT sign, and subregister mapping deterministically.
- semantic_hash seals that map so that if ANY of it changes, the hash changes.

We assume an adversary:
- Can supply any ψ' they want.
- Can lie about what ψ' supposedly encodes.
- Can lie about rails / subregister semantics.

We defend by:
1. Regenerating ψ ourselves from ObjectSpec using Unit 01 rules.
2. Rebuilding LoaderSpec using Unit 02 rules.
3. Checking the resulting semantic_hash and LoaderSpec JSON byte-for-byte against what they claimed.
4. Rejecting mismatches, full stop.

No "close enough".
No "float rounding".
No "structurally similar".
Exact match or it's not trusted.

If that sounds rigid: good. That rigidity is the point. It's how we get certifiable state identity with zero "just trust me" handwaving.



## TEST CONTRACT (DO NOT CHANGE)

Relevant tests:
- tests/test_unit02_contract_cli.py
- tests/test_unit02_doc_contract.py

Required CLI surface in nvqa_cli.py:
- the presence of subcommand token `nve-loader-spec`
  Flags:
    --object
    --weighting
    --phase-mode
    --rail-mode
    --N
    --out-spec
  Behavior:
    1. call NVE (Unit01) to get ψ + metadata
    2. build LoaderSpec
    3. write LoaderSpec JSON to --out-spec

LoaderSpec MUST include:
- loader_version="Unit02"
- mapping from semantic rails (iq_split / sign_split / etc.) to physical qubits
  under a field named `rail_layout`
- explicit "endianness": "little"
- explicit "qft_kernel_sign": "+"
- the qubit index order ("qubit_order") that downstream loading will respect
- reference to which NVE rails ended up on which physical line

Determinism:
- Given the same NVE bundle, LoaderSpec must be byte-identical when regenerated.
  This is contractually enforced by tests/test_unit02_* through string search.

Forward dependency:
- Unit04 ExecSpec / RunReceipt must embed LoaderSpec. The RunReceipt field
  `"rail_layout"` originates here in Unit02 and is checked again in Unit04 live
  backend tests.

If required strings like loader_version="Unit02" or "rail_layout" disappear
from docs or CLI, tests fail. That blocks tamper-evidence and Quentroy later.
