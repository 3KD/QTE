# QTEGUI.py — Quantum Transcendental Encoder (QTE)
# Modes: EGF / Terms / Periodic p/q / Value Phase (PEA) / Digit QROM
# Active-state first: FFT/QFT/Measure/Amplitudes/Tomography/Basis all use Active if no selection
# Entanglement: simple 2-qubit, series registers, multi-constant

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, MULTIPLE

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from typing import List, Dict, Optional, Tuple

# Qiskit
from qiskit import QuantumCircuit
from qiskit_aer import Aer, AerSimulator
from qiskit.quantum_info import Statevector, DensityMatrix

# Optional tomography
try:
    from qiskit_experiments.library import StateTomography
    from qiskit_experiments.framework import ExperimentData
    from qiskit.quantum_info import state_fidelity
    TOMO_OK = True
except Exception:
    TOMO_OK = False

# App modules
from series_encoding import get_series_amplitudes, compute_series, compute_series_value
from ibm_backend import get_backend, initialize_ibm
from harmonic_analysis import compute_fft_spectrum_from_amplitudes
from quantum_embedding import (
    qft_spectrum_from_series, index_qft_spectrum_circuit,
    run_circuit, simulate_statevector, generate_series_encoding,
    encode_entangled_constants, entangle_series_registers, entangle_series_multi,
    analyze_tensor_structure, perform_schmidt_decomposition, mutual_information,
    value_phase_estimation_circuit, periodic_phase_state, digit_qrom_circuit,
)

# Optional I/O
try:
    from state_io import save_statevector, load_statevector
except Exception:
    save_statevector = None
    load_statevector = None


class QTEGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quantum Transcendental Encoder (QTE)")
        self.geometry("1180x860")

        # Saved and Active states
        self.statevectors: Dict[str, Statevector] = {}
        self.active_state_label: Optional[str] = None
        self.active_state: Optional[Statevector] = None

        # -------- Top controls --------
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)

        self.const_label = tk.StringVar(value="π")
        ttk.Label(top, text="Constant").grid(row=0, column=0, sticky="w")
        ttk.Combobox(top, textvariable=self.const_label,
                     values=["π", "e", "ln(2)", "ζ(2)", "ζ(3)", "γ", "Catalan", "φ"],
                     state="readonly", width=9).grid(row=0, column=1, padx=(4, 12))

        self.pi_method = tk.StringVar(value="Machin")
        ttk.Label(top, text="π method").grid(row=0, column=2, sticky="w")
        ttk.Combobox(top, textvariable=self.pi_method,
                     values=["Leibniz", "Nilakantha", "Machin", "Ramanujan", "Chudnovsky"],
                     state="readonly", width=12).grid(row=0, column=3, padx=(4, 12))

        self.phase_mode = tk.StringVar(value="sign")
        ttk.Label(top, text="Phase").grid(row=0, column=4, sticky="w")
        ttk.Combobox(top, textvariable=self.phase_mode,
                     values=["sign", "abs"], state="readonly", width=6).grid(row=0, column=5, padx=(4, 12))

        self.n_qubits = tk.IntVar(value=6)
        ttk.Label(top, text="#qubits").grid(row=0, column=6, sticky="w")
        ttk.Spinbox(top, from_=1, to=12, textvariable=self.n_qubits, width=5).grid(row=0, column=7, padx=(4, 12))

        self.pad_len = tk.IntVar(value=128)
        ttk.Label(top, text="Pad (FFT)").grid(row=0, column=8, sticky="w")
        ttk.Spinbox(top, from_=16, to=4096, increment=16, textvariable=self.pad_len, width=7).grid(row=0, column=9, padx=(4, 12))

        self.use_ibm = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Use IBM", variable=self.use_ibm, command=self._maybe_prompt_ibm).grid(row=0, column=10, padx=(10, 0))

        # Encoding mode
        self.enc_mode = tk.StringVar(value="EGF")
        ttk.Label(top, text="Encoding").grid(row=1, column=0, sticky="w", pady=(6,0))
        ttk.Combobox(top, textvariable=self.enc_mode,
                     values=["EGF", "Terms", "Periodic p/q", "Value Phase (PEA)", "Digit QROM"],
                     state="readonly", width=16).grid(row=1, column=1, padx=(4, 12), pady=(6,0))

        # Mode fields
        self.pea_bits = tk.IntVar(value=10)
        ttk.Label(top, text="PEA bits").grid(row=1, column=2, sticky="e", pady=(6,0))
        ttk.Spinbox(top, from_=2, to=20, textvariable=self.pea_bits, width=5).grid(row=1, column=3, padx=(4,12), pady=(6,0))

        self.p_val = tk.IntVar(value=22)
        self.q_val = tk.IntVar(value=7)
        ttk.Label(top, text="p/q").grid(row=1, column=4, sticky="e", pady=(6,0))
        ttk.Spinbox(top, from_=1, to=100000, textvariable=self.p_val, width=7).grid(row=1, column=5, padx=(4,4), pady=(6,0))
        ttk.Spinbox(top, from_=1, to=100000, textvariable=self.q_val, width=7).grid(row=1, column=6, padx=(4,12), pady=(6,0))

        self.qrom_base = tk.IntVar(value=10)
        self.qrom_bits = tk.IntVar(value=4)
        self.qrom_index = tk.IntVar(value=6)
        ttk.Label(top, text="QROM base/bits/index").grid(row=1, column=7, sticky="e", pady=(6,0))
        ttk.Spinbox(top, from_=2, to=16, textvariable=self.qrom_base, width=5).grid(row=1, column=8, padx=(4,2), pady=(6,0))
        ttk.Spinbox(top, from_=1, to=8, textvariable=self.qrom_bits, width=4).grid(row=1, column=9, padx=(2,2), pady=(6,0))
        ttk.Spinbox(top, from_=1, to=10, textvariable=self.qrom_index, width=5).grid(row=1, column=10, padx=(2,2), pady=(6,0))

        # Status
        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(self, textvariable=self.status_var, anchor="w").pack(fill="x", padx=10, pady=(0, 6))

        # Notebook
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._build_tab_preview()
        self._build_tab_fft()
        self._build_tab_qft()
        self._build_tab_measure()
        self._build_tab_amplitudes()
        self._build_tab_similarity()
        self._build_tab_clustering()
        self._build_tab_tomography()
        self._build_tab_entanglement()
        self._build_tab_gates()
        self._build_tab_state_io()
        self._build_tab_basis()

    # -------- IBM init --------
    def _maybe_prompt_ibm(self):
        if self.use_ibm.get():
            try:
                token = simpledialog.askstring("IBM Login", "Enter your IBM Quantum API Token:", show="*")
                if token:
                    initialize_ibm(token=token)
                    self._set_status("IBM Quantum initialized.")
                else:
                    self.use_ibm.set(False)
            except Exception as e:
                messagebox.showerror("IBM Login Failed", str(e))
                self.use_ibm.set(False)

    # -------- Active state helpers --------
    def _set_active(self, label: str, sv: Statevector, also_save: bool = True):
        self.active_state_label = label
        self.active_state = sv
        if also_save:
            self.statevectors[label] = sv
        self._refresh_all_combos()
        self._set_status(f"Active: {label} (len={len(sv.data)})")

    def _get_active_or_selected(self, combo: ttk.Combobox) -> Tuple[str, Optional[Statevector]]:
        lbl = combo.get()
        if lbl in self.statevectors:
            return lbl, self.statevectors[lbl]
        if self.active_state is not None:
            return self.active_state_label or "[active]", self.active_state
        return "", None

    def _refresh_all_combos(self):
        keys = list(self.statevectors.keys())
        for cb in getattr(self, "_all_combos", []):
            cb.config(values=keys)

    def _register_combo(self, cb: ttk.Combobox):
        if not hasattr(self, "_all_combos"):
            self._all_combos: List[ttk.Combobox] = []
        self._all_combos.append(cb)

    def _set_status(self, msg: str):
        if self.active_state_label:
            self.status_var.set(f"{msg}   |   Active: {self.active_state_label}")
        else:
            self.status_var.set(msg)

    # ================== Tab 1: Encoding Preview ==================
    def _build_tab_preview(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="Encoding Preview")

        btns = ttk.Frame(tab)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="Preview Amplitudes / Digits", command=self.on_preview_amplitudes).pack(side="left", padx=4)
        ttk.Button(btns, text="Prepare / Run (sets Active)", command=self.on_prepare_state).pack(side="left", padx=4)

        self.preview_text = tk.Text(tab, height=20)
        self.preview_text.pack(fill="both", expand=True, padx=6, pady=6)

    def on_preview_amplitudes(self):
        try:
            mode = self.enc_mode.get()
            label = self.const_label.get()
            method = self.pi_method.get() if label == "π" else None
            n = int(self.n_qubits.get())
            dim = 2 ** n

            self.preview_text.delete("1.0", "end")

            if mode in {"EGF", "Terms"}:
                amps = get_series_amplitudes(
                    label, dim, method=method, phase_mode=self.phase_mode.get(),
                    normalize=True, amp_mode=("egf" if mode == "EGF" else "terms")
                )
                self.preview_text.insert("end", f"{label} {mode} amplitudes (first {min(64, dim)} of {dim}):\n\n")
                for i, a in enumerate(amps[:64]):
                    self.preview_text.insert("end", f"{i:02d}: {a.real:+.6e}{'+' if a.imag>=0 else ''}{a.imag:.6e}j\n")
                self._set_status(f"Previewed {mode} amplitudes.")

            elif mode == "Digit QROM":
                base = int(self.qrom_base.get()); bpd = int(self.qrom_bits.get()); nidx = int(self.qrom_index.get())
                x = compute_series_value(label, terms=2048, method=method)
                frac = abs(x) % 1.0
                L = 2 ** nidx
                digits = []
                tmp = frac
                for _ in range(L):
                    tmp *= base
                    d = int(tmp); digits.append(d); tmp -= d
                self.preview_text.insert("end", f"{label} digits (base {base}, first {L}):\n\n")
                self.preview_text.insert("end", " ".join(str(d) for d in digits) + "\n")
                self._set_status("Previewed digits for Digit QROM.")

            elif mode == "Periodic p/q":
                p, q = int(self.p_val.get()), int(self.q_val.get())
                self.preview_text.insert("end", f"Periodic phase e^(2πi p n / q) with p={p}, q={q}, N=2^{n}.\n")
                self.preview_text.insert("end", f"Expected QFT peaks near multiples of N/q = {2**n}/{q}.\n")
                self._set_status("Previewed periodic parameters.")

            elif mode == "Value Phase (PEA)":
                K = int(self.pea_bits.get())
                x = compute_series_value(label, terms=512, method=method) % 1.0
                self.preview_text.insert("end", f"PEA will estimate frac({label}) ≈ {x:.12f} with ~{K} bits.\n")
                self._set_status("Previewed PEA parameters.")

        except Exception as e:
            messagebox.showerror("Preview Error", str(e))

    def on_prepare_state(self):
        try:
            mode = self.enc_mode.get()
            label = self.const_label.get()
            method = self.pi_method.get() if label == "π" else None
            n = int(self.n_qubits.get())

            if mode in {"EGF", "Terms"}:
                sv = generate_series_encoding(
                    label, n_qubits=n, method=method,
                    phase_mode=self.phase_mode.get(),
                    amp_mode=("egf" if mode == "EGF" else "terms")
                )
                key = f"{label}[{mode},{self.phase_mode.get()},{method or '-'}]({n})"
                self._set_active(key, sv, also_save=True)

            elif mode == "Digit QROM":
                base = int(self.qrom_base.get()); bpd = int(self.qrom_bits.get()); nidx = int(self.qrom_index.get())
                qc = digit_qrom_circuit(label, base=base, n_index=nidx, bits_per_digit=bpd, method=method, do_measure=False)
                sv = simulate_statevector(qc)
                key = f"{label}[QROM,b{base},d{bpd},L={2**nidx}]"
                self._set_active(key, sv, also_save=True)

            elif mode == "Periodic p/q":
                p, q = int(self.p_val.get()), int(self.q_val.get())
                qc = periodic_phase_state(p, q, n_qubits=n, do_measure=False, apply_qft=False)  # pre-QFT active
                sv = simulate_statevector(qc)
                key = f"phase(p={p},q={q})[{n}]"
                self._set_active(key, sv, also_save=True)

            elif mode == "Value Phase (PEA)":
                K = int(self.pea_bits.get())
                qc = value_phase_estimation_circuit(label, K=K, method=method, do_measure=True)
                _, counts = run_circuit(qc, use_ibm=bool(self.use_ibm.get()), measure=True)
                self.preview_text.insert("end", "\nPEA counts (top 10):\n")
                for k, v in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:10]:
                    self.preview_text.insert("end", f"{k}: {v}\n")
                self._set_status("Ran PEA (results shown).")

        except Exception as e:
            messagebox.showerror("Prepare/Run Error", str(e))

    # ================== Tab 2: FFT Spectrum ==================
    def _build_tab_fft(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="FFT Spectrum")
        panel = ttk.Frame(tab)
        panel.pack(fill="x", pady=6)
        self.fft_use_active = tk.BooleanVar(value=True)
        ttk.Checkbutton(panel, text="Use Active", variable=self.fft_use_active).pack(side="left", padx=6)
        ttk.Button(panel, text="Compute FFT Spectrum", command=self.on_compute_fft).pack(side="left", padx=6)
        self.fft_canvas_holder = ttk.Frame(tab)
        self.fft_canvas_holder.pack(fill="both", expand=True, padx=6, pady=6)

    def on_compute_fft(self):
        try:
            mode = self.enc_mode.get()
            n = int(self.n_qubits.get())
            dim = 2 ** n

            if self.fft_use_active.get():
                if self.active_state is None:
                    messagebox.showinfo("FFT", "No Active state. Prepare one first.")
                    return
                amps = self.active_state.data
                label = self.active_state_label or "[active]"
                method = "-"
                subtitle = "Active"
            else:
                label = self.const_label.get()
                method = self.pi_method.get() if label == "π" else None
                if mode not in {"EGF", "Terms"}:
                    messagebox.showinfo("FFT", "Use EGF or Terms mode for Series-based FFT.")
                    return
                amps = get_series_amplitudes(
                    label, dim, method=method, phase_mode=self.phase_mode.get(),
                    normalize=True, amp_mode=("egf" if mode == "EGF" else "terms")
                )
                subtitle = f"{mode}"

            power, freqs, mets = compute_fft_spectrum_from_amplitudes(
                amps, remove_dc=True, window="hann", pad_len=int(self.pad_len.get())
            )
            for w in self.fft_canvas_holder.winfo_children():
                w.destroy()
            fig = plt.Figure(figsize=(9.5, 3.6))
            ax = fig.add_subplot(111)
            ax.plot(freqs, power, marker="o")
            ax.set_title(f"{label} {subtitle} FFT (DC={mets['dc_frac']:.3f}, H={mets['entropy_bits']:.3f} bits)")
            ax.set_xlabel("Frequency Index"); ax.set_ylabel("Power"); ax.grid(True)
            canvas = FigureCanvasTkAgg(fig, master=self.fft_canvas_holder)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            self._set_status(f"FFT done. Peak@{int(np.argmax(power))}.")
        except Exception as e:
            messagebox.showerror("FFT Error", str(e))

    # ================== Tab 3: QFT Spectrum ==================
    def _build_tab_qft(self):
        tab = ttk.Frame(self.nb)
        self.nb.add(tab, text="QFT Spectrum")
        grid = ttk.Frame(tab); grid.pack(fill="x", pady=6)

        self.qft_use_active = tk.BooleanVar(value=True)
        ttk.Checkbutton(grid, text="Use Active", variable=self.qft_use_active).grid(row=0, column=0, padx=6, pady=4, sticky="w")

        self.qft_do_measure = tk.BooleanVar(value=True)
        ttk.Checkbutton(grid, text="Measure?", variable=self.qft_do_measure).grid(row=0, column=1, padx=6, pady=4, sticky="w")

        ttk.Button(grid, text="Build QFT Circuit", command=self.on_build_qft_spectrum).grid(row=0, column=2, padx=6, pady=4, sticky="w")
        ttk.Button(grid, text="Run (Backend/Sim)", command=self.on_run_qft_circuit).grid(row=0, column=3, padx=6, pady=4, sticky="w")
        ttk.Button(grid, text="Simulate Statevector", command=self.on_simulate_qft_statevector).grid(row=0, column=4, padx=6, pady=4, sticky="w")

        self.qft_counts_text = tk.Text(tab, height=18)
        self.qft_counts_text.pack(fill="both", expand=True, padx=6, pady=6)

        self.current_qft_circuit = None

    def on_build_qft_spectrum(self):
        try:
            do_meas = bool(self.qft_do_measure.get())
            if self.qft_use_active.get():
                if self.active_state is None:
                    self._set_status("No Active state. Prepare one first.")
                    return
                vec = self.active_state.data
                vec = self._center_hann(vec=vec)  # same-length preprocessing
                qc = index_qft_spectrum_circuit(vec, use_stateprep=True, do_measure=do_meas)
                mets = self._spectrum_metrics(vec)
                self.current_qft_circuit = qc
                self.qft_counts_text.delete("1.0", "end")
                self.qft_counts_text.insert("end", f"QFT (Active) built. len={len(vec)}, DC={mets['dc_frac']:.3f}, H={mets['entropy_bits']:.3f} bits\n")
                self._set_status("QFT spectrum circuit (Active) ready.")
            else:
                label = self.const_label.get()
                method = self.pi_method.get() if label == "π" else None
                n = int(self.n_qubits.get())
                mode = self.enc_mode.get()
                if mode not in {"EGF", "Terms"}:
                    messagebox.showinfo("QFT", "Use EGF or Terms mode for Series-based QFT.")
                    return
                qc, proc_vec, mets = qft_spectrum_from_series(
                    label, n_qubits=n, method=method, phase_mode=self.phase_mode.get(),
                    amp_mode=("egf" if mode == "EGF" else "terms"),
                    preprocess=True, use_stateprep=True, do_measure=do_meas, pad_len=None
                )
                self.current_qft_circuit = qc
                self.qft_counts_text.delete("1.0", "end")
                self.qft_counts_text.insert("end", f"QFT (Series) built. len={mets['len']}, DC={mets['dc_frac']:.3f}, H={mets['entropy_bits']:.3f} bits\n")
                self._set_status("QFT spectrum circuit (Series) ready.")
        except Exception as e:
            messagebox.showerror("QFT Build Error", str(e))

    def on_run_qft_circuit(self):
        try:
            if not self.current_qft_circuit:
                self._set_status("Build QFT spectrum circuit first.")
                return
            _, counts = run_circuit(self.current_qft_circuit, use_ibm=bool(self.use_ibm.get()), measure=True)
            self.qft_counts_text.delete("1.0", "end")
            if counts:
                items = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
                self.qft_counts_text.insert("end", f"Counts ({'IBM' if self.use_ibm.get() else 'Sim'}): top {min(32, len(items))}\n\n")
                for k, v in items[:32]:
                    self.qft_counts_text.insert("end", f"{k}: {v}\n")
                self._set_status(f"Run complete. {len(counts)} bitstrings.")
            else:
                self.qft_counts_text.insert("end", "No counts available.\n")
                self._set_status("Run complete (no counts).")
        except Exception as e:
            messagebox.showerror("QFT Run Error", str(e))

    def on_simulate_qft_statevector(self):
        try:
            if not self.current_qft_circuit:
                self._set_status("Build QFT spectrum circuit first.")
                return
            # Only works if circuit has no measures
            sv = simulate_statevector(self.current_qft_circuit)
            self.qft_counts_text.insert("end", f"\nStatevector simulated:\nlen={len(sv)}\n")
            self._set_status("Statevector simulated.")
        except Exception:
            self.qft_counts_text.insert("end", "\nCircuit has measurement — statevector not available.\n")
            self._set_status("Statevector sim not available (measured circuit).")

    # ================== Tab 4: Measurement ==================
    def _build_tab_measure(self):
        tab = ttk.Frame(self.nb); self.nb.add(tab, text="Measure")
        ttk.Label(tab, text="Select saved state (or leave blank for Active):").pack(pady=5)
        self.measure_combo = ttk.Combobox(tab, values=list(self.statevectors.keys())); self._register_combo(self.measure_combo); self.measure_combo.pack()
        ttk.Button(tab, text="Simulate Measurements", command=self.on_measure_state).pack(pady=6)
        self.measure_canvas = ttk.Frame(tab); self.measure_canvas.pack(fill="both", expand=True)

    def on_measure_state(self):
        try:
            lbl, sv = self._get_active_or_selected(self.measure_combo)
            if sv is None:
                messagebox.showinfo("Missing", "No active or selected state."); return
            n = int(np.log2(len(sv.data)))
            qc = QuantumCircuit(n); qc.initialize(sv.data, range(n)); qc.measure_all()
            backend = get_backend(use_ibm=bool(self.use_ibm.get())) if self.use_ibm.get() else AerSimulator(method="density_matrix")
            counts = backend.run(qc, shots=1024).result().get_counts()
            for w in self.measure_canvas.winfo_children(): w.destroy()
            fig, ax = plt.subplots(figsize=(8, 4)); ax.bar(counts.keys(), counts.values())
            ax.set_title(f"Measurement Outcomes for {lbl}"); ax.set_xlabel("Basis"); ax.set_ylabel("Counts"); fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.measure_canvas); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Measurement Error", str(e))

    # ================== Tab 5: Amplitudes ==================
    def _build_tab_amplitudes(self):
        tab = ttk.Frame(self.nb); self.nb.add(tab, text="Amplitudes")
        row = ttk.Frame(tab); row.pack(fill="x", pady=4)
        ttk.Label(row, text="Select saved state (or leave blank for Active):").pack(side="left")
        self.amp_combo = ttk.Combobox(row, values=list(self.statevectors.keys())); self._register_combo(self.amp_combo); self.amp_combo.pack(side="left", padx=6)
        ttk.Button(row, text="Set Active from Selected", command=self.on_set_active_from_amp).pack(side="left")
        ttk.Button(tab, text="Show |amp|^2", command=self.on_plot_amplitudes).pack(pady=6)
        self.amp_canvas = ttk.Frame(tab); self.amp_canvas.pack(fill="both", expand=True)

    def on_set_active_from_amp(self):
        key = self.amp_combo.get()
        if key in self.statevectors:
            self._set_active(key, self.statevectors[key], also_save=False)

    def on_plot_amplitudes(self):
        try:
            lbl, sv = self._get_active_or_selected(self.amp_combo)
            if sv is None:
                messagebox.showerror("Error", "No active or selected state."); return
            probs = np.abs(sv.data) ** 2
            for w in self.amp_canvas.winfo_children(): w.destroy()
            fig, ax = plt.subplots(figsize=(9, 4)); ax.bar(range(len(probs)), probs)
            ax.set_title(f"|amp|^2 for {lbl}"); ax.set_xlabel("Basis Index"); ax.set_ylabel("Probability"); fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.amp_canvas); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Amplitude Plot Error", str(e))

    # ================== Tab 6: Similarity ==================
    def _build_tab_similarity(self):
        tab = ttk.Frame(self.nb); self.nb.add(tab, text="Similarity")
        ttk.Button(tab, text="Compute Cosine Similarity (saved states)", command=self.on_similarity).pack(pady=6)
        self.sim_text = tk.Text(tab, height=18); self.sim_text.pack(fill="both", expand=True, padx=6, pady=6)

    def on_similarity(self):
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            keys = list(self.statevectors.keys())
            if len(keys) < 2:
                self.sim_text.delete("1.0", "end"); self.sim_text.insert("end", "Need at least 2 saved states.\n"); return
            vecs = [np.concatenate([self.statevectors[k].data.real, self.statevectors[k].data.imag]) for k in keys]
            sim = cosine_similarity(vecs)
            self.sim_text.delete("1.0", "end")
            header = "         " + " ".join(f"{k[:10]:>10}" for k in keys) + "\n"; self.sim_text.insert("end", header)
            for i, row in enumerate(sim):
                self.sim_text.insert("end", f"{keys[i][:10]:>10}: " + " ".join(f"{v:>10.2f}" for v in row) + "\n")
        except Exception as e:
            messagebox.showerror("Similarity Error", str(e))

    # ================== Tab 7: Clustering ==================
    def _build_tab_clustering(self):
        tab = ttk.Frame(self.nb); self.nb.add(tab, text="Clustering")
        self.cluster_canvas = ttk.Frame(tab); self.cluster_canvas.pack(fill="both", expand=True)
        self.cluster_listbox = tk.Listbox(tab, selectmode=MULTIPLE, height=5, exportselection=False)
        self.cluster_listbox.pack(fill="x", padx=10, pady=6)
        ttk.Button(tab, text="Run PCA (saved states)", command=self.on_clustering).pack(pady=6)

    def on_clustering(self):
        try:
            from sklearn.decomposition import PCA
            keys = list(self.statevectors.keys())
            if len(keys) < 2:
                messagebox.showinfo("Clustering", "Save at least 2 states."); return
            sel = [self.cluster_listbox.get(i) for i in self.cluster_listbox.curselection()]
            labels = sel if sel else keys
            vecs, used = [], []
            for k in labels:
                if k in self.statevectors:
                    d = self.statevectors[k].data
                    vecs.append(np.concatenate([d.real, d.imag])); used.append(k)
            if len(vecs) < 2:
                messagebox.showinfo("Clustering", "Need at least 2 valid states."); return
            proj = PCA(n_components=2).fit_transform(np.array(vecs))
            for w in self.cluster_canvas.winfo_children(): w.destroy()
            fig, ax = plt.subplots(figsize=(6, 6))
            for i, lbl in enumerate(used):
                ax.scatter(proj[i, 0], proj[i, 1], label=lbl)
            ax.set_title("PCA Projection"); ax.grid(True); ax.legend()
            canvas = FigureCanvasTkAgg(fig, master=self.cluster_canvas); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Clustering Error", str(e))

    # ================== Tab 8: Tomography ==================
    def _build_tab_tomography(self):
        tab = ttk.Frame(self.nb); self.nb.add(tab, text="Tomography")
        if not TOMO_OK:
            ttk.Label(tab, text="qiskit-experiments not available.").pack(pady=8); return
        ttk.Label(tab, text="Select saved state (or leave blank for Active):").pack(pady=5)
        self.tomo_combo = ttk.Combobox(tab, values=list(self.statevectors.keys())); self._register_combo(self.tomo_combo); self.tomo_combo.pack()
        ttk.Button(tab, text="Run Tomography", command=self.on_run_tomography).pack(pady=6)
        self.tomo_canvas = ttk.Frame(tab); self.tomo_canvas.pack(fill="both", expand=True)

    def on_run_tomography(self):
        try:
            if not TOMO_OK: return
            lbl, sv = self._get_active_or_selected(self.tomo_combo)
            if sv is None:
                messagebox.showinfo("Tomography", "No active or selected state."); return
            n = int(np.log2(len(sv.data)))
            qc = QuantumCircuit(n); qc.initialize(sv.data, range(n))
            tomo = StateTomography(qc); circs = tomo.circuits()
            backend = get_backend(use_ibm=bool(self.use_ibm.get())) if self.use_ibm.get() else Aer.get_backend("qasm_simulator")
            result = backend.run(circs, shots=2048).result()
            data = ExperimentData(experiment=tomo); data.add_data(result)
            analysis_result = tomo.analysis().run(data)
            reconstructed = analysis_result.result.data["state"]
            fid = state_fidelity(DensityMatrix(sv), reconstructed)
            for w in self.tomo_canvas.winfo_children(): w.destroy()
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.set_title(f"Fidelity: {fid:.6f}  ({lbl})")
            ax.text(0.5, 0.5, f"{fid:.6f}", fontsize=20, ha="center", va="center")
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.tomo_canvas); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Tomography Error", str(e))

    # ================== Tab 9: Entanglement ==================
    def _build_tab_entanglement(self):
        tab = ttk.Frame(self.nb); self.nb.add(tab, text="Entanglement")

        self.ent_mode = tk.StringVar(value="series")
        ttk.Radiobutton(tab, text="Simple (2-qubit fractional)", variable=self.ent_mode, value="simple").grid(row=0, column=0, sticky="w", padx=4)
        ttk.Radiobutton(tab, text="Series registers", variable=self.ent_mode, value="series").grid(row=0, column=1, sticky="w", padx=4)
        ttk.Radiobutton(tab, text="Multi (CSV)", variable=self.ent_mode, value="multi").grid(row=0, column=2, sticky="w", padx=4)

        self.ent1 = tk.StringVar(value="π"); self.ent2 = tk.StringVar(value="ζ(3)")
        ttk.Label(tab, text="Const 1:").grid(row=1, column=0, sticky="e"); ttk.Combobox(tab, textvariable=self.ent1, values=["π","e","ln(2)","ζ(2)","ζ(3)","γ","Catalan","φ"]).grid(row=1, column=1, sticky="w")
        ttk.Label(tab, text="Const 2:").grid(row=2, column=0, sticky="e"); ttk.Combobox(tab, textvariable=self.ent2, values=["π","e","ln(2)","ζ(2)","ζ(3)","γ","Catalan","φ"]).grid(row=2, column=1, sticky="w")

        self.series_qubits_each = tk.IntVar(value=3)
        self.series_pattern = tk.StringVar(value="cx_all")
        ttk.Label(tab, text="Series qubits each:").grid(row=3, column=0, sticky="e"); ttk.Spinbox(tab, from_=1, to=8, textvariable=self.series_qubits_each, width=5).grid(row=3, column=1, sticky="w")
        ttk.Label(tab, text="Pattern:").grid(row=3, column=2, sticky="e"); ttk.Combobox(tab, textvariable=self.series_pattern, values=["cx_all","bell_on_0"], state="readonly", width=10).grid(row=3, column=3, sticky="w")

        ttk.Label(tab, text="Multi CSV (e.g. π,ζ(3),e)").grid(row=4, column=0, sticky="e")
        self.multi_csv = tk.Entry(tab, width=40); self.multi_csv.insert(0, "π,ζ(3),e"); self.multi_csv.grid(row=4, column=1, columnspan=2, sticky="w")

        self.multi_topology = tk.StringVar(value="chain")
        ttk.Label(tab, text="Topology:").grid(row=4, column=3, sticky="e"); ttk.Combobox(tab, textvariable=self.multi_topology, values=["chain","star","all_to_all"], state="readonly", width=10).grid(row=4, column=4, sticky="w")

        ttk.Button(tab, text="Build & Analyze", command=self.on_ent_analyze).grid(row=5, column=0, columnspan=5, pady=6)

        self.ent_canvas = ttk.Frame(tab); self.ent_canvas.grid(row=6, column=0, columnspan=5, sticky="nsew")

    def on_ent_analyze(self):
        try:
            for w in self.ent_canvas.winfo_children(): w.destroy()
            mode = self.ent_mode.get()

            if mode == "simple":
                c1 = compute_series(self.ent1.get(), 100)
                c2 = compute_series(self.ent2.get(), 100)
                qc = encode_entangled_constants(c1, c2)
                sv = simulate_statevector(qc)
                cut = 1

            elif mode == "series":
                n_each = int(self.series_qubits_each.get())
                c1, c2 = self.ent1.get(), self.ent2.get()
                m1 = self.pi_method.get() if c1 == "π" else None
                m2 = self.pi_method.get() if c2 == "π" else None
                qc = entangle_series_registers(
                    c1, c2, n_qubits_each=n_each, method1=m1, method2=m2,
                    phase_mode1=self.phase_mode.get(), phase_mode2=self.phase_mode.get(),
                    pattern=self.series_pattern.get(), use_stateprep=True, do_measure=False
                )
                sv = simulate_statevector(qc); cut = n_each

            else:  # multi
                labels = [s.strip() for s in self.multi_csv.get().split(",") if s.strip()]
                if len(labels) < 2:
                    messagebox.showinfo("Multi", "Provide at least 2 labels."); return
                n_each = int(self.series_qubits_each.get())
                topo = self.multi_topology.get()
                qc = entangle_series_multi(
                    labels, n_qubits_each=n_each, methods=None,
                    phase_mode=self.phase_mode.get(), topology=topo,
                    use_stateprep=True, do_measure=False
                )
                sv = simulate_statevector(qc); cut = n_each * (len(labels)//2)  # heuristic

            rhoA, rhoB, rhoAB = analyze_tensor_structure(sv)
            S = perform_schmidt_decomposition(sv, cut=cut)

            fig, axs = plt.subplots(1, 2, figsize=(10, 4))
            probs = np.abs(sv.data) ** 2
            axs[0].bar(range(len(probs)), probs); axs[0].set_title("Entangled State Spectrum")
            axs[1].imshow(np.outer(S, S), cmap="magma"); axs[1].set_title("Schmidt (outer product)")
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.ent_canvas); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)

            self._set_active(f"ent[{mode}]", sv, also_save=False)

        except Exception as e:
            messagebox.showerror("Entanglement Error", str(e))

    # ================== Tab 10: Gates ==================
    def _build_tab_gates(self):
        tab = ttk.Frame(self.nb); self.nb.add(tab, text="Gates")
        ttk.Button(tab, text="Draw Current QFT Circuit (if any)", command=self.on_draw_qft).pack(pady=6)
        ttk.Button(tab, text="Draw Prep for Active/Last Saved", command=self.on_draw_prep_for_last).pack(pady=6)
        self.gate_canvas = ttk.Frame(tab); self.gate_canvas.pack(fill="both", expand=True)

    def on_draw_qft(self):
        try:
            for w in self.gate_canvas.winfo_children(): w.destroy()
            if not getattr(self, "current_qft_circuit", None):
                self._set_status("No QFT circuit yet."); return
            fig = self.current_qft_circuit.draw(output="mpl", filename=None, interactive=False)
            canvas = FigureCanvasTkAgg(fig, master=self.gate_canvas); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Gate Draw Error", str(e))

    def on_draw_prep_for_last(self):
        try:
            for w in self.gate_canvas.winfo_children(): w.destroy()
            if self.active_state is not None:
                sv = self.active_state; label = self.active_state_label or "[active]"
            else:
                keys = list(self.statevectors.keys())
                if not keys: self._set_status("No states available."); return
                label = keys[-1]; sv = self.statevectors[label]
            n = int(np.log2(len(sv.data)))
            qc = QuantumCircuit(n); qc.initialize(sv.data, range(n))
            fig = qc.draw(output="mpl", filename=None, interactive=False)
            canvas = FigureCanvasTkAgg(fig, master=self.gate_canvas); canvas.draw(); canvas.get_tk_widget().pack(fill="both", expand=True)
            self._set_status(f"Drew prep circuit for {label}")
        except Exception as e:
            messagebox.showerror("Gate Draw Error", str(e))

    # ================== Tab 11: State I/O ==================
    def _build_tab_state_io(self):
        tab = ttk.Frame(self.nb); self.nb.add(tab, text="State I/O")
        ttk.Button(tab, text="Save Active", command=self.on_save_active).pack(pady=6)
        ttk.Button(tab, text="Load State (becomes Active)", command=self.on_load_state).pack(pady=6)

    def on_save_active(self):
        try:
            if save_statevector is None:
                messagebox.showinfo("Save", "state_io.save_statevector not available."); return
            if self.active_state is None:
                messagebox.showinfo("Save", "No active state."); return
            label = self.active_state_label or "active_state"
            save_statevector(self.active_state, label)
            self.statevectors[label] = self.active_state
            self._refresh_all_combos()
            self._set_status(f"Saved: {label}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def on_load_state(self):
        try:
            if load_statevector is None:
                messagebox.showinfo("Load", "state_io.load_statevector not available."); return
            label, sv = load_statevector()
            # ensure dtype
            sv = Statevector(np.asarray(sv.data, dtype=complex))
            self._set_active(label, sv, also_save=True)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    # ================== Tab 12: Basis States ==================
    def _build_tab_basis(self):
        tab = ttk.Frame(self.nb); self.nb.add(tab, text="Basis States")
        row = ttk.Frame(tab); row.pack(fill="x", pady=4)
        ttk.Label(row, text="Select saved state (or leave blank for Active):").pack(side="left")
        self.basis_combo = ttk.Combobox(row, values=list(self.statevectors.keys())); self._register_combo(self.basis_combo); self.basis_combo.pack(side="left", padx=6)
        ttk.Button(row, text="Set Active from Selected", command=self.on_set_active_from_basis).pack(side="left")
        ttk.Button(tab, text="Show Basis Amplitudes", command=self.on_show_basis).pack(pady=6)
        self.basis_text = tk.Text(tab, height=22, font=("Courier", 10)); self.basis_text.pack(fill="both", expand=True, padx=6, pady=6)

    def on_set_active_from_basis(self):
        key = self.basis_combo.get()
        if key in self.statevectors:
            self._set_active(key, self.statevectors[key], also_save=False)

    def on_show_basis(self):
        try:
            lbl, sv = self._get_active_or_selected(self.basis_combo)
            if sv is None:
                messagebox.showinfo("Basis", "No active or selected state."); return
            n = int(np.log2(len(sv.data)))
            self.basis_text.delete("1.0", "end")
            for i, a in enumerate(sv.data):
                self.basis_text.insert("end", f"|{i:0{n}b}⟩  →  {a.real:+.6f}{'+' if a.imag>=0 else ''}{a.imag:.6f}j\n")
        except Exception as e:
            messagebox.showerror("Basis Error", str(e))

    # ---------- helpers for QFT metrics ----------
    def _center_hann(self, vec: np.ndarray) -> np.ndarray:
        x = vec.astype(np.complex128)
        m = np.mean(x)
        x = x - m
        if x.size > 1:
            x = x * np.hanning(x.size)
        return x

    def _spectrum_metrics(self, vec: np.ndarray) -> dict:
        X = np.fft.fft(vec)
        P = np.abs(X) ** 2
        S = P.sum() or 1.0
        dc = float(P[0] / S)
        p = P / S
        p = p[p > 0]
        H = float(-np.sum(p * np.log2(p)))
        return {"dc_frac": dc, "entropy_bits": H}


if __name__ == "__main__":
    app = QTEGUI()
    app.mainloop()

