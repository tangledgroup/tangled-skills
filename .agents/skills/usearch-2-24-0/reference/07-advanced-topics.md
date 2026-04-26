# Advanced Topics

## Clustering

Once the index is constructed, USearch performs K-Nearest Neighbors clustering much faster than SciPy, UMAP, or tSNE. The index itself can be seen as a clustering with iterative deepening.

### Python Clustering

```python
clustering = index.cluster(
    min_count=10,   # Minimum cluster size
    max_count=15,   # Maximum cluster count
    threads=...,
)

centroid_keys, sizes = clustering.centroids_popularity
clustering.plot_centroids_popularity()  # Matplotlib histogram
g = clustering.network                   # NetworkX graph
first_members = clustering.members_of(centroid_keys[0])

# Iterative deepening
sub_clustering = clustering.subcluster(min_count=..., max_count=...)
```

For 50,000 clusters on 1M points, USearch can be 100x faster than Scikit-Learn.

### C++ Clustering

Single vector clustering at a specific HNSW level:

```cpp
some_scalar_t vector[3] = {0.1, 0.3, 0.2};
cluster_result_t result = index.cluster(&vector, index.max_level() / 2);
match_t cluster = result.cluster;
member_cref_t member = cluster.member;
distance_t distance = cluster.distance;
```

Full index clustering:

```cpp
index_dense_clustering_config_t config;
config.min_clusters = 1000;
config.max_clusters = 2000;
config.mode = index_dense_clustering_config_t::merge_smallest_k;

clustering_result_t result = cluster(
    queries_begin, queries_end, config,
    &cluster_centroids_keys, &distances_to_cluster_centroids,
    thread_pool, progress_bar);
```

## Joins

USearch implements sub-quadratic approximate, fuzzy, and semantic joins — useful for database fuzzy-matching tasks:

```python
men = Index(...)
women = Index(...)
pairs: dict = men.join(women, max_proposals=0, exact=False)
```

## Exact vs Approximate Search

For smaller collections, bypass HNSW indexing with brute-force SIMD-optimized search:

### Python

```python
from usearch.index import search, MetricKind

vectors = np.random.rand(10_000, 1024).astype(np.float32)
vector = np.random.rand(1024).astype(np.float32)

one_in_many = search(vectors, vector, 50, MetricKind.L2sq, exact=True)
many_in_many = search(vectors, vectors, 50, MetricKind.L2sq, exact=True)
```

### C

```c
usearch_distance_t dist = usearch_distance(
    &vec_a[0], &vec_b[0], usearch_scalar_f32_k, dimensions,
    usearch_metric_cos_k, &error);

// Batch exact search
usearch_exact_search(
    dataset, dataset_count, stride,
    queries, queries_count, stride,
    scalar_kind, top_k, threads,
    result_keys, key_stride,
    result_distances, dist_stride,
    &error);
```

## Multi-Index Lookups

For billions or trillions of vectors, build multiple smaller indexes and query them in parallel:

```python
from usearch.index import Indexes

multi_index = Indexes(
    indexes=[idx1, idx2, idx3],
    paths=["/data/index1.usearch", "/data/index2.usearch"],
    view=True,    # Memory-map from disk
    threads=0,    # Auto-detect
)
results = multi_index.search(query, 10)
```

## Serialization and Disk Serving

USearch supports three serialization modes:

### File-Based

```python
index.save("index.usearch")
index.load("index.usearch")   # Full copy into memory
index.view("index.usearch")   # Memory-map, no RAM load
```

### Buffer-Based (C)

```c
size_t bytes = usearch_serialized_length(index, &error);
void* buffer = malloc(bytes);
usearch_save_buffer(index, buffer, bytes, &error);
usearch_load_buffer(index, buffer, bytes, &error);
usearch_view_buffer(index, buffer, bytes, &error);
```

### Stream-Based

Serialize or reconstruct incrementally with callbacks (C++ API).

Viewing from disk can result in up to 20x cost reduction on AWS and other public clouds.

## Retrieving Metadata

```python
# Python
Index.metadata('index.usearch')   # -> IndexMetadata
Index.restore('index.usearch', view=False)  # -> Index
```

```c
// C
usearch_init_options_t opts;
usearch_metadata("index.usearch", &opts, &error);
usearch_metadata_buffer(buffer, bytes, &opts, &error);
```

## Multi-Vector Indexes

Allow multiple vectors per key (useful for chunked documents):

```python
index = Index(ndim=3, multi=True)
index.add(42, vector_a)
index.add(42, vector_b)  # Same key, different vector
```

```c
// C: retrieve up to 10 vectors for key 42
float many_vectors[10][dimensions];
size_t count = usearch_get(index, 42, 10, &many_vectors[0][0], usearch_scalar_f32_k, &error);
```

## Key Types

- **`uint32_t`** — default, up to 4B entries
- **`uint40_t`** — custom 40-bit type, 37.5% more space-efficient than `uint64_t`, scales to 1 Trillion entries
- **`uint64_t`** — full 64-bit keys

## Application Examples

### Molecular Search with RDKit

