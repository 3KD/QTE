
import re
from typing import Any, Dict, Optional
from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler

_BITRE = re.compile(r'^[01]+$')

def get_backend(name: str):
    svc = QiskitRuntimeService()
    return svc.backend(name)

def _to_bits(k: Any, width: int) -> Optional[str]:
    if isinstance(k, int):
        return format(k, f"0{width}b")
    if isinstance(k, str):
        if _BITRE.match(k):
            return k.zfill(width)
        try:
            return format(int(k), f"0{width}b")
        except Exception:
            return None
    try:
        return format(int(k), f"0{width}b")
    except Exception:
        return None

def _normalize_counts(d: Dict[Any, Any], width: int) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for k, v in d.items():
        b = _to_bits(k, width)
        if b is None:
            continue
        try:
            c = int(v)
        except Exception:
            try:
                c = int(round(float(v)))
            except Exception:
                continue
        out[b] = out.get(b, 0) + c
    return out

def _counts_from_quasi(qd: Dict[Any, Any], width: int, shots: int) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for k, p in qd.items():
        b = _to_bits(k, width)
        if b is None:
            continue
        try:
            prob = float(p)
        except Exception:
            prob = float(getattr(p, "value", 0.0))
        out[b] = out.get(b, 0) + int(round(prob * shots))
    return out

def run_counts(qc, backend, shots: int = 256):
    # Transpile so hardware target accepts the circuit (fixes "h not supported").
    tqc = transpile(qc, backend=backend, optimization_level=1)

    # Bind backend via mode; pass shots through options.
    sampler = Sampler(mode=backend, options={"default_shots": shots})
    job = sampler.run([tqc])   # positional only
    res = job.result()         # PrimitiveResult (indexable)

    width = len(tqc.clbits) or tqc.num_qubits

    # 1) New-style quasi_dists (simulators / some providers)
    if hasattr(res, "quasi_dists"):
        try:
            qd = res.quasi_dists[0]
            return job.job_id(), _counts_from_quasi(qd, width, shots)
        except Exception:
            pass

    # 2) Published results: use the supported join_data().get_counts()
    try:
        pub = res[0]  # SamplerPubResult
        join_data = getattr(pub, "join_data", None)
        if callable(join_data):
            joined = join_data()
            get_counts = getattr(joined, "get_counts", None)
            if callable(get_counts):
                raw = get_counts()  # dict[str|int -> int]
                return job.job_id(), _normalize_counts(raw, width)
    except Exception:
        pass

    # 3) Fallback: pub.data (dict of DataBin). Prefer 'meas', else first with get_counts.
    try:
        pub = res[0]
        data = getattr(pub, "data", None)
        if data:
            if hasattr(data, "get") and "meas" in data and hasattr(data["meas"], "get_counts"):
                return job.job_id(), _normalize_counts(data["meas"].get_counts(), width)
            for db in getattr(data, "values", lambda: [])():
                if hasattr(db, "get_counts"):
                    return job.job_id(), _normalize_counts(db.get_counts(), width)
    except Exception:
        pass

    keys = list(getattr(res, "__dict__", {}).keys())
    raise RuntimeError(f"Sampler result shape not recognized; keys: {keys}")
