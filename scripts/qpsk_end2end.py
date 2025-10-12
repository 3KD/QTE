#!/usr/bin/env python3
import os, re, math, json, argparse, time
from collections import Counter

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler

# ---------- helpers ----------

def iqft_gate(n: int):
    # Still fine; deprecation warning is OK for now
    return QFT(num_qubits=n, inverse=True, do_swaps=False)

def qpsk_indexer(K: int, sym: int, M: int) -> QuantumCircuit:
    qc = QuantumCircuit(K)
    phi = 2*math.pi*sym/M
    # phase ramp
    for j in range(K):
        qc.p((2**j)*phi/(2**K), j)
    qc.append(iqft_gate(K), range(K))
    qc.measure_all()
    return qc

def count_twoq(tqc) -> int:
    cnt = 0
    for ci in tqc.data:
        op = getattr(ci, 'operation', ci)
        if getattr(op, 'num_qubits', 0) >= 2:
            cnt += 1
    return cnt

def _as_counts_from_quasi(qd, width: int, shots: int):
    """qd: dict-like (keys can be int or bitstrings); return int counts dict or None."""
    try:
        items = qd.items()
    except Exception:
        return None
    total_p = 0.0
    out = {}
    for k, p in items:
        try:
            p = float(p)
        except Exception:
            try:
                p = float(getattr(p, "value", 0.0))
            except Exception:
                return None
        if isinstance(k, int):
            b = format(k, f"0{width}b")
        else:
            try:
                if set(str(k)) <= {"0","1"}:
                    b = str(k).zfill(width)
                else:
                    b = format(int(k), f"0{width}b")
            except Exception:
                return None
        out[b] = out.get(b, 0) + int(round(p*shots))
        total_p += p
    if 0.85 <= total_p <= 1.15:
        return out
    return None

def _normalize_counts(cd, width: int):
    """cd: dict mapping bitstrings/ints→counts; returns {bitstring: int} or None."""
    try:
        items = cd.items()
    except Exception:
        return None
    out = {}
    any_int = False
    for k, v in items:
        if isinstance(k, int):
            b = format(k, f"0{width}b")
        else:
            s = str(k)
            if set(s) <= {"0","1"}:
                b = s.zfill(width)
            else:
                try:
                    b = format(int(s), f"0{width}b")
                except Exception:
                    return None
        try:
            c = int(v)
            any_int = True
        except Exception:
            try:
                c = int(round(float(v)))
                any_int = True
            except Exception:
                return None
        out[b] = out.get(b, 0) + c
    return out if any_int else None

def extract_counts(res, width: int, shots: int):
    """Robustly get counts from either Sampler.quasi_dists or 'published results' containers."""
    # 1) Modern path
    qd = getattr(res, "quasi_dists", None)
    if qd:
        return _as_counts_from_quasi(qd[0], width, shots)

    # 2) Published-results path
    # res._pub_results -> [SamplerPubResult], res._metadata -> dict
    pub = getattr(res, "_pub_results", None)
    if isinstance(pub, list) and pub:
        first = pub[0]
        data = None
        # SamplerPubResult.data() -> DataBin
        if hasattr(first, "data"):
            try:
                data = first.data()
            except Exception:
                data = None
        if data is not None:
            # DataBin may expose get_counts() directly
            if hasattr(data, "get_counts"):
                try:
                    cd = data.get_counts()
                    norm = _normalize_counts(cd, width)
                    if norm: return norm
                except Exception:
                    pass
            # Or a values() of DataBins
            vals = None
            try:
                vals = data.values()
            except Exception:
                vals = None
            if vals is not None:
                for db in list(vals):
                    if hasattr(db, "get_counts"):
                        try:
                            cd = db.get_counts()
                            norm = _normalize_counts(cd, width)
                            if norm: return norm
                        except Exception:
                            continue
            # last resort: try attributes that might contain a histogram
            for attr in ("meas","counts","histogram"):
                try:
                    raw = getattr(data, attr)
                    if callable(raw): raw = raw()
                    norm = _normalize_counts(raw, width)
                    if norm: return norm
                except Exception:
                    pass

    # 3) Could not decode
    keys = list(getattr(res, "__dict__", {}).keys())
    raise RuntimeError(f"Could not decode Sampler result. Outer keys: {keys}")

# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True, help="IBM backend name (e.g., ibm_torino)")
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--K", type=int, required=True)
    ap.add_argument("--symbol", type=int, required=True)
    ap.add_argument("--shots", type=int, default=256)
    ap.add_argument("--send", action="store_true", help="actually run")
    ap.add_argument("--resilience-level", type=int, default=None, dest="resilience_level")
    ap.add_argument("--git-commit", action="store_true")
    ap.add_argument("--git-push", action="store_true")
    args = ap.parse_args()

    svc = QiskitRuntimeService()
    backend = svc.backend(args.backend)

    qc  = qpsk_indexer(args.K, args.symbol, args.M)
    tqc = transpile(qc, backend=backend, optimization_level=1)
    twoq = count_twoq(tqc)

    print(f"[target] SYM={args.symbol} on M={args.M} (K={args.K}) backend={args.backend} shots={args.shots}")
    print(f"[circuit] depth={tqc.depth()} two-qubit gates={twoq}")

    if not args.send:
        print("Dry-run only (pass --send to execute).")
        return

    sampler_opts = {"default_shots": args.shots}
    if args.resilience_level is not None:
        sampler_opts["resilience_level"] = args.resilience_level
    sampler = Sampler(mode=backend, options=sampler_opts)

    job = sampler.run([tqc])
    res = job.result()

    width = len(tqc.clbits) or tqc.num_qubits
    counts = extract_counts(res, width, args.shots)

    # summarize
    top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    argmax_bits = top[0][0] if top else None
    p_star = (top[0][1]/max(1,args.shots)) if top else 0.0

    print("job_id:", job.job_id())
    print("top:", top[:10])
    print("p*≈", round(p_star, 6))

    # artifact
    os.makedirs("paper_outputs", exist_ok=True)
    art = f"paper_outputs/qpsk_{args.backend}_M{args.M}_sym{args.symbol}_{args.K}b_{args.shots}s_{job.job_id()}.json"
    with open(art, "w") as f:
        json.dump({
            "backend": args.backend,
            "M": args.M, "K": args.K, "sym": args.symbol,
            "shots": args.shots,
            "top_counts": dict(top[:20]),
            "argmax_bits": argmax_bits,
            "p_star": p_star,
            "depth": tqc.depth(),
            "two_qubit_gate_count": twoq,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }, f, indent=2)
    print("[wrote]", art)

    if args.git_commit:
        os.system(f'git add "{art}"')
        os.system(f'git commit -m "qpsk: M={args.M} K={args.K} sym={args.symbol} shots={args.shots} on {args.backend}"')
        if args.git_push:
            os.system("git push")

if __name__ == "__main__":
    main()
