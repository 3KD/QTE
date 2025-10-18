    # QROM "Digit" encoding

    **Status**
    - [ ] Drafted
    - [ ] Linked in Master
    - [ ] Code referenced
    - [ ] Tests added

    ## Summary
    _Fill in a 2–4 sentence summary here._

    ## Code pointers
    - `file_naming.py:84` — mode: str,               # "EGF", "Terms", "Periodic", "PEA", "QROM", etc.
- `quantum_embedding.py:294` — bits_per_digit: int = 4,     # store each digit in binary on this many qubits
- `quantum_embedding.py:299` — Simulation-friendly QROM:
- `quantum_embedding.py:300` — Prepare (1/√L) Σ_i |i⟩ |digit_i⟩  where digit_i = i-th fractional digit of constant(label) in 'base'.
- `quantum_embedding.py:317` — # clamp digit into available bits
- `_archive/QTEGUI2.py:2` — # Modes: EGF / Terms / Periodic p/q / Value Phase (PEA) / Digit QROM
- `_archive/QTEGUI2.py:304` — values=["EGF", "Terms", "Periodic p/q", "Value Phase (PEA)", "Digit QROM"],
- `_archive/QTEGUI2.py:319` — ttk.Label(top, text="QROM base/bits/index").grid(row=1, column=11, sticky="e")
- `_archive/QTEGUI2.py:503` — elif mode == "Digit QROM":
- `_archive/QTEGUI2.py:515` — self._set_status("Previewed digits for Digit QROM.")
- `_archive/QTEGUI2.py:552` — elif mode == "Digit QROM":
- `_archive/QTEGUI2.py:556` — key = f"{label}[QROM,b{base},d{bpd},L={2**nidx}]"
- `_archive/GTEGUI.py:2` — # Modes: EGF / Terms / Periodic p/q / Value Phase (PEA) / Digit QROM
- `_archive/GTEGUI.py:96` — values=["EGF", "Terms", "Periodic p/q", "Value Phase (PEA)", "Digit QROM"],
- `_archive/GTEGUI.py:113` — ttk.Label(top, text="QROM base/bits/index").grid(row=1, column=7, sticky="e", pady=(6,0))
- `_archive/GTEGUI.py:219` — elif mode == "Digit QROM":
- `_archive/GTEGUI.py:231` — self._set_status("Previewed digits for Digit QROM.")
- `_archive/GTEGUI.py:264` — elif mode == "Digit QROM":
- `_archive/GTEGUI.py:268` — key = f"{label}[QROM,b{base},d{bpd},L={2**nidx}]"
- `_archive/QTEGUI1.py:2` — # Modes: EGF / Terms / Periodic p/q / Value Phase (PEA) / Digit QROM
- `_archive/QTEGUI1.py:304` — values=["EGF", "Terms", "Periodic p/q", "Value Phase (PEA)", "Digit QROM"],
- `_archive/QTEGUI1.py:319` — ttk.Label(top, text="QROM base/bits/index").grid(row=1, column=11, sticky="e")
- `_archive/QTEGUI1.py:503` — elif mode == "Digit QROM":
- `_archive/QTEGUI1.py:515` — self._set_status("Previewed digits for Digit QROM.")
- `_archive/QTEGUI1.py:552` — elif mode == "Digit QROM":
- `_archive/QTEGUI1.py:556` — key = f"{label}[QROM,b{base},d{bpd},L={2**nidx}]"

    ## Test pointers
    _(no matches found)_

    ## Notes from curation
    - elif mode digit qrom
- mode str egf terms periodic pea qrom etc
- modes egf terms periodic p q value phase pea digit qrom
- self set status previewed digits digit qrom
- simulation friendly qrom

    ---
    Back to: [Master](QTEGUI_MASTER.md)
