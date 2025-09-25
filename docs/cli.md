# CLI

Run help:


## Examples

Value mode (polylog continuation, auto backend):


QFT with rail mapping (normalized 64-vector):


Bessel value:


Maclaurin (real coeffs, auto radius):


Backends:
- `auto` prefers mpmath; else series/Euler accel
- `mp` forces mpmath.polylog
- `series` uses internal series (|z|<1) + Euler accel for z∈(-1,0)

Caching:

