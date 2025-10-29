Unit 02 — State Loader Construction and Hardware-Ready Register Layout

This unit defines how a normalized ψ from Unit 01 becomes an actual register layout we can hand to hardware or a simulator. “Becomes” here means: ψ (a complex amplitude vector with ‖ψ‖₂ = 1, already locked under NVE metadata) is turned into something loadable: rail-split, ordered, sized to an n-qubit register, and expressed in a form an initializer / loader circuit can actually realize without guesswork.

This unit answers: given ψ and its metadata (endianness="little", qft_kernel_sign="+", rail_mode, etc.), how do we map ψ into basis states on an n-qubit device in a way that is:
- deterministic,
- reconstructable from metadata alone,
- and admissible for later attestation and Quentroy Entropy checks on real hardware shot data.

Dependencies:
- Requires Unit 01 (Normalized Vector Embedding / NVE, NVQA, Quentroy Entropy naming, rail modes, endianness, qft_kernel_sign).
- Assumes `package_nve(...)` is implemented and returns:
  {
    "psi": np.ndarray (normalized),
    "metadata": {
      "object_spec": {...},
      "weighting_mode": "...",
      "phase_mode": "...",
      "rail_mode": "...",
      "endianness": "little",
      "qft_kernel_sign": "+",
      "length": L,
      "norm_l2": 1.0,
      "nve_version": "Unit01"
    }
  }

Later units depend on this for:
- Unit 03 / 04 style “actual circuit synthesis and run on backend.”
- Unit 05 / 11 Quentroy Entropy certification from real device shot counts.
- Unit 07 similarity / atlas geometry that assumes consistent basis alignment across runs, not guessed qubit order.
- Unit 11 / 25 tamper + payload verification, where we claim “this exact ψ (with this layout) got prepared.”

If this unit changes, downstream physical prep, entropy certification, crypto attestation, and atlas comparisons all become untrustworthy. So once committed, this file is treated as binding.


SCOPE OF THIS UNIT

We are doing three things here:

(1) Register dimension resolution  
    We take ψ of length L and decide what register shape is required.  
    - If ψ is length L and L is not a power of two, we define how to embed ψ into the next power-of-two dimension by padding trailing zeros in a declared way.  
    - We assign an integer number of logical qubits n such that 2ⁿ ≥ L_after_padding.  
    - We record n in metadata.  
    - We record how many trailing basis states are actually “unused / forced-zero,” not just silently pad and pretend it was native.

(2) Rail -> subregister mapping  
    rail_mode from Unit 01 can be:
    - "none"        (ψ is already a straightforward complex state vector),
    - "iq_split"    (real and imag stored in two rails concatenated),
    - "sign_split"  (positive and negative magnitude rails concatenated).
    We must define:
    - how those rails become physically distinct subregisters or contiguous address blocks,
    - how those subregisters map to computational basis indices under the global little-endian convention,
    - and how we reconstruct semantic meaning later from raw counts.

(3) Loader spec  
    We output a deterministic loader spec: a structure that later units will turn into actual circuit instructions.  
    The loader spec is not yet the circuit; it’s the binding contract that says “qubit 0 gets this bit significance, these amplitudes correspond to these basis states, here is where rail A vs rail B lives, here is which padded states are zero, here is the declared QFT kernel sign alignment, here is the declared endianness.”  
    That loader spec is what we will sign, serialize, and later compare against hardware output to prove that hardware actually prepared what we said.


KEY CONVENTIONS (LOCKED HERE)

Endianness
- We continue to enforce little-endian basis indexing from Unit 01.
- Bit j (j=0 is least significant) maps to qubit j. Index m = Σ_j 2^j * b_j.
- We do not reorder qubits later just to make pretty plots. If someone wants MSB-first visuals, they must explicitly note that it’s a display transform.
- Any loader spec that violates this is rejected as nonconforming.

QFT kernel sign
- Still “+”.
- All Fourier / Hadamard / conjugate-basis, etc., mapping in later entropy checks assumes that sign.
- No one is allowed to silently flip the Fourier sign just because some DSP lib likes “-”.
- Loader spec must restate qft_kernel_sign = "+" so downstream has zero ambiguity.

Padding / extension policy
- If ψ length L is not an exact power of two, we choose n = ceil(log2(L)).  
  Let D = 2**n.  
  We embed ψ into length D by appending zeros to the tail (highest index end).
- We must record:
  - original_length = L
  - padded_length = D
  - pad_count = D - L
- The padded amplitudes must literally be 0.0 exactly, not tiny epsilons.
- The norm guarantee from Unit 01 applies to ψ prior to padding. After padding with exact zeros, norm is still 1.0.
- Anyone who measures an occupation in a padded basis state later is either seeing noise, leakage, or adversarial tampering. We will use that in later trust tests.

Rail packing and register layout
- If rail_mode == "none":  
  ψ already corresponds to one register of size L (or D after padding). Done.

