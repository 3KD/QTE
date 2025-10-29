# Auto-generated: QTE extended CLI subcommands registrar
# Usage from qte_cli.py: from qte_cli_ext_register import add_qte_ext; add_qte_ext(sub)
import os, json
from typing import Optional
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Operator

def _draw_text(qc: QuantumCircuit) -> str:
    try:
        return qc.decompose().draw(output="text").single_string()
    except Exception:
        return qc.draw(output="text")

def _ensure_dir(p:str):
    d=os.path.dirname(p)
    if d: os.makedirs(d, exist_ok=True)

# Handlers (imports inside to avoid global hard deps)
def _cmd_qft(args):
    from tools.qft_module import qft
    qc = qft(args.n, inverse=args.inverse, do_swaps=not args.no_swaps, approximation_degree=args.approx)
    s = _draw_text(qc); print(s)
    if args.out: _ensure_dir(args.out); open(args.out,"w").write(s); print(f"Saved {args.out}")

def _cmd_stqft(args):
    from tools.qft_module import st_qft
    circs = st_qft(args.n, args.window, args.step)
    out=[]
    for i,qc in enumerate(circs):
        out.append(f"\n=== window {i} ===\n{_draw_text(qc)}")
    txt="".join(out); print(txt)
    if args.out: _ensure_dir(args.out); open(args.out,"w").write(txt); print(f"Saved {args.out}")

def _cmd_lct(args):
    from tools.lct_czt import frac_fourier, chirp_z
    qc = frac_fourier(args.n, args.alpha) if args.mode=="frft" else chirp_z(args.n, args.k0, args.dk)
    s = _draw_text(qc); print(s)
    if args.out: _ensure_dir(args.out); open(args.out,"w").write(s); print(f"Saved {args.out}")

def _cmd_hankel(args):
    from tools.hankel_bessel import discrete_hankel_unitary
    qc = discrete_hankel_unitary(args.n, order=args.nu)
    s = _draw_text(qc); print(s)
    if args.out: _ensure_dir(args.out); open(args.out,"w").write(s); print(f"Saved {args.out}")

def _cmd_sphbessel(args):
    from tools.hankel_bessel import spherical_bessel_unitary
    qc = spherical_bessel_unitary(args.n, ell=args.ell)
    s = _draw_text(qc); print(s)
    if args.out: _ensure_dir(args.out); open(args.out,"w").write(s); print(f"Saved {args.out}")

def _cmd_hilbert(args):
    from tools.hilbert_wavelet_ntt import hilbert_transform
    qc = hilbert_transform(args.n); s = _draw_text(qc); print(s)
    if args.out: _ensure_dir(args.out); open(args.out,"w").write(s); print(f"Saved {args.out}")

def _cmd_walsh(args):
    from tools.hilbert_wavelet_ntt import walsh_hadamard
    qc = walsh_hadamard(args.n); s = _draw_text(qc); print(s)
    if args.out: _ensure_dir(args.out); open(args.out,"w").write(s); print(f"Saved {args.out}")

def _cmd_cipher(args):
    from qe_crypto.unitary_cipher import cipher_u
    from tools.leakage_meter import leakage_score_from_state
    key = (args.key.encode("utf-8") if args.key_format=="str" else bytes.fromhex(args.key))
    nonce = (args.nonce.encode("utf-8") if args.nonce_format=="str" else bytes.fromhex(args.nonce))
    qc = cipher_u(args.n, key, nonce, rounds=args.rounds)
    s = _draw_text(qc); print(s)
    psi = Statevector.from_label('0'*args.n).evolve(qc)
    score = leakage_score_from_state(psi, paulis=args.paulis)
    print(f"\nLeakage proxy (sqrt avg Pauli^2) with paulis={args.paulis}: {score:.6g}")
    if args.out: _ensure_dir(args.out); open(args.out,"w").write(s); print(f"Saved {args.out}")

def _cmd_teleport(args):
    from qe_crypto.teleport_demo import one_qubit_teleport
    qc = one_qubit_teleport(); s = _draw_text(qc); print(s)
    if args.out: _ensure_dir(args.out); open(args.out,"w").write(s); print(f"Saved {args.out}")

def _cmd_leakage(args):
    from qe_crypto.unitary_cipher import cipher_u
    from tools.leakage_meter import leakage_score_from_state
    key=b'K'*32; nonce=b'N'*16
    base = Statevector.from_label('0'*args.n)
    scores=[]
    for r in range(args.r_min, args.r_max+1):
        qc = cipher_u(args.n, key, nonce, rounds=r)
        s = leakage_score_from_state(base.evolve(qc), paulis=args.paulis)
        scores.append((r,float(s)))
        print(f"rounds={r:2d}  leakage≈ {s:.6g}")
    if args.json: _ensure_dir(args.json); open(args.json,"w").write(json.dumps({"n":args.n,"paulis":args.paulis,"scores":scores}, indent=2)); print(f"Wrote {args.json}")

def _cmd_sff(args):
    from tools.qft_module import qft
    from qe_crypto.unitary_cipher import cipher_u
    from physics.kubo_otoc_sff import spectral_form_factor
    qc = qft(args.n) if args.src=="qft" else cipher_u(args.n, b'K'*32, b'N'*16, rounds=args.rounds)
    from qiskit.quantum_info import Operator
    val = spectral_form_factor(Operator(qc), t=args.t)
    print(f"K(t={args.t}) for src={args.src}: {val:.6g}")

