#!/usr/bin/env python3
import os, json, math, argparse
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFTGate
from scripts._sampler_utils import get_backend, run_counts

def iqft_gate(n: int):
    # In Qiskit 2.x prefer QFTGate (avoids the deprecation noise of QFT class)
    return QFTGate(n, inverse=True, do_swaps=False)

def qpsk_indexer(K: int, sym: int, M: int) -> QuantumCircuit:
    qc = QuantumCircuit(K, name=f"qpsk_indexer_K{K}_sym{sym}_M{M}")
    phi = 2*math.pi*sym/M
    for j in range(K):
        qc.p((2**j) * phi / (2**K), j)      # phased “chirp”
    qc.append(iqft_gate(K), range(K))
    qc.measure_all()
    return qc

def count_twoq(tqc) -> int:
    # Robust to CircuitInstruction vs legacy tuple shapes
    cnt = 0
    for ci in tqc.data:
        op = getattr(ci, "operation", ci)
        if getattr(op, "num_qubits", 0) >= 2:
            cnt += 1
    return cnt

def main():
    ap = argparse.ArgumentParser(description="QPSK end-to-end (golden runner)")
    ap.add_argument("--backend", required=True)
    ap.add_argument("--M", type=int, required=True)
    ap.add_argument("--K", type=int, required=True)
    ap.add_argument("--symbol", type=int, required=True)
    ap.add_argument("--shots", type=int, default=256)
    ap.add_argument("--seed-transpile", type=int, default=None)
    ap.add_argument("--artifact-dir", default="paper_outputs")
    args = ap.parse_args()

    backend = get_backend(args.backend)

    # Build + transpile
    qc  = qpsk_indexer(args.K, args.symbol, args.M)
    seed = args.seed_transpile if args.seed_transpile is not None else (
        int(os.getenv("QISKIT_SEED_TRANSPILE")) if os.getenv("QISKIT_SEED_TRANSPILE") else None
    )
    tqc = transpile(qc, backend=backend, optimization_level=1, seed_transpiler=seed)
    twoq = count_twoq(tqc)

    print(f"[target] SYM={args.symbol} on M={args.M} (K={args.K}) backend={args.backend} shots={args.shots}")
    print(f"[circuit] depth={tqc.depth()} two-qubit gates={twoq} seed={seed}")

    # Execute on hardware via your robust sampler utils
    jid, counts = run_counts(tqc, backend, shots=args.shots)
    tot = max(1, sum(counts.values()))
    top = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    pstar = (top[0][1] / tot) if top else 0.0

    print("job_id:", jid)
    print("top:", top[:10])
    print(f"p*≈ {pstar:.6f}")

    # Write artifact
    os.makedirs(args.artifact_dir, exist_ok=True)
    art = os.path.join(
        args.artifact_dir,
        f"qpsk_{args.backend}_M{args.M}_sym{args.symbol}_{args.K}b_{args.shots}s_{jid}.json"
    )
    payload = {
        "backend": args.backend,
        "M": args.M,
        "K": args.K,
        "sym": args.symbol,
        "shots": args.shots,
        "job_id": jid,
        "top_counts": dict(top[:20]),
        "argmax_bits": (top[0][0] if top else None),
        "p_star": pstar,
        "depth": tqc.depth(),
        "two_qubit_gate_count": twoq,
        "seed_transpiler": seed,
    }
    with open(art, "w") as f:
        json.dump(payload, f, indent=2)
    print("[wrote]", art)

if __name__ == "__main__":
    main()
