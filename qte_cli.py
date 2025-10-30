#!/usr/bin/env python3
import os
import argparse
import numpy as np
import series_encoding as se
from qte_cli_ext_register import add_qte_ext

def main():
    ap = argparse.ArgumentParser(description="Quantum series encoder CLI")
    ap.add_argument("--nq", type=int, default=6, help="number of qubits (vector length = 2**nq)")
    ap.add_argument("--mode", choices=["terms","egf"], default="terms", help="amplitude mode")
    ap.add_argument("--rail", action="store_true", help="append [rail] to the label")
    ap.add_argument("--label", required=True, help="series/transform label")
    ap.add_argument("--value", action="store_true", help="print scalar value instead of vector")
    ap.add_argument("--dump", type=str, default="", help="optional .npy path to save the vector")

    # cache + backend toggles
    ap.add_argument("--cache", dest="cache", action="store_true", help="enable cache")
    ap.add_argument("--no-cache", dest="cache", action="store_false", help="disable cache")
    ap.set_defaults(cache=None)
    ap.add_argument("--backend", choices=["auto","series","mp"], default=None,
                    help="polylog backend override (env QTE_POLYLOG_BACKEND if omitted)")

    args = ap.parse_args()
    if hasattr(args, 'func'):
        return args.func(args)

    # Apply toggles via env (read by series_encoding)
    if args.cache is not None:
        os.environ["QTE_CACHE"] = "1" if args.cache else "0"
    if args.backend is not None:
        os.environ["QTE_POLYLOG_BACKEND"] = args.backend

    # Banner
    try:
        import mpmath as _mp  # noqa: F401
        have_mp = True
    except Exception:
        have_mp = False
    print(f"[polylog backend] mpmath={'ON' if have_mp else 'OFF'}  "
          f"backend={os.environ.get('QTE_POLYLOG_BACKEND','auto')}  "
          f"cache={os.environ.get('QTE_CACHE','0')}")

    # Compose label (with optional [rail])
    base = args.label.strip()
    label = base if "[rail]" in base.lower() or not args.rail else base + "[rail]"

    if args.value:
        val = se.compute_series_value(label)
        # robust print for real/complex results
        try:
            c = complex(val)
            if abs(c.imag) < 1e-12:
                print(f"{c.real:.16g}")
            else:
                sign = '+' if c.imag >= 0 else '-'
                print(f"{c.real:.16g}{sign}{abs(c.imag):.16g}j")
        except Exception:
            print(val)
        return

    dim = 2 ** int(args.nq)
    v = se.get_series_amplitudes(label, dim, amp_mode=args.mode, normalize=True)
    print(f"len={len(v)} norm={np.linalg.norm(v):.12g}")

    if args.dump:
        np.save(args.dump, v)
        print("saved", args.dump)

if __name__ == "__main__":
    main()
