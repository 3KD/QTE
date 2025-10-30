# Unit 37 — Registry Diff Auditor

Compares two registry snapshots (e.g., from Units 34–36 flows) and emits a deterministic JSON diff including added, removed, and modified entries with hash evidence.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-regdiff
- --old
- --new
- --out-diff
- regdiff_version="Unit37"

### Required JSON fields in the diff output (verbatim keys must exist)
{
  "regdiff_version": "Unit37",
  "old_registry_sha256": "",
  "new_registry_sha256": "",
  "added_keys": [],
  "removed_keys": [],
  "modified_keys": [],
  "modified_detail": {},
  "timestamp_utc": ""
}

### Determinism
- Deterministic given identical inputs; only `timestamp_utc` varies.
