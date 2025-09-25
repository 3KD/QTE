# Labels reference

QTE label grammar with quick examples for `qte_cli.py`.

## Constants / series
- `π`, `e`, `ln(2)`, `ζ(k)` for k=2..5, `γ` (Euler–Mascheroni), Catalan, `φ`, `exp(π)`, `2^√2`.

Examples:
~~~bash
./qte_cli.py --value --label "ζ(3)"
./qte_cli.py --nq 8 --mode terms --label "π"
~~~

## Polylog
- Syntax: `Li(s,z)` / `polylog(s, z)` (complex `s,z` supported).
- Backends: `--backend {auto,series,mp}` or env `QTE_POLYLOG_BACKEND`.
- Principal branch used near the real axis.

Examples:
~~~bash
QTE_POLYLOG_BACKEND=auto ./qte_cli.py --value --label "polylog(2, 1.1)"
./qte_cli.py --value --label "Li(3, 0.9)" --cache
~~~

## Bessel
- Cylindrical Bessel J_n: `J0`, `J1`, `J2`, …

Example:
~~~bash
./qte_cli.py --value --label "J2(1.0)"
~~~

## Maclaurin
- `Maclaurin[f(x); x=<point>; r=<radius>]` with helpers `auto_r`, `real_coeffs`.

Examples:
~~~bash
./qte_cli.py --nq 4 --mode terms --label "Maclaurin[log(1+x); auto_r; real_coeffs]"
./qte_cli.py --nq 8 --mode terms --label "Maclaurin[exp(x^2); r=0.7]"
~~~

## Transforms (QFT)
- `QFT[f(x); N=<pow2>; a=<start>; b=<end>; ifft]` — sample on [a,b], IFFT to register.

Example:
~~~bash
./qte_cli.py --nq 6 --mode terms --label "QFT[sin(2*pi*x); N=64; a=0; b=1; ifft]"
~~~

## Rail mapping
- Append `[rail]` to map plus/minus amplitudes to even/odd rails.

Example:
~~~bash
./qte_cli.py --nq 6 --mode terms --label "QFT[sin(2*pi*x); N=64; a=0; b=1; ifft][rail]"
~~~

## Caching
- Enable with `--cache` or `QTE_CACHE=1`.
- Clear at runtime:
~~~python
import series_encoding as se
se.qte_cache_clear()
~~~
