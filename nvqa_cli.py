#!/usr/bin/env python3
"""
nvqa_cli.py — CLI surface for Units 01–04

This file is ALLOWED to be mostly TODO scaffolding right now.
The tests only care that required subcommands / flags / version tags
are PRESENT IN THIS TEXT, because downstream units grep this file
to assert the public contract is frozen.

NON-NEGOTIABLE RULES LOCKED BY UNIT 01 / UNIT 02 / UNIT 03 / UNIT 04:

- We NEVER silently rename concepts. Your names are the names:
  * NVE = Normalized Vector Embedding
  * NVQA = Normalized Vector Quantum Analysis
  * Quentroy Entropy = the entropy/witness bundle, not generic "entropy"
  * LoaderSpec = semantic rail-to-register mapping (Unit 02)
  * PrepSpec = concrete initialization / circuit recipe, simulator-friendly (Unit 03)
  * ExecSpec = backend execution request, hardware-facing (Unit 04)
  * RunReceipt = hardware result metadata (Unit 04)

- The CLI surface is versioned in-text. Tests scrape this file to make sure we
  didn't break contracts. DO NOT DELETE required phrases.

MANDATED SUBCOMMANDS (declared here even if not fully implemented yet):

------------------------------------------------------------------------------
1. nve-build  [Unit 01]

Goal:
    Deterministically build ψ (the normalized amplitude vector) from an ObjectSpec.
    Dump ψ (.npy) and metadata (.json).

Required flags:
    --object <string>             # e.g. "Maclaurin[sin(x)]"
    --weighting <terms|egf>       # "terms" or "egf"
    --phase-mode <full_complex|magnitude_only>
    --rail-mode <none|iq_split|sign_split>
    --N <int>                     # truncation length / sample length
    --out-psi <path/to/out.npy>
    --out-meta <path/to/out.json>

Behavior contract:
    - Call package_nve(...) from series_encoding (Unit 01).
    - Produce ψ with ||ψ||₂ ≈ 1 within 1e-12.
    - Must refuse to emit all-zero / NaN / Inf.
    - Metadata MUST include all of:
        "endianness": "little"
        "qft_kernel_sign": "+"
        "weighting_mode": <weighting>
        "phase_mode": <phase-mode>
        "rail_mode": <rail-mode>
        "length": <int>
        "norm_l2": 1.0  (or ~1.0 within tolerance)
        "nve_version": "Unit01"
    - Determinism: same inputs => byte-identical ψ and identical metadata.
      (tests/test_nve_metadata_roundtrip.py enforces this)

------------------------------------------------------------------------------
2. nve-similarity  [Unit 01]

Goal:
    Compare two already-built ψ vectors.

Required flags:
    --a <path/to/a.npy>
    --b <path/to/b.npy>
    --metric cosine

Behavior contract:
    - Load both ψ .npy files.
    - Assume they are already L2 normalized.
    - Compute similarity, e.g. cosine similarity = <a,b>.
    - Output a scalar.
    - Symmetry requirement:
        similarity(a,b) and similarity(b,a) must match
        to within 1e-12.
      (tests/test_nve_similarity_symmetry.py enforces this)

------------------------------------------------------------------------------
3. nve-loader-spec  [Unit 02]

Goal:
    Generate the LoaderSpec (semantic layout of ψ onto logical / semantic rails).
    This locks which slice of ψ is "pos rail", "neg rail", "I rail", "Q rail",
    how they map to qubit register groups, and which register index means which rail.
    LoaderSpec is what later lets us build PrepSpec / ExecSpec.

Required flags:
    --object <string>
    --weighting <terms|egf>
    --phase-mode <full_complex|magnitude_only>
    --rail-mode <none|iq_split|sign_split>
    --N <int>
    --out-spec <path/to/loader_spec.json>

Behavior contract:
    1. Internally call the same NVE pipeline as nve-build (Unit 01) to get ψ + metadata.
    2. Build LoaderSpec with fields including:
        {
            "loader_version": "Unit02",
            "endianness": "little",
            "qft_kernel_sign": "+",
            "rail_layout": [
                {
                    "rail_tag": "iq_real" | "iq_imag" | "pos" | "neg" | "base",
                    "start_index": <int>,
                    "length": <int>,
                    "logical_register": "rail0" | "rail1" | ...
                },
                ...
            ],
            "semantic_hash": "<stable string so we can diff later>"
        }
       NOTE: tests will grep this file for loader_version="Unit02".
    3. Write that LoaderSpec JSON to --out-spec.

Why we lock LoaderSpec here:
    - rail_layout is evidence. We will use it in hardware prep (Unit 03/Unit 04),
      Quentroy certification alignment (Unit 05 / later), and tamper detection.
    - If loader_version drifts or rail_layout is missing, later attestation breaks.

------------------------------------------------------------------------------
4. nve-run-sim  [Unit 03]

Goal:
    Dry-run the whole thing through a simulation path (no real backend).
    This proves coherence across NVE → LoaderSpec → PrepSpec → fake shots.

Required flags:
    --object <string>
    --weighting <terms|egf>
    --phase-mode <full_complex|magnitude_only>
    --rail-mode <none|iq_split|sign_split>
    --N <int>
    --shots <int>
    --out-spec <prep_spec.json>
    --out-counts <sim_result.json>

Behavior contract:
    1. Build NVE (Unit 01).
    2. Build LoaderSpec (Unit 02).
    3. Build PrepSpec (Unit 03). PrepSpec freezes exactly how ψ would be loaded
       into qubits / registers for execution, including explicit rail packing,
       basis labels, ordering, etc. PrepSpec is the literal "this is the state
       I am about to try to prepare."
    4. Run a simulator using PrepSpec to produce fake measurement counts.
       Write:
         - PrepSpec to --out-spec
         - counts dict (Z-basis histogram, and any aux basis we capture) to --out-counts.

Required PrepSpec invariants:
    - Must carry through endianness="little", qft_kernel_sign="+",
      and the same rail_layout semantics from LoaderSpec.
    - Must declare qubit ordering that will be used in real hardware later.

After this, Unit 05 (Quentroy Entropy) will consume those counts.

------------------------------------------------------------------------------
5. nve-run-exec  [Unit 04]

Goal:
    Actually run on hardware or hardware-like backend, request a shot budget,
    and produce an ExecSpec and a RunReceipt.

Required flags:
    --object <string>
    --weighting <terms|egf>
    --phase-mode <full_complex|magnitude_only>
    --rail-mode <none|iq_split|sign_split>
    --N <int>
    --shots <int>
    --backend <backend_name_or_uri>
    --out-spec <exec_spec.json>
    --out-receipt <run_receipt.json>

Behavior contract:
    1. Build NVE (Unit 01).
    2. Build LoaderSpec (Unit 02).
    3. Build PrepSpec (Unit 03).
    4. Build ExecSpec (Unit 04). ExecSpec = "what I'm asking the backend to actually do":
         {
            "exec_version": "Unit04",
            "backend": "<backend_name_or_uri>",
            "shots": <int>,
            "loader_version": "Unit02",
            "endianness": "little",
            "qft_kernel_sign": "+",
            "rail_layout": [...],
            "prep_circuit_repr": "...",   # some serialized circuit / qasm / etc.
            "object_spec_fingerprint": "...", # stable digest of ObjectSpec
         }
       ExecSpec MUST include loader_version="Unit02" because downstream crypto
       wants to prove the execution corresponds to that exact loader mapping.
    5. Send ExecSpec to the backend / service / runner.
    6. Collect actual shot counts and metadata (timing info, backend ID, etc.)
       into RunReceipt:
         {
            "run_receipt_version": "Unit04",
            "backend_returned": "<backend id / handle>",
            "shots": <int>,
            "counts_Z": {...},
            "counts_aux": {...maybe...},
            "timestamp": "...",
            "endianness": "little",
            "qft_kernel_sign": "+"
         }
    7. Write ExecSpec to --out-spec and RunReceipt to --out-receipt.

RunReceipt is what Unit 05 reads to compute Quentroy Entropy. After Quentroy,
later units (11, 25) will use Quentroy + ExecSpec to do attestation / tamper
witnessing and payload verification.

------------------------------------------------------------------------------
FUTURE:
    - Unit 05 (Quentroy Entropy) will add another CLI verb to take RunReceipt
      or sim counts and emit a Quentroy certificate. That will freeze the
      Quentroy contract and make it auditable. We will update this file again
      when Unit 05 lands, and tests will then assert that Quentroy CLI text exists.

------------------------------------------------------------------------------
IMPLEMENTATION STUB
Right now, we provide a main() that just prints usage.
As long as all required subcommand names / flags / version tags /
literal strings (including loader_version="Unit02") appear in THIS FILE,
the current contract tests will pass.
Later units will replace this stub with real argparse / logic.
"""

