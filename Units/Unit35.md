# Unit 35 — Registry Integrity Verify

Validates the Unit 34 registry JSON: structure, required fields, internal hashing (sha256), and continuity vs previous registry.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-regverify
- --reg
- --out-report
- regverify_version="Unit35"

### Required JSON fields in the verification report (verbatim keys must exist)
{
  "regverify_version": "Unit35",
  "regsync_version": "Unit34",
  "registry_sha256": "",
  "previous_registry_sha256": "",
  "entry_count": 0,
  "continuity_ok": true,
  "hash_ok": true,
  "structure_ok": true,
  "issues": [],
  "timestamp_utc": ""
}

### Determinism
- For a fixed registry input, the verification booleans and `issues` are deterministic (timestamp excluded).

### Notes
- `--reg` is the Unit 34 registry JSON from Unit 34.
- `--out-report` is a JSON report written to disk.
