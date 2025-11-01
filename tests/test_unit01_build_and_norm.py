import json, subprocess, sys, tempfile, numpy as np, pathlib as pl

def _run_build(label, nq=8, out_dir=None):
    out_dir = pl.Path(out_dir or tempfile.mkdtemp())
    npy = out_dir/"u1_state.npy"
    cmd = [sys.executable, "qte_cli.py", "--label", label, "--nq", str(nq), "--dump", str(npy)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, f"builder failed: {r.stderr or r.stdout}"
    assert npy.exists(), "state .npy not produced"
    return np.load(npy), npy

def test_unit01_build_maclaurin_sin_norm_l2():
    x, _ = _run_build("Maclaurin[sin(x)]")
    # unit-norm within tight tolerance
    nrm = np.linalg.norm(x)
    assert np.isfinite(nrm)
    assert abs(nrm - 1.0) < 1e-10, f"non-unit norm: {nrm}"

def test_unit01_build_cos_vs_sin_shape_equal():
    a, _ = _run_build("Maclaurin[sin(x)]", nq=8)
    b, _ = _run_build("Maclaurin[cos(x)]", nq=8)
    assert a.shape == b.shape and a.ndim == 1
