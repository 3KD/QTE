#!/usr/bin/env python3
# Sessionless IBM Runtime runner (Torino) using SamplerV2(mode=backend).
# No Session, works on open-plan. Builds your PRF-driven phase-mix circuit.

import argparse, json, sys, math, datetime
from pathlib import Path

# make project root importable so qe_crypto resolves if run from tools/
_PROJ = Path(__file__).resolve().parents[1]
if str(_PROJ) not in sys.path:
    sys.path.insert(0, str(_PROJ))

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService
try:
    from qiskit_ibm_runtime import SamplerV2 as Sampler
except Exception:  # pragma: no cover
    # If this ever triggers, your runtime is too old for sessionless mode.
    raise RuntimeError("Need qiskit-ibm-runtime with SamplerV2.")

from qe_crypto.primitives import prf_bits

_ALIAS = {"torino": "ibm_torino", "ibm_torino": "ibm_torino"}

def _bits_to_angle(bits: int, t_bits: int) -> float:
    return (bits / float(1 << t_bits)) * (2.0 * math.pi)

def _angles_from_prf(key: bytes, nonce: bytes, n: int, rounds: int, t_bits: int):
    angles = []
    ctr = 0
    for _ in range(rounds):
        layer = []
        for q in range(n):
            b = prf_bits(key, nonce, ctr, t_bits)
            layer.append(_bits_to_angle(b, t_bits))
            ctr += 1
        angles.append(layer)
    return angles

def build_circuit(n: int, rounds: int, t_bits: int, *, key: bytes, nonce: bytes, basis: str):
    qc = QuantumCircuit(n, n)
    for layer in _angles_from_prf(key, nonce, n, rounds, t_bits):
        qc.h(range(n))
        for q, theta in enumerate(layer):
            qc.rz(theta, q)
        qc.h(range(n))
    if basis.upper() == "X":
        qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc

def _counts_from_quasi(quasi, shots: int, n_hint: int = None):
    # quasi is a dict[int|str->p] or a list with [dict]
    if isinstance(quasi, list) and quasi:
        dist = quasi[0]
    elif isinstance(quasi, dict):
        dist = quasi
    else:
        raise RuntimeError("Unsupported Sampler result format.")
    keys = list(dist.keys())
    nbits = n_hint
    if nbits is None and keys:
        k0 = keys[0]
        nbits = k0.bit_length() if isinstance(k0, int) else len(str(k0))
    nbits = nbits or 1
    counts = {}
    for k, p in dist.items():
        bitstr = format(k, f"0{nbits}b") if isinstance(k, int) else str(k)
        c = int(round(float(p) * shots))
        if c > 0:
            counts[bitstr] = counts.get(bitstr, 0) + c
    # normalize to shots (rounding)
    tot = sum(counts.values())
    if tot and tot != shots:
        for b in list(counts):
            counts[b] = int(round(counts[b] * shots / tot))
    return counts

def _metrics_from_counts(counts, n):
    # quick entropy-ish proxies to sanity check randomness
    shots = max(1, sum(counts.values()))
    probs = np.array([c/shots for c in counts.values()], dtype=float)
    # KL to uniform over observed support (rough proxy)
    if len(probs):
        kl = float(np.sum(probs * np.log((probs + 1e-12) / (1.0/len(probs)))))
    else:
        kl = float("nan")
    H = float(-np.sum(probs * np.log2(probs + 1e-12)))
    maxH = float(n)  # bits
    flat = float(np.max(probs) - np.min(probs)) if len(probs) else float("nan")
    return {"entropy_bits": H, "kl_to_uniform": kl, "flatness": flat}

def main():
    ap = argparse.ArgumentParser(description="Run IND-CPA proxy on IBM Torino (sessionless).")
    ap.add_argument("--backend", required=True, help="torino or ibm_torino")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--t_bits", type=int, default=12)
    ap.add_argument("--shots", type=int, default=128)
    ap.add_argument("--basis", choices=["Z","X","z","x"], default="X")
    ap.add_argument("--nonce", help="hex nonce (optional)")
    ap.add_argument("--key", help="hex key (optional, 32 bytes recommended)")
    ap.add_argument("--instance", help="IBM Cloud instance hub/group/project", default=None)
    ap.add_argument("--out", default=str(_PROJ/"docs/results/ibm_torino_run.json"))
    args = ap.parse_args()

    service = QiskitRuntimeService(instance=args.instance) if args.instance else QiskitRuntimeService()
    bname = _ALIAS.get(args.backend, args.backend)
    backend = service.backend(bname)  # backend OBJECT (no session)

    key = bytes.fromhex(args.key) if args.key else b"K"*32
    nonce = bytes.fromhex(args.nonce) if args.nonce else b"N"*12

    qc = build_circuit(args.n, args.rounds, args.t_bits, key=key, nonce=nonce, basis=args.basis)
    tqc = transpile(qc, backend=backend)

    # SamplerV2: pass backend via 'mode'
    sampler = Sampler(mode=backend)
    job = sampler.run([tqc], shots=args.shots)
    res = job.result()

    # Try common fields
    quasi = None
    if hasattr(res, "quasi_dists"): quasi = res.quasi_dists
    elif isinstance(res, dict) and "quasi_dists" in res: quasi = res["quasi_dists"]
    else: 
        # last resort: some builds use 'dist' or 'data' dict
        if hasattr(res, "data") and isinstance(res.data, dict) and "quasi_dists" in res.data:
            quasi = res.data["quasi_dists"]
        else:
            raise RuntimeError("SamplerV2 result missing quasi_dists")

    counts = _counts_from_quasi(quasi, args.shots, qc.num_clbits)
    metrics = _metrics_from_counts(counts, args.n)

    record = {
        "time_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "backend": backend.name,
        "params": {"n": args.n, "rounds": args.rounds, "t_bits": args.t_bits, "shots": args.shots, "basis": args.basis},
        "job_id": getattr(job, "job_id", lambda: None)(),
        "counts": counts,
        "metrics": metrics,
    }

    outp = Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"backend": record["backend"], **record["metrics"], "out": str(outp), "job_id": record["job_id"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