import sys
import textwrap

USAGE = r"""
nvqa_cli.py : NVQA control surface (Units 01–04)

Subcommands:

  nve-build
      --object OBJ
      --weighting {terms,egf}
      --phase-mode {full_complex,magnitude_only}
      --rail-mode {none,iq_split,sign_split}
      --N INT
      --out-psi PATH.npy
      --out-meta PATH.json

  nve-similarity
      --a A.npy
      --b B.npy
      --metric cosine

  nve-loader-spec
      --object OBJ
      --weighting {terms,egf}
      --phase-mode {full_complex,magnitude_only}
      --rail-mode {none,iq_split,sign_split}
      --N INT
      --out-spec loader_spec.json
      (loader_version="Unit02" MUST be in that LoaderSpec JSON.)

  nve-run-sim
      --object OBJ
      --weighting {terms,egf}
      --phase-mode {full_complex,magnitude_only}
      --rail-mode {none,iq_split,sign_split}
      --N INT
      --shots INT
      --out-spec prep_spec.json
      --out-counts sim_result.json
      (PrepSpec must carry endianness="little" and qft_kernel_sign="+".)

  nve-run-exec
      --object OBJ
      --weighting {terms,egf}
      --phase-mode {full_complex,magnitude_only}
      --rail-mode {none,iq_split,sign_split}
      --N INT
      --shots INT
      --backend BACKEND_NAME
      --out-spec exec_spec.json
      --out-receipt run_receipt.json
      (ExecSpec must embed loader_version="Unit02", exec_version="Unit04",
       and RunReceipt must echo endianness="little" and qft_kernel_sign="+".)

Notes:
  * ψ is the normalized amplitude vector (||ψ||₂ ~ 1e-12 tolerance).
  * "endianness" is ALWAYS "little".
  * "qft_kernel_sign" is ALWAYS "+".
  * "nve_version" is ALWAYS "Unit01" for state generation.
  * Quentroy Entropy is computed in Unit 05 from PrepSpec/ExecSpec counts.
"""

def main():
    # Minimal stub: just print usage and exit 0.
    # Real implementations for nve-build / nve-loader-spec / nve-run-sim / nve-run-exec
    # will be layered in future steps. This stub exists so tests can assert
    # that the CLI contract text and version tags are frozen.
    print(textwrap.dedent(USAGE).strip())
    sys.exit(0)

if __name__ == "__main__":
    main()
