
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, Union
from datetime import datetime

Json = Dict[str, Any]

@dataclass
class QTEArtifact:
    # Core
    type: str                     # 'ergodic' | 'topo' | 'vib_spec' | 'bessel' | 'signaling' | ...
    timestamp: str                # ISO8601
    backend: Optional[str] = None
    shots: Optional[int] = None
    job_id: Optional[Union[str, dict]] = None

    # Experiment description / knobs
    params: Dict[str, Any] = None   # e.g. {'K':7,'M':128,'mu':3.9,'phi':..., 'basis':'bessel', ...}

    # Hardware/circuit info
    circuit: Dict[str, Any] = None  # e.g. {'depth':232,'twoq':82,'seed':3,'width':7}

    # Measured metrics (names are stable across families when possible)
    metrics: Dict[str, Any] = None  # common keys below

    # Optional extra files
    artifacts: Dict[str, Any] = None

    def to_json(self) -> Json:
        d = asdict(self)
        # ensure dict defaults
        for k in ('params','circuit','metrics','artifacts'):
            if d.get(k) is None: d[k] = {}
        return d

# ---- Common metrics (documented, not enforced) ----
# Shared:  metrics.ks_entropy, metrics.corr_decay_tau, metrics.spectral_radius, metrics.spectral_gap,
#          metrics.ipr_mean, metrics.ipr_var, metrics.mutual_information, metrics.fidelity,
#          metrics.winding, metrics.chern, metrics.dos_peaks, metrics.fc_max, metrics.hankel_unitarity_error
#
# Rule: add new metrics under metrics.<name> (snake_case). Keep names short & consistent.
