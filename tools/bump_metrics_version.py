#!/usr/bin/env python3
from pathlib import Path
import re
p = Path(__file__).with_name("metrics_version.py")
s = p.read_text(encoding="utf-8")
m = re.search(r'VERSION\s*=\s*"(\d+)\.(\d+)\.(\d+)"', s)
if not m:
    raise SystemExit("could not parse metrics version")
maj, minr, patch = map(int, m.groups())
patch += 1
new = re.sub(r'VERSION\s*=\s*"[0-9\.]+"', f'VERSION = "{maj}.{minr}.{patch}"', s)
p.write_text(new + "\n", encoding="utf-8")
print(new.strip())
