
import json, math, time, argparse, pathlib
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

def build_phase_integer_circuit(SYM: int, K: int, M: int) -> QuantumCircuit:
    """Prepare a phase-gradient then collapse to |SYM> with inverse-QFT."""
    qc = QuantumCircuit(K, K, name="phase_to_int")
    # Hadamards to make uniform superposition
    for q in range(K):
        qc.h(q)
    # Program phases so that IQFT lands on the integer SYM (mod 2^K)
    # angle on qubit j is 2π * SYM / 2^(j+1)
    tau = 2 * math.pi
    for j in range(K):
        qc.p(tau * SYM / (2 ** (j + 1)), j)
    # Inverse QFT (no swaps; order matches our bitstring basis)
    iqft = QFT(num_qubits=K, inverse=True, do_swaps=False, name="iqft_dg")
    qc.append(iqft, range(K))
    qc.measure(range(K), range(K))
    # Sampler measures in Z automatically; no explicit measure needed.
    return qc

def hdist(a: int, b: int, M: int) -> int:
    return min((a - b) % M, (b - a) % M)

def extract_counts_primitive_result(job):
    """
    Robustly extract counts for SamplerV2 PrimitiveResult:
      result[0].data.c is a BitArray with helpers get_int_counts()/get_bitstrings().
    """
    counts = {}
    try:
        pub = job.result()[0]
        data = getattr(pub, "data", None)
        if data is None or getattr(data, "c", None) is None:
            return {}
        c = data.c
        gi = getattr(c, "get_int_counts", None)
        if callable(gi):
            ic = gi()
            # keys are integers; normalize to zero-padded bitstrings
            K = getattr(c, "num_bits", None) or 0
            for k, v in ic.items():
                counts[format(int(k), f"0{K}b")] = int(v)
        else:
            # Fallback: expand bitstrings
            bs = c.get_bitstrings()
            if not bs:
                return {}
            K = getattr(c, "num_bits", None) or len(bs[0])
            for b in bs:
                s = b if isinstance(b, str) else "".join("1" if t else "0" for t in b)
                counts[s] = counts.get(s, 0) + 1
    except Exception:
        return {}
    return counts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--send", action="store_true", help="Submit to IBM backends")
    ap.add_argument("--backend", default="ibm_torino")
    ap.add_argument("--M", type=int, default=1024)
    ap.add_argument("--symbol", type=int, required=True)
    ap.add_argument("--K", type=int, required=True)
    ap.add_argument("--shots", type=int, default=4096)
    ap.add_argument("--no-poll", action="store_true")
    args = ap.parse_args()

    BACKEND = args.backend
    M = args.M
    SYM = args.symbol % M
    K = args.K
    shots = args.shots

    print(f"[target] SYM={SYM} on M={M} (K={K}) backend={BACKEND} shots={shots}")

    # Build circuit and bind backend
    qc = build_phase_integer_circuit(SYM, K, M)
    svc = QiskitRuntimeService()
    backend_obj = svc.backend(BACKEND)

    # Transpile to ISA so Sampler accepts it (fixes the 'h not supported' error)
    tqc = transpile(qc, backend=backend_obj)

    # Submit via SamplerV2 using backend mode
    sampler = Sampler(mode=backend_obj)
    job = sampler.run([tqc], shots=shots)
    jid = job.job_id()
    print(f"[submit] job_id={jid} backend={BACKEND} shots={shots}")

    if args.no_poll:
        print("[note] --no-poll set; exiting after submission only.")
        return 0

    # Poll simple
    prev = None
    t0 = time.time()
    while True:
        s = str(job.status())
        if s != prev:
            print(f"[status] {s}")
            prev = s
        if s in ("DONE", "CANCELLED", "ERROR", "FAILED"):
            break
        time.sleep(5)

    if s != "DONE":
        print(f"[warn] final status {s}")
        return 1

    # Extract counts
    counts = extract_counts_primitive_result(job)
    if not counts:
        print("[error] could not extract counts")
        return 1

    # Metrics
    shots_eff = max(1, sum(counts.values()))
    mb = max(counts, key=counts.get)
    ab = int(mb, 2)
    top = counts[mb] / shots_eff
    p_star = counts.get(format(SYM, f"0{K}b"), 0) / shots_eff
    dist = hdist(SYM, ab, 1 << K)
    ok_pm1 = (dist <= 1)
    p_pm1 = 0.0
    for d in (-1, 0, 1):
        p_pm1 += counts.get(format((SYM + d) % (1 << K), f"0{K}b"), 0) / shots_eff

    out = {
        "backend": BACKEND, "job_id": jid,
        "M": M, "K": K, "sym": SYM, "shots": shots,
        "ideal_bin": SYM, "counts": counts,
        "argmax_bits": mb, "argmax_bin": ab,
        "argmax_freq": round(top, 6), "ok_pm1": ok_pm1,
        "p_pm1": round(p_pm1, 6), "p_ideal": round(p_star, 6),
        "tvd_delta": round(1.0 - p_star, 6)
    }
    pathlib.Path("paper_outputs").mkdir(exist_ok=True)
    fn = f"paper_outputs/qpsk_{BACKEND}_M{M}_sym{SYM}_{K}b_{shots}s_{jid}.json"
    with open(fn, "w") as f:
        json.dump(out, f, indent=2)
    print("[wrote]", fn)
    print(f"[quick] ideal={SYM} argmax={ab} ok±1={ok_pm1} "
          f"top={top:.3f} p±1={p_pm1:.3f} p*={p_star:.3f} tvd={1-p_star:.3f}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