```python
from usearch.index import Index, MetricKind
from rdkit import Chem
from rdkit.Chem import AllChem
import numpy as np

molecules = [Chem.MolFromSmiles('CCOC'), Chem.MolFromSmiles('CCO')]
encoder = AllChem.GetRDKitFPGenerator()

fingerprints = np.vstack([encoder.GetFingerprint(m) for m in molecules])
fingerprints = np.packbits(fingerprints, axis=1)

index = Index(ndim=2048, metric=MetricKind.Tanimoto)
index.add(np.arange(len(molecules)), fingerprints)
matches = index.search(fingerprints, 10)
```

### Geospatial Search with Vincenty Distance

```python
from numba import cfunc, types, carray
import math

ndim = 2
semi_major, flattening = 6378137.0, 1 / 298.257223563
semi_minor = (1 - flattening) * semi_major

def vincenty_distance(first_ptr, second_ptr):
    first, second = carray(first_ptr, ndim), carray(second_ptr, ndim)
    lat1, lon1, lat2, lon2 = first[0], first[1], second[0], second[1]
    diff_lon = lon2 - lon1
    rlat1 = math.atan((1 - flattening) * math.tan(lat1))
    rlat2 = math.atan((1 - flattening) * math.tan(lat2))
    sin_rlat1, cos_rlat1 = math.sin(rlat1), math.cos(rlat1)
    sin_rlat2, cos_rlat2 = math.sin(rlat2), math.cos(rlat2)
    lon_on_sphere = diff_lon
    for _ in range(100):
        sin_lon, cos_lon = math.sin(lon_on_sphere), math.cos(lon_on_sphere)
        sin_ang = math.sqrt((cos_rlat2 * sin_lon)**2 +
            (cos_rlat1 * sin_rlat2 - sin_rlat1 * cos_rlat2 * cos_lon)**2)
        if sin_ang == 0: return 0.0
        cos_ang = sin_rlat1 * sin_rlat2 + cos_rlat1 * cos_rlat2 * cos_lon
        ang = math.atan2(sin_ang, cos_ang)
        sin_az = cos_rlat1 * cos_rlat2 * sin_lon / sin_ang
        cos2_az = 1 - sin_az ** 2
        cos2_mid = cos_ang - 2 * sin_rlat1 * sin_rlat2 / cos2_az if cos2_az != 0 else 0.0
        corr = flattening / 16 * cos2_az * (4 + flattening * (4 - 3 * cos2_az))
        prev = lon_on_sphere
        lon_on_sphere = diff_lon + (1 - corr) * flattening * (
            sin_az * (ang + corr * sin_ang * (cos2_mid +
            corr * cos_ang * (-1 + 2 * cos2_mid ** 2))))
        if abs(lon_on_sphere - prev) <= 1e-12: break
    u_sq = cos2_az * (semi_major**2 - semi_minor**2) / (semi_minor**2)
    ca = 1 + u_sq/16384 * (4096 + u_sq*(-768 + u_sq*(320 - 175*u_sq)))
    cb = u_sq/1024 * (256 + u_sq*(-128 + u_sq*(74 - 47*u_sq)))
    delta = cb * sin_ang * (cos2_mid + cb/4 * (cos_ang*(-1 + 2*cos2_mid**2)
        - cb/6 * cos2_mid * (-3 + 4*sin_ang**2) * (-3 + 4*cos2_mid**2)))
    return semi_minor * ca * (ang - delta) / 1000.0

from usearch.index import CompiledMetric, MetricKind, MetricSignature

@cfunc(types.float32(types.CPointer(types.float32), types.CPointer(types.float32)))
def wrapped_vincenty(a, b):
    return vincenty_distance(a, b)

index = Index(ndim=ndim, metric=CompiledMetric(
    pointer=wrapped_vincenty.address,
    kind=MetricKind.Haversine,
    signature=MetricSignature.ArrayArray,
))
```

### Multimodal Semantic Search

Combine USearch with embedding models for text-to-image search:

```python
from ucall import Server
from uform import get_model, Modality
from usearch.index import Index
import numpy as np

processors, models = get_model('unum-cloud/uform3-image-text-english-small')
model_text = models[Modality.TEXT_ENCODER]
model_image = models[Modality.IMAGE_ENCODER]
processor_text = processors[Modality.TEXT_ENCODER]
processor_image = processors[Modality.IMAGE_ENCODER]

server = Server()
index = Index(ndim=256)

@server
def add(key: int, photo: pil.Image.Image):
    image = processor_image(photo)
    vector = model_image(image)
    index.add(key, vector.flatten(), copy=True)

@server
def search(query: str) -> np.ndarray:
    tokens = processor_text(query)
    vector = model_text(tokens)
    matches = index.search(vector.flatten(), 3)
    return matches.keys

server.run()
```

## Integrations

USearch is integrated into:
- **ClickHouse** — C++ vector index for MergeTree tables
- **DuckDB** — Vector Similarity Search extension
- **ScyllaDB** — Rust vector store
- **TiDB/TiFlash** — C++ vector index
- **YugaByte** — C++ vector index
- **MemGraph** — Graph database vector search
- **Google UniSim/RetSim** — Research at scale
- **LangChain** — Python and JavaScript vector stores
- **Microsoft Semantic Kernel** — Python and C#
- **GPTCache** — Python caching
- **Sentence-Transformers** — Quantization support
- **Pathway** — Rust streaming
- **Vald** — GoLang gRPC vector DB
- **MatrixOne** — GoLang distributed DB
