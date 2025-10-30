def test_payload_demo_returns_capacity_even_without_deps():
    import importlib
    lite = importlib.import_module("QTEGUI_Lite")
    T = lite.PayloadTab
    tab = T.__new__(T)
    T.__init__(tab, master=None)  # headless-friendly __init__
    out = tab.run_demo(n=5, v=3, key=b"K")
    assert isinstance(out, dict)
    assert "capacity" in out or "capacity_bits" in out
