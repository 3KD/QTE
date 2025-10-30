# Unit 30 — Hardware Cross-Run Consistency Auditor

Compares multiple receipts/certificates across **different hardware backends** to quantify consistency. Emits a deterministic JSON report.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in `nvqa_cli.py`:
- nve-consistency
- --inputs
- --out-report
- consistency_version="Unit30"

### Required JSON fields (verbatim keys must exist)
{
  "consistency_version": "Unit30",
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "endianness": "little",
  "qft_kernel_sign": "+",
  "manifest_path": "",
  "N_pairs": 0,
  "backend_pairs": [],
  "metric": "hellinger",
  "pairwise_stats": {
    "hellinger_mean": 0.0,
    "hellinger_max": 0.0,
    "bhattacharyya_mean": 0.0,
    "kl_bits_mean": 0.0,
    "ks_pvalue_min": 1.0
  },
  "inconsistency_alert": false,
  "threshold_note": "cosmetic guidance only"
}

### Determinism
- Deterministic given the same ordered input set and parameters.
- Live acquisitions are **opt-in** via `NVQA_LIVE=1`; this unit only analyzes existing artifacts.

### Notes
- `--inputs` accepts a text manifest of JSON paths or a glob that resolves to receipts; pairs are formed by backend name.
- Emit one consistency report JSON at `--out-report`.
