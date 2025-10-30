
import os, csv, math
import numpy as np
import matplotlib.pyplot as plt
from series_encoding import get_series_amplitudes
from harmonic_analysis import compute_fft_spectrum_from_amplitudes

LABELS = [
    "π","e","ln(2)","ζ(2)","ζ(3)","γ","Catalan","φ","J0",
    "Li(2,0.5)","polylog(3, 0.5)",
    "Maclaurin[sin(x)]","Maclaurin[log(1+x)]","Maclaurin[exp(x^2); r=0.7]"
]
NQ = 8
MODES = ["terms","egf"]
os.makedirs("paper_outputs", exist_ok=True)

def safename(s):
    return (s.replace("/","_").replace("(","").replace(")","")
              .replace(" ","").replace(",","_").replace("|","_"))

csv_path = "paper_outputs/metrics.csv"
with open(csv_path, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["label","mode","nqubits","len","dc_frac","entropy_bits","peak_index"])
    for lab in LABELS:
        for mode in MODES:
            try:
                dim = 2**NQ
                a = get_series_amplitudes(lab, dim, amp_mode=mode, normalize=True)
                probs = np.abs(a)**2
                fig = plt.figure(figsize=(9,3.2))
                plt.bar(range(dim), probs)
                plt.title(f"{lab} {mode.upper()} |amp|^2 (n={NQ})")
                plt.xlabel("index"); plt.ylabel("prob"); plt.tight_layout()
                f1 = f"paper_outputs/{safename(lab)}_{mode}_n{NQ}_amps.png"
                fig.savefig(f1); plt.close(fig)

                P, F, M = compute_fft_spectrum_from_amplitudes(a, remove_dc=True, window="hann", pad_len=512)
                fig2 = plt.figure(figsize=(9,3.2))
                plt.plot(F, P, marker="o")
                plt.title(f"{lab} {mode.upper()} FFT  (DC={M['dc_frac']:.3f}, H={M['entropy_bits']:.3f} bits)")
                plt.xlabel("freq index"); plt.ylabel("power"); plt.grid(True); plt.tight_layout()
                f2 = f"paper_outputs/{safename(lab)}_{mode}_n{NQ}_fft.png"
                fig2.savefig(f2); plt.close(fig2)

                peak = int(np.argmax(P)) if len(P) else -1
                w.writerow([lab, mode, NQ, dim, M["dc_frac"], M["entropy_bits"], peak])
                print("DONE", lab, mode)
            except Exception as e:
                print("SKIP", lab, mode, e)
print("BATCH_OK", csv_path)
