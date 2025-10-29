# QTEGUI API Map

_git rev_: `a576fe9`

## File: QTEGUI.py

### Flags

- **has_FigureCanvasTkAgg**: True
- **has_tk_import**: True
- **has_ttk_import**: True
- **has_eval**: False
- **has_TOMO_OK**: True
- **has_fft_wrapper**: True
- **tabs_wired**: True
- **imports_entropy_lab**: True
- **imports_harmonic_analysis**: True
- **imports_quantum_embedding**: True

### Top-level functions

- `_qte_call`

### Classes and methods


### Tabs (builders)

- (no `_build_tab_*` methods found)

### Event Handlers (`on_*`)

- (none)

## File: QTEGUI_Lite.py

### EntropyTab
- `__init__`
- `_build_ui`
- `compute_certificate`
- `save_certificate`
- `verify_certificate`

### SpectrumTab
- `__init__`
- `_build_ui`
- `spectrum`

### PayloadTab
- `__init__`
- `_build_ui`
- `run_demo`

## Coverage Checklist

- Wiring to Lite tabs present in QTEGUI: **yes**
- TOMO_OK defined: **yes**
- FFT wrapper `_fft_from_gui` used: **yes**
- Matplotlib Tk canvas import: **yes**
- Tk imports guarded: **likely**
- Optional deps present in code: entropy_lab, harmonic_analysis, quantum_embedding

