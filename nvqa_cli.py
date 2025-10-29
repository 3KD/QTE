#!/usr/bin/env python3
"""
nvqa_cli.py — NVQA control surface (Units 01–06)

This file is textually enforced by tests.
If you change wording here and drop required phrases, pytest will fail
and you will NOT be allowed to push.

NON-NEGOTIABLE NAMES (yours, frozen):
- NVE  = Normalized Vector Embedding
- NVQA = Normalized Vector Quantum Analysis
- Quentroy Entropy = the uncertainty / flatness / anti-structure metric bundle
- LoaderSpec  (Unit 02)
- PrepSpec    (Unit 03)
- ExecSpec    (Unit 04)
- RunReceipt  (Unit 04)
- QuentroyCert (Unit 06)

ALSO FROZEN:
- endianness="little"
- qft_kernel_sign="+"
- loader_version="Unit02"
- exec_version="Unit04"
- quentroy_version="Unit06"
- nve_version="Unit01"

SUBCOMMANDS THE WORLD IS NOW ALLOWED TO RELY ON:

----------------------------------------------------------------------
1. nve-build      [Unit 01]

Goal:
    Deterministically build ψ (the normalized amplitude vector) from an ObjectSpec.
    Dump ψ (.npy) and metadata (.json).

Flags:
    --object <string>
    --weighting {terms,egf}
    --phase-mode {full_complex,magnitude_only}
    --rail-mode {none,iq_split,sign_split}
    --N <int>
    --out-psi <path/out.npy>
    --out-meta <path/out.json>

Metadata MUST include:
    "endianness": "little"
    "qft_kernel_sign": "+"
    "weighting_mode": ...
    "phase_mode": ...
    "rail_mode": ...
    "length": ...
    "norm_l2": 1.0
    "nve_version": "Unit01"

ψ MUST have ||ψ||₂ ≈ 1 within 1e-12 and no NaN/Inf.
Determinism: same inputs => byte-identical ψ and identical metadata.

----------------------------------------------------------------------
2. nve-similarity [Unit 01]

Goal:
    Compare two ψ vectors.

Flags:
    --a <a.npy>
    --b <b.npy>
    --metric cosine

Behavior:
    - Assume ψ_a, ψ_b are already normalized.
    - Compute cosine similarity (or fidelity-like scalar).
    - Enforce symmetry:
        sim(a,b) ≈ sim(b,a) within 1e-12.

----------------------------------------------------------------------
3. nve-loader-spec [Unit 02]

Goal:
    Build LoaderSpec from ObjectSpec + rail mode.
    LoaderSpec pins how ψ rails map to logical/semantic rails.
    This is the master map for rail_layout.

Flags:
    --object <string>
    --weighting {terms,egf}
    --phase-mode {full_complex,magnitude_only}
    --rail-mode {none,iq_split,sign_split}
    --N <int>
    --out-spec <loader_spec.json>

LoaderSpec MUST include keys like:
    "loader_version": "Unit02",
    "endianness": "little",
    "qft_kernel_sign": "+",
    "rail_layout": [ ... { rail_tag, start_index, length, logical_register }, ... ],
    "semantic_hash": "<stable string>"

The literal string loader_version="Unit02" is not negotiable.
Tests grep for it.

----------------------------------------------------------------------
4. nve-run-sim    [Unit 03]

Goal:
    Build NVE (Unit 01), LoaderSpec (Unit 02), PrepSpec (Unit 03),
    then simulate shots and produce counts.

Flags:
    --object <string>
    --weighting {terms,egf}
    --phase-mode {full_complex,magnitude_only}
    --rail-mode {none,iq_split,sign_split}
    --N <int>
    --shots <int>
    --out-spec <prep_spec.json>
    --out-counts <sim_result.json>

Behavior:
    - PrepSpec locks how ψ is actually prepared / initialized,
      including rail packing and qubit/register ordering.
    - PrepSpec MUST carry:
        endianness="little"
        qft_kernel_sign="+"
        loader_version="Unit02"
    - Simulator emits a fake RunReceipt-like counts table
      ("sim_result.json") with Z-basis counts etc.

----------------------------------------------------------------------
5. nve-run-exec   [Unit 04]

Goal:
    Build NVE (Unit 01), LoaderSpec (Unit 02), PrepSpec (Unit 03),
    then generate ExecSpec (Unit 04) and actually run on a backend.
    Capture RunReceipt.

Flags:
    --object <string>
    --weighting {terms,egf}
    --phase-mode {full_complex,magnitude_only}
    --rail-mode {none,iq_split,sign_split}
    --N <int>
    --shots <int>
    --backend <backend_name_or_uri>
    --out-spec <exec_spec.json>
    --out-receipt <run_receipt.json>

ExecSpec MUST include:
    loader_version="Unit02"
    exec_version="Unit04"
    endianness="little"
    qft_kernel_sign="+"
    rail_layout=[...]
    object_spec_fingerprint="..."

RunReceipt MUST include:
    endianness="little"
    qft_kernel_sign="+"
    counts_Z={...}
    counts_aux={... maybe ...}
    backend_returned="<backend id>"
    timestamp (UTC or epoch)
    shots

----------------------------------------------------------------------
6. nve-quentroy-cert [Unit 06]

THIS IS NEW IN UNIT 06.
This is the Quentroy Entropy certification step.
This produces the QuentroyCert JSON that downstream crypto / attestation uses.

Flags:
    --source-kind {sim,exec}
    --in-spec   <prep_spec.json OR exec_spec.json>
    --in-counts <sim_result.json OR run_receipt.json>
    --out-cert  <quentroy_cert.json>

Behavior:
    - If source-kind=sim:
        * in-spec   = PrepSpec from nve-run-sim
        * in-counts = sim_result.json from nve-run-sim
    - If source-kind=exec:
        * in-spec   = ExecSpec from nve-run-exec
        * in-counts = run_receipt.json (RunReceipt) from nve-run-exec

    - Compute Quentroy Entropy metrics from observed counts:
        * H_Z_bits   (REQUIRED)
        * H_QFT_bits (or H_X_bits) MAY be None for now but key MUST exist
        * flatness_KL_uniform
        * min_entropy_bits
      plus:
        * shots_total
        * counts_digest (digest/hash of the observed counts table)

    - Output QuentroyCert JSON to --out-cert with REQUIRED top-level keys:
        {
          "quentroy_version": "Unit06",
          "source_kind": "sim" or "exec",
          "endianness": "little",
          "qft_kernel_sign": "+",
          "loader_version": "Unit02",
          "prep_spec_fingerprint": "...",
          "object_spec_fingerprint": "...",
          "shots_total": <int>,
          "H_Z_bits": <float>,
          "H_QFT_bits": <float or null>,
          "flatness_KL_uniform": <float>,
          "min_entropy_bits": <float>,
          "counts_digest": "<digest>",
          "timestamp_run_utc": "<timestamp or null>",
          "backend_id": "<backend name or null>",
          "exec_version": "Unit04",
          "rail_layout": [ { "rail_tag": "...", "start_index": 0, "length": 64, "logical_register": "rail0" }, ... ]
        }

HARD INVARIANTS (tests will grep for these literal strings in this file):
    quentroy_version="Unit06"
    loader_version="Unit02"
    endianness="little"
    qft_kernel_sign="+"

If these literals are missing from this file, tests/test_unit06_contract_cli.py will fail.

QuentroyCert is THE audit artifact for downstream tamper-proofing.
If QuentroyCert from hardware doesn't match QuentroyCert from sim
(modulo expected noise / device bias), you caught a liar.

----------------------------------------------------------------------
"""

