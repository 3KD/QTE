def test_qtegui_imports_and_class():
    import importlib
    m = importlib.import_module("QTEGUI")
    assert hasattr(m, "QTEGUI")
    # TOMO_OK should exist (flag)
    assert hasattr(m, "TOMO_OK")

def test_lite_tabs_classes_present():
    import importlib
    lite = importlib.import_module("QTEGUI_Lite")
    for name in ("EntropyTab", "SpectrumTab", "PayloadTab"):
        assert hasattr(lite, name)
