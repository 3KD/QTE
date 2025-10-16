
import csv, math, cmath, numpy as np
from series_encoding import compute_series_value

items = [
    ("π", None), ("e", None), ("ln(2)", None),
    ("ζ(2)", None), ("ζ(3)", 5000), ("ζ(4)", None), ("ζ(5)", 15000),
    ("γ", 50000), ("Catalan", 20000), ("φ", None),
    ("exp(π)", None), ("2^√2", None),
    ("Liouville", 6), ("Champernowne10", 32),
    ("Li(2,0.5)", 4000), ("polylog(3, 0.5)", 4000),
    ("J0(1.0)", 32),
    ("Maclaurin[sin(x); x=0.3]", None),
    ("Maclaurin[log(1+x); x=0.3]", None),
    ("Maclaurin[exp(x^2); x=0.4]", None),
]

def realish(z):
    try:
        v = complex(z)
        if abs(v.imag) < 1e-12:
            return float(v.real)
        return v
    except Exception:
        return z

rows = []
for lbl, terms in items:
    try:
        val = compute_series_value(lbl, terms=terms) if terms is not None else compute_series_value(lbl)
        rows.append((lbl, realish(val)))
        print("OK", lbl, rows[-1][1])
    except Exception as e:
        rows.append((lbl, f"ERR: {e}"))
        print("ERR", lbl, e)

with open("paper_outputs/special_values.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["label","value"]); w.writerows(rows)
print("TABLE_OK paper_outputs/special_values.csv")
