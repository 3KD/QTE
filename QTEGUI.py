# QTEGUI — minimal wrapper hosting QTEGUI_Lite tabs
from __future__ import annotations
import tkinter as tk
from tkinter import ttk

# Transitional: pull tabs from QTEGUI_Lite if available
try:
    from QTEGUI_Lite import EntropyTab, SpectrumTab, PayloadTab
except Exception:
    EntropyTab = SpectrumTab = PayloadTab = None

class QTEGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quantum Transcendental Encoder (QTE)")
        self.geometry("1100x800")
        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True, padx=10, pady=10)
        # add tabs when present
        try:
            if EntropyTab is not None:
                nb.add(EntropyTab(nb), text="Entropy")
            if SpectrumTab is not None:
                nb.add(SpectrumTab(nb), text="Spectrum")
            if PayloadTab is not None:
                nb.add(PayloadTab(nb), text="Payload")
        except Exception as e:
            print("[WARN] Could not add Lite tabs:", e)

if __name__ == "__main__":
    app = QTEGUI()
    app.mainloop()
