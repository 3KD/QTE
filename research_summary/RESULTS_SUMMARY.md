# Results Summary
_Generated: 2025-10-14T23:52:16_

## Inventory
- **bessel**: 1 files
- **chsh**: 2 files
- **ergodic**: 2 files
- **other**: 5 files
- **qpsk**: 11 files
- **ramsey**: 2 files
- **signaling**: 1 files
- **topo**: 1 files
- **vib_spec**: 1 files

## Ramsey (single-qubit)
| file | backend | shots | points | visibility | R² | amp |
|---|---:|---:|---:|---:|---:|---:|
| `ramsey_ibm_torino_256s.json` | ibm_torino | 256 | None |  |  |  |
| `ramsey_ibm_torino_256s_fit.json` | ibm_torino | 256 | None | 0.752 | 0.990 |  |

## CHSH (Bell test)
| file | backend | shots | S |
|---|---:|---:|---:|
| `chsh2_ibm_torino_256s.json` | ibm_torino | 256 | -0.016 |
| `chsh_ibm_torino_256s.json` | ibm_torino | 256 | -0.109 |

## QPSK / Indexer
| file | backend | K | M | shots | p* | depth | twoq |
|---|---|---:|---:|---:|---:|---:|---:|
| `qpsk_ibm_torino_M256_sym145_8b_512s_d3kquthfk6qs73e69g10.json` | ibm_torino | 8 | 256 | 512 | - | None | None |
| `qpsk_ibm_torino_M256_sym145_8b_512s_d3kr09odd19c7396bcng.json` | ibm_torino | 8 | 256 | 512 | - | None | None |
| `qpsk_ibm_torino_M256_sym145_8b_512s_d3ksg203qtks738borl0.json` | ibm_torino | 8 | 256 | 512 | - | None | None |
| `qpsk_ibm_torino_M128_sym73_7b_512s_d3libb03qtks738cedmg.json` | ibm_torino | 7 | 128 | 512 | 0.0195 | 232 | 82 |
| `qpsk_ibm_torino_M1024_sym145_10b_512s_d3k9ri9fk6qs73emaj5g.json` | ibm_torino | 10 | 1024 | 512 | - | None | None |
| `qpsk_ibm_torino_M128_sym73_7b_256s_d3lf0dodd19c7396v5eg.json` | ibm_torino | 7 | 128 | 256 | - | None | None |
| `qpsk_ibm_torino_M256_sym145_8b_512s_d3k9gohfk6qs73ema9eg.json` | ibm_torino | 8 | 256 | 512 | - | None | None |
| `qpsk_ibm_torino_M256_sym145_8b_512s_d3kkohodd19c739654rg.json` | ibm_torino | 8 | 256 | 512 | - | None | None |
| `qpsk_ibm_torino_M32_sym10_5b_128s_d3k9giodd19c738g12og.json` | ibm_torino | 5 | 32 | 128 | - | None | None |
| `qpsk_ibm_torino_M32_sym10_5b_128s_d3kkod03qtks738bh030.json` | ibm_torino | 5 | 32 | 128 | - | None | None |
| `qpsk_ibm_torino_M64_sym19_6b_256s_d3lf0b83qtks738cb73g.json` | ibm_torino | 6 | 64 | 256 | - | None | None |

## Other
- `pi_ramanujan_terms_n8_sh4096_aer_local_fallback.json` — backend=aer_local_fallback shots=4096
- `pi_ramanujan_terms_n8_sh4096_ibm_torino.json` — backend=ibm_torino shots=4096
- `entanglement_smoke.json` — backend=None shots=None
- `entangle_pi_zeta_ibm_torino_n4_sh512_d3ksbrpfk6qs73e6athg.json` — backend=ibm_torino shots=512
- `entangle_pi_zeta_ibm_torino_n4_sh512_d3ksg5g3qtks738borp0.json` — backend=ibm_torino shots=512
- `qte_demo_bessel_4.json` — backend=aer_local_fallback shots=None
- `qte_demo_ergodic_1.json` — backend=ibm_torino shots=512
- `qte_demo_signaling_5.json` — backend=ibm_torino shots=256
- `qte_demo_topo_2.json` — backend=ibm_torino shots=1024
- `qte_demo_vib_spec_3.json` — backend=aer_local_fallback shots=None
- `ergodic_ibm_torino_64N_256s_demo123.json` — backend=ibm_torino shots=256