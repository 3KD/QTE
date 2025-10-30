#!/usr/bin/env python3
from pathlib import Path
import argparse, json, sys

class NonceLedger:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("[]\n", encoding="utf-8")

    def _load(self):
        try:
            return set(json.loads(self.path.read_text(encoding="utf-8")))
        except Exception:
            return set()

    def _save(self, s):
        self.path.write_text(json.dumps(sorted(s)) + "\n", encoding="utf-8")

    def has(self, nonce: str) -> bool:
        return nonce in self._load()

    def record(self, nonce: str) -> bool:
        "True iff nonce was fresh and is now recorded; False if duplicate."
        s = self._load()
        if nonce in s:
            return False
        s.add(nonce)
        self._save(s)
        return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="docs/results/nonces.json")
    ap.add_argument("--nonce", required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    L = NonceLedger(args.file)
    if args.check:
        ok = not L.has(args.nonce)
        print(json.dumps({"fresh": ok, "checked_only": True, "file": args.file}))
        sys.exit(0 if ok else 1)
    ok = L.record(args.nonce)
    print(json.dumps({"recorded_fresh": ok, "file": args.file}))
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
