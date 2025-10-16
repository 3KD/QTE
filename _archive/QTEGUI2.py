# QTEGUI.py — Quantum Transcendental Encoder (QTE)
# Modes: EGF / Terms / Periodic p/q / Value Phase (PEA) / Digit QROM
# Multi-constant picker with per-constant methods + syntax:  π(Machin), e, Li(2,0.5)
# Extras: register block labeling, grid overlays, Schmidt entropies, register marginals

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, MULTIPLE

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from typing import List, Dict, Optional, Tuple

# Qiskit
from qiskit import QuantumCircuit, transpile
from qiskit_aer import Aer
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
    analyze_tensor_structure, perform_schmidt_decomposition,
    value_phase_estimation_circuit, periodic_phase_state, digit_qrom_circuit,
)

# -----------------------------
# Constant picker & parsing
# -----------------------------

METHOD_CHOICES: Dict[str, List[str]] = {
    "π": ["Leibniz", "Nilakantha", "Machin", "Ramanujan", "Chudnovsky"],
    "pi": ["Leibniz", "Nilakantha", "Machin", "Ramanujan", "Chudnovsky"],
}
DEFAULT_METHOD: Dict[str, str] = {"π": "Machin", "pi": "Machin"}
KNOWN_METHODS = {m.lower() for arr in METHOD_CHOICES.values() for m in arr}

SUGGESTED_LABELS = [
    "π", "e", "ln(2)", "ζ(2)", "ζ(3)", "γ", "Catalan", "φ",
    "exp(π)", "2^√2", "Liouville", "Champernowne10",
    "Li(2,0.5)", "polylog(3, 0.5)"
]

def _norm_label(label: str) -> str:
    s = label.strip()
    return "π" if s.lower() == "pi" else s

def _supports_method(label: str) -> bool:
    l = _norm_label(label).strip().lower()
    return l in ("π",)

def _canonical_method(label: str, method: Optional[str]) -> Optional[str]:
    lab = _norm_label(label)
    if not _supports_method(lab):
        return None
    if not method:
        return DEFAULT_METHOD.get(lab, "Machin")
    opts = METHOD_CHOICES.get(lab, [])
    return method if method in opts else DEFAULT_METHOD.get(lab, "Machin")

def _split_top_level(s: str) -> List[str]:
    out, depth, buf = [], 0, []
    for ch in s:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth = max(0, depth - 1)
        if ch == ',' and depth == 0:
            token = ''.join(buf).strip()
            if token:
                out.append(token)
            buf = []
        else:
            buf.append(ch)
    token = ''.join(buf).strip()
    if token:
        out.append(token)
    return out

def _parse_constants_syntax(s: str) -> List[Tuple[str, Optional[str]]]:
    """
    Grammar (informal):
      token := LABEL [ "(" ARGS ")" ] [ "(" METHOD ")" ]?
    Only π/pi consumes METHOD (Leibniz, Nilakantha, Machin, Ramanujan, Chudnovsky).
    Examples:
      "π(Machin)" -> ("π", "Machin")
      "Li(2,0.5)" -> ("Li(2,0.5)", None)
    """
    parts = _split_top_level(s)
    out: List[Tuple[str, Optional[str]]] = []
    for raw in parts:
        t = raw.strip()
        if not t:
            continue

        # locate outermost trailing "(...)"
        depth, last_open, last_close = 0, -1, -1
        for i, ch in enumerate(t):
            if ch == '(':
                if depth == 0:
                    last_open = i
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    last_close = i
        if depth != 0:
            raise ValueError(f"Unbalanced parentheses in: {t}")

        label, method = t, None

        if last_open != -1 and last_close == len(t) - 1:
            inside = t[last_open + 1:last_close].strip()
            before = t[:last_open].strip()
            if inside.lower() in KNOWN_METHODS and _supports_method(before or t):
                label = before or t
                method = inside
            else:
                label = t  # parentheses belong to label (e.g., Li(2,0.5))

        label = _norm_label(label)

        if _supports_method(label):
            method = _canonical_method(label, method)
        else:
            method = None

        out.append((label, method))
    return out

def _constants_to_syntax(pairs: List[Tuple[str, Optional[str]]]) -> str:
    toks = []
    for lab, meth in pairs:
        lab = _norm_label(lab)
        if meth and _supports_method(lab):
            toks.append(f"{lab}({meth})")
        else:
            toks.append(lab)
    return ", ".join(toks)

