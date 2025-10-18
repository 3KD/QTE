    # Precision scaling

    **Status**
    - [ ] Drafted
    - [ ] Linked in Master
    - [ ] Code referenced
    - [ ] Tests added

    ## Summary
    _Fill in a 2–4 sentence summary here._

    ## Code pointers
    - `sbrv_precision.py:1` — # QTE add-on: Stacked Binary Residual Vectors (SBRV).
- `sbrv_precision.py:17` — Build SBRV:
- `series_encoding.py:6` — # - SBRV precision stacking: build_sbrv / reconstruct_sbrv
- `series_encoding.py:516` — # SBRV: stacked binary residual vectors (quantized residual stacking)
- `series_encoding.py:592` — (optional) SBRV refine -> SRD/IQ pack -> pad/truncate to 2^n -> L2 normalize
- `qte_smoke.py:18` — # SBRV improves with level
- `qte_smoke.py:22` — print("SBRV improves:", np.linalg.norm(a3-a) <= np.linalg.norm(a1-a))
- `precision_scaling.py:1` — # QTE add-on: simple fidelity/distortion bound for SBRV depth L.

    ## Test pointers
    - `qte_smoke.py:18` — # SBRV improves with level
- `qte_smoke.py:22` — print("SBRV improves:", np.linalg.norm(a3-a) <= np.linalg.norm(a1-a))

    ## Notes from curation
    - sbrv precision stacking build sbrv reconstruct sbrv

    ---
    Back to: [Master](QTEGUI_MASTER.md)
