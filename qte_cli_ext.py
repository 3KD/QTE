#!/usr/bin/env python3
import os, sys, json, math, argparse, numpy as np
from typing import Optional
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Operator

# QTE modules (from tools/ and qe_crypto/)
from tools.qft_module import qft, st_qft
from tools.lct_czt import frac_fourier, chirp_z
from tools.hankel_bessel import discrete_hankel_unitary, spherical_bessel_unitary
from tools.hilbert_wavelet_ntt import hilbert_transform, walsh_hadamard
from qe_crypto.unitary_cipher import cipher_u
from tools.leakage_meter import leakage_score_from_state
from physics.kubo_otoc_sff import spectral_form_factor

def _ensure_dir(p:str):
    os.makedirs(os.path.dirname(p), exist_ok=True)

def _draw_text(qc: QuantumCircuit) -> str:
    try:
        return qc.decompose().draw(output="text").single_string()
    except Exception:
        return qc.draw(output="text")

def cmd_qft(args):
    qc = qft(args.n, inverse=args.inverse, do_swaps=not args.no_swaps, approximation_degree=args.approx)
    print(_draw_text(qc))
    if args.out:
        _ensure_dir(args.out)
        with open(args.out, "w") as f: f.write(_draw_text(qc))
        print(f"Saved ASCII circuit to {args.out}")

def cmd_stqft(args):
    circs = st_qft(args.n, args.window, args.step)
    for i, qc in enumerate(circs):
        print(f"\n=== window {i} ===")
        print(_draw_text(qc))
    if args.out:
        _ensure_dir(args.out)
        with open(args.out, "w") as f:
            for i, qc in enumerate(circs):
                f.write(f"\n=== window {i} ===\n{_draw_text(qc)}\n")
        print(f"Saved ST-QFT ASCII circuits to {args.out}")

def cmd_lct(args):
    if args.mode == "frft":
        qc = frac_fourier(args.n, args.alpha)
    elif args.mode == "czt":
        qc = chirp_z(args.n, args.k0, args.dk)
    else:
        raise SystemExit("Unknown LCT mode")
    print(_draw_text(qc))
    if args.out:
        _ensure_dir(args.out)
        with open(args.out, "w") as f: f.write(_draw_text(qc))
        print(f"Saved ASCII circuit to {args.out}")

def cmd_hankel(args):
    qc = discrete_hankel_unitary(args.n, order=args.nu)
    print(_draw_text(qc))
    if args.out:
        _ensure_dir(args.out)
        with open(args.out, "w") as f: f.write(_draw_text(qc))
        print(f"Saved ASCII circuit to {args.out}")

def cmd_sphbessel(args):
    qc = spherical_bessel_unitary(args.n, ell=args.ell)
    print(_draw_text(qc))
    if args.out:
        _ensure_dir(args.out)
        with open(args.out, "w") as f: f.write(_draw_text(qc))
        print(f"Saved ASCII circuit to {args.out}")

def cmd_hilbert(args):
    qc = hilbert_transform(args.n)
    print(_draw_text(qc))
    if args.out:
        _ensure_dir(args.out)
        with open(args.out, "w") as f: f.write(_draw_text(qc))
        print(f"Saved ASCII circuit to {args.out}")

def cmd_walsh(args):
    qc = walsh_hadamard(args.n)
    print(_draw_text(qc))
    if args.out:
        _ensure_dir(args.out)
        with open(args.out, "w") as f: f.write(_draw_text(qc))
        print(f"Saved ASCII circuit to {args.out}")

def cmd_cipher(args):
    key = (args.key.encode("utf-8") if args.key_format=="str" else bytes.fromhex(args.key))
    nonce = (args.nonce.encode("utf-8") if args.nonce_format=="str" else bytes.fromhex(args.nonce))
    qc = cipher_u(args.n, key, nonce, rounds=args.rounds)
    print(_draw_text(qc))
    # quick leakage run on |0...0>
    psi = Statevector.from_label('0'*args.n).evolve(qc)
    score = leakage_score_from_state(psi, paulis=args.paulis)
    print(f"\nLeakage proxy (sqrt avg Pauli^2) with paulis={args.paulis}: {score:.6g}")
    if args.out:
        _ensure_dir(args.out)
        with open(args.out, "w") as f: f.write(_draw_text(qc))
        print(f"Saved ASCII circuit to {args.out}")

def cmd_teleport(args):
    from qe_crypto.teleport_demo import one_qubit_teleport
    qc = one_qubit_teleport()
    print(_draw_text(qc))
    if args.out:
        _ensure_dir(args.out)
        with open(args.out, "w") as f: f.write(_draw_text(qc))
        print(f"Saved ASCII circuit to {args.out}")

