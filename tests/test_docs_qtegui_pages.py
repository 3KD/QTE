from pathlib import Path

def test_qte_docs_exist():
    d = Path("docs")
    for name in [
        "QTEGUI.md",
        "QTEGUI_ROADMAP.md",
        "QTE_TAB_05_GATES.md",
        "QTEGUI_API_MAP_final.md",
        "QTEGUI_FUNCTION_CHECKLIST_final.md",
    ]:
        assert (d / name).exists()
