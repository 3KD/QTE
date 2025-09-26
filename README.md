[![Docs](https://img.shields.io/badge/docs-pages-blue)](https://3KD.github.io/QTE/) [![CI](https://github.com/3KD/QTE/actions/workflows/ci.yml/badge.svg)](https://github.com/3KD/QTE/actions/workflows/ci.yml)

# QTE (Quantum Series Encoder)

Preprint-batch code: polylog analytic continuation (mp/series/auto backends),
Bessel J_n values + vectors, QFT labels with [rail], Maclaurin helpers, cache, CLI.

## Quick start
```bash
pip install -r requirements.txt
./qte_cli.py --nq 6 --mode terms --label 'QFT[sin(2*pi*x); N=64; a=0; b=1; ifft][rail]'
./qte_cli.py --value --label 'polylog(2, 1.1)'

