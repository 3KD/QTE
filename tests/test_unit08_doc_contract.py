import pathlib

def test_unit08_doc_contract_strings_present():
    root = pathlib.Path(__file__).resolve().parents[1]
    doc = (root / "Units" / "Unit08.md").read_text()
    req = [
        "## CONTRACT (DO NOT CHANGE)",
        "nve-atlas-report",
        "--embed",
        "--clusters",
        "--out-report",
        "--out-fig",
        'report_version="Unit08"',
        '"report_version": "Unit08"',
        '"atlas_version": "Unit07"',
        '"nve_version": "Unit01"',
        '"endianness": "little"',
        '"qft_kernel_sign": "+"',
        '"similarity_metric": "cosine"',
        '"symmetry_tolerance": 1e-12',
        '"S": "atlas_similarity_matrix.json"',
        '"layout": "atlas_layout.json"',
        '"embedding_algo": "FIXED_LINEAR_MAP_V1"',
        '"coords":',
        '"x":',
        '"y":',
        '"clusters":',
        '"labels":',
        '"items":',
        '"psi_fingerprint":',
        '"semantic_hash":',
        '"manifest":',
        '"metrics":',
        '"silhouette_score":',
        '"davies_bouldin":',
        '"calinski_harabasz":',
        '"component_variance":',
        '"figures":',
        '"figure_paths":',
    ]
    miss = [b for b in req if b not in doc]
    assert not miss, f"Unit08.md missing required tokens: {miss}"
