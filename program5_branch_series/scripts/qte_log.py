
from __future__ import annotations
import json, csv
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

# Flatten nested dict with dotted keys (metrics.ks_entropy)
def _flatten(prefix: str, d: Dict[str, Any], out: Dict[str, Any]):
    for k,v in (d or {}).items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            _flatten(key, v, out)
        else:
            out[key] = v

def _to_row(j: Dict[str, Any]) -> Dict[str, Any]:
    row: Dict[str, Any] = {}
    # top-level
    for k in ("type","timestamp","backend","shots","file"):
        row[k] = j.get(k)
    # job_id: stringify for CSV
    row["job_id"] = json.dumps(j.get("job_id")) if j.get("job_id") is not None else ""
    # flatten params/circuit/metrics
    _flatten("params", j.get("params",{}), row)
    _flatten("circuit", j.get("circuit",{}), row)
    _flatten("metrics", j.get("metrics",{}), row)
    return row

def log_artifact(artifact_path: Path, payload: Dict[str, Any], index_csv: Path):
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    with artifact_path.open("w") as f:
        json.dump(payload, f, indent=2)
    # append CSV (header grows as needed)
    row = _to_row({**payload, "file": str(artifact_path)})
    hdr = list(row.keys())
    if index_csv.exists():
        # read header
        with index_csv.open("r", newline="") as rf:
            r = csv.reader(rf)
            try:
                old_hdr = next(r)
            except StopIteration:
                old_hdr = []
        # merge headers (preserve order, append new keys)
        for k in hdr:
            if k not in old_hdr:
                old_hdr.append(k)
        # rewrite file with merged header + keep old rows, then append new row in that order
        with index_csv.open("r", newline="") as rf:
            rows = list(csv.DictReader(rf))
        with index_csv.open("w", newline="") as wf:
            w = csv.DictWriter(wf, fieldnames=old_hdr)
            w.writeheader()
            for rr in rows:
                # fill missing new keys with ''
                for k in old_hdr:
                    rr.setdefault(k, "")
                w.writerow(rr)
            # align new row
            for k in old_hdr:
                row.setdefault(k, "")
            w.writerow(row)
    else:
        with index_csv.open("w", newline="") as wf:
            w = csv.DictWriter(wf, fieldnames=hdr)
            w.writeheader()
            w.writerow(row)