def add_qte_ext(sub):
    # --- QFT ---
    p=sub.add_parser("qft", help="Build/display QFT circuit")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--inverse", action="store_true")
    p.add_argument("--no-swaps", action="store_true")
    p.add_argument("--approx", type=int, default=0, help="Approximation degree")
    p.add_argument("--out"); p.set_defaults(func=_cmd_qft)

    # --- ST-QFT ---
    p=sub.add_parser("st-qft", help="Short-Time QFT on sliding windows")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--window", type=int, required=True)
    p.add_argument("--step", type=int, default=1)
    p.add_argument("--out"); p.set_defaults(func=_cmd_stqft)

    # --- LCT (FrFT / CZT) ---
    p=sub.add_parser("lct", help="Linear Canonical Transforms")
    p.add_argument("mode", choices=["frft","czt"])
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--alpha", type=float, default=0.5)
    p.add_argument("--k0", type=float, default=0.0)
    p.add_argument("--dk", type=float, default=1.0)
    p.add_argument("--out"); p.set_defaults(func=_cmd_lct)

    # --- Hankel / Spherical-Bessel ---
    p=sub.add_parser("hankel", help="Discrete Hankel transform (demo)")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--nu", type=float, default=0.0)
    p.add_argument("--out"); p.set_defaults(func=_cmd_hankel)

    p=sub.add_parser("spherical-bessel", help="Spherical-Bessel transform (demo)")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--ell", type=int, default=0)
    p.add_argument("--out"); p.set_defaults(func=_cmd_sphbessel)

    # --- Hilbert / Walsh ---
    p=sub.add_parser("hilbert", help="Hilbert transform"); p.add_argument("--n", type=int, required=True); p.add_argument("--out"); p.set_defaults(func=_cmd_hilbert)
    p=sub.add_parser("walsh", help="Walsh–Hadamard"); p.add_argument("--n", type=int, required=True); p.add_argument("--out"); p.set_defaults(func=_cmd_walsh)

    # --- Cipher / Teleport / Leakage / SFF ---
    p=sub.add_parser("cipher", help="Build cipher circuit and compute leakage on |0..0>")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--rounds", type=int, default=3)
    p.add_argument("--key", type=str, default="k"*32); p.add_argument("--key-format", choices=["str","hex"], default="str")
    p.add_argument("--nonce", type=str, default="n"*16); p.add_argument("--nonce-format", choices=["str","hex"], default="str")
    p.add_argument("--paulis", type=int, default=128)
    p.add_argument("--out"); p.set_defaults(func=_cmd_cipher)

    p=sub.add_parser("teleport", help="One-qubit teleport circuit"); p.add_argument("--out"); p.set_defaults(func=_cmd_teleport)

    p=sub.add_parser("leakage", help="Leakage vs rounds (cipher on |0..0>)")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--r-min", type=int, default=0)
    p.add_argument("--r-max", type=int, default=5)
    p.add_argument("--paulis", type=int, default=128)
    p.add_argument("--json"); p.set_defaults(func=_cmd_leakage)

    p=sub.add_parser("sff", help="Spectral Form Factor on a source circuit")
    p.add_argument("--src", choices=["qft","cipher"], default="qft")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--t", type=int, default=1)
    p.add_argument("--rounds", type=int, default=3, help="if src=cipher")
    p.set_defaults(func=_cmd_sff)


def _cmd_entropy(args):
    import json
    from qiskit.quantum_info import Statevector
    from tools.entropy_metrics import entropy_kpis
    # Load/prepare state
    if args.src == "zero":
        psi = Statevector.from_label('0'*args.n)
    elif args.src == "random":
        import numpy as np
        v = np.random.randn(2**args.n) + 1j*np.random.randn(2**args.n)
        v = v/np.linalg.norm(v)
        psi = Statevector(v)
    else:
        # Expect a .npz with key 'state' or 'psi'
        import numpy as np
        data = np.load(args.src)
        for key in ("state","psi","arr_0"):
            if key in data: 
                v = data[key]
                break
        else:
            raise RuntimeError("No 'state' or 'psi' in npz")
        psi = Statevector(v)
    kpis = entropy_kpis(psi, basis=args.basis)
    print("Entropy KPIs (basis={}):".format(args.basis))
    for k,v in kpis.items():
        print(f"  {k:>14s} : {v:.6f}")
    if args.json:
        import os
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json,"w") as f: json.dump({"basis":args.basis, "kpis":kpis}, f, indent=2)
        print(f"Wrote {args.json}")

def _cmd_dct(args):
    from tools.dct_dst import dct2_unitary
    qc = dct2_unitary(args.n); s=_draw_text(qc); print(s)
    if args.out: _ensure_dir(args.out); open(args.out,"w").write(s); print(f"Saved {args.out}")

def _cmd_dst(args):
    from tools.dct_dst import dst2_unitary
    qc = dst2_unitary(args.n); s=_draw_text(qc); print(s)
    if args.out: _ensure_dir(args.out); open(args.out,"w").write(s); print(f"Saved {args.out}")


    # --- Entropy KPIs ---
    p=sub.add_parser("entropy", help="Compute entropy KPIs for a state")
    p.add_argument("--n", type=int, required=True)
    p.add_argument("--src", choices=["zero","random","file"], default="zero")
    p.add_argument("--basis", choices=["comp","qft"], default="comp")
    p.add_argument("--json", help="Write KPIs to JSON")
    p.set_defaults(func=_cmd_entropy)

    # --- DCT/DST demos ---
    p=sub.add_parser("dct", help="DCT-II unitary (demo)"); p.add_argument("--n", type=int, required=True); p.add_argument("--out"); p.set_defaults(func=_cmd_dct)
    p=sub.add_parser("dst", help="DST-II unitary (demo)"); p.add_argument("--n", type=int, required=True); p.add_argument("--out"); p.set_defaults(func=_cmd_dst)
