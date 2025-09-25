# cli_runner.py
import argparse
import numpy as np
import matplotlib.pyplot as plt

from series_encoding import get_series_amplitudes
from quantum_embedding import (
    generate_series_encoding,
    qft_spectrum_from_series,
    run_circuit,
)
from harmonic_analysis import (
    compute_fft_spectrum_from_amplitudes,
)

def print_top_basis_states(statevector, label, k=16):
    probs = np.abs(statevector.data)**2
    pairs = [(i, p) for i, p in enumerate(probs)]
    pairs.sort(key=lambda t: t[1], reverse=True)
    print(f"\nTop {k} basis states for {label}:")
    for i, p in pairs[:k]:
        print(f"|{i:0{int(np.log2(len(probs)))}b}>  {p:.6f}")

def main():
    parser = argparse.ArgumentParser(description="Quantum Transcendental CLI Tool")
    parser.add_argument("--label", type=str, required=True, help="Constant label (e.g., e, π, ζ(3), ln(2))")
    parser.add_argument("--qubits", type=int, default=6, help="Number of qubits")
    parser.add_argument("--method", type=str, default=None, help="Series method (π: Ramanujan|Machin)")
    parser.add_argument("--phase", type=str, default="sign", choices=["sign", "abs"], help="Phase mode for signed series")
    parser.add_argument("--pad-len", type=int, default=128, help="Zero-pad length for FFT/QFT spectrum")
    parser.add_argument("--plot", action="store_true", help="Plot FFT spectrum")
    parser.add_argument("--qft", action="store_true", help="Build QFT spectrum circuit and run")
    parser.add_argument("--use-ibm", action="store_true", help="Use IBM backend (counts)")

    args = parser.parse_args()
    dim = 2 ** args.qubits
    label = args.label

    print(f"\n📌 Encoding {label} with {args.qubits} qubits (method={args.method or '-'}, phase={args.phase})")

    if args.qft:
        print("\n== QFT spectrum mode ==")
        qc, proc_vec, mets = qft_spectrum_from_series(
            label,
            n_qubits=args.qubits,
            method=args.method,
            phase_mode=args.phase,
            preprocess=True,
            pad_len=args.pad_len,
            use_stateprep=True,
            do_measure=True,
        )
        print(f"Preprocess metrics: DC={mets['dc_frac']:.3f}, H={mets['entropy_bits']:.3f} bits, len={mets['len']}")
        sv, counts = run_circuit(qc, use_ibm=args.use_ibm, measure=True)
        if counts:
            print("\nTop counts:")
            for k, v in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:16]:
                print(f"{k}: {v}")
        else:
            print("No counts returned (did you run on a statevector sim with measures?).")
        return

    # Plain amplitude encoding path
    sv = generate_series_encoding(label, n_qubits=args.qubits, method=args.method, phase_mode=args.phase)
    print_top_basis_states(sv, label)

    # Optional FFT spectrum
    if args.plot:
        amps = get_series_amplitudes(label, dim, method=args.method, phase_mode=args.phase, normalize=True)
        power, freqs, mets = compute_fft_spectrum_from_amplitudes(
            amps, remove_dc=True, window="hann", pad_len=args.pad_len
        )
        print(f"\nFFT metrics: DC={mets['dc_frac']:.3f}, H={mets['entropy_bits']:.3f} bits, peak@{int(np.argmax(power))}")
        plt.figure(figsize=(10, 4))
        plt.plot(freqs, power, marker="o")
        plt.title(f"{label} FFT — {args.method or '-'} / {args.phase}  (DC={mets['dc_frac']:.3f}, H={mets['entropy_bits']:.3f} bits)")
        plt.xlabel("Frequency Index"); plt.ylabel("Power"); plt.grid(True); plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    main()

