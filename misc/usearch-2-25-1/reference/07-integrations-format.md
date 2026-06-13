# Integrations and File Format

## Database and Framework Integrations

USearch is integrated into several major databases and frameworks:

**ClickHouse**: Native C++ integration for ANN vector search indexes. Available as a built-in index type in MergeTree family tables.

**DuckDB**: Vector Similarity Search (VSS) extension using USearch as the backend engine.

**ScyllaDB**: Rust-based vector store implementation with presentation materials available.

**TiDB / TiFlash**: C++ integration for vector search indexes in distributed SQL databases.

**YugaByte DB**: C++ wrapper for vector indexing in distributed NewSQL database.

**MemGraph**: Graph database with native vector index support via C++ integration.

**Google UniSim**: Google's internal similarity search library uses USearch as a reference implementation.

**LangChain**: Python and JavaScript integrations for LLM application vector stores.

**Microsoft Semantic Kernel**: Python and C# bindings for AI orchestration framework.

**GPTCache**: Python cache layer for LLM applications using USearch for semantic matching.

**Sentence-Transformers**: Python integration for semantic search with quantized embeddings.

**Pathway**: Rust streaming data platform with USearch-backed vector search.

**Vald**: GoLang distributed vector search system.

**MatrixOne**: GoLang distributed cloud-native database.

## Application Examples

### Molecular Search (Cheminformatics)

Binary fingerprints from RDKit molecules searched with Tanimoto coefficient:

```python
from usearch.index import Index, MetricKind
from rdkit import Chem
from rdkit.Chem import AllChem
import numpy as np

molecules = [Chem.MolFromSmiles('CCOC'), Chem.MolFromSmiles('CCO')]
encoder = AllChem.GetRDKitFPGenerator()
fingerprints = np.vstack([encoder.GetFingerprint(x) for x in molecules])
fingerprints = np.packbits(fingerprints, axis=1)

index = Index(ndim=2048, metric=MetricKind.Tanimoto)
keys = np.arange(len(molecules))
index.add(keys, fingerprints)
matches = index.search(fingerprints, 10)
```

This approach was used to build the "USearch Molecules" dataset: 7 billion small molecules with 28 billion fingerprints.

### Geospatial Indexing

Haversine distance built-in; custom Vincenty formula for Earth's oblateness via CompiledMetric with Numba. See Distance Metrics reference for the full Vincenty implementation.

### Multimodal Semantic Search

Combine image and text encoders (e.g., UForm or CLIP) with USearch for text-to-image search:

```python
from usearch.index import Index
index = Index(ndim=256)  # Shared embedding space

# Add images: encode -> flatten -> index.add(key, vector)
# Search text: encode -> flatten -> index.search(vector, k)
```

## File Format Specification

### Current Version (v2)

Dense index files consist of two parts:

**Matrix BLOB** (optional, prepended):
- 32-bit or 64-bit unsigned integers for row count and column count
- Row count = number of vectors
- Column count = bytes per vector
- Stored as raw binary matrix data

**Index BLOB**:
1. **Metadata** (64 bytes):
   - 7-byte magic: `usearch`
   - 3-byte version: major, minor, patch
   - 1-byte enums: metric, scalar, key, compressed_slot types
   - 8-byte integers: present vectors, deleted vectors, dimensions
   - 1-byte flags: multi-vector support

2. **Levels**: Sequence of 1-byte integers representing each node's HNSW level

3. **Core**:
   - Header: size (uint64), connectivity (uint64), connectivity_base (uint64), max_level (uint64), entry_slot (uint64)
   - Nodes: Contiguous blocks of bytes, one per node, in same order as levels

### Upcoming Version (v3)

Designed for Apache Arrow compatibility with variable-length binary strings:
1. File header with metadata
2. Offset array of N+1 uint64 values (byte offsets for each vector)
3. Data chunks: vector data co-located with proximity graph entries

Benefits: variable-length support, optimized memory mapping, Arrow array casting, better database integration.

## Functionality Matrix by Language

Core operations (add, search, remove, save, load, view) are available in all bindings: C++, Python, C99, Java, JavaScript, Rust, Go, Swift.

Extended features vary by language:
- User-defined metrics: C++, Python, C99, Rust
- Batch operations: Python, Java, JavaScript
- Filter predicates: C++, C99, Rust, Swift
- Joins: C++, Python
- Variable-length vectors: C++ only
- 4B+ capacities (uint40_t/uint64): C++ only

## Citation

```bibtex
@software{Vardanian_USearch,
doi = {10.5281/zenodo.7949416},
author = {Vardanian, Ash},
title = {{USearch by Unum Cloud}},
url = {https://github.com/unum-cloud/USearch},
version = {2.25.1},
year = {2026},
}
```
