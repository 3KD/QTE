
import os, csv, numpy as np
from quantum_embedding import entangle_series_multi, simulate_statevector, perform_schmidt_decomposition
from series_encoding import get_series_amplitudes
import matplotlib.pyplot as plt

os.makedirs("paper_outputs", exist_ok=True)

SETS = [
    ["π","e","ζ(3)"],
    ["π","J0","e"],
    ["Maclaurin[sin(x)]","Maclaurin[log(1+x)]","ζ(3)"]
]
REGQ = 3
TOPOLOGIES = ["chain","star"]

def safe(s):
    return (s.replace("/","_").replace("(","").replace(")","").replace(",","_").replace(" ",""))

def entropy_from_svals(S):
    p = (S**2); p = p[p>1e-15]
    return float(-(p*np.log2(p)).sum()) if p.size else 0.0

csv_path = "paper_outputs/multi_metrics.csv"
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["labels","topology","regq","total_qubits","cut","schmidt_entropy_bits"])
    for labs in SETS:
        for topo in TOPOLOGIES:
            qc = entangle_series_multi(labs, n_qubits_each=REGQ, methods=None,
                                       phase_mode="sign", topology=topo,
                                       use_stateprep=True, do_measure=False)
            sv = simulate_statevector(qc)
            n = int(np.log2(len(sv.data))); R = len(labs)
            for k in range(1, R):
                S = perform_schmidt_decomposition(sv, cut=REGQ*k)
                H = entropy_from_svals(S)
                w.writerow([",".join(labs), topo, REGQ, n, k, H])
            probs = (np.abs(sv.data)**2).reshape(*([2**REGQ]*R))
            fig, axes = plt.subplots(1, R, figsize=(4*R, 3))
            if R == 1: axes = [axes]
            for i in range(R):
                axes[i].bar(range(2**REGQ), probs.sum(axis=tuple(j for j in range(R) if j!=i)))
                axes[i].set_title(f"{labs[i]} ({REGQ}q)")
                axes[i].set_xticks(range(2**REGQ))
            fig.tight_layout()
            fig.savefig(f"paper_outputs/marginals_{safe('_'.join(labs))}_{topo}_q{REGQ}.png")
            plt.close(fig)

print("MULTI_OK", csv_path)
