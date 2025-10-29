#!/usr/bin/env python3
"""
nvqa_cli.py — Unit 01 primary CLI

Required subcommands (future TODO):

1. nve-build:
   --object "Maclaurin[sin(x)]"
   --weighting egf
   --phase-mode full_complex
   --rail-mode iq_split
   --N 64
   --out-psi <.npy>
   --out-meta <.json>

Must:
- run package_nve(...)
- save ψ with ||ψ||₂≈1 within 1e-12
- save metadata including:
    endianness="little"
    qft_kernel_sign="+"
    nve_version="Unit01"
- refuse to proceed if NaN/Inf or norm=0

2. nve-similarity:
   --a <.npy>
   --b <.npy>
   --metric cosine
Return symmetric similarity (abs difference ≤1e-12 if you swap a/b).
"""

import sys

def main():
    print("TODO Unit01 nvqa_cli.py: implement nve-build / nve-similarity according to README_Unit01.md contract")
    sys.exit(0)

if __name__ == "__main__":
    main()

# Unit 02 TODO:
# subcommand: nve-loader-spec
# Flags:
#   --object <...>
#   --weighting <...>
#   --phase-mode <...>
#   --rail-mode <...>
#   --N <int>
#   --out-spec <path>
#
# Behavior:
#   1. build NVE bundle (Unit 01)
#   2. build LoaderSpec via loader_layout.build_loader_spec (Unit 02)
#   3. write JSON via loader_layout.loader_spec_to_json

# Unit 03 TODO:
# subcommand: nve-run-sim
# Flags:
#   --object <...>
#   --weighting <...>
#   --phase-mode <...>
#   --rail-mode <...>
#   --N <int>
#   --shots <int>
#   --out-spec <prep_spec.json>
#   --out-counts <sim_result.json>
#
# Behavior:
#   1. build NVE bundle (Unit 01)
#   2. build LoaderSpec (Unit 02)
#   3. build PrepSpec + simulate counts (Unit 03)
#   4. write both JSON artifacts

# Unit 04 TODO:
# subcommand: nve-run-exec
# Flags: --object --weighting --phase-mode --rail-mode --N --shots --backend --out-spec --out-receipt
# Behavior:
#   1. build NVE bundle (Unit 01)
#   2. build LoaderSpec (Unit 02)
#   3. build PrepSpec (Unit 03)
#   4. build ExecSpec + run backend (Unit 04)
#   5. write ExecSpec + RunReceipt JSON
