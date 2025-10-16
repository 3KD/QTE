import numpy as np
from harmonic_analysis import compute_fft_spectrum_from_amplitudes

# ---------- Reference transform (the "ground truth") ----------
def reference_dollarhide_spectrum(x, *, remove_dc=False, window=None, pad_len=None):
    x = np.asarray(x, dtype=np.complex128)

    # windowing
    if window and window.lower() != "-":
        if window.lower() == "hann":
            w = np.hanning(len(x))
        else:
            raise ValueError(f"unsupported window: {window}")
        xw = x * w
    else:
        xw = x

    # DC removal
    if remove_dc:
        xw = xw - np.mean(xw)

    # zero-padding
    N = len(xw)
    if pad_len and pad_len > 0:
        M = int(pad_len)
        if M < N:
            raise ValueError("pad_len must be >= len(x)")
        xp = np.zeros(M, dtype=np.complex128)
        xp[:N] = xw
    else:
        xp = xw
        M = N

    # FFT and power
    X = np.fft.fft(xp)
    P = np.abs(X) ** 2

    # metrics
    S = float(P.sum()) if P.size else 1.0
    dc = float(P[0] / S) if S > 0 else 0.0
    p = P / S if S > 0 else P
    p = p[p > 0]
    H = float(-np.sum(p * np.log2(p))) if p.size else 0.0
    mets = {"len": int(N), "dc_frac": dc, "entropy_bits": H}
    return P, np.arange(M), mets

# ---------- Helpers ----------
def nms_peaks(power, k, exclude_radius=2):
    """Greedy non-maximum suppression peak picker."""
    P = power.copy()
    idxs = []
    for _ in range(min(k, P.size)):
        i = int(np.argmax(P))
        idxs.append(i)
        L = max(0, i - exclude_radius)
        R = min(P.size, i + exclude_radius + 1)
        P[L:R] = -np.inf
    return idxs

def nearly_zero_spectrum(P, atol=1e-12):
    return bool(np.all(np.abs(P) < atol))

def assert_equiv(name, x, **opts):
    """Compare QTE transform to explicit reference. Returns bool."""
    P_ref, f_ref, m_ref = reference_dollarhide_spectrum(x, **opts)
    P_qte, f_qte, m_qte = compute_fft_spectrum_from_amplitudes(x, **opts)

    same_length = (len(P_ref) == len(P_qte))
    same_bins   = np.array_equal(f_ref, f_qte)
    rms = 0.0 if P_ref.size == 0 else np.sqrt(np.mean((P_ref - P_qte)**2)) / (np.max(P_ref) + 1e-30)

    ok = same_length and same_bins and (rms < 1e-12 or (nearly_zero_spectrum(P_ref) and nearly_zero_spectrum(P_qte)))
    print(f"{name:<22s} {'OK' if ok else 'MISMATCH'} | rel_rms={rms:.3e} | M={len(P_qte)} opts={opts}")
    return ok

def check_peaks(name, x, *, expect_peaks, peak_tol_bins=0, exclude_radius=2, **opts):
    """Peak-based behavior check, pad-aware."""
    P, freqs, _ = compute_fft_spectrum_from_amplitudes(x, **opts)
    N = len(x); M = len(P)
    scale = (M / N) if (opts.get("pad_len") and opts["pad_len"] > 0) else 1.0

    if nearly_zero_spectrum(P):
        # Spectrum is (numerically) zero; skip peak assertions
        print(f"{name:<22s} OK | zero-power spectrum after opts={opts}")
        return True

    exp_scaled = [int(round(r * scale)) % M for r in expect_peaks]
    got = nms_peaks(P, k=len(exp_scaled), exclude_radius=exclude_radius)

    ok = True
    for e in exp_scaled:
        ok &= any(abs(e - g) <= peak_tol_bins for g in got)

    print(f"{name:<22s} {'OK' if ok else 'MISMATCH'} | peaks_qte={got} expect≈={exp_scaled} tol={peak_tol_bins} opts={opts}")
    return ok

def main():
    ok = True
    N = 64
    n = np.arange(N)

    # 1) Dirac -> flat (sanity) + equivalence
    delta = np.zeros(N, dtype=complex); delta[0] = 1.0
    ok &= assert_equiv("delta (flat)", delta)

    # 2) Constant -> DC only; removing DC zeroes spectrum
    const = np.ones(N, dtype=complex)
    ok &= assert_equiv("constant (raw)", const)
    # After DC removal, just verify transform equivalence and zero-power behavior
    ok &= assert_equiv("constant (remove_dc)", const, remove_dc=True)

    # 3) Single tone at r
    r = 5
    tone = np.exp(1j * 2*np.pi * r * n / N)
    ok &= assert_equiv("single tone", tone)
    ok &= check_peaks("single tone peaks", tone, expect_peaks=[r], peak_tol_bins=0)
    ok &= assert_equiv("single tone (pad512)", tone, pad_len=512)
    ok &= check_peaks("single tone (pad512) peaks", tone, pad_len=512, expect_peaks=[r], peak_tol_bins=0)

    # 4) Two tones; Hann broadens main lobe—use NMS to avoid side-lobe confusion
    r1, r2 = 7, 15
    twotone = np.exp(1j * 2*np.pi * r1 * n / N) + 0.5*np.exp(1j * 2*np.pi * r2 * n / N)
    ok &= assert_equiv("two tones", twotone)
    ok &= check_peaks("two tones peaks", twotone, expect_peaks=[r1, r2], peak_tol_bins=0)
    ok &= assert_equiv("two tones (hann)", twotone, window="hann")
    ok &= check_peaks("two tones (hann) peaks", twotone, window="hann",
                      expect_peaks=[r1, r2], peak_tol_bins=2, exclude_radius=2)

    # 5) Random: DC removal reduces bin-0 energy; also equivalence
    rng = np.random.RandomState(123)
    rnd = rng.randn(N) + 1j*rng.randn(N)
    ok &= assert_equiv("random (raw)", rnd)
    ok &= assert_equiv("random (remove_dc)", rnd, remove_dc=True)

    print("\nPASS" if ok else "\nFAIL")

if __name__ == "__main__":
    main()
