try:
    from qiskit_ibm_runtime import SamplerV2 as _Sampler  # modern
except Exception:
    try:
        from qiskit_ibm_runtime import Sampler as _Sampler  # legacy runtime
    except Exception:
        try:
            from qiskit.primitives import Sampler as _Sampler  # local fallback
        except Exception:
            _Sampler = None

def _make_sampler(*, backend=None, session=None):
    """Return a Sampler instance that works across versions."""
    if _Sampler is None:
        raise RuntimeError("No compatible Sampler available on this install.")
    # Prefer session (if provided and supported)
    if session is not None:
        try:
            return _Sampler(session=session)
        except Exception:
            pass
    # Else backend if supported
    if backend is not None:
        try:
            return _Sampler(backend=backend)
        except Exception:
            pass
    # Else bare sampler
    return _Sampler()
