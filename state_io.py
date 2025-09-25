# state_io.py — macOS/Tk-safe Save/Open helpers for QTE
import os
import numpy as np
from typing import Optional, Tuple
from qiskit.quantum_info import Statevector

try:
    from tkinter import filedialog
except Exception:
    filedialog = None

try:
    from file_naming import build_filename
except Exception:
    build_filename = None


def _suggest_name(label: str, n_qubits: int, data: np.ndarray) -> str:
    base = label or "state"
    if build_filename:
        # optional content-hash naming
        byte_view = np.asarray(data, dtype=np.complex128).view(np.uint8).tobytes()
        return build_filename(base, n_qubits, state_bytes=byte_view, ext="npz")
    return f"{base}__n{n_qubits}.npz"


def save_statevector(sv: Statevector, label: str, out_dir: str = "states") -> str:
    """Non-dialog fallback: write into ./states/"""
    os.makedirs(out_dir, exist_ok=True)
    n_qubits = int(np.log2(len(sv.data)))
    fname = _suggest_name(label or "state", n_qubits, sv.data)
    path = os.path.join(out_dir, fname)
    np.savez(path, data=sv.data, label=label or "", n_qubits=n_qubits)
    return path


def save_statevector_dialog(parent, sv: Statevector, label: Optional[str] = None) -> Optional[str]:
    """Native save dialog (macOS-safe). Returns path or None if cancelled."""
    if filedialog is None:
        return save_statevector(sv, label or "state")

    n_qubits = int(np.log2(len(sv.data)))
    suggested = _suggest_name(label or "state", n_qubits, sv.data)

    # IMPORTANT: valid (label, pattern) tuples only — avoids nil crash on macOS Tk
    filetypes = [("QTE State (*.npz)", "*.npz"), ("All Files", "*")]

    path = filedialog.asksaveasfilename(
        parent=parent,
        title="Save QTE State",
        initialfile=suggested,
        defaultextension=".npz",
        filetypes=filetypes,
        confirmoverwrite=True,
    )
    if not path:
        return None
    np.savez(path, data=sv.data, label=label or "", n_qubits=n_qubits)
    return path


def load_statevector_dialog(parent) -> Optional[Tuple[str, Statevector]]:
    """Native open dialog (macOS-safe). Returns (label, Statevector) or None."""
    if filedialog is None:
        return None
    filetypes = [("QTE State (*.npz)", "*.npz"), ("All Files", "*")]
    path = filedialog.askopenfilename(
        parent=parent,
        title="Load QTE State",
        filetypes=filetypes,
    )
    if not path:
        return None
    with np.load(path, allow_pickle=False) as npz:
        data = np.asarray(npz["data"], dtype=np.complex128)
        try:
            raw = npz["label"]
            label = str(raw.item()) if hasattr(raw, "item") else str(raw)
        except KeyError:
            label = os.path.basename(path)
    return label, Statevector(data)

