# ibm_backend.py
from __future__ import annotations
from typing import Optional

from qiskit_aer import Aer, AerSimulator

_provider = None
_runtime = None

def initialize_ibm(api_token: Optional[str] = None, instance: Optional[str] = None) -> None:
    """
    Initialize IBM access. Tries qiskit-ibm-provider first, then qiskit-ibm-runtime.
    Safe to call multiple times.
    """
    global _provider, _runtime

    # Provider path
    try:
        from qiskit_ibm_provider import IBMProvider
        if api_token:
            try:
                IBMProvider.save_account(token=api_token, overwrite=True)
            except Exception:
                pass
            _provider = IBMProvider(token=api_token, instance=instance) if instance else IBMProvider(token=api_token)
        else:
            _provider = IBMProvider(instance=instance) if instance else IBMProvider()
        return
    except Exception:
        _provider = None

    # Runtime path
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
        if api_token:
            try:
                QiskitRuntimeService.save_account(channel="ibm_quantum", token=api_token, overwrite=True)
            except Exception:
                pass
            _runtime = QiskitRuntimeService(instance=instance) if instance else QiskitRuntimeService()
        else:
            _runtime = QiskitRuntimeService(instance=instance) if instance else QiskitRuntimeService()
    except Exception:
        _runtime = None

def _pick_provider_backend(min_qubits: int = 1, name: Optional[str] = None):
    if _provider is None:
        try:
            from qiskit_ibm_provider import IBMProvider
            globals()['_provider'] = IBMProvider()
        except Exception:
            return None
    if name:
        try:
            return _provider.get_backend(name)
        except Exception:
            pass
    try:
        from qiskit_ibm_provider import least_busy
        cands = _provider.backends(simulator=False, operational=True, min_num_qubits=min_qubits)
        if cands:
            return least_busy(cands)
    except Exception:
        pass
    for sim_name in ("ibmq_qasm_simulator", "simulator_mps"):
        try:
            return _provider.get_backend(sim_name)
        except Exception:
            continue
    return None

def _pick_runtime_backend(min_qubits: int = 1, name: Optional[str] = None):
    if _runtime is None:
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
            globals()['_runtime'] = QiskitRuntimeService()
        except Exception:
            return None
    try:
        if name:
            return _runtime.backend(name)
    except Exception:
        pass
    try:
        bks = _runtime.backends(simulator=False)
        bks = [b for b in bks if getattr(b.configuration(), "num_qubits", 0) >= min_qubits]
        for b in bks:
            try:
                if b.status().operational:
                    return b
            except Exception:
                continue
        if bks:
            return bks[0]
    except Exception:
        pass
    try:
        sims = _runtime.backends(simulator=True)
        if sims:
            return sims[0]
    except Exception:
        pass
    return None

def get_backend(use_ibm: bool = False, fallback: str = "aer_simulator", *, min_qubits: int = 1, name: Optional[str] = None):
    """
    Returns a backend-like object with .run(...).
    If use_ibm=False or no IBM access, returns an Aer simulator.
    """
    if use_ibm:
        try:
            bk = _pick_provider_backend(min_qubits=min_qubits, name=name)
            if bk is not None:
                return bk
        except Exception:
            pass
        try:
            bk = _pick_runtime_backend(min_qubits=min_qubits, name=name)
            if bk is not None:
                return bk
        except Exception:
            pass
    try:
        return Aer.get_backend(fallback)
    except Exception:
        return AerSimulator()

def list_ibm_backends():
    out = []
    if _provider:
        try:
            out.extend([b.name for b in _provider.backends()])
        except Exception:
            pass
    if _runtime:
        try:
            out.extend([b.name for b in _runtime.backends()])
        except Exception:
            pass
    return sorted(set(out))

def get_ibm_status():
    if _provider:
        for b in _provider.backends():
            try:
                s = b.status()
                print(f"{b.name}: {getattr(s, 'pending_jobs', '?')} jobs, operational: {s.operational}")
            except Exception as e:
                print(f"⚠️ provider {b.name}: {e}")
    if _runtime:
        for b in _runtime.backends():
            try:
                s = b.status()
                print(f"{b.name}: {getattr(s, 'pending_jobs', '?')} jobs, operational: {s.operational}")
            except Exception as e:
                print(f"⚠️ runtime {b.name}: {e}")