def cmd_leakage(args):
    key = b'K'*32; nonce = b'N'*16
    base = Statevector.from_label('0'*args.n)
    scores=[]
    for r in range(args.r_min, args.r_max+1):
        qc = cipher_u(args.n, key, nonce, rounds=r)
        out = base.evolve(qc)
        s = leakage_score_from_state(out, paulis=args.paulis)
        scores.append((r, s))
        print(f"rounds={r:2d}  leakage≈ {s:.6g}")
    if args.json:
        _ensure_dir(args.json)
        with open(args.json,"w") as jf: json.dump({"n":args.n,"paulis":args.paulis,"scores":scores}, jf, indent=2)
        print(f"Wrote {args.json}")

def cmd_sff(args):
    # Build operator source
    if args.src == "qft":
        qc = qft(args.n)
    elif args.src == "cipher":
        qc = cipher_u(args.n, b'K'*32, b'N'*16, rounds=args.rounds)
    else:
        raise SystemExit("Unknown src")
    U = Operator(qc)
    val = spectral_form_factor(U, t=args.t)
    print(f"K(t={args.t}) for src={args.src}: {val:.6g}")

def main():
    ap = argparse.ArgumentParser(prog="qte-cli-ext", description="QTE extended CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("qft", help="Build/display QFT circuit")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--inverse", action="store_true")
    p.add_argument("--no-swaps", action="store_true")
    p.add_argument("--approx", type=int, default=0, help="Approximation degree")
    p.add_argument("--out", help="Save ASCII circuit to file")
    p.set_defaults(func=cmd_qft)

    p = sub.add_parser("st-qft", help="Short-Time QFT on sliding windows")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--window", type=int, required=True)
    p.add_argument("--step", type=int, default=1)
    p.add_argument("--out", help="Save all ASCII circuits to file")
    p.set_defaults(func=cmd_stqft)

    p = sub.add_parser("lct", help="Linear Canonical Transforms")
    p.add_argument("mode", choices=["frft","czt"])
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--alpha", type=float, default=0.5, help="FrFT order (0..1)")
    p.add_argument("--k0", type=float, default=0.0, help="CZT center")
    p.add_argument("--dk", type=float, default=1.0, help="CZT spacing")
    p.add_argument("--out", help="Save ASCII circuit to file")
    p.set_defaults(func=cmd_lct)

    p = sub.add_parser("hankel", help="Discrete Hankel transform (demo)")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--nu", type=float, default=0.0)
    p.add_argument("--out", help="Save ASCII circuit to file")
    p.set_defaults(func=cmd_hankel)

    p = sub.add_parser("spherical-bessel", help="Spherical-Bessel transform (demo)")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--ell", type=int, default=0)
    p.add_argument("--out", help="Save ASCII circuit to file")
    p.set_defaults(func=cmd_sphbessel)

    p = sub.add_parser("hilbert", help="Hilbert transform")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--out", help="Save ASCII circuit to file")
    p.set_defaults(func=cmd_hilbert)

    p = sub.add_parser("walsh", help="Walsh–Hadamard")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--out", help="Save ASCII circuit to file")
    p.set_defaults(func=cmd_walsh)

    p = sub.add_parser("cipher", help="Build cipher circuit and compute leakage on |0..0>")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--rounds", type=int, default=3)
    p.add_argument("--key", type=str, default="k"*32)
    p.add_argument("--key-format", choices=["str","hex"], default="str")
    p.add_argument("--nonce", type=str, default="n"*16)
    p.add_argument("--nonce-format", choices=["str","hex"], default="str")
    p.add_argument("--paulis", type=int, default=128)
    p.add_argument("--out", help="Save ASCII circuit to file")
    p.set_defaults(func=cmd_cipher)

    p = sub.add_parser("teleport", help="One-qubit teleport circuit")
    p.add_argument("--out", help="Save ASCII circuit to file")
    p.set_defaults(func=cmd_teleport)

    p = sub.add_parser("leakage", help="Leakage vs rounds (cipher on |0..0>)")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--r-min", type=int, default=0)
    p.add_argument("--r-max", type=int, default=5)
    p.add_argument("--paulis", type=int, default=128)
    p.add_argument("--json", help="Write JSON results")
    p.set_defaults(func=cmd_leakage)

    p = sub.add_parser("sff", help="Spectral Form Factor on a source circuit")
    p.add_argument("--src", choices=["qft","cipher"], default="qft")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--t", type=int, default=1)
    p.add_argument("--rounds", type=int, default=3, help="if src=cipher")
    p.set_defaults(func=cmd_sff)

    args = ap.parse_args()
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
