Unit 03 — Circuit Prep Spec and Simulation Harness

What this unit does:
- Takes LoaderSpec from Unit 02 (which already locked rail layout, qubit count, padding, endianness="little", qft_kernel_sign="+").
- Produces a deterministic "prep description" that says exactly how to initialize |0...0> and rotate it into ψ on n_qubits, with rails in the right index ranges.
- Provides a simulator harness to generate ideal shot counts from that prep description (no noise, no routing constraints).
- Bundles all of that plus the counts into a run record we can analyze for Quentroy Entropy in the next units.

Why this matters:
- Later we are going to claim “we prepared this state, here are the counts, here’s Quentroy.” That’s an auditable chain only if (1) ψ is frozen (Unit 01), (2) LoaderSpec is frozen (Unit 02), and (3) the prep circuit spec we *say* we ran is frozen (this unit).
- Crypto / payload verification / tamper detection (later units) rely on being able to show: “the circuit that should have produced these counts is exactly this one, and this circuit corresponds to ψ from Unit 01 under the layout from Unit 02.” So this spec can’t drift.

Dependencies (must already exist and obey their contracts):
- Unit 01 output bundle (`package_nve`): gives ψ and metadata including rail_mode, endianness="little", qft_kernel_sign="+", nve_version="Unit01".
- Unit 02 output (`build_loader_spec`): gives LoaderSpec with
  - loader_version="Unit02"
  - register_qubits.{n_qubits, padded_length, pad_count}
  - rail_layout (ranges for rails)
  - amplitudes.vector (the padded ψ, serialized)
  - endianness="little"
  - qft_kernel_sign="+"

Downstream units depend on this for:
- entropy / Quentroy certificate (Unit 05 / Unit 11),
- trust / attestation and payload verification (Unit 11 / Unit 25),
- similarity geometry and atlas (Unit 07) when they consume simulated distributions,
- crypto watermark / keyed scrambles later, where we prove “this scrambled circuit was derived from this clean prep circuit.”

Scope lock:
Once this unit is committed, the prep contract format (what fields are in the prep description, how we serialize it, how we simulate it) is considered binding unless we explicitly bump a version like "prep_version".


WHAT WE FREEZE IN THIS UNIT

We define a "PrepSpec". PrepSpec is a dict with these required fields:

{
  "nve_version": "Unit01",              # carried through unchanged
  "loader_version": "Unit02",           # must match LoaderSpec
  "prep_version": "Unit03",

  "endianness": "little",               # must still be "little"
  "qft_kernel_sign": "+",               # must still be "+"

  "n_qubits": <int>,                    # from LoaderSpec["register_qubits"]["n_qubits"]
  "padded_length": <int>,               # from LoaderSpec["register_qubits"]["padded_length"]
  "pad_count": <int>,                   # from LoaderSpec["register_qubits"]["pad_count"]

  "rail_mode": "none" | "iq_split" | "sign_split",
  "rail_layout": { ... exactly from LoaderSpec["rail_layout"] ... },

  "amplitudes": {
     "vector": [ ... same order as LoaderSpec["amplitudes"]["vector"] ... ],
     "dtype": "float64" | "complex128"
  },

  "init_sequence": [
     # abstract gates / loader steps that would prepare that amplitude vector
     # on ideal hardware. This is NOT physical transpiled gates, this is a
     # declarative sequence so later units can prove "this is what we meant".
     # format is frozen here.
     {
       "op": "prepare_basis_amplitudes",
       "target_register": "full",
       "amplitude_source": "amplitudes.vector",
       "endianness": "little"
     }
     # later we can extend with phase tweaks, rail tagging, keyed scrambles,
     # etc. but the base element must always exist.
  ]
}

Rules:
- PrepSpec["prep_version"] MUST be "Unit03".
- PrepSpec copies LoaderSpec data structurally: n_qubits, rail_layout, amplitudes, etc.
- We are not allowed to silently reorder amplitudes, flip endianness, or split rails differently. If any of that changes, the version must bump and tests must break until updated.
- `init_sequence` is declarative, not executable qiskit. It's the human/audit-readable contract that says “this prep should realize those amplitudes on that register.”

Note on why we keep "init_sequence" abstract instead of dumping qiskit gates:
- Transpilation, routing, hardware-native gate sets, and pulse level control vary across targets and break determinism.
- We only need to prove “intended logical state == ψ with this qubit ordering and rail layout.”
- So we freeze a declarative init description here, not a backend-specific transpiled circuit. Backend-specific synthesis is a later unit and will reference PrepSpec + loader_version + nve_version by hash.


