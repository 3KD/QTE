#!/usr/bin/env python3
# (same content as you pasted; make sure the last line is exactly "PY" below to close)
from __future__ import annotations
import argparse, json, hmac, hashlib
import numpy as np
from typing import Dict, Tuple
from entropy_lab import entropy_certificate_pack, entropy_certificate_verify
def int_to_basis_amplitudes(n: int, v: int) -> np.ndarray:
    d = 1 << n
    if v < 0 or v >= d: raise ValueError(f"v must be in [0,{d-1}]")
    a = np.zeros(d, dtype=np.complex128); a[v] = 1.0; return a
def _prng(key: bytes):
    seed = int.from_bytes(hashlib.sha256(key).digest()[:8], "big"); return np.random.default_rng(seed)
def scramble_amplitudes(a: np.ndarray, key: bytes) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    rng=_prng(key); d=a.size; perm=np.arange(d); rng.shuffle(perm); phases=np.exp(1j*rng.uniform(0,2*np.pi,d))
    return phases * a[perm], {"perm":perm, "phases":phases}
def unscramble_amplitudes(b: np.ndarray, params: Dict[str, np.ndarray]) -> np.ndarray:
    perm=params["perm"]; phases=params["phases"]; inv=np.empty_like(perm); inv[perm]=np.arange(perm.size)
    a_hat=np.zeros_like(b); a_hat[perm]=b/(phases+0.0j); return a_hat[inv]
def hmac_tag(payload_bytes: bytes, mac_key: bytes, tag_bits: int = 128) -> str:
    take=max(1, tag_bits//8); return hmac.new(mac_key, payload_bytes, hashlib.sha256).digest()[:take].hex()
def capacity_report(n:int)->Dict[str,float]: return {"bits_per_register_plain":float(n),"bits_per_register_superdense":float(2*n)}
def main():
    ap=argparse.ArgumentParser(description="QTE payload MVP")
    g=ap.add_mutually_exclusive_group()
    ap.add_argument("--n",type=int,default=8)
    g.add_argument("--payload-int",type=int)
    g.add_argument("--payload-hex",type=str)
    ap.add_argument("--key",type=str,default="demo-key")
    ap.add_argument("--tamper",action="store_true")
    ap.add_argument("--mac-key",type=str)
    ap.add_argument("--json",action="store_true")
    ap.add_argument("--atol-bits",type=float,default=1e-9)
    args=ap.parse_args()
    n=int(args.n); d=1<<n
    if args.payload_int is not None:
        v=int(args.payload_int)%d; payload_bytes=v.to_bytes((n+7)//8 or 1,"big")
    elif args.payload_hex:
        raw=bytes.fromhex(args.payload_hex); v=int.from_bytes(raw,"big")%d; payload_bytes=raw
    else:
        v=0; payload_bytes=b"\x00"
    a=int_to_basis_amplitudes(n,v)
    cert=entropy_certificate_pack(a,basis_pair="Z/QFT")
    a_scr,params=scramble_amplitudes(a,args.key.encode())
    if args.tamper and d>=2:
        perm=params["perm"].copy(); perm[0],perm[1]=perm[1],perm[0]; params={"perm":perm,"phases":params["phases"]}
    a_recv=unscramble_amplitudes(a_scr,params)
    ok,info=entropy_certificate_verify(a_recv,cert,atol_bits=args.atol_bits)
    mac = hmac_tag(payload_bytes, args.mac_key.encode()) if args.mac_key else None
    cap=capacity_report(n)
    summary={"n":n,"d":d,"payload_int":v,"tampered":bool(args.tamper),"verify_ok":bool(ok),
             "verify_info":info,"capacity_bits_per_register_plain":cap["bits_per_register_plain"],
             "capacity_bits_per_register_superdense":cap["bits_per_register_superdense"],"mac_tag_hex":mac,"certificate":cert}
    if args.json: print(json.dumps(summary,indent=2)); return
    print("=== QTE Payload MVP ===")
    print(f" n={n} (d={d})   payload |v> with v={v}")
    print(f" scramble key:   {args.key!r}  (deterministic phase+perm)")
    print(f" tampered:       {summary['tampered']}")
    print(f" verify:         {'OK' if summary['verify_ok'] else 'MISMATCH'}")
    if not summary["verify_ok"]: print(" deltas:", summary["verify_info"].get("deltas", {}))
    print(f" capacity:       {cap['bits_per_register_plain']} bits/register (plain)")
    print(f"                 {cap['bits_per_register_superdense']} bits/register (superdense; needs ebits)")
    if mac: print(f" MAC (hex):      {mac}")
if __name__ == "__main__": main()
