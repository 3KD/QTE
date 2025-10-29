# Unit 10 — Attestation & Provenance Chain

Generates a deterministic **attestation** JSON that binds together the Quentroy certificate (Unit 06), its verification result (Unit 09), and environment/provenance facts (source commit, Python/Qiskit versions, backend properties, etc.).

## CONTRACT (DO NOT CHANGE)
CLI surface that MUST appear literally in nvqa_cli.py:
- nve-attest
- --cert
- --verdict
- --out-attestation
- attest_version="Unit10"

### Required inputs
- `--cert` : path to Quentroy certificate JSON (Unit 06 output)
- `--verdict` : path to verification VERDICT JSON (Unit 09 output)
- `--out-attestation` : path to write deterministic attestation JSON

### Required ATTESTATION JSON fields (verbatim keys must exist)
{
  "attest_version": "Unit10",
  "cert_path": "",
  "verdict_path": "",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "quentroy_version": "Unit06",
  "verify_version": "Unit09",
  "endianness": "little",
  "qft_kernel_sign": "+",
  "git_commit": "",
  "python_version": "",
  "qiskit_version": "",
  "backend_name": "",
  "backend_properties_digest": "",
  "receipt_chain": {
    "exec_receipt_sha256": "",
    "counts_sha256": "",
    "cert_sha256": "",
    "verdict_sha256": ""
  },
  "manifest_sha256": "",
  "passed": true,
  "determinism_note": "Fixed ordering and canonical JSON ensures bit-for-bit stability for same inputs."
}

### Determinism
- For fixed inputs and environment snapshot, attestation is **bit-for-bit stable** (canonical JSON dump, sorted keys, fixed float formatting).
