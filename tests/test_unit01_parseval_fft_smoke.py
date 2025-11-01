import numpy as np, subprocess, sys, tempfile, pathlib as pl

def _build(label, Nq=8):
    out_dir = pl.Path(tempfile.mkdtemp())
    npy = out_dir/"state.npy"
    cmd = [sys.executable, "qte_cli.py", "--label", label, "--nq", str(Nq), "--dump", str(npy)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, f"builder failed: {r.stderr or r.stdout}"
    return np.load(npy)

def test_unit01_parseval_energy_conservation():
    x = _build("Maclaurin[sin(x)] egf", 8).astype(np.complex128)
    # Probability conservation in FFT domain (unitary normalization)
    X = np.fft.fft(x) / np.sqrt(x.size)
    e_time = np.vdot(x, x).real
    e_freq = np.vdot(X, X).real
    assert abs(e_time - 1.0) < 1e-10, "input not normalized"
    assert abs(e_freq - 1.0) < 1e-8, f"Parseval violation: {e_time} vs {e_freq}"
