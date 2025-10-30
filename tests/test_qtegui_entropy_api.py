def test_entropy_tab_has_save_and_verify():
    import importlib
    lite = importlib.import_module("QTEGUI_Lite")
    T = lite.EntropyTab
    assert hasattr(T, "save_certificate")
    assert hasattr(T, "verify_certificate")
