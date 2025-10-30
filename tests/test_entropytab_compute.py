import importlib, numpy as np
def test_entropytab_compute_certificate():
    lite = importlib.import_module("QTEGUI_Lite")
    T = lite.EntropyTab
    tab = T.__new__(T)
    try: T.__init__(tab, master=None)
    except Exception: pass
    tab.last_amplitudes = np.array([1,0], complex)  # |0>
    cert = tab.compute_certificate()
    assert isinstance(cert, dict)
    assert 'H_Z_bits' in cert and 'H_QFT_bits' in cert
