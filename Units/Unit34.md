# Unit 34 — Attestation Registry Sync

Consumes a Unit 33 attestation and updates a **registry index** (JSON), producing a new registry file and optional manifest delta.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-regsync
- --attestation
- --out-reg
- regsync_version="Unit34"

### Required JSON fields in the registry output (verbatim keys must exist)
{
  "regsync_version": "Unit34",
  "attest_version": "Unit33",
  "registry_sha256": "",
  "attestation_sha256": "",
  "previous_registry_sha256": "",
  "entries": [],
  "entry_count": 0,
  "timestamp_utc": "",
  "integrity_note": ""
}

### Determinism
- For a fixed prior registry + attestation, the new registry content (excluding `timestamp_utc`) is deterministic.

### Notes
- `--attestation` is the Unit 33 JSON.
- `--out-reg` is the resulting registry JSON written to disk.
