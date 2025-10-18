    # Periodic p/q & PEA

    **Status**
    - [ ] Drafted
    - [ ] Linked in Master
    - [ ] Code referenced
    - [ ] Tests added

    ## Summary
    _Fill in a 2–4 sentence summary here._

    ## Code pointers
    - `file_naming.py:84` — mode: str,               # "EGF", "Terms", "Periodic", "PEA", "QROM", etc.
- `quantum_embedding.py:246` — PEA for a 'black-box' phase U = e^{2πi x}, where x = frac(constant(label)).
- `entropy_lab.py:224` — pQ  = np.abs(F)**2
- `entropy_lab.py:225` — HQ  = _shannon_bits(pQ)
- `entropy_lab.py:226` — HQinf = _min_entropy_bits(pQ)
- `_archive/QTEGUI2.py:2` — # Modes: EGF / Terms / Periodic p/q / Value Phase (PEA) / Digit QROM
- `_archive/QTEGUI2.py:304` — values=["EGF", "Terms", "Periodic p/q", "Value Phase (PEA)", "Digit QROM"],
- `_archive/QTEGUI2.py:308` — ttk.Label(top, text="PEA bits").grid(row=1, column=6, sticky="e")
- `_archive/QTEGUI2.py:312` — ttk.Label(top, text="p/q").grid(row=1, column=8, sticky="e")
- `_archive/QTEGUI2.py:517` — elif mode == "Periodic p/q":
- `_archive/QTEGUI2.py:519` — self.preview_text.insert("end", f"Periodic phase e^(2πi p n / q) with p={p}, q={q}, N=2^{n}.\n")
- `_archive/QTEGUI2.py:521` — self._set_status("Previewed periodic parameters.")
- `_archive/QTEGUI2.py:523` — elif mode == "Value Phase (PEA)":
- `_archive/QTEGUI2.py:527` — self.preview_text.insert("end", f"PEA will estimate frac({label}) ≈ {x:.12f} with ~{K} bits.\n")
- `_archive/QTEGUI2.py:528` — self._set_status("Previewed PEA parameters.")
- `_archive/QTEGUI2.py:561` — elif mode == "Periodic p/q":
- `_archive/QTEGUI2.py:570` — elif mode == "Value Phase (PEA)":
- `_archive/QTEGUI2.py:580` — self._set_status("Ran PEA (results shown).")
- `_archive/GTEGUI.py:2` — # Modes: EGF / Terms / Periodic p/q / Value Phase (PEA) / Digit QROM
- `_archive/GTEGUI.py:96` — values=["EGF", "Terms", "Periodic p/q", "Value Phase (PEA)", "Digit QROM"],
- `_archive/GTEGUI.py:101` — ttk.Label(top, text="PEA bits").grid(row=1, column=2, sticky="e", pady=(6,0))
- `_archive/GTEGUI.py:106` — ttk.Label(top, text="p/q").grid(row=1, column=4, sticky="e", pady=(6,0))
- `_archive/GTEGUI.py:233` — elif mode == "Periodic p/q":
- `_archive/GTEGUI.py:235` — self.preview_text.insert("end", f"Periodic phase e^(2πi p n / q) with p={p}, q={q}, N=2^{n}.\n")
- `_archive/GTEGUI.py:237` — self._set_status("Previewed periodic parameters.")
- `_archive/GTEGUI.py:239` — elif mode == "Value Phase (PEA)":
- `_archive/GTEGUI.py:242` — self.preview_text.insert("end", f"PEA will estimate frac({label}) ≈ {x:.12f} with ~{K} bits.\n")
- `_archive/GTEGUI.py:243` — self._set_status("Previewed PEA parameters.")
- `_archive/GTEGUI.py:271` — elif mode == "Periodic p/q":
- `_archive/GTEGUI.py:278` — elif mode == "Value Phase (PEA)":
- `_archive/GTEGUI.py:285` — self._set_status("Ran PEA (results shown).")
- `_archive/QTEGUI1.py:2` — # Modes: EGF / Terms / Periodic p/q / Value Phase (PEA) / Digit QROM
- `_archive/QTEGUI1.py:304` — values=["EGF", "Terms", "Periodic p/q", "Value Phase (PEA)", "Digit QROM"],
- `_archive/QTEGUI1.py:308` — ttk.Label(top, text="PEA bits").grid(row=1, column=6, sticky="e")
- `_archive/QTEGUI1.py:312` — ttk.Label(top, text="p/q").grid(row=1, column=8, sticky="e")
- `_archive/QTEGUI1.py:517` — elif mode == "Periodic p/q":
- `_archive/QTEGUI1.py:519` — self.preview_text.insert("end", f"Periodic phase e^(2πi p n / q) with p={p}, q={q}, N=2^{n}.\n")
- `_archive/QTEGUI1.py:521` — self._set_status("Previewed periodic parameters.")
- `_archive/QTEGUI1.py:523` — elif mode == "Value Phase (PEA)":
- `_archive/QTEGUI1.py:527` — self.preview_text.insert("end", f"PEA will estimate frac({label}) ≈ {x:.12f} with ~{K} bits.\n")
- `_archive/QTEGUI1.py:528` — self._set_status("Previewed PEA parameters.")
- `_archive/QTEGUI1.py:561` — elif mode == "Periodic p/q":
- `_archive/QTEGUI1.py:570` — elif mode == "Value Phase (PEA)":
- `_archive/QTEGUI1.py:580` — self._set_status("Ran PEA (results shown).")

    ## Test pointers
    _(no matches found)_

    ## Notes from curation
    - elif mode value phase pea
- mode str egf terms periodic pea qrom etc
- modes egf terms periodic p q value phase pea digit qrom
- pea black box phase u e 2 i x where x frac constant label
- self preview text insert end f pea estimate frac label x 12f wit
- self set status previewed pea parameters
- self set status ran pea results shown

    ---
    Back to: [Master](QTEGUI_MASTER.md)
