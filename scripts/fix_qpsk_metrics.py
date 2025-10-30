#!/usr/bin/env python3
import csv, json, math, os, re, sys, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "research_summary" / "results_index.csv"
OUT_CSV = ROOT / "research_summary" / "results_index.fixed.csv"
PO_DIR = ROOT / "paper_outputs"

def bits_for_M(M: int) -> int:
    return max(1, math.ceil(math.log2(M)))

def parse_M_K_sym_from_name(name: str):
    m = re.search(r"_M(\d+)_sym(\d+)_([0-9]+)b", name)
    k_m = re.search(r"_([0-9]+)b_", name)
    M = int(m.group(1)) if m else None
    sym = int(m.group(2)) if m else None
    K = int(k_m.group(1)) if k_m else None
    return M, K, sym

def normalize_counts(counts, width):
    norm = {}
    for k, v in counts.items():
        try:
            ik = int(k)
            bs = format(ik, f"0{width}b")
        except Exception:
            bs = str(k)
            if len(bs) < width: bs = bs.zfill(width)
            elif len(bs) > width: bs = bs[-width:]
        norm[bs] = int(v)
    return norm

def main():
    if not CSV_PATH.exists():
        print(f"[err] CSV not found: {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    with open(CSV_PATH, newline="") as f:
        rows = list(csv.DictReader(f))
    by_file = {r.get("file",""): i for i, r in enumerate(rows)}

    changed = skipped = 0
    for jf in PO_DIR.glob("qpsk_*.json"):
        try:
            J = json.loads(jf.read_text())
        except Exception as e:
            print(f"[warn] bad json {jf}: {e}", file=sys.stderr)
            continue
        file_key = str(Path("paper_outputs") / jf.name)
        if file_key not in by_file: continue

        shots = J.get("shots")
        counts = J.get("counts")
        M, K, sym = parse_M_K_sym_from_name(jf.name)
        if shots is None or counts is None or M is None or sym is None:
            skipped += 1
            continue

        width = bits_for_M(M)
        C = normalize_counts(counts, width)
        s = sum(C.values()) or 1
        target = format(sym, f"0{width}b")
        p_star = C.get(target, 0) / s

        row = rows[by_file[file_key]]
        row["p_star"] = f"{p_star:.6f}"
        changed += 1

    if changed == 0:
        print("[info] No rows updated (no counts found or nothing to change).")
        sys.exit(0)

    fieldnames = list(rows[0].keys())
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows: w.writerow(r)
    shutil.move(OUT_CSV, CSV_PATH)
    print(f"[ok] Updated {changed} rows; skipped {skipped}. Wrote back to {CSV_PATH}")

if __name__ == "__main__":
    main()
