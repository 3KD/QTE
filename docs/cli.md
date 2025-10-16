# CLI

Run help:
```bash
./qte_cli.py --help
```

## Examples

Value mode (polylog continuation, auto backend):
```bash
QTE_POLYLOG_BACKEND=auto ./qte_cli.py --value --label "polylog(2, 1.1)"
```

QFT with rail mapping (normalized 64-vector):
```bash
./qte_cli.py --nq 6 --mode terms --label "QFT[sin(2*pi*x); N=64; a=0; b=1; ifft][rail]"
```

Bessel value:
```bash
./qte_cli.py --value --label "J2(1.0)"
```

Maclaurin (real coeffs, auto radius):
```bash
./qte_cli.py --nq 4 --mode terms --label "Maclaurin[log(1+x); auto_r; real_coeffs]"
```

Backends:
- `auto` prefers mpmath; else series/Euler accel
- `mp` forces mpmath.polylog
- `series` uses internal series (|z|<1) + Euler accel for z∈(-1,0)

Caching:
```bash
./qte_cli.py --value --label "Li(3,0.9)" --cache
```
```python
import series_encoding as se
se.qte_cache_clear()
```
