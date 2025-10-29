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
