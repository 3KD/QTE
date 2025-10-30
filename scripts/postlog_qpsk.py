#!/usr/bin/env python3
import json, sys, csv, math, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "research_summary" / "results_index.csv"

def bits_for_M(M): return max(1, math.ceil(math.log2(M)))
def parse_M_K_sym(name):
    m = re.search(r"_M(\d+)_sym(\d+)_([0-9]+)b", name)
    km = re.search(r"_([0-9]+)b_", name)
    M = int(m.group(1)) if m else None
    sym = int(m.group(2)) if m else None
    K = int(km.group(1)) if km else None
    return M, K, sym

def normalize_counts(counts, width):
    norm = {}
    for k,v in counts.items():
        try:
            ik = int(k); k = format(ik, f"0{width}b")
        except Exception:
            k = str(k).zfill(width)[-width:]
        norm[k] = int(v)
    return norm

def main():
    if len(sys.argv) != 3:
        print("usage: postlog_qpsk.py <artifact.json> <twoq_depth.json>", file=sys.stderr)
        sys.exit(2)
    art = Path(sys.argv[1]); td = Path(sys.argv[2])
    J = json.loads(art.read_text())
    TD = json.loads(td.read_text()) if td.exists() and td.read_text().strip() else {}

    name = art.name
    backend = J.get("backend","")
    shots = J.get("shots","")
    counts = J.get("counts", {})
    M, K, sym = parse_M_K_sym(name)

    if None in (M, K, sym) or shots in ("", None):
        p_star_str = ""
    else:
        width = bits_for_M(M)
        C = normalize_counts(counts, width)
        s = sum(C.values()) or 1
        target = format(sym, f"0{width}b")
        p_star_str = f"{(C.get(target, 0)/s):.6f}"

    depth = str(TD.get("depth",""))
    twoq  = str(TD.get("twoq",""))

    with open(CSV, newline="") as f:
        rdr = csv.DictReader(f); fieldnames = rdr.fieldnames; rows = list(rdr)

    row = {
      "type":"qpsk","timestamp":"", "backend":backend, "shots":shots,
      "file": str(Path("paper_outputs")/name), "job_id": J.get("job_id",""),
      "ramsey_points":"","ramsey_amp":"","visibility":"","R2":"","psi":"","S":"",
      "terms":"","angles_rad":"", "M":M or "", "K":K or "", "symbol":sym or "",
      "p_star": p_star_str, "depth": depth, "twoq": twoq
    }

    idx = next((i for i,r in enumerate(rows) if r.get("file")==row["file"]), None)
    if idx is None:
        rows.append({k:str(v) for k,v in row.items()})
    else:
        for k,v in row.items():
            if str(v) != "": rows[idx][k] = str(v)

    with open(CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows: w.writerow(r)

    print(f"[ok] logged {row['file']}  p*={row['p_star']} depth={depth} twoq={twoq}")

if __name__=="__main__":
    main()
