#!/usr/bin/env python3
import re, json, pathlib

p = pathlib.Path("QTEGUI.py")
s = p.read_text(encoding="utf-8")

report = {"file": str(p), "lines": s.count("\n")+1, "problems": [], "notes": []}

# 1) optional imports block
if "entropy_lab" not in s:
    report["notes"].append("entropy_lab optional import not referenced—GUI may lack entropy pane toggle")
if re.search(r'^\s*try:\s*\n\s*import\s+entropy_lab', s, flags=re.M) and "except" not in s.split("\n", 200)[:200]:
    report["problems"].append("suspicious try without except near header")

# 2) SUGGESTED_LABELS sanity
if "SUGGESTED_LABELS" not in s:
    report["problems"].append("SUGGESTED_LABELS missing")
if re.search(r'\]\s*"\]\]\]"', s):
    report["problems"].append("SUGGESTED_LABELS looks corrupted")

# 3) FFT API usage (expect dict access like out["P"])
if "compute_fft_spectrum_from_amplitudes" in s and '["P"]' not in s:
    report["notes"].append("Verify GUI treats FFT output as dict (P, dc, entropy_bits, flatness).")

# 4) Schmidt purity with NumPy arrays (not DensityMatrix @ DensityMatrix)
if re.search(r'DensityMatrix', s) and re.search(r'@\s*DensityMatrix|DensityMatrix\s*@', s):
    report["problems"].append("uses @ with DensityMatrix (purity should be with NumPy arrays)")

# 5) caret support (^)
if re.search(r'sin\(x\)\^2', s) and "**" not in s:
    report["notes"].append("caret '^' found; ensure replacement to '**' before eval")

# 6) entropy certificate exposure
if "entropy_certificate_from_amplitudes" not in s:
    report["notes"].append("GUI may not expose entropy certificates yet.")

# 7) eval guard
if "eval(" in s:
    report["notes"].append("eval() detected; confirm sandboxed numpy namespace only")

# 8) TODO/FIXME triage
if re.search(r'\b(TODO|FIXME)\b', s):
    report["notes"].append("TODO/FIXME present; triage outstanding items")

pathlib.Path("docs/QTEGUI_AUDIT.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
