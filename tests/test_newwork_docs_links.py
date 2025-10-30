from pathlib import Path

SLUGS = ['periodic-p-q-pea', 'entanglement-analyzer-schmidt-cuts', 'qrom-digit-encoding']

def test_notes_exist():
    d = Path("docs")
    for s in SLUGS:
        p = d / f"NOTE{'_'}{s}.md"
        assert p.exists(), f"missing note page: {p}"

def test_master_links_notes():
    master = Path("docs/QTEGUI_MASTER.md").read_text(encoding="utf-8")
    for s in SLUGS:
        assert f"NOTE{'_'}{s}.md" in master, f"Master missing link for: {s}"
