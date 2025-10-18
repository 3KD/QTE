    # Entanglement analyzer & Schmidt

    **Status**
    - [ ] Drafted
    - [ ] Linked in Master
    - [ ] Code referenced
    - [ ] Tests added

    ## Summary
    _Fill in a 2–4 sentence summary here._

    ## Code pointers
    - `file_naming.py:3` — # Includes an entanglement signature (per-register-cut Schmidt entropies).
- `file_naming.py:53` — # ---- Entanglement signature ---------------------------------------------------
- `sweep_polylog.py:12` — # Entanglement per register-cut (only if we have a multi-register structure)
- `run_series_grid.py:2` — # Quick local batch: build several series states (and algebra combos) and save with entanglement-aware filenames.
- `quantum_embedding.py:132` — Useful only as a demo for simple 'fractional' entanglement.
- `quantum_embedding.py:236` — return S  # singular values (Schmidt coeffs)
- `quantum_embedding.py:356` — # --- QTE hotfix (append-only): numpy-based Schmidt decomposition for tests ---
- `tools/review_qtegui.py:25` — # 4) Schmidt purity with NumPy arrays (not DensityMatrix @ DensityMatrix)
- `tools/smoke_all.py:51` — ok("Schmidt entropy = 1 bit")
- `_archive/QTEGUI2.py:4` — # Extras: register block labeling, grid overlays, Schmidt entropies, register marginals
- `_archive/QTEGUI2.py:410` — # NEW: parse multi label and get Schmidt entropy
- `_archive/QTEGUI2.py:851` — # Register grid + Schmidt entropies
- `_archive/QTEGUI2.py:863` — # Schmidt entropies across register cuts
- `_archive/QTEGUI2.py:870` — "Schmidt entropies (bits):  " +
- `_archive/QTEGUI2.py:1096` — # ================== Tab 9: Entanglement ==================
- `_archive/QTEGUI2.py:1098` — tab = ttk.Frame(self.nb); self.nb.add(tab, text="Entanglement")
- `_archive/QTEGUI2.py:1164` — axs[1].imshow(np.outer(S, S), cmap="magma"); axs[1].set_title("Schmidt (outer product)")
- `_archive/QTEGUI2.py:1169` — messagebox.showerror("Entanglement Error", str(e))
- `_archive/GTEGUI.py:4` — # Entanglement: simple 2-qubit, series registers, multi-constant
- `_archive/GTEGUI.py:573` — # ================== Tab 9: Entanglement ==================
- `_archive/GTEGUI.py:575` — tab = ttk.Frame(self.nb); self.nb.add(tab, text="Entanglement")
- `_archive/GTEGUI.py:644` — axs[1].imshow(np.outer(S, S), cmap="magma"); axs[1].set_title("Schmidt (outer product)")
- `_archive/GTEGUI.py:651` — messagebox.showerror("Entanglement Error", str(e))
- `_archive/QTEGUI1.py:4` — # Extras: register block labeling, grid overlays, Schmidt entropies, register marginals
- `_archive/QTEGUI1.py:410` — # NEW: parse multi label and get Schmidt entropy
- `_archive/QTEGUI1.py:819` — # Register grid + Schmidt entropies
- `_archive/QTEGUI1.py:831` — # Schmidt entropies across register cuts
- `_archive/QTEGUI1.py:838` — "Schmidt entropies (bits):  " +
- `_archive/QTEGUI1.py:1008` — # ================== Tab 9: Entanglement ==================
- `_archive/QTEGUI1.py:1010` — tab = ttk.Frame(self.nb); self.nb.add(tab, text="Entanglement")
- `_archive/QTEGUI1.py:1076` — axs[1].imshow(np.outer(S, S), cmap="magma"); axs[1].set_title("Schmidt (outer product)")
- `_archive/QTEGUI1.py:1081` — messagebox.showerror("Entanglement Error", str(e))

    ## Test pointers
    _(no matches found)_

    ## Notes from curation
    - 4 schmidt purity numpy arrays not densitymatrix densitymatrix
- 9 entanglement
- axs 1 imshow np outer s s cmap magma axs 1 set title schmidt outer pr
- build entanglement
- entanglement per register cut only if we have multi register structure
- entanglement signature
- entanglement simple 2 qubit series registers multi constant
- extras register block labeling grid overlays schmidt entropies register ma
- hotfix append only numpy based schmidt decomposition tests
- includes entanglement signature per register cut schmidt entropies
- messagebox showerror entanglement error str e
- new parse multi label get schmidt entropy
- ok schmidt entropy 1 bit
- register grid schmidt entropies
- return s singular values schmidt coeffs
- schmidt entropies across register cuts
- schmidt entropies bits
- schmidt entropy

    ---
    Back to: [Master](QTEGUI_MASTER.md)
