#!/usr/bin/env python3
import json, argparse, numpy as np
from entropy_lab import entropy_certificate_pack, entropy_certificate_verify

def main():
    ap = argparse.ArgumentParser(description="QTE entropy certificate tool")
    ap.add_argument("--state", help="Comma-separated amplitudes (complex like 0.5+0.5j)", required=True)
    ap.add_argument("--verify", help="Path to JSON certificate to verify", default=None)
    ap.add_argument("--atol", type=float, default=0.05, help="tolerance in bits (default 0.05)")
    args = ap.parse_args()

    def parse_amp(s):
        # Python complex parser accepts 'j'; allow bare real too
        return complex(s)

    a = np.array([parse_amp(x) for x in args.state.split(",")], complex)
    cert = entropy_certificate_pack(a)
    print(json.dumps(cert, indent=2))

    if args.verify:
        ref = json.load(open(args.verify, "r"))
        ok, info = entropy_certificate_verify(a, ref, atol_bits=args.atol)
        print("\nVERIFY:", "OK" if ok else "MISMATCH")
        print(json.dumps(info, indent=2))

if __name__ == "__main__":
    main()
