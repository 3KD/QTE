# Unit 06 — Quentroy Certificate / Attested Witness Blob

## SCOPE / PURPOSE

Unit 06 defines the final attested cert blob we hand to anyone downstream when we claim:
"this quantum(-ish) state ψ was prepared, measured, and its uncertainty fingerprint matches
what we said it would." This is the thing a verifier ingests.

This unit consumes:
- an executed run receipt (Unit04) OR simulator baseline (Unit03),
- the Quentroy Entropy bundle (Unit05),
- the canonical NVE / LoaderSpec provenance (Units 01/02),
and fuses them into a single JSON object we call a Quentroy Certificate.

This cert is what people store, transmit, and sign.
This cert is what auditing / crypto (Units 11, 25+) will work with.
This cert is what we assert in any public claim.

Once Unit 06 is live, nobody should have to look at raw shot counts or hardware receipts
just to verify a run label. They only need this cert blob and access to the canonical
generation rules that were locked in Units 01–05.

This unit is the public witness boundary.

## WHAT IT PRODUCES

We produce `attested_cert.json` by running the CLI surface:

    nve-quentroy-cert \
      --counts hw_counts.json \
      --out-cert attested_cert.json \
      quentroy_version="Unit06"

The output MUST be a single JSON object with (at minimum) the following keys:

    {
      "nve_version": "Unit01",
      "loader_version": "Unit02",
      "prep_version": "Unit03",
      "exec_version": "Unit04",
      "quentroy_version": "Unit06",

      "endianness": "little",
      "qft_kernel_sign": "+",
      "rail_layout": "... canonical rail → logical qubit mapping ...",
      "qubit_order": "... canonical little-endian bit order ...",

      "backend_name": "<backend>",       // e.g. "ibm_xx" or "sim"
      "shots": <int>,                    // integer shot count

      "H_Z_bits": <float>,
      "H_X_bits": <float>,
      "KL_to_uniform_bits": <float>,
      "min_entropy_bits": <float>,
      "MU_lower_bound_bits": <float>,

      "psi_fingerprint": "<stable deterministic hash of ψ>",
      "semantic_hash": "<stable semantic hash from LoaderSpec>",
      "timestamp_utc": "<ISO8601 timestamp>",

      "hardware_signature": "<opaque / may be empty now>",
      "integrity_note": "no tamper detected / etc."
    }

The point:
- `nve_version`, `loader_version`, `prep_version`, `exec_version` prove lineage.
- `endentianness` being "little" and `qft_kernel_sign` being "+" lock global conventions.
- `rail_layout` and `qubit_order` certify how ψ occupied registers.
- `backend_name` and `shots` bind to reality (or sim).
- The Quentroy block (H_Z_bits, H_X_bits, KL_to_uniform_bits, min_entropy_bits,
  MU_lower_bound_bits) is the uncertainty/flatness signature.
- `psi_fingerprint` and `semantic_hash` tie back to the canonical ψ from Unit01 and LoaderSpec from Unit02.
- `hardware_signature` and `integrity_note` prepare the slot where later crypto (Unit 11 / later Units 25+) can attach real auth, MACs, PRF twirls, etc.

Anyone verifying later SHOULD reject the run if:
- `endianness` is not "little"
- `qft_kernel_sign` is not "+"
- `loader_version` != "Unit02"
- `quentroy_version` != "Unit06"
- `exec_version` != "Unit04" (unless explicitly declared "sim"/no hardware, see below)

The only valid exception is if this cert is labeled as derived purely from a sim baseline:
in that case, you can have `"backend_name": "sim"` and `"exec_version": "Unit04_simulated"`,
but the rest of the fields (endianness, qft_kernel_sign, loader_version="Unit02", etc.)
still MUST match. We are not letting simulation drift conventions.

## HOW THIS CONNECTS UPSTREAM

Unit 01 (NVE):
- gave you ψ (normalized vector embedding) deterministically: nve_version="Unit01".
- locked `endianness="little"`, `qft_kernel_sign="+"`, L2 norm ||ψ||₂ ≈ 1e-12.
- gave you `psi_fingerprint` (stable hash) as a reproducible identifier.
- also defined `nve-similarity` and the similarity symmetry tolerance 1e-12 which
  becomes useful for atlas clustering, but that's orthogonal here.

Unit 02 (LoaderSpec):
- mapped rails / sign-split / iq_split into logical qubit registers.
- produced loader_version="Unit02".
- produced `rail_layout`, `semantic_hash`.
- froze how meaning is bound to rail index / qubit index.

