# Unit 31 — Provenance Packager

Collects a set of receipts/certificates and packs them into a single immutable archive with a manifest and hashes.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-provenance
- --inputs
- --out-archive
- provenance_version="Unit31"

### Required JSON fields in the archive manifest (verbatim keys must exist)
{
  "provenance_version": "Unit31",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "endianness": "little",
  "qft_kernel_sign": "+",
  "archive_format": "tar.gz",
  "item_count": 0,
  "items": [
    {
      "path": "",
      "bytes": 0,
      "sha256": "",
      "backend_name": "",
      "timestamp_utc": ""
    }
  ],
  "bundle_sha256": "",
  "deterministic_ordering": true
}

### Determinism
- Deterministic bundle ordering (lexicographic by path) for identical inputs.
- Live acquisitions are **not** performed; this is a packaging step only.

### Notes
- `--inputs` may be a text file listing JSON paths or a glob pattern resolved by the CLI.
- `--out-archive` points to the resulting `tar.gz`.