SIMULATION HARNESS

This unit also defines the simulator we use for ideal counts.

We define SimSpec / SimResult like this:

SimSpec =
{
  "prep_spec": <PrepSpec dict>,
  "shots": <int>
}

SimResult =
{
  "prep_version": "Unit03",
  "n_qubits": <int>,
  "shots": <int>,
  "rail_mode": "...",
  "counts": {
     "<basis_index_decimal_string>": <int>,
     ...
  },
  "distribution": {
     "<basis_index_decimal_string>": <float>,  # empirical freq = counts[i]/shots
     ...
  },
  "norm_check_l2": <float>,  # should be ~1.0
  "endianness": "little",
  "qft_kernel_sign": "+"
}

Rules:
- We generate an *ideal* outcome distribution from the amplitude vector in PrepSpec["amplitudes"]["vector"]:
  p[i] = |amp[i]|^2
- We draw multinomial counts from that ideal p for the requested number of shots.
- We then return both raw counts and normalized empirical frequencies.
- We must assert:
  - prep_spec.prep_version == "Unit03" or raise,
  - prep_spec.endianness == "little" or raise,
  - prep_spec.qft_kernel_sign == "+" or raise,
  - ∑_i p[i] is within 1e-12 of 1.0 (if not, reject),
  - n_qubits matches padded_length == 2**n_qubits (if not, reject).
- We DO NOT rename rails, split rails, or compress rails. We just give raw basis index strings "0", "1", "2", ... in little-endian meaning (same as before).
- pad_count basis states at the tail have amplitude exactly 0, so their ideal p[i] = 0. If simulated counts ever show those indices with nonzero counts, well, random multinomial draws could technically still spit zeros only. On real hardware later: any population in padded states is “leakage.” We’ll inspect that in cert units. We’re making that explicit, not sweeping it.


NEW PYTHON MODULE FOR THIS UNIT: prep_circuit.py

prep_circuit.py must expose:

1. synthesize_init_circuit(loader_spec: dict) -> dict
   Input:
   - LoaderSpec from Unit 02
   Output:
   - PrepSpec dict (as defined above)
   Must:
   - copy through nve_version, loader_version
   - set prep_version="Unit03"
   - assert endianness == "little", qft_kernel_sign == "+"
   - assert loader_version == "Unit02"
   - assert amplitudes vector length == padded_length
   - assert padded_length == 2**n_qubits
   - embed init_sequence as specified (array with one dict element "prepare_basis_amplitudes", referencing amplitudes.vector)
   - be deterministic (same LoaderSpec in => byte-identical PrepSpec out after stable json dump)

2. simulate_counts(prep_spec: dict, shots: int) -> dict
   Input:
   - PrepSpec dict
   - integer shots
   Output:
   - SimResult dict (as defined above)
   Must:
   - compute ideal p[i] = |amp[i]|^2
   - sample multinomial (pure python/numpy rng is fine)
   - return counts, distribution, norm_check_l2 (~1.0)
   - enforce invariants above
   - refuse if shots <= 0

3. prep_run_bundle(nve_bundle: dict, shots: int) -> dict
   Convenience wrapper to chain Unit 01 → Unit 02 → Unit 03 in-memory:
   Steps:
   - call build_loader_spec(nve_bundle)  (Unit 02)
   - call synthesize_init_circuit(...)   (this unit)
   - call simulate_counts(...)           (this unit)
   Returns:
   {
     "nve_version": ...,
     "loader_version": ...,
     "prep_version": "Unit03",
     "shots": shots,
     "prep_spec": <PrepSpec>,
     "sim_result": <SimResult>
   }
   This becomes the thing later entropy/cert code will consume.
   Must raise if anything in the chain violates its contract.

Absolute rule: none of these functions are allowed to silently “fix” drifting metadata. If loader_spec says rail_mode="iq_split", you keep that. If it says "endianness":"little", you keep that. If something is wrong, you error out, you do NOT patch it.


TEST PLAN FOR THIS UNIT

We add 4 tests.

tests/test_prep_shape_matches_loader.py
- Build a fake loader_spec with:
  n_qubits=3, padded_length=8, pad_count=0, rail_mode="none", amplitudes.vector length 8, norm=1.
- synthesize_init_circuit(loader_spec) must produce:
  - PrepSpec["n_qubits"] == 3
  - PrepSpec["padded_length"] == 8
  - PrepSpec["pad_count"] == 0
  - PrepSpec["rail_mode"] == "none"
  - PrepSpec["rail_layout"] copied straight through
  - PrepSpec["prep_version"] == "Unit03"
  - init_sequence[0]["op"] == "prepare_basis_amplitudes"
  - init_sequence[0]["endianness"] == "little"
  - endianness == "little", qft_kernel_sign == "+"

