    # Dual-rail / sign-split encoding

    **Status**
    - [ ] Drafted
    - [ ] Linked in Master
    - [ ] Code referenced
    - [ ] Tests added

    ## Summary
    _Fill in a 2–4 sentence summary here._

    ## Code pointers
    - `series_encoding.py:5` — # - encode_srd_iq / decode_srd_iq  (Sign-split dual-rail in I/Q)
- `series_encoding.py:496` — # SRD (Sign-split) on I/Q rails
- `series_encoding.py:499` — def encode_srd_iq(a: np.ndarray) -> np.ndarray:
- `series_encoding.py:509` — def decode_srd_iq(re_rail: np.ndarray, im_rail: np.ndarray) -> np.ndarray:
- `series_encoding.py:510` — """Reconstruct original real values from SRD/IQ rails."""
- `series_encoding.py:587` — srd_mode: str = "iq",
- `series_encoding.py:592` — (optional) SBRV refine -> SRD/IQ pack -> pad/truncate to 2^n -> L2 normalize
- `series_encoding.py:601` — if srd_mode.lower() == "iq":
- `series_encoding.py:602` — packed = encode_srd_iq(a)   # complex: re=positive, im=negative
- `rail_masks.py:1` — # QTE add-on: simple rail masks & carriers.
- `dual_rail_composition.py:1` — # QTE add-on: Dual-rail (ancilla-tag) composition spec.
- `dual_rail_composition.py:6` — def compose_dual_rail(psiA: np.ndarray,
- `dual_rail_composition.py:24` — def decompose_dual_rail(spec: Dict[str, Any]):
- `qte_smoke.py:4` — encode_srd_iq, decode_srd_iq, build_sbrv, reconstruct_sbrv
- `qte_smoke.py:12` — # SRD/IQ round-trip (norm-invariant)
- `qte_smoke.py:14` — c = encode_srd_iq(a)
- `qte_smoke.py:15` — art = decode_srd_iq(c.real, c.imag)
- `qte_smoke.py:16` — print("SRD/IQ ok:", np.allclose(a/np.linalg.norm(a), art/np.linalg.norm(art), atol=1e-6))
- `qte_smoke.py:27` — res = qte_extras_encode(coeffs, n_qubits=nq, srd_mode="iq", sbrv_levels=2)
- `sign_split_register.py:1` — # QTE add-on: Sign-Split Registers (SRD) + I/Q packing
- `sign_split_register.py:5` — def sign_split(a: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
- `sign_split_register.py:19` — def encode_srd_ancilla(a: np.ndarray,
- `sign_split_register.py:24` — Phase-insensitive SRD (ancilla-tag) spec:
- `sign_split_register.py:28` — p, n = sign_split(a)
- `sign_split_register.py:31` — def encode_srd_iq(a: np.ndarray) -> np.ndarray:
- `sign_split_register.py:33` — Phase-aware SRD (I/Q) packing: c = p + i n  with a = p - n.
- `sign_split_register.py:36` — p, n = sign_split(a)
- `sign_split_register.py:40` — def decode_srd_iq(real_part: np.ndarray, imag_part: np.ndarray) -> np.ndarray:

    ## Test pointers
    - `qte_smoke.py:4` — encode_srd_iq, decode_srd_iq, build_sbrv, reconstruct_sbrv
- `qte_smoke.py:12` — # SRD/IQ round-trip (norm-invariant)
- `qte_smoke.py:14` — c = encode_srd_iq(a)
- `qte_smoke.py:15` — art = decode_srd_iq(c.real, c.imag)
- `qte_smoke.py:16` — print("SRD/IQ ok:", np.allclose(a/np.linalg.norm(a), art/np.linalg.norm(art), atol=1e-6))
- `qte_smoke.py:27` — res = qte_extras_encode(coeffs, n_qubits=nq, srd_mode="iq", sbrv_levels=2)

    ## Notes from curation
    - add dual rail ancilla tag composition spec
- add rail split extra sign qubit strict egf weighting qft amplitudes
- add sign split registers srd i q packing
- encode srd iq decode srd iq sign split dual rail i q
- srd sign split i q rails

    ---
    Back to: [Master](QTEGUI_MASTER.md)
