#!/usr/bin/env python3
import argparse, json, datetime, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qe_crypto.phase_mix import avg_state_over_nonces, trace_distance_to_maxmix
from qe_crypto.shadow_dist import shadow_score_from_rho

try:
    from tools import write_claims as _wc
    _HAS_CLAIMS = True
except Exception:
    _HAS_CLAIMS = False

def _rand_state(n, seed=42):
    rng = np.random.default_rng(seed)
    d = 2**n
    v = rng.normal(size=d) + 1j*rng.normal(size=d)
    return v / np.linalg.norm(v)

def main():
    ap = argparse.ArgumentParser(description="IND-CPA Monte Carlo + shadow score")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--samples", type=int, default=192)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--t_bits", type=int, default=12)
    ap.add_argument("--eps_target", type=float, default=0.20, help="trace distance target")
    ap.add_argument("--m_shadow", type=int, default=256)
    ap.add_argument("--seed", type=int, default=123)
    ap.add_argument("--out", default="docs/results/ind_cpa_run.json")
    args = ap.parse_args()

    psi = _rand_state(args.n, seed=args.seed)
    master_key = b"K"*32
    rho_enc = avg_state_over_nonces(psi, master_key,
                                    num_samples=args.samples,
                                    t_bits=args.t_bits, rounds=args.rounds,
                                    seed=args.seed+1)

    td = trace_distance_to_maxmix(rho_enc)
    s  = shadow_score_from_rho(rho_enc, m=args.m_shadow, seed=args.seed+2)

    meta = {
        "time_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "params": {
            "n": args.n, "samples": args.samples, "rounds": args.rounds,
            "t_bits": args.t_bits, "m_shadow": args.m_shadow, "seed": args.seed
        },
        "metrics": {"trace_distance": td, "shadow_score": s},
        "targets": {"epsilon": args.eps_target}
    }

    outp = Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))

    if _HAS_CLAIMS:
        _wc.write(path="docs/results/claims.md",
                  eps=str(args.eps_target), fmin_chip="0.99", fmin_metro="0.90")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