class ConstantPicker(tk.Toplevel):
    def __init__(self, master, initial: List[Tuple[str, Optional[str]]]):
        super().__init__(master)
        self.title("Pick constants")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self._selected: Dict[str, Optional[str]] = {_norm_label(lab): meth for lab, meth in initial}

        body = ttk.Frame(self, padding=8)
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky="nsw", padx=(0,10))
        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nse")

        ttk.Label(left, text="Constants").pack(anchor="w")

        self.box = tk.Listbox(left, selectmode=MULTIPLE, height=12, exportselection=False, width=28)
        for lab in SUGGESTED_LABELS:
            self.box.insert("end", lab)
        self.box.pack()
        self.box.bind("<<ListboxSelect>>", self._on_select)

        for i, lab in enumerate(SUGGESTED_LABELS):
            if _norm_label(lab) in self._selected:
                self.box.selection_set(i)

        addrow = ttk.Frame(left); addrow.pack(fill="x", pady=(8,0))
        self.custom_var = tk.StringVar(value="")
        ttk.Entry(addrow, textvariable=self.custom_var, width=20).pack(side="left")
        ttk.Button(addrow, text="Add", command=self._add_custom).pack(side="left", padx=4)

        ttk.Label(right, text="Method (for highlighted π)").grid(row=0, column=0, sticky="w")
        self.method_var = tk.StringVar(value="")
        self.method_combo = ttk.Combobox(right, textvariable=self.method_var, state="disabled",
                                         values=METHOD_CHOICES.get("π", []), width=18)
        self.method_combo.grid(row=1, column=0, sticky="w", pady=(2,8))
        ttk.Button(right, text="Set Method", command=self._apply_method).grid(row=2, column=0, sticky="w")

        btns = ttk.Frame(body); btns.grid(row=1, column=0, columnspan=2, sticky="e", pady=(10,0))
        ttk.Button(btns, text="OK", command=self._ok).pack(side="right", padx=6)
        ttk.Button(btns, text="Cancel", command=self._cancel).pack(side="right")

        self.result: Optional[List[Tuple[str, Optional[str]]]] = None

    def _on_select(self, _evt=None):
        sel = self._current_highlight()
        if sel and _supports_method(sel):
            self.method_combo.config(state="readonly", values=METHOD_CHOICES.get(_norm_label(sel), []))
            self.method_var.set(self._selected.get(_norm_label(sel)) or _canonical_method(sel, None))
        else:
            self.method_combo.config(state="disabled")
            self.method_var.set("")

    def _current_highlight(self) -> Optional[str]:
        idxs = self.box.curselection()
        if not idxs:
            return None
        return _norm_label(self.box.get(idxs[0]).strip())

    def _apply_method(self):
        sel = self._current_highlight()
        if not sel or not _supports_method(sel):
            return
        meth = self.method_var.get().strip()
        if not meth:
            meth = _canonical_method(sel, None)
        self._selected[sel] = _canonical_method(sel, meth)

    def _add_custom(self):
        lab = _norm_label(self.custom_var.get().strip())
        if not lab:
            return
        self._selected.setdefault(lab, _canonical_method(lab, None))
        self.box.insert("end", lab)
        self.custom_var.set("")

    def _ok(self):
        final: List[Tuple[str, Optional[str]]] = []
        for i in self.box.curselection():
            lab = _norm_label(self.box.get(i).strip())
            final.append((lab, self._selected.get(lab)))
        self.result = final
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()

# -----------------------------
# GUI
# -----------------------------

class QTEGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quantum Transcendental Encoder (QTE)")
        self.geometry("1180x860")

        self.statevectors: Dict[str, Statevector] = {}
        self.active_state_label: Optional[str] = None
        self.active_state: Optional[Statevector] = None

        # -------- Top controls --------
        top = ttk.Frame(self); top.pack(fill="x", padx=10, pady=8)

        # NEW: constants syntax + picker
        ttk.Label(top, text="Constant(s)").grid(row=0, column=0, sticky="w")
        self.const_syntax = tk.StringVar(value="π")
        ttk.Entry(top, textvariable=self.const_syntax, width=36).grid(row=0, column=1, padx=(4,6))
        ttk.Button(top, text="Pick…", command=self.on_pick_constants).grid(row=0, column=2, padx=(0,12))

        # π method (convenience default if single π without explicit method)
        self.pi_method = tk.StringVar(value="Machin")
        ttk.Label(top, text="π method").grid(row=0, column=3, sticky="w")
        ttk.Combobox(top, textvariable=self.pi_method,
                     values=METHOD_CHOICES["π"], state="readonly", width=12).grid(row=0, column=4, padx=(4, 12))

        self.phase_mode = tk.StringVar(value="sign")
        ttk.Label(top, text="Phase").grid(row=0, column=5, sticky="w")
        ttk.Combobox(top, textvariable=self.phase_mode,
                     values=["sign", "abs"], state="readonly", width=6).grid(row=0, column=6, padx=(4, 12))

        self.n_qubits = tk.IntVar(value=6)
        ttk.Label(top, text="#qubits").grid(row=0, column=7, sticky="w")
        ttk.Spinbox(top, from_=1, to=12, textvariable=self.n_qubits, width=5).grid(row=0, column=8, padx=(4, 12))

        self.pad_len = tk.IntVar(value=128)
        ttk.Label(top, text="Pad (FFT)").grid(row=0, column=9, sticky="w")
        ttk.Spinbox(top, from_=16, to=4096, increment=16, textvariable=self.pad_len, width=7).grid(row=0, column=10, padx=(4, 12))

        self.use_ibm = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, text="Use IBM", variable=self.use_ibm, command=self._maybe_prompt_ibm).grid(row=0, column=11, padx=(6, 6))

        # Multi controls
        self.reg_qubits = tk.IntVar(value=3)
        self.multi_topology = tk.StringVar(value="chain")
        ttk.Label(top, text="RegQ").grid(row=1, column=0, sticky="e")
        ttk.Spinbox(top, from_=1, to=8, textvariable=self.reg_qubits, width=5).grid(row=1, column=1, sticky="w")
        ttk.Label(top, text="Topology").grid(row=1, column=2, sticky="e")
        ttk.Combobox(top, textvariable=self.multi_topology, values=["chain","star","all_to_all"], state="readonly", width=10).grid(row=1, column=3, sticky="w")

        # Encoding mode row
        self.enc_mode = tk.StringVar(value="EGF")
        ttk.Label(top, text="Encoding").grid(row=1, column=4, sticky="e")
        ttk.Combobox(top, textvariable=self.enc_mode,
                     values=["EGF", "Terms", "Periodic p/q", "Value Phase (PEA)", "Digit QROM"],
                     state="readonly", width=16).grid(row=1, column=5, padx=(4, 12))

        self.pea_bits = tk.IntVar(value=10)
        ttk.Label(top, text="PEA bits").grid(row=1, column=6, sticky="e")
        ttk.Spinbox(top, from_=2, to=20, textvariable=self.pea_bits, width=5).grid(row=1, column=7, padx=(4,12))

        self.p_val = tk.IntVar(value=22); self.q_val = tk.IntVar(value=7)
        ttk.Label(top, text="p/q").grid(row=1, column=8, sticky="e")
        ttk.Spinbox(top, from_=1, to=100000, textvariable=self.p_val, width=7).grid(row=1, column=9, sticky="w")
        ttk.Spinbox(top, from_=1, to=100000, textvariable=self.q_val, width=7).grid(row=1, column=10, sticky="w")

        self.qrom_base = tk.IntVar(value=10)
        self.qrom_bits = tk.IntVar(value=4)
        self.qrom_index = tk.IntVar(value=6)
        ttk.Label(top, text="QROM base/bits/index").grid(row=1, column=11, sticky="e")
        ttk.Spinbox(top, from_=2, to=16, textvariable=self.qrom_base, width=5).grid(row=1, column=12)
        ttk.Spinbox(top, from_=1, to=8, textvariable=self.qrom_bits, width=4).grid(row=1, column=13)
        ttk.Spinbox(top, from_=1, to=10, textvariable=self.qrom_index, width=5).grid(row=1, column=14)

        # Status line
        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(self, textvariable=self.status_var, anchor="w").pack(fill="x", padx=10, pady=(0, 6))

        # Notebook tabs
        self.nb = ttk.Notebook(self); self.nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))
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

    # -------- constants helpers --------
    def on_pick_constants(self):
        pairs = self._current_constants(default_if_empty=True)
        dlg = ConstantPicker(self, pairs)
        self.wait_window(dlg)
        if dlg.result is not None:
            self.const_syntax.set(_constants_to_syntax(dlg.result))

    def _current_constants(self, *, default_if_empty=False) -> List[Tuple[str, Optional[str]]]:
        s = self.const_syntax.get().strip()
        if not s and default_if_empty:
            s = "π"
        try:
            pairs = _parse_constants_syntax(s) if s else []
        except Exception as e:
            messagebox.showerror("Constant(s) parse error", str(e))
            return []
        if len(pairs) == 1 and _supports_method(pairs[0][0]) and not pairs[0][1]:
            pairs = [(pairs[0][0], self.pi_method.get())]
        return pairs

    def _single_constant_required(self, ctx: str) -> Optional[Tuple[str, Optional[str]]]:
        pairs = self._current_constants(default_if_empty=True)
        if len(pairs) != 1:
            messagebox.showinfo(ctx, f"{ctx} requires a single constant. Current selection: {len(pairs)}.\n"
                                     f"Use Prepare/Run to build a multi-register Active state, then run {ctx} with 'Use Active'.")
            return None
        return pairs[0]

    # -------- format/helpers --------
    def _fmt_amp(self, a: complex) -> str:
        return f"{a.real:+.6e}{'+' if a.imag>=0 else ''}{a.imag:.6e}j"

    def _preview_multi_registers(self, pairs: List[Tuple[str, Optional[str]]], mode: str, n_each: int):
        """Print per-register preview for multi selections."""
        self.preview_text.insert("end", f"Multi-constant preview ({mode}). Each register: {n_each} qubits.\n\n")
        dim_each = 2 ** n_each
        for (lab, meth) in pairs:
            try:
                amps = get_series_amplitudes(
                    lab, dim_each,
                    method=meth,
                    phase_mode=self.phase_mode.get(),
                    normalize=True,
                    amp_mode=("egf" if mode == "EGF" else "terms")
                )
                self.preview_text.insert("end", f"{lab}{f'[{meth}]' if meth else ''} → first {min(8, dim_each)} amps:\n")
                for i, a in enumerate(amps[:8]):
                    self.preview_text.insert("end", f"  {i:02d}: {self._fmt_amp(a)}\n")
                self.preview_text.insert("end", "\n")
            except Exception as ex:
                self.preview_text.insert("end", f"{lab}: preview error: {ex}\n\n")

    # NEW: parse multi label and get Schmidt entropy
    def _parse_multi_label(self, label: str):
        """Parse labels like: multi[π,e,ln(2)|chain|3] → (['π','e','ln(2)'], 'chain', 3)."""
        if not isinstance(label, str) or not label.startswith("multi["):
            return None
        try:
            inside = label.split("multi[", 1)[1]
            regs_part, topo, tail = inside.split("|", 2)
            regq = int(tail.split("]", 1)[0])
            regs = [s.strip() for s in regs_part.split(",") if s.strip()]
            return regs, topo, regq
        except Exception:
            return None

    def _schmidt_entropy_bits(self, sv: Statevector, cut: int) -> float:
        """Von Neumann entropy (bits) of left block of 'cut' qubits vs the rest (pure state)."""
        try:
            S = perform_schmidt_decomposition(sv, cut=cut)
            p = (S ** 2)
            p = p[p > 1e-15]
            return float(-np.sum(p * np.log2(p)))
        except Exception:
            return float("nan")

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
        tab = ttk.Frame(self.nb); self.nb.add(tab, text="Encoding Preview")

        btns = ttk.Frame(tab); btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="Preview Amplitudes / Digits", command=self.on_preview_amplitudes).pack(side="left", padx=4)
        ttk.Button(btns, text="Prepare / Run (sets Active)", command=self.on_prepare_state).pack(side="left", padx=4)

        self.preview_text = tk.Text(tab, height=20)
        self.preview_text.pack(fill="both", expand=True, padx=6, pady=6)

    def on_preview_amplitudes(self):
        try:
            mode = self.enc_mode.get()
            pairs = self._current_constants(default_if_empty=True)
            n = int(self.n_qubits.get()); dim = 2 ** n

            self.preview_text.delete("1.0", "end")

            if len(pairs) > 1 and mode in {"EGF", "Terms"}:
                n_each = int(self.reg_qubits.get())
                self._preview_multi_registers(pairs, mode, n_each)
                self.preview_text.insert("end", "Use 'Prepare / Run' to create the entangled multi-register Active state.\n")
                return

            if mode in {"EGF", "Terms"}:
                label, method = pairs[0]
                amps = get_series_amplitudes(
                    label, dim, method=method, phase_mode=self.phase_mode.get(),
                    normalize=True, amp_mode=("egf" if mode == "EGF" else "terms")
                )
                self.preview_text.insert("end", f"{label} {mode} amplitudes (first {min(64, dim)} of {dim}):\n\n")
                for i, a in enumerate(amps[:64]):
                    self.preview_text.insert("end", f"{i:02d}: {self._fmt_amp(a)}\n")
                self._set_status(f"Previewed {mode} amplitudes.")

            elif mode == "Digit QROM":
                label, method = pairs[0]
                base = int(self.qrom_base.get()); bpd = int(self.qrom_bits.get()); nidx = int(self.qrom_index.get())
                x = compute_series_value(label, terms=2048, method=method)
                frac = abs(x) % 1.0
                L = 2 ** nidx
                digits, tmp = [], frac
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
                label, method = pairs[0]
                K = int(self.pea_bits.get())
                x = compute_series_value(label, terms=512, method=method) % 1.0
                self.preview_text.insert("end", f"PEA will estimate frac({label}) ≈ {x:.12f} with ~{K} bits.\n")
                self._set_status("Previewed PEA parameters.")

        except Exception as e:
            messagebox.showerror("Preview Error", str(e))

    def on_prepare_state(self):
        try:
            mode = self.enc_mode.get()
            pairs = self._current_constants(default_if_empty=True)
            n = int(self.n_qubits.get())

            if len(pairs) == 1:
                label, method = pairs[0]
                if mode in {"EGF", "Terms"}:
                    sv = generate_series_encoding(
                        label, n_qubits=n, method=method,
                        phase_mode=self.phase_mode.get(),
                        amp_mode=("egf" if mode == "EGF" else "terms")
                    )
                    key = f"{label}[{mode},{self.phase_mode.get()},{method or '-'}]({n})"
                    self._set_active(key, sv, also_save=True)
                    self.preview_text.delete("1.0", "end")
                    self.preview_text.insert("end", f"Prepared Active: {key}\nlen={len(sv.data)}\n")

                elif mode == "Digit QROM":
                    base = int(self.qrom_base.get()); bpd = int(self.qrom_bits.get()); nidx = int(self.qrom_index.get())
                    qc = digit_qrom_circuit(label, base=base, n_index=nidx, bits_per_digit=bpd, method=method, do_measure=False)
                    sv = simulate_statevector(qc)
                    key = f"{label}[QROM,b{base},d{bpd},L={2**nidx}]"
                    self._set_active(key, sv, also_save=True)
                    self.preview_text.delete("1.0", "end")
                    self.preview_text.insert("end", f"Prepared Active: {key}\nlen={len(sv.data)}\n")

                elif mode == "Periodic p/q":
                    p, q = int(self.p_val.get()), int(self.q_val.get())
                    qc = periodic_phase_state(p, q, n_qubits=n, do_measure=False, apply_qft=False)
                    sv = simulate_statevector(qc)
                    key = f"phase(p={p},q={q})[{n}]"
                    self._set_active(key, sv, also_save=True)
                    self.preview_text.delete("1.0", "end")
                    self.preview_text.insert("end", f"Prepared Active: {key}\nlen={len(sv.data)}\n")

                elif mode == "Value Phase (PEA)":
                    K = int(self.pea_bits.get())
                    qc = value_phase_estimation_circuit(label, K=K, method=method, do_measure=True)
                    _, counts = run_circuit(qc, use_ibm=bool(self.use_ibm.get()), measure=True)
                    self.preview_text.insert("end", "\nPEA counts (top 10):\n")
                    if counts:
                        for k, v in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:10]:
                            self.preview_text.insert("end", f"{k}: {v}\n")
                    else:
                        self.preview_text.insert("end", "(no counts)\n")
                    self._set_status("Ran PEA (results shown).")

            else:
                labels = [lab for lab, _ in pairs]
                methods = [meth for _, meth in pairs]
                n_each = int(self.reg_qubits.get())
                topo = self.multi_topology.get()
                qc = entangle_series_multi(
                    labels, n_qubits_each=n_each, methods=methods,
                    phase_mode=self.phase_mode.get(), topology=topo,
                    use_stateprep=True, do_measure=False
                )
                sv = simulate_statevector(qc)
                key = f"multi[{','.join(labels)}|{topo}|{n_each}]"
                self._set_active(key, sv, also_save=True)
                # Multi summary in preview
                self.preview_text.delete("1.0", "end")
                total_qubits = n_each * len(labels)
                self.preview_text.insert("end",
                    f"Prepared entangled multi-register Active:\n"
                    f"  Labels: {', '.join(labels)}\n"
                    f"  Topology: {topo}\n"
                    f"  Qubits per register: {n_each}  |  Total qubits: {total_qubits}\n"
                    f"  State length: {len(sv.data)}\n"
                )

        except Exception as e:
            messagebox.showerror("Prepare/Run Error", str(e))

    # ================== Tab 2: FFT Spectrum ==================
    def _build_tab_fft(self):
        tab = ttk.Frame(self.nb); self.nb.add(tab, text="FFT Spectrum")
        panel = ttk.Frame(tab); panel.pack(fill="x", pady=6)
        self.fft_use_active = tk.BooleanVar(value=True)
        ttk.Checkbutton(panel, text="Use Active", variable=self.fft_use_active).pack(side="left", padx=6)
        ttk.Button(panel, text="Compute FFT Spectrum", command=self.on_compute_fft).pack(side="left", padx=6)
        self.fft_canvas_holder = ttk.Frame(tab); self.fft_canvas_holder.pack(fill="both", expand=True, padx=6, pady=6)

    def on_compute_fft(self):
        try:
            mode = self.enc_mode.get()
            n = int(self.n_qubits.get()); dim = 2 ** n

            if self.fft_use_active.get():
                if self.active_state is None:
                    messagebox.showinfo("FFT", "No Active state. Prepare one first.")
                    return
                amps = self.active_state.data
                label = self.active_state_label or "[active]"
                subtitle = "Active"
            else:
                single = self._single_constant_required("FFT")
                if not single:
                    return
                label, method = single
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
            for w in self.fft_canvas_holder.winfo_children(): w.destroy()
            fig = plt.Figure(figsize=(9.5, 3.6)); ax = fig.add_subplot(111)
            ax.plot(freqs, power, marker="o")
            ax.set_title(f"{label} {subtitle} FFT (DC={mets['dc_frac']:.3f}, H={mets['entropy_bits']:.3f} bits)")
            ax.set_xlabel("Frequency Index"); ax.set_ylabel("Power"); ax.grid(True)
            canvas = FigureCanvasTkAgg(fig, master=self.fft_canvas_holder); canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            self._set_status(f"FFT done. Peak@{int(np.argmax(power))}.")
        except Exception as e:
            messagebox.showerror("FFT Error", str(e))

    # ================== Tab 3: QFT Spectrum ==================
    def _build_tab_qft(self):
        tab = ttk.Frame(self.nb); self.nb.add(tab, text="QFT Spectrum")
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
                vec = self._center_hann(vec=vec)
                qc = index_qft_spectrum_circuit(vec, use_stateprep=True, do_measure=do_meas)
                mets = self._spectrum_metrics(vec)
                self.current_qft_circuit = qc
                self.qft_counts_text.delete("1.0", "end")
                self.qft_counts_text.insert("end", f"QFT (Active) built. len={len(vec)}, DC={mets['dc_frac']:.3f}, H={mets['entropy_bits']:.3f} bits\n")
                self._set_status("QFT spectrum circuit (Active) ready.")
            else:
                single = self._single_constant_required("QFT")
                if not single:
                    return
                label, method = single
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

        # NEW: register helpers + deterministic controls
        optrow = ttk.Frame(tab); optrow.pack(pady=(0,6))
        self.show_reg_grid = tk.BooleanVar(value=True)
        ttk.Checkbutton(optrow, text="Show register grid", variable=self.show_reg_grid).pack(side="left", padx=6)

        self.meas_shots = tk.IntVar(value=1024)
        ttk.Label(optrow, text="Shots").pack(side="left")
        ttk.Spinbox(optrow, from_=1, to=131072, textvariable=self.meas_shots, width=7).pack(side="left", padx=4)

        self.fix_seed = tk.BooleanVar(value=True)
        ttk.Checkbutton(optrow, text="Fix RNG", variable=self.fix_seed).pack(side="left", padx=6)
        self.meas_seed = tk.IntVar(value=12345)
        ttk.Label(optrow, text="Seed").pack(side="left")
        ttk.Spinbox(optrow, from_=0, to=2**31-1, textvariable=self.meas_seed, width=10).pack(side="left", padx=4)

        self.exact_counts = tk.BooleanVar(value=False)
        ttk.Checkbutton(optrow, text="Exact (shots×|amp|²)", variable=self.exact_counts).pack(side="left", padx=6)

        ttk.Button(optrow, text="Show Register Marginals", command=self.on_show_marginals).pack(side="left", padx=12)

        self.measure_canvas = ttk.Frame(tab); self.measure_canvas.pack(fill="both", expand=True)

    def on_measure_state(self):
        try:
            lbl, sv = self._get_active_or_selected(self.measure_combo)
            if sv is None:
                messagebox.showinfo("Missing", "No active or selected state."); return

            n = int(np.log2(len(sv.data)))
            shots = int(self.meas_shots.get())

            # Build counts
            if self.exact_counts.get():
                # Deterministic counts from the statevector
                probs = np.abs(sv.data) ** 2
                counts = {format(i, f'0{n}b'): int(round(shots * p)) for i, p in enumerate(probs)}
            else:
                qc = QuantumCircuit(n); qc.initialize(sv.data, range(n)); qc.measure_all()
                if self.use_ibm.get():
                    backend = get_backend(use_ibm=True)
                else:
                    backend = Aer.get_backend("qasm_simulator")
                    if self.fix_seed.get():
                        seed = int(self.meas_seed.get())
                        try:
                            backend.set_options(seed_simulator=seed, seed_transpiler=seed)
                        except Exception:
                            pass
                counts = backend.run(qc, shots=shots).result().get_counts()

            # sorted counts for plotting
            items = sorted(((int(k, 2), v) for k, v in counts.items()), key=lambda t: t[0])
            xs_counts = [x for x, _ in items]
            ys_counts = [y for _, y in items]
            labels = [format(x, f'0{n}b') for x in xs_counts]

            probs = np.abs(sv.data) ** 2
            xs_all = list(range(len(probs)))
            ys_theory = [shots * p for p in probs]

            # Try to parse multi-register layout from the Active label
            parsed = self._parse_multi_label(lbl)
            regs, regq = ([], None)
            if parsed:
                regs, _topo, regq = parsed
            else:
                maybe = int(self.reg_qubits.get())
                if n % max(1, maybe) == 0:
                    regq = maybe
                    R = n // regq
                    regs = [f"R{i}" for i in range(R)]

            for w in self.measure_canvas.winfo_children():
                w.destroy()
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(xs_counts, ys_counts, label="Measured")
            ax.plot(xs_all, ys_theory, marker="o", linestyle="-", label="Shots × |amp|²")

            # thin tick labels if too dense
            if len(xs_counts) > 64:
                step = max(1, len(xs_counts) // 64)
                take = list(range(0, len(xs_counts), step))
                ax.set_xticks([xs_counts[i] for i in take])
                ax.set_xticklabels([labels[i] for i in take], rotation=90, fontsize=8)
            else:
                ax.set_xticks(xs_counts)
                ax.set_xticklabels(labels, rotation=90, fontsize=8)

            title = f"Measurement Outcomes for {lbl}"
            if regs and regq:
                layout = " | ".join(f"{r}[{regq}]" for r in regs)
                title += f"\nBit layout (MSB→LSB): {layout}"
            ax.set_title(title)
            ax.set_xlabel("Basis"); ax.set_ylabel("Counts")
            if len(xs_counts) <= 256:
                ax.legend(loc="upper right", fontsize=8)
            fig.tight_layout()

            # Register grid + Schmidt entropies
            if self.show_reg_grid.get() and regs and regq:
                R = len(regs)
                N = 1 << n
                major = 1 << (regq * (R - 1))     # leftmost register boundary
                minor = (1 << (regq * (R - 2))) if R >= 2 else None
                for x in range(0, N + 1, major):
                    ax.axvline(x - 0.5, linewidth=1.2, alpha=0.25)
                if minor:
                    for x in range(0, N + 1, minor):
                        ax.axvline(x - 0.5, linewidth=0.6, alpha=0.08, linestyle="--")

                # Schmidt entropies across register cuts
                try:
                    e_cuts = []
                    for k in range(1, R):
                        e_cuts.append(self._schmidt_entropy_bits(sv, cut=regq * k))
                    if e_cuts:
                        ax.text(0.02, 0.98,
                                "Schmidt entropies (bits):  " +
                                " | ".join([f"{'|'.join(regs[:k])} ‖ {'|'.join(regs[k:])}: {e:.3f}"
                                            for k, e in enumerate(e_cuts, start=1)]),
                                transform=ax.transAxes, va="top", ha="left", fontsize=9)
                except Exception:
                    pass

            canvas = FigureCanvasTkAgg(fig, master=self.measure_canvas)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Measurement Error", str(e))

    def on_show_marginals(self):
        try:
            lbl, sv = self._get_active_or_selected(self.measure_combo)
            if sv is None:
                messagebox.showinfo("Marginals", "No active or selected state."); return

            n = int(np.log2(len(sv.data)))
            parsed = self._parse_multi_label(lbl)
            if parsed:
                regs, _topo, regq = parsed
            else:
                regq = int(self.reg_qubits.get())
                if n % regq != 0:
                    messagebox.showinfo("Marginals", "Can't infer register structure."); return
                R = n // regq
                regs = [f"R{i}" for i in range(R)]

            R = len(regs)
            # reshape to R axes of size 2**regq, MSB→LSB
            probs = (np.abs(sv.data) ** 2).reshape(*([2 ** regq] * R))

            for w in self.measure_canvas.winfo_children():
                w.destroy()
            fig, axes = plt.subplots(1, R, figsize=(4 * R, 3))
            if R == 1:
                axes = [axes]
            for i in range(R):
                axes_i = tuple(j for j in range(R) if j != i)
                m = probs.sum(axis=axes_i)
                xs = np.arange(2 ** regq)
                axes[i].bar(xs, m)
                axes[i].set_title(f"Marginal: {regs[i]}  ({regq} qubits)")
                axes[i].set_xticks(xs)
                axes[i].set_xticklabels([format(x, f'0{regq}b') for x in xs], fontsize=8, rotation=0)
                axes[i].set_xlabel("Local basis"); axes[i].set_ylabel("Prob.")
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.measure_canvas); canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Marginals Error", str(e))

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
        row = ttk.Frame(tab); row.pack(fill="x", pady=6)
        self.sim_include_active = tk.BooleanVar(value=True)
        ttk.Checkbutton(row, text="Include Active", variable=self.sim_include_active).pack(side="left", padx=6)
        ttk.Button(row, text="Compute Cosine Similarity", command=self.on_similarity).pack(side="left", padx=6)
        self.sim_text = tk.Text(tab, height=18); self.sim_text.pack(fill="both", expand=True, padx=6, pady=6)

    def on_similarity(self):
        try:
            from sklearn.metrics.pairwise import cosine_similarity

            labels = []
            vecs = []

            # Active state (optional)
            if self.sim_include_active.get() and self.active_state is not None:
                d = self.active_state.data
                vecs.append(np.concatenate([d.real, d.imag]))
                labels.append(self.active_state_label or "[active]")

            # Saved states
            for k, sv in self.statevectors.items():
                if labels and k == labels[0]:
                    continue
                d = sv.data
                vecs.append(np.concatenate([d.real, d.imag]))
                labels.append(k)

            if len(vecs) < 2:
                self.sim_text.delete("1.0", "end")
                self.sim_text.insert("end", "Need at least 2 states (including Active).\n")
                return

            sim = cosine_similarity(vecs)
            self.sim_text.delete("1.0", "end")
            header = "         " + " ".join(f"{k[:14]:>14}" for k in labels) + "\n"
            self.sim_text.insert("end", header)
            for i, row in enumerate(sim):
                self.sim_text.insert("end", f"{labels[i][:14]:>14}: " + " ".join(f"{v:>14.3f}" for v in row) + "\n")
        except Exception as e:
            messagebox.showerror("Similarity Error", str(e))

    # ================== Tab 7: Clustering ==================
    def _build_tab_clustering(self):
        tab = ttk.Frame(self.nb); self.nb.add(tab, text="Clustering")
        ctrl = ttk.Frame(tab); ctrl.pack(fill="x", pady=6)
        self.cluster_include_active = tk.BooleanVar(value=True)
        ttk.Checkbutton(ctrl, text="Include Active", variable=self.cluster_include_active).pack(side="left", padx=6)
        ttk.Button(ctrl, text="Run PCA (saved + active)", command=self.on_clustering).pack(side="left", padx=6)
        self.cluster_listbox = tk.Listbox(tab, selectmode=MULTIPLE, height=6, exportselection=False)
        self.cluster_listbox.pack(fill="x", padx=10, pady=6)
        self.cluster_canvas = ttk.Frame(tab); self.cluster_canvas.pack(fill="both", expand=True)

    def on_clustering(self):
        try:
            from sklearn.decomposition import PCA

            used = []
            vecs = []

            if self.cluster_include_active.get() and self.active_state is not None:
                d = self.active_state.data
                vecs.append(np.concatenate([d.real, d.imag]))
                used.append(self.active_state_label or "[active]")

            all_keys = list(self.statevectors.keys())
            selected = [self.cluster_listbox.get(i) for i in self.cluster_listbox.curselection()]
            keys = selected if selected else all_keys
            for k in keys:
                if k in self.statevectors and k not in used:
                    d = self.statevectors[k].data
                    vecs.append(np.concatenate([d.real, d.imag]))
                    used.append(k)

            if len(vecs) < 2:
                messagebox.showinfo("Clustering", "Need at least 2 states (saved or Active).")
                return

            proj = PCA(n_components=2).fit_transform(np.array(vecs))
            for w in self.cluster_canvas.winfo_children(): w.destroy()
            fig, ax = plt.subplots(figsize=(6, 6))
            for i, lbl in enumerate(used):
                ax.scatter(proj[i, 0], proj[i, 1])
                ax.text(proj[i, 0], proj[i, 1], " " + lbl, fontsize=8, va="center", ha="left")
            ax.set_title("PCA Projection"); ax.grid(True)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.cluster_canvas); canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
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
            if not TOMO_OK:
                return
            lbl, sv = self._get_active_or_selected(self.tomo_combo)
            if sv is None:
                messagebox.showinfo("Tomography", "No active or selected state."); return

            n = int(np.log2(len(sv.data)))
            qc = QuantumCircuit(n); qc.initialize(sv.data, range(n))
            tomo = StateTomography(qc)
            circs = tomo.circuits()

            # Choose backend and transpile away experiment ops (e.g., PauliMeasZ)
            if self.use_ibm.get():
                backend = get_backend(use_ibm=True)
            else:
                try:
                    backend = Aer.get_backend("aer_simulator")
                except Exception:
                    backend = Aer.get_backend("qasm_simulator")

            circs_t = transpile(circs, backend=backend, optimization_level=0)
            result = backend.run(circs_t, shots=2048).result()

            data = ExperimentData(experiment=tomo)
            data.add_data(result)
            analysis_result = tomo.analysis().run(data)
            reconstructed = analysis_result.result.data["state"]
            fid = state_fidelity(DensityMatrix(sv), reconstructed)

            for w in self.tomo_canvas.winfo_children(): w.destroy()
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.set_title(f"Fidelity: {fid:.6f}  ({lbl})")
            ax.text(0.5, 0.5, f"{fid:.6f}", fontsize=20, ha="center", va="center")
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.tomo_canvas); canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
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
        ttk.Label(tab, text="Const 1:").grid(row=1, column=0, sticky="e"); ttk.Combobox(tab, textvariable=self.ent1, values=SUGGESTED_LABELS, state="normal", width=24).grid(row=1, column=1, sticky="w")
        ttk.Label(tab, text="Const 2:").grid(row=2, column=0, sticky="e"); ttk.Combobox(tab, textvariable=self.ent2, values=SUGGESTED_LABELS, state="normal", width=24).grid(row=2, column=1, sticky="w")

        self.series_qubits_each = tk.IntVar(value=3)
        self.series_pattern = tk.StringVar(value="cx_all")
        ttk.Label(tab, text="Series qubits each:").grid(row=3, column=0, sticky="e"); ttk.Spinbox(tab, from_=1, to=8, textvariable=self.series_qubits_each, width=5).grid(row=3, column=1, sticky="w")
        ttk.Label(tab, text="Pattern:").grid(row=3, column=2, sticky="e"); ttk.Combobox(tab, textvariable=self.series_pattern, values=["cx_all","bell_on_0"], state="readonly", width=10).grid(row=3, column=3, sticky="w")

        ttk.Label(tab, text="Multi CSV (e.g. π,ζ(3),e)").grid(row=4, column=0, sticky="e")
        self.multi_csv = tk.Entry(tab, width=40); self.multi_csv.insert(0, "π,ζ(3),e"); self.multi_csv.grid(row=4, column=1, columnspan=2, sticky="w")

        self.multi_topology_tab = tk.StringVar(value="chain")
        ttk.Label(tab, text="Topology:").grid(row=4, column=3, sticky="e"); ttk.Combobox(tab, textvariable=self.multi_topology_tab, values=["chain","star","all_to_all"], state="readonly", width=10).grid(row=4, column=4, sticky="w")

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
                sv = simulate_statevector(qc); cut = 1

            elif mode == "series":
                n_each = int(self.series_qubits_each.get())
                c1, c2 = self.ent1.get(), self.ent2.get()
                m1 = self.pi_method.get() if _supports_method(c1) else None
                m2 = self.pi_method.get() if _supports_method(c2) else None
                qc = entangle_series_registers(
                    c1, c2, n_qubits_each=n_each, method1=m1, method2=m2,
                    phase_mode1=self.phase_mode.get(), phase_mode2=self.phase_mode.get(),
                    pattern=self.series_pattern.get(), use_stateprep=True, do_measure=False
                )
                sv = simulate_statevector(qc); cut = n_each

            else:
                labels = [s.strip() for s in self.multi_csv.get().split(",") if s.strip()]
                if len(labels) < 2:
                    messagebox.showinfo("Multi", "Provide at least 2 labels."); return
                n_each = int(self.series_qubits_each.get())
                topo = self.multi_topology_tab.get()
                qc = entangle_series_multi(
                    labels, n_qubits_each=n_each, methods=None,
                    phase_mode=self.phase_mode.get(), topology=topo,
                    use_stateprep=True, do_measure=False
                )
                sv = simulate_statevector(qc); cut = n_each * (len(labels)//2)

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
            fig = self.current_qft_circuit.draw(
                output="mpl", fold=80, idle_wires=False, plot_barriers=False, scale=0.8
            )
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.gate_canvas); canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
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
            fig = qc.draw(output="mpl", fold=80, idle_wires=False, plot_barriers=False, scale=0.8)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.gate_canvas); canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
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
            try:
                from state_io import save_statevector
            except Exception:
                save_statevector = None
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
            try:
                from state_io import load_statevector
            except Exception:
                load_statevector = None
            if load_statevector is None:
                messagebox.showinfo("Load", "state_io.load_statevector not available."); return
            label, sv = load_statevector()
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
        x = vec.astype(np.complex128); m = np.mean(x); x = x - m
        if x.size > 1: x = x * np.hanning(x.size)
        return x

    def _spectrum_metrics(self, vec: np.ndarray) -> dict:
        X = np.fft.fft(vec); P = np.abs(X) ** 2; S = P.sum() or 1.0
        dc = float(P[0] / S); p = P / S; p = p[p > 0]
        H = float(-np.sum(p * np.log2(p)))
        return {"dc_frac": dc, "entropy_bits": H}


if __name__ == "__main__":
    app = QTEGUI()
    app.mainloop()
