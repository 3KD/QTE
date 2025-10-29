# Unit 06 — Quentroy Certificate / Attested Witness Blob

Defines the Quentroy certificate format computed from measured counts and metadata.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags that MUST appear literally in nvqa_cli.py:
- nve-quentroy-cert
- --counts
- --basis
- --out-cert
- quentroy_version="Unit06"
- loader_version="Unit02"
- endianness="little"
- qft_kernel_sign="+"

### Required JSON fields (verbatim keys must exist)
{
  "nve_version": "Unit01",
  "loader_version": "Unit02",
  "prep_version": "Unit03",
  "exec_version": "Unit04",
  "quentroy_version": "Unit06",
  "rail_layout": "",
  "qubit_order": "",
  "backend_name": "",
  "shots": 0,
  "H_Z_bits": 0.0,
  "H_X_bits": 0.0,
  "KL_to_uniform_bits": 0.0,
  "min_entropy_bits": 0.0,
  "MU_lower_bound_bits": 0.0,
  "psi_fingerprint": "",
  "semantic_hash": "",
  "timestamp_utc": "",
  "hardware_signature": "",
  "integrity_note": "",
  "counts_source": "",
  "psi_source": "",
  "endianness": "little",
  "qft_kernel_sign": "+"
}

### Behavior (documentation)
- Deterministic for fixed counts.
- Accepts Z/X basis via --basis.
- Emits all fields above.
