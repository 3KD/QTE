import subprocess, sys, tempfile, numpy as np, pathlib as pl

def _build(label, out_name):
    out_dir = pl.Path(tempfile.mkdtemp())
    npy = out_dir/out_name
    cmd = [sys.executable, "qte_cli.py", "--label", label, "--nq", "8", "--dump", str(npy)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, f"builder failed: {r.stderr or r.stdout}"
    return np.load(npy)

def test_unit01_terms_vs_egf_both_normalized_and_different():
    x_terms = _build("Maclaurin[sin(x)] terms", "terms.npy")
    x_egf   = _build("Maclaurin[sin(x)] egf", "egf.npy")
    n1 = np.linalg.norm(x_terms); n2 = np.linalg.norm(x_egf)
    assert abs(n1-1.0) < 1e-10 and abs(n2-1.0) < 1e-10
    # Expect some difference between weighting modes
    assert np.linalg.norm(x_terms - x_egf) > 1e-6
