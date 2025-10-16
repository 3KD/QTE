#!/usr/bin/env python3
import os, re, math, json, argparse, time
from collections import Counter

from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
from scripts._sampler_utils import run_counts
import sys

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
    qc.append(iqft_gate(K, degree=degree), range(K))
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

def extract_counts(res, width, shots, circuit=None, backend=None):
    """
    Make counts from a Sampler result across API shapes:
      1) Modern Sampler: res.quasi_dists[0]  (keys int, values probs)
      2) Published results: res._pub_results[0].data[...]  (nested containers)
      3) Last resort: re-run via scripts._sampler_utils.run_counts(circuit, backend, shots)
    Returns a dict like {"000": n, ...} with width bits.
    """
    def _bits(k):
        try:
            if isinstance(k, int):
                return format(k, f"0{width}b")
            if isinstance(k, str):
                ks = k.strip()
                if set(ks) <= {"0","1"}:
                    return ks.zfill(width)
                return format(int(ks), f"0{width}b")
            return format(int(k), f"0{width}b")
        except Exception:
            return None

    def _norm_counts(d):
        out = {}
        for k,v in (d or {}).items():
            b = _bits(k)
            if b is None: 
                continue
            try:
                c = int(v)
            except Exception:
                try:
                    c = int(round(float(v)))
                except Exception:
                    continue
            out[b] = out.get(b, 0) + c
        return out

    # 1) Modern: quasi_dists
    qd = getattr(res, "quasi_dists", None)
    if qd:
        out = {}
        for k, p in qd[0].items():
            b = _bits(k)
            if b is None:
                continue
            try:
                prob = float(p)
            except Exception:
                prob = float(getattr(p, "value", 0.0))
            out[b] = out.get(b, 0) + int(round(prob*shots))
        if out:
            return out

    # 2) Published results container
    try:
        pubs = getattr(res, "_pub_results", None)
        if pubs:
            first = pubs[0]
            data  = getattr(first, "data", None) or getattr(first, "_data", None)
            # Try common accessors in order
            # 2a) A plain dict of bitstrings somewhere
            def bfs(root, max_nodes=12000, max_depth=8):
                from collections import deque
                q = deque([(root,0)])
                seen=set()
                while q:
                    node,d = q.popleft()
                    if id(node) in seen: 
                        continue
                    seen.add(id(node))
                    if isinstance(node, dict):
                        # heuristic: keys look like bitstrings?
                        if node and all(isinstance(k,str) and set(k) <= {"0","1"} for k in list(node.keys())[: min(6,len(node))]):
                            return node
                        for v in node.values(): 
                            if d < max_depth: q.append((v,d+1))
                    elif isinstance(node, (list,tuple,set)):
                        for v in node:
                            if d < max_depth: q.append((v,d+1))
                    else:
                        # Try a few common attributes / methods
                        for attr in ("data","_data","metadata","_metadata","dict","model_dump","payload","_payload","values"):
                            try:
                                v = getattr(node, attr)
                            except Exception:
                                continue
                            if callable(v):
                                try:
                                    v = v()
                                except Exception:
                                    continue
                            # Try to JSON-decode strings
                            if isinstance(v, str):
                                try:
                                    import json as _json
                                    v = _json.loads(v)
                                except Exception:
                                    pass
                            if d < max_depth:
                                q.append((v,d+1))
                return None

            raw = bfs(data)
            if raw:
                out = _norm_counts(raw)
                if out:
                    return out

            # 2b) Some containers (DataBin) expose get_counts()
            try:
                vals = data.values() if hasattr(data, "values") else []
                for db in vals:
                    gc = getattr(db, "get_counts", None)
                    if callable(gc):
                        out = _norm_counts(gc())
                        if out:
                            return out
            except Exception:
                pass
    except Exception:
        pass

    # 3) Last resort: re-run just this circuit to obtain counts
    if circuit is not None and backend is not None:
        print("[warn] published-results decode failed; falling back to run_counts() one-shot.")
        _jid, out = run_counts(circuit, backend, shots=shots)
        return out

    raise RuntimeError("Could not decode Sampler result.")

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

    seed = args.seed_transpile if args.seed_transpile is not None else (
    int(os.getenv('QISKIT_SEED_TRANSPILE')) if os.getenv('QISKIT_SEED_TRANSPILE') else None)
tqc = transpile(qc, backend=backend, optimization_level=1, seed_transpiler=seed)
twoq = count_twoq(tqc)
print(f"[target] SYM={args.symbol} on M={args.M} (K={args.K}) backend={args.backend} shots={args.shots}")
if not args.send:
    print("Dry-run only (pass --send to execute).")
    sys.exit(0)
    sampler_opts = {"default_shots": args.shots}
    if args.resilience_level is not None:
        sampler_opts["resilience_level"] = args.resilience_level
    try:
        sampler = Sampler(mode=backend, options=sampler_opts)
    except Exception as e:
        if 'resilience_level' in str(e):
            sampler_opts.pop('resilience_level', None)
            print("[warn] 'resilience_level' not supported for Sampler on this install; proceeding without it.")
            sampler = Sampler(mode=backend, options=sampler_opts)
        else:
            raise

    job = sampler.run([tqc])
    res = job.result()

    width = len(tqc.clbits) or tqc.num_qubits
    counts = extract_counts(res, width, args.shots, circuit=tqc, backend=backend)

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
