# Unit 07 — Function Atlas (Similarity, PCA & Clustering of Quantum Fingerprints)

Turns a set of fingerprints into embeddings and clusters.

## CONTRACT (DO NOT CHANGE)
CLI surface (must appear in nvqa_cli.py):
- nve-atlas
- --inputs
- --out-embed
- --out-clusters
- atlas_version="Unit07"

### Required artifacts / fields that docs MUST mention
{
  "atlas_version": "Unit07",
  "nve_version": "Unit01",
  "endianness": "little",
  "qft_kernel_sign": "+",
  "similarity_metric": "cosine",
  "symmetry_tolerance": 1e-12,
  "items": [
    {
      "psi_fingerprint": "",
      "semantic_hash": "",
      "manifest": {}
    }
  ],
  "S": "atlas_similarity_matrix.json",
  "layout": "atlas_layout.json",
  "embedding": {
    "embedding_algo": "FIXED_LINEAR_MAP_V1",
    "coords": [
      {"x": 0.0, "y": 0.0}
    ]
  }
}

### Notes
- Uses nve-similarity and requires similarity symmetry tolerance 1e-12.
