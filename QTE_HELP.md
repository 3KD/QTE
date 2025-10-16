# Quick label cheat-sheet

**Constants/series**: π, e, ln(2), ζ(2..5), γ, Catalan, φ, exp(π), 2^√2

**Polylog**: `Li(s,z)` / `polylog(s,z)` — complex `s,z` supported. Backend via `QTE_POLYLOG_BACKEND={auto,mp,series}`.  
`auto` prefers `mpmath` if installed; otherwise uses series (|z|<1) + Euler accel for z∈(-1,0).

**Bessel**: `J0`, `J1`, … ; values like `J2(1.0)`.

**Maclaurin**: `Maclaurin[f(x); x=0.3; r=0.6]` or `Maclaurin[log(1+x); auto_r; real_coeffs]`.

**Transforms**: `QFT[sin(2*pi*x); N=64; a=0; b=1; ifft]` — frequency sample (IFFT) over [a,b] to length N.  
Append **`[rail]`** to any label to map ± amplitudes to even/odd rails.

## CLI examples
```bash
./qte_cli.py --nq 6 --mode terms --label "QFT[sin(2*pi*x); N=64; a=0; b=1; ifft][rail]"
./qte_cli.py --value --label "polylog(2, 0.9+0.2j)" --cache

```