- If rail_mode == "iq_split":  
  Unit 01 said: we took complex a[n] = x[n] + i y[n], split into rails r_real[n]=x[n], r_imag[n]=y[n], and concatenated [r_real || r_imag] -> r_concat, then normalized r_concat to ψ.  
  Interpretation here in Unit 02:
  - The first half of ψ corresponds to the “real rail subspace.”  
  - The second half of ψ corresponds to the “imag rail subspace.”  
  - We must assign disjoint contiguous basis index ranges for those two halves.
  - Loader spec must clearly tag these as rail_real and rail_imag with exact index ranges, not vibes.

- If rail_mode == "sign_split":  
  Unit 01 said: we split positive and negative magnitude contributions into two rails r_pos, r_neg and concatenated. Then normalized.  
  Interpretation here:
  - First half of ψ is the positive rail,
  - Second half of ψ is the negative rail.
  - Loader spec must tag rail_pos / rail_neg and ranges.

In all split-rail cases, we are defining a multi-register logical interpretation. Physically, it may all live on one n-qubit register. Logically, we treat those halves as different semantic channels. That semantic mapping is what allows us to take returned shots later and say “yes, the device actually preserved sign information vs. no, it collapsed sign and lied.”


LOADER SPEC STRUCTURE

We define a loader spec object. This object is produced in this unit and consumed in Unit 04 to actually synthesize and run hardware.

We call it LoaderSpec. LoaderSpec is a dict with required fields:

{
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "endianness": "little",
  "qft_kernel_sign": "+",

  "object_spec": { ...copy of Unit 01 object_spec... },

  "rail_mode": "none" | "iq_split" | "sign_split",
  "rail_layout": {
      // if rail_mode=="none":
      //   "kind": "single",
      //   "range": [0, D-1]

      // if rail_mode=="iq_split":
      //   "kind": "iq_split",
      //   "real_range": [0, D/2 - 1],
      //   "imag_range": [D/2, D-1]

      // if rail_mode=="sign_split":
      //   "kind": "sign_split",
      //   "pos_range": [0, D/2 - 1],
      //   "neg_range": [D/2, D-1]
  },

  "register_qubits": {
      "n_qubits": n,
      "original_length": L,
      "padded_length": D,
      "pad_count": D-L
  },

  "amplitudes": {
      "vector": [ ... list of floats or complex pairs, deterministic order ... ],
      "dtype": "float64" | "complex128"
  }
}

Rules:
- LoaderSpec["amplitudes"]["vector"] is the direct data we will ask Unit 04 to prepare on hardware.
- LoaderSpec MUST be deterministic given the same ψ input bundle from Unit 01.
- No field is allowed to be omitted “because it’s obvious.”
- No field is allowed to silently change meaning later. If it changes, loader_version must bump.


ATTACK / ADVERSARY MODEL FOR THIS UNIT

The attacker can:
- Hand us some different vector ψ′ and claim “this is what got loaded.”
- Claim different rail assignments than we actually declared.
- Claim different endianness.
- Claim different n_qubits mapping than we used.

We defend by:
- Serializing LoaderSpec in full before any run.
- Treating that LoaderSpec as the contract.
- In later units, we get counts back from hardware and we interpret them using that exact LoaderSpec. If the counts don’t match the rail breakup, qubit ordering, padded zeros, etc., we call fraud.

So this unit’s job is basically: freeze a machine-verifiable, post-hoc-checkable loader contract.


IMPLEMENTATION REQUIREMENTS FOR THIS UNIT

We need a new module for this unit. Create `loader_layout.py` at repo root with the following required functions.

Required functions:

1. resolve_register_shape(psi: np.ndarray) -> dict
   Input:
   - psi: np.ndarray (normalized), length L
   Output (returns both data and shape info):
   {
     "psi_padded": np.ndarray length D,
     "original_length": L,
     "padded_length": D,
     "pad_count": D-L,
     "n_qubits": n
   }
   where:
     n = smallest integer with 2**n >= L
     D = 2**n
   MUST:
   - append exact zeros to get length D
   - not renormalize (norm stays ~1.0)
   - assert no NaN/Inf
   - assert abs(||psi||₂ - 1.0) <= 1e-12 pre-pad
   - assert abs(||psi_padded||₂ - 1.0) <= 1e-12 post-pad

2. derive_rail_layout(psi_padded: np.ndarray, rail_mode: str) -> dict
   Input:
   - psi_padded (length D)
   - rail_mode in {"none","iq_split","sign_split"}
   Output:
   - dict that matches LoaderSpec["rail_layout"] contract:
     * kind
     * index ranges
   MUST:
   - if rail_mode=="none":
       kind="single"
       range=[0, D-1]
   - if rail_mode=="iq_split":
       kind="iq_split"
       real_range=[0, D/2 - 1]
       imag_range=[D/2, D-1]
       assert D even
   - if rail_mode=="sign_split":
       kind="sign_split"
       pos_range=[0, D/2 - 1]
       neg_range=[D/2, D-1]
       assert D even
   - must NOT reorder amplitudes. Only annotate.