tests/test_prep_serialization_fields.py
- Verify that PrepSpec coming out of synthesize_init_circuit has all mandatory top-level keys:
  nve_version, loader_version, prep_version,
  endianness, qft_kernel_sign,
  n_qubits, padded_length, pad_count,
  rail_mode, rail_layout,
  amplitudes, init_sequence
- Verify that amplitudes.vector length == padded_length and matches loader_spec["amplitudes"]["vector"] exactly (no reorder).

tests/test_prep_simulation_distribution_norm.py
- Create a tiny PrepSpec with 2 qubits (padded_length=4), amplitudes like [1,0,0,0] so norm is 1.
- simulate_counts(prep_spec, shots=100) must:
  - return sim_result where 'counts' keys are "0","1","2","3"
  - sum(counts.values()) == 100
  - distribution["0"] ~ 1.0, others ~0
  - sim_result["norm_check_l2"] ~ 1.0 within 1e-12
  - sim_result["prep_version"] == "Unit03"
  - sim_result["endianness"] == "little"
  - sim_result["qft_kernel_sign"] == "+"

tests/test_prep_determinism.py
- Given the same loader_spec twice, synthesize_init_circuit twice, and ensure that a stable JSON dump of each PrepSpec is byte-identical.
- Determinism is mandatory. If not deterministic, you can’t later claim cryptographic or forensic reproducibility.

CLI IMPACT

We extend nvqa_cli.py again with a new subcommand stub:

nve-run-sim
Example:
./nvqa_cli.py nve-run-sim \
  --object "Maclaurin[sin(x)]" \
  --weighting egf \
  --phase-mode full_complex \
  --rail-mode iq_split \
  --N 64 \
  --shots 1024 \
  --out-spec /abs/path/sin_prep.json \
  --out-counts /abs/path/sin_counts.json

Behavior:
- Internally:
  - build NVE bundle (Unit 01),
  - build LoaderSpec (Unit 02),
  - build PrepSpec and simulate counts (Unit 03),
  - write PrepSpec JSON and SimResult JSON to the given paths.
- Must refuse if any invariant from Units 01/02/03 is violated.


ACCEPTANCE CRITERIA FOR THIS UNIT

Unit 03 is considered integrated if:
- prep_circuit.py exists with synthesize_init_circuit, simulate_counts, prep_run_bundle, all raising on invariant breakage.
- the 4 new tests stub out the rules above.
- nvqa_cli.py contains a TODO stub for nve-run-sim with the correct flags / behavior statement.
- all required version markers are enforced (prep_version == "Unit03") and we NEVER silently alter rail layout, endianness, qft_kernel_sign, or amplitude ordering.

This locks the intended logical prep circuit and the reference simulator path. Later units (entropy certificate, crypto witness, tamper proofing, atlas) will rely on this exact shape.

## TEST CONTRACT (DO NOT CHANGE)

Relevant tests:
- tests/test_unit03_contract_cli.py

Required CLI surface in nvqa_cli.py:
- subcommand token `nve-run-sim`
  Flags:
    --object
    --weighting
    --phase-mode
    --rail-mode
    --N
    --shots
    --out-spec
    --out-counts
  Behavior:
    1. build ψ via Unit01 (`psi_source`: "nve-build")
    2. build LoaderSpec via Unit02
    3. build PrepSpec for a simulator backend (backend: "sim")
         PrepSpec MUST include:
           {
             "prep_version": "Unit03",
             "psi_source": "nve-build",
             "backend": "sim",
             "shots": <int>,
             "qubit_order": [...],
             "rail_layout": {... mirrors LoaderSpec ...}
           }
    4. run a simulator shot loop and dump synthetic counts JSON to --out-counts

Requirements enforced by tests/test_unit03_contract_cli.py:
- nvqa_cli.py must literally contain:
    "nve-run-sim"
    "--shots"
    'prep_version="Unit03"'
    'backend": "sim"'
    "qubit_order"
    "rail_layout"
    'psi_source": "nve-build"'
- total reported counts must sum to `shots` in downstream usage.

Downstream tie-in:
- Unit03 PrepSpec is what Unit04 turns into an ExecSpec for real hardware.
- If PrepSpec stops carrying "rail_layout", "qubit_order", or loses prep_version="Unit03",
  then ExecSpec -> RunReceipt mapping becomes unverifiable, and Quentroy cert breaks.
