# Entropy Certificates (Z/QFT)

Deterministic “entropy certificates” travel with an amplitude vector \(a \in \mathbb{C}^d\) and can be recomputed by a receiver to verify integrity.

## Fields (schema v1)

- `d` — Hilbert space dimension \(d\)
- `basis_pair` — currently `"Z/QFT"` (computational + discrete Fourier)
- `H_Z_bits` — Shannon entropy of \(p_z = |a|^2\) (bits)
- `Hmin_Z_bits` — Min-entropy of \(p_z\) (bits)
- `H_QFT_bits` — Shannon entropy of \(p_f = |Fa|^2\) with unitary DFT \(F/\sqrt{d}\) (bits)
- `Hmin_QFT_bits` — Min-entropy of \(p_f\) (bits)
- `flatness` — spectral flatness of two-sided power \( |\mathrm{FFT}(a)|^2 \) (geom/arith mean)
- `version` — schema version (int)

## Theoretical checks

- **Maassen–Uffink (MUB) bound**: for dimension \(d\),
  \[
  H_Z(a) + H_{QFT}(a) \ge \log_2 d.
  \]
  We test this for standard basis vectors and several \(d\).

- **Ensemble von Neumann entropy**:  
  `ensemble_von_neumann_entropy(w, states)` computes \(S(\rho)\) for \(\rho = \sum_i w_i |\psi_i\rangle\!\langle\psi_i|\).

## CLI

Emit and (optionally) verify a certificate:

```bash
./tools/entropy_cert_cli.py --state 0.70710678,0,0,0.70710678 > bell_cert.json
./tools/entropy_cert_cli.py --state 0.70710678,0,0,0.70710678 --verify bell_cert.json

