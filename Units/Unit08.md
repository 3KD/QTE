# Unit 08 — Atlas Report Generator (Metrics + Publication Figures)

Generates a deterministic analysis report and figures from the Function Atlas (Unit 07).

## CONTRACT (DO NOT CHANGE)
CLI surface that MUST appear literally in nvqa_cli.py:
- nve-atlas-report
- --embed
- --clusters
- --out-report
- --out-fig
- report_version="Unit08"

### Required inputs
- Embedding array (from Unit 07) path via `--embed`
- Cluster labels JSON (from Unit 07) path via `--clusters`

### Required JSON fields (the report MUST contain these keys)
{
  "report_version": "Unit08",
  "atlas_version": "Unit07",
  "nve_version": "Unit01",
  "endianness": "little",
  "qft_kernel_sign": "+",
  "similarity_metric": "cosine",
  "symmetry_tolerance": 1e-12,
  "S": "atlas_similarity_matrix.json",
  "layout": "atlas_layout.json",
  "embedding": {
    "embedding_algo": "FIXED_LINEAR_MAP_V1",
    "coords": [
      { "x": 0.0, "y": 0.0 }
    ]
  },
  "clusters": {
    "algo": "FIXED_KMEANS_V1",
    "labels": [0]
  },
  "items": [
    {
      "psi_fingerprint": "",
      "semantic_hash": "",
      "manifest": {}
    }
  ],
  "metrics": {
    "silhouette_score": 0.0,
    "davies_bouldin": 0.0,
    "calinski_harabasz": 0.0,
    "component_variance": [1.0, 0.0]
  },
  "figures": {
    "figure_paths": ["atlas_scatter.svg"]
  }
}

### Determinism
- For fixed inputs, the report and figures are bit-for-bit stable (fixed seeds, fixed linear map).
