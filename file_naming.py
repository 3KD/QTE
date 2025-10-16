# file_naming.py
# Canonical, parseable filenames for QTE artifacts (plots, csv, npy, etc.)
# Includes an entanglement signature (per-register-cut Schmidt entropies).

from __future__ import annotations
import re, time, math
import numpy as np
from typing import Dict, List, Optional, Tuple
from qiskit.quantum_info import Statevector

# ---- ASCII-safe labels -------------------------------------------------------

_ASCII_MAP = {
    "π": "pi", "ζ": "zeta", "γ": "gamma", "φ": "phi", "√": "sqrt", "·": "x", "×": "x",
    "–": "-", "—": "-", " ": "", "∞": "inf",
}
_ALLOWED = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.+()[],^")

def _ascii_safe(s: str) -> str:
    out = []
    for ch in s:
        ch = _ASCII_MAP.get(ch, ch)
        if ch in _ALLOWED:
            out.append(ch)
        else:
            out.append(f"~{ord(ch):x}")  # hex-escape anything odd
    return "".join(out)

def format_constant_token(label: str, method: Optional[str]) -> str:
    lab = _ascii_safe(label)
    if method:
        return f"{lab}({method})"
    return lab

def format_constant_list(pairs: List[Tuple[str, Optional[str]]]) -> str:
    return "+".join(format_constant_token(l, m) for (l, m) in pairs)

# ---- Optional: parse multi[...] labels like the GUI emits --------------------

def parse_multi_label(label: str):
    """multi[π,e,ln(2)|chain|3] -> (['π','e','ln(2)'], 'chain', 3) or None."""
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

# ---- Entanglement signature ---------------------------------------------------

def schmidt_entropies_all_cuts(
    sv: Statevector, regq: int, n_regs: int, tol: float = 1e-12
) -> List[float]:
    """Von Neumann entropy (bits) across every register boundary cut."""
    N = int(math.log2(len(sv.data)))
    assert regq * n_regs == N, f"regq*n_regs must equal total qubits: {regq}*{n_regs}!={N}"
    ents = []
    from quantum_embedding import perform_schmidt_decomposition
    for k in range(1, n_regs):
        S = perform_schmidt_decomposition(sv, cut=regq * k)
        p = (S ** 2)
        p = p[p > tol]
        H = float(-np.sum(p * np.log2(p))) if p.size else 0.0
        ents.append(H)
    return ents

def ent_tag_from_entropies(ents: List[float], millis: bool = True) -> str:
    if millis:
        vals = [str(int(round(e * 1000))) for e in ents]  # 1.234 bits -> "1234"
        return "Ebitsm=" + "-".join(vals)
    else:
        vals = [f"{e:.3f}" for e in ents]
        return "Ebits=" + "-".join(vals)

# ---- Filename build/parse -----------------------------------------------------

def build_qte_filename(
    *,
    constants: List[Tuple[str, Optional[str]]],
    mode: str,               # "EGF", "Terms", "Periodic", "PEA", "QROM", etc.
    n_qubits: int,
    phase_mode: Optional[str] = None,         # "sign"/"abs"/None
    regq: Optional[int] = None,               # per-register qubits if multi
    topology: Optional[str] = None,           # "chain"/"star"/"all_to_all"
    pattern: Optional[str] = None,            # entangle pattern tag if used
    entropies_bits: Optional[List[float]] = None,  # per-cut entropies
    extra: Optional[Dict[str, str]] = None,   # freeform small tags
    suffix: str = ".png",                     # or ".csv", ".npy", ...
) -> str:
    """
    Canonical pattern:
    QTE__C=<consts>__Mode=<mode>__N=<n>__Phase=<phase?>__RegQ=<r?>__Topo=<t?>__Pat=<p?>__Ebitsm=<a-b-c>__K=key:val,...__TS=YYYYmmddTHHMMSS<suffix>
    """
    fields = []
    fields.append(f"C={format_constant_list(constants)}")
    fields.append(f"Mode={_ascii_safe(mode)}")
    fields.append(f"N={int(n_qubits)}")
    if phase_mode:
        fields.append(f"Phase={_ascii_safe(phase_mode)}")
    if regq:
        fields.append(f"RegQ={int(regq)}")
    if topology:
        fields.append(f"Topo={_ascii_safe(topology)}")
    if pattern:
        fields.append(f"Pat={_ascii_safe(pattern)}")
    if entropies_bits is not None:
        fields.append(ent_tag_from_entropies(entropies_bits, millis=True))
    if extra:
        kv = ",".join(f"{_ascii_safe(k)}:{_ascii_safe(str(v))}" for k, v in sorted(extra.items()))
        if kv:
            fields.append(f"K={kv}")
    ts = time.strftime("%Y%m%dT%H%M%S")
    fields.append(f"TS={ts}")
    core = "QTE__" + "__".join(fields)
    return core + suffix

_PARSE_RE = re.compile(r"QTE__(?P<body>.+?)(?:\.(?P<ext>[A-Za-z0-9]+))?$")

def parse_qte_filename(name: str) -> Dict[str, str]:
    m = _PARSE_RE.match(name)
    if not m:
        return {}
    body = m.group("body")
    parts = body.split("__")
    out: Dict[str, str] = {}
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            out[k] = v
    if m.group("ext"):
        out["EXT"] = m.group("ext")
    return out

