#!/usr/bin/env python3
"""
nvqa_cli.py — CLI surface for Units 01–06

THIS FILE IS A CONTRACT. pytest greps this text.
If you change or remove these substrings, you break the pipeline.
We are allowed to add NEW sections, but edits to existing promises
must update tests in lockstep.

-------------------------------------------------
1. nve-build  (Unit01 origin of ψ)
-------------------------------------------------
Usage:
  nve-build \
    --object "Maclaurin[sin(x)]" \
    --weighting egf \
    --phase-mode full_complex \
    --rail-mode iq_split \
    --N 64 \
    --out-psi sin_state.npy \
    --out-meta sin_meta.json

Semantics:
  - Deterministic NVE (Normalized Vector Embedding).
  - Produces ψ with L2 norm ||ψ||₂ ≈ 1e-12 tolerance to 1.0.
    (exact substring required by tests:  ||ψ||₂ ≈ 1e-12 )
  - Emits metadata:
        endianness="little"
        qft_kernel_sign="+"
        nve_version="Unit01"
  - Refuses to emit NaN/Inf.
  - Refuses to emit ||ψ||₂ == 0.
  - Records full ObjectSpec, weighting, phase_mode, rail_mode,
    and rail_layout info for reconstruction later.

Also defined in Unit01:
  nve-similarity \
    --a A.npy \
    --b B.npy \
    --metric cosine

  This MUST produce a symmetric similarity measure:
    similarity(ψ_a, ψ_b) ≈ similarity(ψ_b, ψ_a)
    with similarity symmetry tolerance 1e-12
  Downstream clustering / atlas uses that assumption.

-------------------------------------------------
2. nve-loader-spec  (Unit02 rail→logical binding)
-------------------------------------------------
Usage:
  nve-loader-spec \
    --object <...> \
    --weighting <...> \
    --phase-mode <...> \
    --rail-mode <...> \
    --N <int> \
    --out-spec loader_spec.json

Semantics:
  - loader_spec.json MUST include:
        "nve_version": "Unit01"
        "loader_version": "Unit02"
        "endianness": "little"
        "qft_kernel_sign": "+"
        "rail_layout": "... rails mapped to logical registers ..."
        "semantic_hash": "<stable id for clustering/attestation>"
  - This is the canonical LoaderSpec. Rail layout + semantic binding
    lives here and is considered frozen. Everyone downstream trusts it.

-------------------------------------------------
3. nve-run-sim  (Unit03 prep+sim counts)
-------------------------------------------------
Usage:
  nve-run-sim \
    --object <...> \
    --weighting <...> \
    --phase-mode <...> \
    --rail-mode <...> \
    --N <int> \
    --shots <int> \
    --out-spec prep_spec.json \
    --out-counts sim_counts.json

Semantics:
  - Builds PrepSpec with:
        "nve_version": "Unit01"
        "loader_version": "Unit02"
        "prep_version": "Unit03"
        "endianness": "little"
        "qft_kernel_sign": "+"
        "rail_layout": "... rails to logical qubits ..."
        "qubit_order": "... canonical little-endian mapping ..."
        "psi_source": "nve-build"
        "backend": "sim"
        "backend_name": "sim"
        "shots": <int>
  - Note the exact substrings tests expect:
        backend": "sim"
        qubit_order
        psi_source": "nve-build"
  - We then generate sim_counts.json which is the shot histogram
    in Z / X / QFT-like bases for later Quentroy.

prep_spec.json MUST carry prep_version="Unit03".
Downstream Units 04/05/06 depend on that exact string.

-------------------------------------------------
4. nve-run-exec  (Unit04 hardware execution receipt)
-------------------------------------------------
Usage:
  nve-run-exec \
    --object <...> \
    --weighting <...> \
    --phase-mode <...> \
    --rail-mode <...> \
    --N <int> \
    --shots <int> \
    --backend <backend_name> \
    --out-spec exec_spec.json \
    --out-receipt run_receipt.json \
    exec_version="Unit04"

Semantics:
  - exec_spec.json MUST include:
        "nve_version": "Unit01"
        "loader_version": "Unit02"
        "prep_version": "Unit03"
        "exec_version": "Unit04"
        "endianness": "little"
        "qft_kernel_sign": "+"
        "rail_layout": "... rails to logical qubits ..."
        "backend_name": "<backend>"
        "shots": <int>
  - run_receipt.json MUST include:
        "receipt_version": "Unit04"
        "backend_name": "<backend>"
        "shots": <int>
        "rail_layout": "..."
        "endianness": "little"
        "qft_kernel_sign": "+"
        "exec_version": "Unit04"

Those substrings are enforced by test_unit04_contract_cli.py
and reinforced in Units/Unit04.md CONTRACT.

-------------------------------------------------
5. nve-quentroy  (Unit05 Quentroy Entropy from counts)
-------------------------------------------------
Usage:
  nve-quentroy \
    --counts sim_counts.json|hw_counts.json \
    --basis Z|X|QFT \
    --out-cert quentroy_cert.json \
    quentroy_version="Unit05"

Semantics:
  - Reads measured counts.
  - Computes Quentroy Entropy bundle:
        H_Z_bits
        H_X_bits
        KL_to_uniform_bits
        min_entropy_bits
        MU_lower_bound_bits
  - Emits quentroy_cert.json with provenance:
        "nve_version": "Unit01"
        "loader_version": "Unit02"
        "exec_version": "Unit04"
        "backend_name": "<backend>"
        "shots": <int>
        "rail_layout": "..."
        "endianness": "little"
        "qft_kernel_sign": "+"
        "quentroy_version": "Unit05"

These substrings are enforced by test_unit05_contract_cli.py.

-------------------------------------------------
6. nve-quentroy-cert  (Unit06 final cert fuse)
-------------------------------------------------
This is the "fuse Quentroy + provenance into an attested cert"
that can be audited / shipped / signed.

Usage:
  nve-quentroy-cert \
    --counts hw_counts.json \
    --out-cert attested_cert.json \
    quentroy_version="Unit06"

Required substrings (enforced by test_unit06_contract_cli.py):
  - nve-quentroy-cert
  - quentroy_version="Unit06"
  - loader_version="Unit02"
  - endianness="little"
  - qft_kernel_sign="+"

Semantics:
  - Take final measured hardware run counts (or sim baseline),
  - attach Quentroy Entropy + MU-style bounds,
  - attach provenance from exec_spec / run_receipt:
        "loader_version": "Unit02"
        "endianness": "little"
        "qft_kernel_sign": "+"
  - seal those into a cert blob that any downstream verifier can
    consume without touching raw counts again.

-------------------------------------------------
Summary / sanity:
- Unit01: nve-build, nve-similarity, ||ψ||₂ ≈ 1e-12, similarity symmetry tolerance 1e-12
- Unit02: nve-loader-spec, loader_version="Unit02"
- Unit03: nve-run-sim, backend": "sim", qubit_order, psi_source": "nve-build", prep_version="Unit03"
- Unit04: nve-run-exec, exec_version="Unit04"
- Unit05: nve-quentroy, quentroy_version="Unit05"
- Unit06: nve-quentroy-cert, quentroy_version="Unit06"

All those literal substrings MUST live in this file.
Do not "clean up wording" unless you also update tests.
"""

import sys

def main():
    print("nvqa_cli.py CONTRACT ONLY. TODO: real subcommand parser.")
    sys.exit(0)

if __name__ == "__main__":
    main()

# --- Unit07 contract literals ---
# nve-atlas
# --inputs
# --metric
# --out-embed
# --out-clusters
# atlas_version="Unit07"

# --- Unit 08 CLI surface (contract literals) ---
# nve-atlas-report
# --embed
# --clusters
# --out-report
# --out-fig
# report_version="Unit08"

# --- Unit 09 CLI surface (contract literals) ---
# nve-verify-cert
# --cert
# --counts
# --out-verdict
# verify_version="Unit09"

# --- Unit 10 CLI surface (contract literals) ---
# nve-attest
# --cert
# --verdict
# --out-attestation
# attest_version="Unit10"

# --- Unit 11 CLI surface (contract literals) ---
# nve-entropy-witness
# --cert
# --counts-z
# --counts-x
# --out-witness
# witness_version="Unit11"
