# Unit 32 — Bundle Verifier

Verifies a provenance archive (see Unit 31), recomputes file hashes, checks manifest integrity, and emits a verification report.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-verify
- --archive
- --out-report
- verify_version="Unit32"

### Required JSON fields in the verification report (verbatim keys must exist)
{
  "verify_version": "Unit32",
  "provenance_version": "Unit31",
  "archive_format": "tar.gz",
  "archive_path": "",
  "archive_sha256": "",
  "manifest_sha256": "",
  "item_count": 0,
  "items": [
    {
      "path": "",
      "expected_sha256": "",
      "actual_sha256": "",
      "bytes": 0,
      "status": "ok"
    }
  ],
  "mismatches": 0,
  "verified_true": true,
  "timestamp_utc": ""
}

### Determinism
- For a fixed input archive, report contents are deterministic.
- No live backend calls are made in this unit.

### Notes
- `--archive` points to a `.tar.gz` created by Unit 31.
- `--out-report` is a JSON file with the fields above.
