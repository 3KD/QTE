def test_qtegui_imports():
    import importlib
    m = importlib.import_module("QTEGUI")
    assert hasattr(m, "QTEGUI")

def test_lite_tabs_present():
    import importlib
    lite = importlib.import_module("QTEGUI_Lite")
    for name in ("EntropyTab","SpectrumTab","PayloadTab"):
        assert hasattr(lite, name)
