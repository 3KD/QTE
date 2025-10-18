    # Tomography path & fallback

    **Status**
    - [ ] Drafted
    - [ ] Linked in Master
    - [ ] Code referenced
    - [ ] Tests added

    ## Summary
    _Fill in a 2–4 sentence summary here._

    ## Code pointers
    - `QTEGUI.py:6` — # --- Tomography availability flag (safe) ---
- `QTEGUI.py:11` — TOMO_OK = (StateTomography is not None)
- `tests/test_qtegui_presence.py:5` — # TOMO_OK should exist (flag)
- `tests/test_qtegui_presence.py:6` — assert hasattr(m, "TOMO_OK")
- `_archive/QTEGUI2.py:20` — # Optional tomography
- `_archive/QTEGUI2.py:25` — TOMO_OK = True
- `_archive/QTEGUI2.py:27` — TOMO_OK = False
- `_archive/QTEGUI2.py:1045` — # ================== Tab 8: Tomography ==================
- `_archive/QTEGUI2.py:1047` — tab = ttk.Frame(self.nb); self.nb.add(tab, text="Tomography")
- `_archive/QTEGUI2.py:1048` — if not TOMO_OK:
- `_archive/QTEGUI2.py:1052` — ttk.Button(tab, text="Run Tomography", command=self.on_run_tomography).pack(pady=6)
- `_archive/QTEGUI2.py:1057` — if not TOMO_OK:
- `_archive/QTEGUI2.py:1061` — messagebox.showinfo("Tomography", "No active or selected state."); return
- `_archive/QTEGUI2.py:1094` — messagebox.showerror("Tomography Error", str(e))
- `_archive/GTEGUI.py:3` — # Active-state first: FFT/QFT/Measure/Amplitudes/Tomography/Basis all use Active if no selection
- `_archive/GTEGUI.py:20` — # Optional tomography
- `_archive/GTEGUI.py:25` — TOMO_OK = True
- `_archive/GTEGUI.py:27` — TOMO_OK = False
- `_archive/GTEGUI.py:539` — # ================== Tab 8: Tomography ==================
- `_archive/GTEGUI.py:541` — tab = ttk.Frame(self.nb); self.nb.add(tab, text="Tomography")
- `_archive/GTEGUI.py:542` — if not TOMO_OK:
- `_archive/GTEGUI.py:546` — ttk.Button(tab, text="Run Tomography", command=self.on_run_tomography).pack(pady=6)
- `_archive/GTEGUI.py:551` — if not TOMO_OK: return
- `_archive/GTEGUI.py:554` — messagebox.showinfo("Tomography", "No active or selected state."); return
- `_archive/GTEGUI.py:571` — messagebox.showerror("Tomography Error", str(e))
- `_archive/QTEGUI1.py:20` — # Optional tomography
- `_archive/QTEGUI1.py:25` — TOMO_OK = True
- `_archive/QTEGUI1.py:27` — TOMO_OK = False
- `_archive/QTEGUI1.py:974` — # ================== Tab 8: Tomography ==================
- `_archive/QTEGUI1.py:976` — tab = ttk.Frame(self.nb); self.nb.add(tab, text="Tomography")
- `_archive/QTEGUI1.py:977` — if not TOMO_OK:
- `_archive/QTEGUI1.py:981` — ttk.Button(tab, text="Run Tomography", command=self.on_run_tomography).pack(pady=6)
- `_archive/QTEGUI1.py:986` — if not TOMO_OK: return
- `_archive/QTEGUI1.py:989` — messagebox.showinfo("Tomography", "No active or selected state."); return
- `_archive/QTEGUI1.py:1006` — messagebox.showerror("Tomography Error", str(e))

    ## Test pointers
    - `tests/test_qtegui_presence.py:5` — # TOMO_OK should exist (flag)
- `tests/test_qtegui_presence.py:6` — assert hasattr(m, "TOMO_OK")

    ## Notes from curation
    - 8 tomography
- active state first fft qft measure amplitudes tomography basis all use active
- build tomography
- messagebox showerror tomography error str e
- messagebox showinfo tomography no active selected state return
- optional tomography
- run tomography
- tomography availability flag safe

    ---
    Back to: [Master](QTEGUI_MASTER.md)
