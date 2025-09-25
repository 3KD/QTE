# smoke_test.py
from series_encoding import get_series_amplitudes
from harmonic_analysis import compute_fft_spectrum_from_amplitudes
from quantum_embedding import qft_spectrum_from_series, run_circuit, generate_series_encoding

def main():
    label = "π"
    n_qubits = 6

    # 1) Amplitude encode
    sv = generate_series_encoding(label, n_qubits=n_qubits, method="Ramanujan", phase_mode="sign")
    print("State len:", len(sv))

    # 2) FFT (classical)
    amps = get_series_amplitudes(label, 2**n_qubits, method="Ramanujan", phase_mode="sign", normalize=True)
    power, freqs, mets = compute_fft_spectrum_from_amplitudes(amps, remove_dc=True, window="hann", pad_len=128)
    print("FFT metrics:", {k: round(v, 3) if isinstance(v, float) else v for k, v in mets.items()})

    # 3) QFT spectrum circuit (quantum-native)
    qc, vec, m2 = qft_spectrum_from_series(label, n_qubits=n_qubits, method="Ramanujan", phase_mode="sign",
                                           preprocess=True, pad_len=128, use_stateprep=True, do_measure=True)
    print("QFT preproc metrics:", {k: round(v, 3) if isinstance(v, float) else v for k, v in m2.items()})
    sv2, counts = run_circuit(qc, use_ibm=False, measure=True)
    print("Counts keys:", 0 if not counts else len(counts))

if __name__ == "__main__":
    main()

