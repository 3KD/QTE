# Unit 36 — Registry Rollback Reconstructor

Restores an earlier Unit 34 registry state using recorded hashes and backups, enabling deterministic replays of historical registry snapshots.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-regrollback
- --target-hash
- --out-reg
- regrollback_version="Unit36"

### Required JSON fields in the rollback output (verbatim keys must exist)
{
  "regrollback_version": "Unit36",
  "regverify_version": "Unit35",
  "restored_registry_sha256": "",
  "target_registry_sha256": "",
  "rollback_success": true,
  "entries_restored": 0,
  "timestamp_utc": "",
  "note": ""
}

### Determinism
- Deterministic when given identical target hash and backup set.
- `timestamp_utc` and `note` may vary.

### Notes
- `--target-hash` identifies the registry version to restore.
- `--out-reg` writes the reconstructed registry to disk.