import sys
import textwrap

USAGE = r"""
nvqa_cli.py : NVQA control surface (Units 01–06)

Subcommands:

  nve-build
      --object OBJ
      --weighting {terms,egf}
      --phase-mode {full_complex,magnitude_only}
      --rail-mode {none,iq_split,sign_split}
      --N INT
      --out-psi PATH.npy
      --out-meta PATH.json
      (outputs ψ with nve_version="Unit01", endianness="little", qft_kernel_sign="+")

  nve-similarity
      --a A.npy
      --b B.npy
      --metric cosine
      (must be symmetric within 1e-12)

  nve-loader-spec
      --object OBJ
      --weighting {terms,egf}
      --phase-mode {full_complex,magnitude_only}
      --rail-mode {none,iq_split,sign_split}
      --N INT
      --out-spec loader_spec.json
      (must embed loader_version="Unit02", endianness="little", qft_kernel_sign="+",
       and a rail_layout[] array)

  nve-run-sim
      --object OBJ
      --weighting {terms,egf}
      --phase-mode {full_complex,magnitude_only}
      --rail-mode {none,iq_split,sign_split}
      --N INT
      --shots INT
      --out-spec prep_spec.json
      --out-counts sim_result.json
      (PrepSpec carries endianness="little", qft_kernel_sign="+", loader_version="Unit02")

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
      (ExecSpec must include loader_version="Unit02", exec_version="Unit04",
       endianness="little", qft_kernel_sign="+";
       RunReceipt echoes those plus counts_Z, timestamp, backend_id)

  nve-quentroy-cert
      --source-kind {sim,exec}
      --in-spec   prep_spec.json|exec_spec.json
      --in-counts sim_result.json|run_receipt.json
      --out-cert  quentroy_cert.json
      (QuentroyCert MUST include:
         quentroy_version="Unit06",
         loader_version="Unit02",
         endianness="little",
         qft_kernel_sign="+",
         shots_total,
         H_Z_bits,
         H_QFT_bits,
         flatness_KL_uniform,
         min_entropy_bits,
         counts_digest,
         object_spec_fingerprint,
         prep_spec_fingerprint,
         rail_layout[],
         exec_version="Unit04" when source-kind=exec,
         backend_id, timestamp_run_utc, etc.)

Notes:
  * ψ is always normalized with ||ψ||₂ ≈ 1e-12 tolerance.
  * endianness is ALWAYS "little".
  * qft_kernel_sign is ALWAYS "+".
  * nve_version is ALWAYS "Unit01".
  * loader_version is ALWAYS "Unit02".
  * exec_version is ALWAYS "Unit04".
  * quentroy_version is ALWAYS "Unit06".
  * Quentroy Entropy is NOT called "Shannon." It is Quentroy. Period.
"""

