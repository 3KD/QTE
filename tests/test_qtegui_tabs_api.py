
import importlib, types

def test_tabs_importable():
    lite = importlib.import_module("QTEGUI_Lite")
    assert hasattr(lite, "EntropyTab")
    assert hasattr(lite, "SpectrumTab")
    assert hasattr(lite, "PayloadTab")

def test_entropy_tab_api_signatures():
    lite = importlib.import_module("QTEGUI_Lite")
    assert hasattr(lite.EntropyTab, "save_certificate")
    assert hasattr(lite.EntropyTab, "verify_certificate")

def test_payload_demo_runs_headless():
    lite = importlib.import_module("QTEGUI_Lite")
    t = lite.PayloadTab  # class exists
    # just instantiate without a Tk root (headless allowed by our stub design)
    tab = t.__new__(t)
    lite.PayloadTab.__init__(tab, master=None)
    out = tab.run_demo(n=5, v=3, key=b"K")
    assert isinstance(out, dict)
    assert "capacity" in out
