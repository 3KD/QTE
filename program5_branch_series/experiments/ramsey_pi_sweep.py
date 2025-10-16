import json, time, math, argparse
from pathlib import Path
import numpy as np

from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler, Session

def build(phi_param: Parameter) -> QuantumCircuit:
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.rz(phi_param, 0)
    qc.h(0)
    return qc

def run(backend_name: str, shots: int, npts: int, span: float):
    phi = Parameter("phi")
    base = build(phi)

    phis = np.linspace(-span, span, npts).tolist()
    # bind per-point (Qiskit 2.x: assign_parameters(..., inplace=False))
    circuits = [base.assign_parameters({phi: float(p)}, inplace=False) for p in phis]

    service = QiskitRuntimeService()  # uses your saved account
    with Session(service=service, backend=backend_name) as sess:
        smp = Sampler(session=sess)
        # NOTE: pass shots on run(), not via OptionsV2
        job = smp.run(circuits, shots=shots)
        res = job.result()

    # SamplerResult.quasi_dists is a list of dicts like {"0": p0, "1": p1}
    quasi = res.quasi_dists
    p1 = [float(q.get("1", 0.0)) for q in quasi]
    pred = [math.sin(0.5*float(p))**2 for p in phis]  # ideal Ramsey
    rmse = (sum((a-b)**2 for a,b in zip(p1, pred))/len(pred))**0.5 if p1 else float("nan")

    out = {
        "backend": backend_name,
        "shots": shots,
        "npts": npts,
        "span": span,
        "phi": phis,
        "p1": p1,
        "pred_p1": pred,
        "rmse": rmse,
        "ts": int(time.time()),
        "qiskit_runtime_version": getattr(res, "version", None),
    }

    outdir = Path("paper_outputs")
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    outfile = outdir / f"ramsey_pi_sweep_{backend_name}_{shots}s_{npts}pts_span{span}_{stamp}.json"
    outfile.write_text(json.dumps(out, indent=2))
    print(f"Wrote {outfile}")
    print(f"RMSE vs sin^2(phi/2): {rmse:.4f}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_torino")
    ap.add_argument("--shots", type=int, default=4096)
    ap.add_argument("--npts", type=int, default=13)
    ap.add_argument("--span", type=float, default=3.141592653589793)  # π by default
    args = ap.parse_args()
    run(args.backend, args.shots, args.npts, args.span)
