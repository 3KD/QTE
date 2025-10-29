\
#!/usr/bin/env python3
# Sessionless IBM Runtime runner for our IND-CPA proxy on Torino (or any backend).

import argparse, json, sys, math, datetime
from pathlib import Path

# Ensure project root is importable so qe_crypto is found when run from tools/
_PROJ_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJ_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJ_ROOT))

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService

# Prefer SamplerV2; fall back to classic Sampler (which may require Session)
try:
    from qiskit_ibm_runtime import SamplerV2 as Sampler  # modern, sessionless-capable
except Exception:  # pragma: no cover
    from qiskit_ibm_runtime import Sampler               # older

from qe_crypto.primitives import prf_bits

_BACKEND_ALIAS = {"torino": "ibm_torino", "ibm_torino": "ibm_torino"}

def _bits_to_angle(bits: int, t_bits: int) -> float:
    return (bits / float(1 << t_bits)) * (2.0 * math.pi)

def _angles_from_prf(key: bytes, nonce: bytes, n: int, rounds: int, t_bits: int):
    angles = []; ctr = 0
    for _ in range(rounds):
        layer = []
        for q in range(n):
            b = prf_bits(key, nonce, ctr, t_bits)
            layer.append(_bits_to_angle(b, t_bits))
            ctr += 1
        angles.append(layer)
    return angles

def build_circuit(n: int, rounds: int, t_bits: int, *, key: bytes, nonce: bytes, basis: str = "Z") -> QuantumCircuit:
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

def _counts_from_sampler_result(res, shots: int, n_bits_hint: int = None):
    # handle SamplerV2 and classic shapes
    qd = getattr(res, "quasi_dists", None)
    if qd is None and isinstance(res, dict):
        qd = res.get("quasi_dists") or res.get("quasi_distribution") or res.get("quasi_dist")
    dist = (qd[0] if isinstance(qd, list) and qd else qd) or {}
    keys = list(dist.keys())
    if n_bits_hint is None:
        if keys and isinstance(keys[0], int):
            n_bits_hint = max(1, keys[0].bit_length())
        elif keys and isinstance(keys[0], str):
            n_bits_hint = len(keys[0])
        else:
            n_bits_hint = 1
    counts = {}
    for k, p in dist.items():
        bitstr = format(k, f"0{n_bits_hint}b") if isinstance(k, int) else str(k)
        c = int(round(float(p) * shots))
        if c > 0:
            counts[bitstr] = counts.get(bitstr, 0) + c
    tot = sum(counts.values())
    if tot and tot != shots:
        for b in list(counts):
            counts[b] = int(round(counts[b] * shots / tot))
    return counts

def run_sessionless(service, backend_name, circuit, shots: int):
    """
    Session-based Sampler to avoid backend= ctor issues across qiskit-ibm-runtime versions.
    Returns (job_id, approx_counts) using quasi-dists mapped to integer counts.
    """
    from qiskit_ibm_runtime import Session, Sampler
    with Session(service=service, backend=backend_name) as session:
        sampler = Sampler(session=session)
        job = sampler.run(circuits=[circuit], shots=shots)
        res = job.result()
        # Try V2 quasi_dists first, fallback if structure differs
        counts = {}
        try:
            qd = res.quasi_dists[0]  # dict-like {bitstring_int: prob}
            ncl = circuit.num_clbits or circuit.num_qubits
            for k, prob in qd.items():
                # Convert int keys to bitstrings; res keys may already be bitstrings depending on backend
                if isinstance(k, int):
                    bs = format(k, f'0{ncl}b')
                else:
                    bs = str(k)
                counts[bs] = int(round(prob * shots))
        except Exception:
            # last resort: access .meas.get_counts() if available
            try:
                counts = res[0].data.c.get_counts()
            except Exception:
                counts = {}
        return job.job_id(), counts


def _entropy_bits(counts):
    p = np.array(list(counts.values()), dtype=float)
    p = p / p.sum()
    h = -np.sum(p * np.log2(p + 1e-12))
    return float(h)

def _flatness(counts):
    p = np.array(list(counts.values()), dtype=float)
    p = p / p.sum()
    return float(np.max(p) - np.min(p))

def _kl_to_uniform(counts):
    p = np.array(list(counts.values()), dtype=float); p = p / p.sum()
    q = np.ones_like(p) / len(p)
    return float(np.sum(p * np.log2((p + 1e-12)/(q + 1e-12))))

def main():
    ap = argparse.ArgumentParser(description="Run IND-CPA proxy on IBM backend (torino).")
    ap.add_argument("--backend", required=True, help="e.g., torino or ibm_torino")
    ap.add_argument("--n", type=int, default=3)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--t_bits", type=int, default=12)
    ap.add_argument("--shots", type=int, default=128)
    ap.add_argument("--basis", choices=["Z","X","z","x"], default="Z")
    ap.add_argument("--nonce", help="hex nonce", default=None)
    ap.add_argument("--key", help="hex key (32 bytes recommended)", default=None)
    ap.add_argument("--instance", help="IBM Cloud instance (hub/group/project)", default=None)
    ap.add_argument("--out", default="docs/results/ibm_torino_run.json")
    args = ap.parse_args()

    service = QiskitRuntimeService(instance=args.instance) if args.instance else QiskitRuntimeService()
    backend_name = _BACKEND_ALIAS.get(args.backend, args.backend)
    backend = service.backend(backend_name)

    key = bytes.fromhex(args.key) if args.key else b"K"*32
    nonce = bytes.fromhex(args.nonce) if args.nonce else b"N"*12

    qc = build_circuit(args.n, args.rounds, args.t_bits, key=key, nonce=nonce, basis=args.basis)
    tqc = transpile(qc, backend=backend)

    job_id, counts = run_sessionless(service, backend_name, tqc, args.shots)

    metrics = {
        "entropy_bits": round(_entropy_bits(counts), 4),
        "kl_to_uniform": round(_kl_to_uniform(counts), 6),
        "flatness": round(_flatness(counts), 6),
    }
    record = {
        "time_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "backend": backend_name,
        "n": args.n, "rounds": args.rounds, "t_bits": args.t_bits, "shots": args.shots, "basis": args.basis,
        "job_id": job_id,
        "counts": counts,
        "metrics": metrics,
    }

    outp = Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"backend": record["backend"], **record["metrics"], "out": str(outp), "job_id": record["job_id"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