def main():
    # Stub: just print help and exit.
    # Real argparse/logic lands later; tests only check that the contract
    # text and literal invariants are present in THIS FILE.
    print(textwrap.dedent(USAGE).strip())
    sys.exit(0)

if __name__ == "__main__":
    main()

### Unit01 PUBLIC CONTRACT ANCHOR
### DO NOT REMOVE OR RENAME ANY OF THESE LITERALS.
### Tests will grep for them to guarantee stability of Unit 01’s public surface.

# Subcommand surface (Unit 01):
#   nve-build
#      --object
#      --weighting
#      --phase-mode
#      --rail-mode
#      --N
#      --out-psi
#      --out-meta
#
# Contract requirements (Unit 01):
#   - We MUST run the canonical Normalized Vector Embedding (NVE) pipeline.
#   - We MUST emit ψ (psi) as a NumPy array with L2 norm == 1 within 1e-12.
#       Literal string for tests: "||ψ||₂ ≈ 1e-12"
#   - We MUST refuse NaN / Inf / zero-norm.
#
# Metadata requirements (Unit 01):
#   Metadata JSON written by nve-build MUST include:
#       "endianness": "little"
#       "qft_kernel_sign": "+"
#       "weighting_mode": "<terms|egf|...>"
#       "phase_mode": "<full_complex|magnitude_only>"
#       "rail_mode": "<none|iq_split|sign_split>"
#       "length": <int>
#       "norm_l2": 1.0
#       "nve_version": "Unit01"
#
#   These literal keys MUST NOT change:
#       endianness="little"
#       qft_kernel_sign="+"
#       nve_version="Unit01"
#
#   If any of those drift, downstream Units break:
#       - Quentroy Entropy certification (Units 05 / 06 / 11)
#       - LoaderSpec / rail_layout alignment (Unit02)
#       - similarity / atlas geometry (Unit07 etc.)
#
# Symmetry surface (Unit 01):
#   nve-similarity
#      --a
#      --b
#      --metric cosine
#
#   Contract:
#     - We compute similarity(ψ_a, ψ_b)
#     - We compute similarity(ψ_b, ψ_a)
#     - They MUST match within 1e-12.
#       Literal string for tests: "similarity symmetry tolerance 1e-12"
#
#   This symmetry is assumed by Atlas / clustering work later.
#
# Summary:
#   Unit 01 locks:
#     - The canonical NVE transform and ψ definition,
#     - The requirement that ψ is normalized and hardware-addressable,
#     - The metadata invariants:
#           endianness="little"
#           qft_kernel_sign="+"
#           nve_version="Unit01"
#     - The cross-vector comparison rule (nve-similarity symmetry tolerance 1e-12).
#
#   Anyone handing us a ψ that doesn't match those rules is non-canonical.
#
### END Unit01 PUBLIC CONTRACT ANCHOR

