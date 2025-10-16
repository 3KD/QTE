from __future__ import annotations
import argparse, sys, subprocess, json, importlib, inspect
from typing import Any, Dict, List

def _try_import(name: str):
    try:
        return importlib.import_module(name)
    except Exception:
        return None

def _safe_call(obj, *a, **kw):
    try:
        return obj(*a, **kw)
    except Exception as e:
        return f"[error] {type(e).__name__}: {e}"

def _list_public_callables(mod) -> List[str]:
    out = []
    for k, v in vars(mod).items():
        if k.startswith("_"): 
            continue
        if inspect.isfunction(v) or inspect.isclass(v):
            out.append(k)
    return sorted(out)

def cmd_list(args: argparse.Namespace) -> int:
    modules = {
        "quantum_embedding": _try_import("quantum_embedding"),
        "series_encoding":   _try_import("series_encoding"),
        "physics.lorentz":   _try_import("physics.lorentz"),
        "metrics_extra":     _try_import("metrics_extra"),
    }
    info: Dict[str, Any] = {}
    for name, mod in modules.items():
        if mod is None:
            info[name] = {"available": False}
        else:
            info[name] = {
                "available": True,
                "callables": _list_public_callables(mod)
            }
    print(json.dumps(info, indent=2))
    return 0

def cmd_demo(args: argparse.Namespace) -> int:
    if args.which == "entanglement":
        import numpy as np
        me = _try_import("metrics_extra")
        if me is None or not hasattr(me, "schmidt_entropy"):
            print("[warn] metrics_extra.schmidt_entropy unavailable")
            return 1
        psi = np.array([1/np.sqrt(2),0,0,1/np.sqrt(2)], dtype=complex)
        S = me.schmidt_entropy(psi, n_qubits=2, cut=1)
        print(f"Bell-state entropy (bits): {S:.6f}")
        return 0
    elif args.which == "trig":
        se = _try_import("series_encoding")
        if se is None or not hasattr(se, "_qte_maclaurin_coeffs"):
            print("[warn] series_encoding._qte_maclaurin_coeffs unavailable")
            return 1
        coeffs = se._qte_maclaurin_coeffs("sin(x)^2", n_terms=6, radius=4.0, m=0)
        print(f"sin^2 constant term (a0/2): {coeffs[0]}")
        return 0
    else:
        print(f"[error] unknown demo {args.which}")
        return 2

def cmd_gui(args: argparse.Namespace) -> int:
    # try the adapter first (preferred)
    qa = _try_import("qtegui.adapter")
    if qa and hasattr(qa, "launch_gui"):
        res = _safe_call(getattr(qa, "launch_gui"))
        if isinstance(res, str) and res.startswith("[error]"):
            print(res)
            return 1
        return 0
    # fallback: try legacy QTEGUI.py
    legacy = _try_import("QTEGUI")
    for entry in ("main", "run", "launch", "App"):
        fn = getattr(legacy, entry, None) if legacy else None
        if callable(fn):
            _safe_call(fn)
            return 0
        if entry == "App" and fn is not None:
            app = fn()
            for m in ("run", "main", "__call__"):
                if hasattr(app, m):
                    _safe_call(getattr(app, m))
                    return 0
    print("[error] could not find GUI entrypoint (qtegui_adapter.launch_gui or QTEGUI.main)")
    return 1

def cmd_test(args: argparse.Namespace) -> int:
    # delegate to pytest but keep our process simple
    cmd = [sys.executable, "-m", "pytest", "-q"]
    if args.k:
        cmd += ["-k", args.k]
    if args.path:
        cmd += [args.path]
    return subprocess.call(cmd)

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="qtegui", description="QTE GUI/CLI driver")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List available modules & callables")
    p_list.set_defaults(func=cmd_list)

    p_demo = sub.add_parser("demo", help="Run small demos (entanglement|trig)")
    p_demo.add_argument("which", choices=["entanglement","trig"])
    p_demo.set_defaults(func=cmd_demo)

    p_gui = sub.add_parser("gui", help="Launch the GUI via qtegui_adapter or legacy QTEGUI.py")
    p_gui.set_defaults(func=cmd_gui)

    p_test = sub.add_parser("test", help="Run pytest through the CLI")
    p_test.add_argument("--k", help="pytest -k expression", default=None)
    p_test.add_argument("path", nargs="?", default="tests")
    p_test.set_defaults(func=cmd_test)
    return p

def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)
    return ns.func(ns)

if __name__ == "__main__":
    raise SystemExit(main())
