#!/usr/bin/env python3
import itertools, json, csv, datetime
from pathlib import Path
import numpy as np
from qe_crypto.phase_mix import avg_state_over_nonces, trace_distance_to_maxmix
from qe_crypto.shadow_dist import shadow_score_from_rho

def _rand_state(n, seed=7):
    rng = np.random.default_rng(seed)
    d = 2**n
    v = rng.normal(size=d) + 1j*rng.normal(size=d)
    return v / np.linalg.norm(v)

def main():
    n=4; seed=7
    rounds_list  = [1,2,3]
    t_bits_list  = [8,10,12,14]
    samples_list = [96,192,384]
    eps_targets  = [0.2, 0.1]

    psi = _rand_state(n, seed=seed)
    master_key = b"K"*32
    rows = []
    for r, t, s in itertools.product(rounds_list, t_bits_list, samples_list):
        rho = avg_state_over_nonces(psi, master_key,
                                    num_samples=s, t_bits=t, rounds=r, seed=seed+11)
        td = trace_distance_to_maxmix(rho)
        sh = shadow_score_from_rho(rho, m=256, seed=seed+13)
        rows.append({"rounds": r, "t_bits": t, "samples": s,
                     "trace_distance": td, "shadow_score": sh})

    outdir = Path("docs/results"); outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.utcnow().isoformat()+"Z"

    # CSV
    csv_path = outdir / "sweep_ind_cpa.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    # Markdown table
    md_path = outdir / "sweep_ind_cpa.md"
    with md_path.open("w") as f:
        f.write(f"# IND-CPA Sweep (generated {ts})\n\n")
        f.write("| rounds | t_bits | samples | trace_distance | shadow_score |\n|---:|---:|---:|---:|---:|\n")
        for row in sorted(rows, key=lambda d:(d["rounds"], d["t_bits"], d["samples"])):
            f.write(f"| {row['rounds']} | {row['t_bits']} | {row['samples']} | {row['trace_distance']:.6f} | {row['shadow_score']:.6f} |\n")
        f.write("\nTargets: ε ∈ "+str(eps_targets)+" (trace distance).\n")

    # JSON
    (outdir/"sweep_ind_cpa.json").write_text(json.dumps({"time_utc": ts, "rows": rows}, indent=2)+"\n")

    print(json.dumps({"csv": str(csv_path), "md": str(md_path), "count": len(rows)}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