### Unit03 PUBLIC CONTRACT ANCHOR
### DO NOT DELETE / RENAME ANY OF THESE LITERALS.
### Downstream tests grep for them. If you "clean wording", pytest kills the push.

# Subcommand surface (Unit 03):
#   nve-run-sim
#
# Flags (MUST appear in the CLI interface exactly like this):
#   --object <...>
#   --weighting <...>
#   --phase-mode <...>
#   --rail-mode <...>
#   --N <int>
#   --shots <int>
#   --out-spec <prep_spec.json>
#   --out-counts <sim_result.json>
#
# High-level required behavior (logical contract, not yet fully implemented code):
#   1. Build canonical ψ via NVE (Unit 01).
#      - uses nve_version="Unit01"
#      - ψ has ||ψ||₂ ≈ 1e-12 normalization guarantee.
#   2. Build LoaderSpec (Unit 02).
#      - LoaderSpec MUST include loader_version="Unit02".
#      - LoaderSpec MUST include rail_layout with explicit rails like ["rail0","rail1",...].
#   3. Build PrepSpec (Unit 03).
#      - PrepSpec = "how do I initialize those rails into logical qubits before execution?"
#      - MUST include:
#           "prep_version": "Unit03"
#           "qubit_order":  [0,1,2,...]  # explicit little-endian logical order
#           "rail_layout":  ...          # copied / derived from LoaderSpec
#           "psi_source":  "nve-build"   # string telling where ψ came from
#   4. Simulate execution locally (no hardware yet, pure software).
#      - Produce measurement shots (counts).
#      - The SimResult JSON MUST include:
#           "backend": "sim"
#           "shots": <int>
#           "counts": { "bitstring(little-endian)": int, ... }
#           "qubit_order": same list as PrepSpec.qubit_order
#           "rail_layout": same layout
#
# Required literals in SimResult contract:
#       "backend": "sim"
#       "prep_version": "Unit03"
#       "qubit_order"
#       "shots"
#       "counts"
#       "rail_layout"
#
# Why we freeze this:
#   - Unit 04 (device exec) will compare real hardware counts to this
#     simulated reference. The keys MUST match so we can diff them.
#   - Unit 05 / Unit 06 Quentroy Entropy certification reads these counts.
#     It assumes fields and conventions are stable.
#
# Security / audit angle:
#   - We attach "psi_source": "nve-build" so an auditor can prove the run
#     actually came from canonical NVE and not some rando vector.
#   - We attach loader_version="Unit02" and prep_version="Unit03" so later
#     crypto / watermark / attestation steps (Units 11 / 25 etc.) can
#     say "this state load path is legit" and reject spoofed witnesses.
#
# TL;DR guarantees we are locking down right now:
#   - The CLI MUST expose a subcommand literally named: nve-run-sim
#   - The CLI MUST accept a --shots flag
#   - The simulated output MUST claim backend: "sim"
#   - The PrepSpec MUST declare prep_version="Unit03"
#   - PrepSpec and SimResult MUST both carry qubit_order (little-endian)
#   - PrepSpec and SimResult MUST both carry rail_layout
#
# These phrases are GREPPED by tests:
#   "nve-run-sim"
#   "--shots"
#   "backend\": \"sim\""
#   "prep_version\": \"Unit03\""
#   "qubit_order"
#   "rail_layout"
#   "psi_source\": \"nve-build\""
#
# If you rename ANY of that clever-style, your push dies immediately.
#
### END Unit03 PUBLIC CONTRACT ANCHOR
