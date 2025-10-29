# Unit 07 — Function Atlas (Similarity, PCA & Clustering of Quantum Fingerprints)

Turns saved fingerprints (from Units 02–04 outputs) into a geometric atlas via similarity metrics and embeddings. Produces:
- **Embeddings** (e.g., PCA or other deterministic maps) for visualization/analysis.
- **Cluster labels** grouping related fingerprints by structure.

## Inputs
- A newline-delimited list of artifact paths (amplitude vectors / fingerprints), e.g. `data/fp_list.txt`.
- Optional config flags controlling feature map and metric.

## Outputs
- `--out-embed` → `.npy` array of shape (M, d) with embeddings for M inputs.
- `--out-clusters` → JSON mapping of input index → cluster label.

## CONTRACT (DO NOT CHANGE)
CLI subcommand and flags (must appear literally in `nvqa_cli.py`):
- nve-atlas
- --inputs
- --out-embed
- --out-clusters
- atlas_version="Unit07"

### Determinism notes
Given fixed inputs and params, embeddings and labels must be bit-for-bit stable (fixed random seeds).

### Example call (documentation)
```bash
./nvqa_cli.py nve-atlas \
  --inputs data/fp_list.txt \
  --out-embed out/atlas_embed.npy \
  --out-clusters out/atlas_clusters.json
```

### JSON schema (sketch)
- `embed`: ndarray saved via `.npy` (float64)
- `clusters`: `{ "labels": [int, ...], "method": "kmeans|spectral|agglo", "params": {...} }`

