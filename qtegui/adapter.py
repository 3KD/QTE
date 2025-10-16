from __future__ import annotations
import importlib, types

def _load_external() -> types.ModuleType | None:
    try:
        return importlib.import_module("qtegui_adapter")
    except Exception:
        return None

_ext = _load_external()

if _ext is not None:
    # expose everything from the project's adapter (root-level qtegui_adapter.py)
    for k, v in vars(_ext).items():
        if not k.startswith("_"):
            globals()[k] = v
else:
    # minimal fallback shims (won't break imports if external not present)
    def launch_gui():
        raise RuntimeError("qtegui_adapter.py not found; cannot launch GUI.")

    def list_components():
        return {"note": "qtegui_adapter.py missing; limited features available."}