Unit 03 (PrepSpec / nve-run-sim):
- prep_version="Unit03".
- added qubit_order, psi_source="nve-build", backend": "sim", etc.
- defined shots and how we intend to sample / measure.

Unit 04 (ExecSpec / nve-run-exec):
- exec_version="Unit04".
- bound backend_name (real hardware), shots, and rail_layout / qubit_order / endianness.
- emitted run_receipt.json ("receipt_version": "Unit04") for the live backend.

Unit 05 (Quentroy bundle / nve-quentroy):
- quentroy_version="Unit05".
- took counts (hardware or sim) and computed:
  H_Z_bits,
  H_X_bits,
  KL_to_uniform_bits,
  min_entropy_bits,
  MU_lower_bound_bits.
- attached provenance like backend_name, shots, rail_layout.

Unit 06 (this unit):
- quentroy_version="Unit06" is now the seal version, NOT "Unit05".
- In Unit 06 we fuse all of it into a single cert blob that a verifier can ingest
  without having direct access to your backend or raw counts.

Why "Unit06" instead of "Unit05" in the final cert?
Because `nve-quentroy` (Unit05) is "compute Quentroy from counts," and now
`nve-quentroy-cert` (Unit06) is "package Quentroy + provenance +
conventions + hashes into an auditable witness."

We want the final top-level cert to say quentroy_version="Unit06"
so you can't fake provenance by taking old Quentroy numbers out of context.


## VERIFIER BEHAVIOR

A verifier that gets attested_cert.json SHOULD do:

1. Check version anchors:
   - assert cert["nve_version"] == "Unit01"
   - assert cert["loader_version"] == "Unit02"
   - assert cert["prep_version"] == "Unit03"
   - assert cert["exec_version"].startswith("Unit04")
   - assert cert["quentroy_version"] == "Unit06"

2. Check global invariants:
   - assert cert["endianness"] == "little"
   - assert cert["qft_kernel_sign"] == "+"
   - assert "rail_layout" in cert
   - assert "qubit_order" in cert
   - assert "backend_name" in cert
   - assert "shots" in cert

3. Check Quentroy fields exist and are floats / sane:
   - H_Z_bits
   - H_X_bits
   - KL_to_uniform_bits
   - min_entropy_bits
   - MU_lower_bound_bits

4. Check ψ identity:
   - recompute ψ from cert["psi_fingerprint"] / ObjectSpec if provided,
     or request canonical ψ from whoever claims authorship.
   - verify the ψ hash matches `psi_fingerprint`.
   - if mismatch: reject.

5. Optionally check cryptographic seal:
   - if hardware_signature is not empty and you know how to verify it,
     verify it.
   - if it's empty, you still CAN accept the cert as a "lab claim," but
     it's not yet cryptographically anchored.

In other words: the Unit 06 cert is the minimum standalone evidence that
should ever be allowed to leave the lab. Anything less than this is not auditable.

## CONTRACT (DO NOT CHANGE)

pytest will grep this exact block. Do not edit these substrings unless you also
update tests and bump versions. This is law.

CLI surface string we promise exists in nvqa_cli.py:

    nve-quentroy-cert \
      --counts hw_counts.json \
      --out-cert attested_cert.json \
      quentroy_version="Unit06"

Required substrings in both this file AND nvqa_cli.py:

    nve-quentroy-cert
    quentroy_version="Unit06"
    loader_version="Unit02"
    endianness="little"
    qft_kernel_sign="+"

Required fields inside attested_cert.json (verifier MUST see these):

    "nve_version": "Unit01",
    "loader_version": "Unit02",
    "prep_version": "Unit03",
    "exec_version": "Unit04",
    "quentroy_version": "Unit06",

    "endianness": "little",
    "qft_kernel_sign": "+",
    "rail_layout": "...",
    "qubit_order": "...",
    "backend_name": "<backend>",
    "shots": <int>,

    "H_Z_bits": <float>,
    "H_X_bits": <float>,
    "KL_to_uniform_bits": <float>,
    "min_entropy_bits": <float>,
    "MU_lower_bound_bits": <float>,

    "psi_fingerprint": "<stable deterministic hash of ψ>",
    "semantic_hash": "<stable semantic hash>",
    "timestamp_utc": "<ISO8601 timestamp>",

    "hardware_signature": "<opaque or empty>",
    "integrity_note": "..."

If any of those required substrings disappear from Unit06.md or nvqa_cli.py,
pytest should (and will) fail, and we don't push.
