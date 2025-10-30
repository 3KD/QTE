#!/usr/bin/env python3

# write_claims.py — generate a stamped claims.md with frozen metrics

import os, sys, json, subprocess, argparse, datetime
from pathlib import Path
from typing import Optional, Any, Dict

# --- robust import of metrics version (works as script or as package import) ---
sys.path.insert(0, os.path.dirname(__file__))
try:
    from metrics_version import VERSION as METRICS_VERSION  # script context
except Exception:
    try:
        from tools.metrics_version import VERSION as METRICS_VERSION  # package context
    except Exception:
        METRICS_VERSION = "0.0.0"

def _git_sha_short() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True
        )
        return out.stdout.strip()
    except Exception:
        return "nogit"

def write(path: str = "docs/results/claims.md",
          eps: str = "2^-20",
          fmin_chip: str = "0.99",
          fmin_metro: str = "0.90",
          extra: Optional[Dict[str, Any]] = None) -> dict:
    """
    Create a stamped claims file and return the metadata dict.
    """
    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z")
    meta = {
        "time_utc": now,
        "git_sha": _git_sha_short(),
        "metrics.version": METRICS_VERSION,
        "epsilon_target": eps,
        "F_min_on_chip": fmin_chip,
        "F_min_metro": fmin_metro,
    }
    if isinstance(extra, dict):
        meta.update(extra)

    # Simple, tooling-friendly markdown payload: JSON block with the stamp
    lines = [
        "# Claims (stamped)",
        "",
        "```json",
        json.dumps(meta, indent=2),
        "```",
        "",
    ]
    md = "\n".join(lines)

    outp = Path(path)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(md, encoding="utf-8")
    return meta

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Write a stamped claims.md")
    ap.add_argument("--out", default="docs/results/claims.md", help="Output path")
    ap.add_argument("--eps", default="2^-20")
    ap.add_argument("--fmin_chip", default="0.99")
    ap.add_argument("--fmin_metro", default="0.90")
    ap.add_argument("--extra", help="JSON string to merge into metadata", default=None)
    args = ap.parse_args(argv)

    extra = None
    if args.extra:
        try:
            extra = json.loads(args.extra)
        except Exception:
            extra = None

    write(path=args.out, eps=args.eps, fmin_chip=args.fmin_chip, fmin_metro=args.fmin_metro, extra=extra)
    print(json.dumps({"written": args.out, "metrics_version": METRICS_VERSION}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
