# Unit 33 — Public Attestation Publisher

Consumes a Unit 32 verification **report** and emits a signed **attestation** JSON that can be published or archived.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-attest
- --report
- --out-attestation
- attest_version="Unit33"

### Required JSON fields in the attestation (verbatim keys must exist)
{
  "attest_version": "Unit33",
  "verify_version": "Unit32",
  "report_sha256": "",
  "attestation_sha256": "",
  "archive_sha256": "",
  "manifest_sha256": "",
  "item_count": 0,
  "mismatches": 0,
  "verified_true": true,
  "signer": "",
  "signature_alg": "ed25519",
  "signature_b64": "",
  "timestamp_utc": ""
}

### Determinism
- For a fixed input report and signer key, the attestation is deterministic (except `timestamp_utc` if not fixed).

### Notes
- `--report` is the Unit 32 JSON file.
- `--out-attestation` is the attestation JSON containing the fields above.