3. build_loader_spec(nve_bundle: dict) -> dict
   Input:
   - nve_bundle exactly from Unit 01 package_nve()
     {
       "psi": np.ndarray,
       "metadata": {...}
     }
   Steps:
   - read psi, metadata
   - call resolve_register_shape -> get shape info + psi_padded
   - call derive_rail_layout(psi_padded, metadata["rail_mode"])
   - assemble LoaderSpec:
     {
       "nve_version": metadata["nve_version"],
       "loader_version": "Unit02",
       "endianness": metadata["endianness"],            # MUST be "little" or raise
       "qft_kernel_sign": metadata["qft_kernel_sign"],  # MUST be "+" or raise
       "object_spec": metadata["object_spec"],
       "rail_mode": metadata["rail_mode"],
       "rail_layout": <from derive_rail_layout>,
       "register_qubits": {
           "n_qubits": n,
           "original_length": L,
           "padded_length": D,
           "pad_count": D-L
       },
       "amplitudes": {
           "vector": serialized psi_padded (list form, deterministic),
           "dtype": "float64" | "complex128"
       }
     }
   MUST:
   - confirm still ||psi_padded||₂ ~ 1.0 within 1e-12
   - confirm no NaN/Inf
   - include pad_count etc
   - be deterministic: same nve_bundle in => identical dict out byte-for-byte after stable JSON dump

4. loader_spec_to_json(spec: dict, path: str) -> None
   - write LoaderSpec to disk at `path` as JSON
   - stable key ordering for determinism tests
   - refuse to write if spec fails invariants

All four functions MUST raise instead of silently fixing anything.

TESTS FOR THIS UNIT

Add:

tests/test_loader_shape_padding.py
- Create a fake ψ of length 3 that is already unit norm.
- resolve_register_shape must say:
    n_qubits == 2
    padded_length == 4
    pad_count == 1
- The padded ψ must be identical in first 3 slots and exactly 0 in the last slot.
- Norm must still be ~1.0.

tests/test_loader_rail_layout.py
- For rail_mode="none":
  kind="single", range covers [0, D-1].
- For rail_mode="iq_split":
  kind="iq_split", and ranges are disjoint halves [0, D/2-1], [D/2, D-1].
- For rail_mode="sign_split":
  kind="sign_split", same shape rule (pos_range / neg_range).
- Assert no amplitude reordering happened, only annotation.

tests/test_loader_spec_integrity.py
- build_loader_spec(nve_bundle) must emit:
  loader_version == "Unit02"
  copies nve_version from metadata
  endianness == "little"
  qft_kernel_sign == "+"
  register_qubits.n_qubits consistent with padded_length == 2**n_qubits
  amplitudes.vector length == padded_length
  last pad_count entries are exactly 0 or 0+0j
  norm ~1.0 within 1e-12
  no NaN/Inf

tests/test_loader_spec_determinism.py
- Build the same nve_bundle twice from the same ObjectSpec.
- build_loader_spec on both must JSON-dump identically
  (stable ordering, exact byte match).
- If not identical, determinism is broken and later attestation is impossible.

CLI IMPACT

`nvqa_cli.py` must grow:

nve-loader-spec
Example:
./nvqa_cli.py nve-loader-spec \
  --object "Maclaurin[sin(x)]" \
  --weighting egf \
  --phase-mode full_complex \
  --rail-mode iq_split \
  --N 64 \
  --out-spec /abs/path/sin_loader.json

Behavior:
- internally call the same build path as nve-build to get the Unit 01 bundle
- call build_loader_spec(bundle)
- write LoaderSpec JSON to --out-spec using loader_spec_to_json
- refuse on invariant violation

This is mandatory so later units can consume loader specs without guessing rail split semantics or qubit indexing.


ACCEPTANCE CRITERIA FOR THIS UNIT

This unit is considered integrated / valid if and only if:
- loader_layout.py exists with resolve_register_shape, derive_rail_layout, build_loader_spec, loader_spec_to_json as defined here,
- the 4 new tests exist and assert the behaviors above (even if they’re TODO at first, the rules they claim are binding),
- nvqa_cli.py exposes an nve-loader-spec subcommand stub with the required flags and behavior contract,
- downstream code is not allowed to reinterpret ψ, change endianness, drop rail mapping, or invent a different padding story without bumping loader_version.

FUTURE NOTES TIED TO THIS UNIT

- Hardware init cost:
  We’re not yet solving “how do I cheaply prepare ψ on hardware with limited native initialization.” That is Unit 04. Unit 02 only pins the logical layout and padding so Unit 04 has a stable target to hit.

- Multiple physical registers:
  Some backends expose disjoint qubit blocks or topology constraints. We are not routing around coupling maps here. We’re just freezing semantic layout. Physical routing / transpile comes later.

- Entropy witness alignment:
  Quentroy Entropy (Units 05 / 11) assumes we know which logical subspace corresponds to which semantic rail. That assumption comes straight from LoaderSpec["rail_layout"]. That’s why rail_layout exists as a first-class field and is versioned here, not invented later.

- Payload watermarking / keyed twirl:
  Later units that introduce keyed scrambling, authentication, and watermarking depend on having a deterministic loader spec so we can prove “the decrypted / unscrambled state matches exactly what LoaderSpec said.” If LoaderSpec drifts, you can’t prove anything. So loader_version="Unit02" matters for crypto arguments later.
