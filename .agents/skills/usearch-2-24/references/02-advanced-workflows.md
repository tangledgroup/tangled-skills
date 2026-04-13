# USearch Advanced Workflows

This reference covers advanced USearch features including custom metrics with JIT compilation, clustering, joins, filtering, multi-index lookups, and application-specific patterns.

## Custom Metrics with JIT Compilation

USearch supports user-defined distance metrics through Just-In-Time (JIT) compilation. This allows you to implement custom similarity functions beyond the built-in metrics.

### Using Numba for Python JIT

[Numba](https://numba.readthedocs.io/) compiles Python functions to native code, enabling custom metrics with near-C performance.

```python
from numba import cfunc, types, carray
from usearch.index import Index, MetricKind, MetricSignature, CompiledMetric
import numpy as np

ndim = 256

# Define custom metric with fixed dimension signature
@cfunc(types.float32(
    types.CPointer(types.float32),
    types.CPointer(types.float32)
))
def custom_inner_product(a, b):
    """Custom inner product distance: 1 - (A·B)"""
    a_array = carray(a, ndim)
    b_array = carray(b, ndim)
    result = 0.0
    for i in range(ndim):
        result += a_array[i] * b_array[i]
    return 1 - result

# Create index with custom metric
metric = CompiledMetric(
    pointer=custom_inner_product.address,
    kind=MetricKind.IP,  # Classify as inner-product-like
    signature=MetricSignature.ArrayArray  # Two array pointers
)

index = Index(ndim=ndim, metric=metric, dtype=np.float32)
```

### Variable-Dimension Metrics

For metrics that need to know the dimension at runtime:

```python
from numba import cfunc, types, carray
from usearch.index import MetricKind, MetricSignature, CompiledMetric, Index

@cfunc(types.float32(
    types.CPointer(types.float32),
    types.CPointer(types.float32),
    types.uint64  # Dimension passed as third argument
))
def variable_dim_distance(a, b, ndim):
    """Euclidean distance with explicit dimension"""
    a_array = carray(a, ndim)
    b_array = carray(b, ndim)
    result = 0.0
    for i in range(ndim):
        diff = a_array[i] - b_array[i]
        result += diff * diff
    return result  # Squared L2 distance

metric = CompiledMetric(
    pointer=variable_dim_distance.address,
    kind=MetricKind.L2sq,
    signature=MetricSignature.ArrayArraySize  # Includes size parameter
)

# Can now use with any dimension
index_100 = Index(ndim=100, metric=metric)
index_1000 = Index(ndim=1000, metric=metric)
```

### Using Cppyy for C++ JIT

[Cppyy](https://cppyy.readthedocs.io/) with Cling allows JIT compilation of C++ code:

```python
import cppyy
import cppyy.ll
from usearch.index import Index, MetricKind, MetricSignature, CompiledMetric

ndim = 256

# Define C++ function as string
cppyy.cppdef(f"""
float custom_metric(float *a, float *b) {{
    float result = 0.0;
#pragma unroll  // Explicit loop unrolling for optimization
    for (size_t i = 0; i != {ndim}; ++i)
        result += a[i] * b[i];
    return 1.0f - result;
}}
""")

# Get function pointer
function = cppyy.gbl.custom_metric
metric = CompiledMetric(
    pointer=cppyy.ll.addressof(function),
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArray
)

index = Index(ndim=ndim, metric=metric)
```

### Using PeachPy for Assembly

[PeachPy](https://github.com/Maratyszcza/PeachPy) allows writing x86-64 assembly directly:

```python
from peachpy import Argument, ptr, float_, const_float_
from peachpy.x86_64 import (
    abi, Function, uarch, isa,
    GeneralPurposeRegister64, YMMRegister,
    LOAD, VMOVUPS, VFMADD231PS, VPERM2F128, VADDPS, VHADDPS, VXORPS, VSUBPS, RETURN
)
from usearch.index import MetricKind, MetricSignature, CompiledMetric, Index

ndim = 8  # Must be multiple of 8 for AVX2

a = Argument(ptr(const_float_), name="a")
b = Argument(ptr(const_float_), name="b")

with Function("inner_product", (a, b), float_, target=uarch.default + isa.avx2) as asm_function:
    # Load addresses into registers
    reg_a, reg_b = GeneralPurposeRegister64(), GeneralPurposeRegister64()
    LOAD.ARGUMENT(reg_a, a)
    LOAD.ARGUMENT(reg_b, b)

    # Load vectors into YMM registers (256-bit = 8 float32)
    ymm_a = YMMRegister()
    ymm_b = YMMRegister()
    VMOVUPS(ymm_a, [reg_a])
    VMOVUPS(ymm_b, [reg_b])

    # Accumulate product: c = a * b
    ymm_c = YMMRegister()
    VXORPS(ymm_c, ymm_c, ymm_c)  # Zero accumulator
    VFMADD231PS(ymm_c, ymm_a, ymm_b)  # Fused multiply-add

    # Horizontal reduction to sum all elements
    ymm_c_permuted = YMMRegister()
    VPERM2F128(ymm_c_permuted, ymm_c, ymm_c, 1)  # Shuffle halves
    VADDPS(ymm_c, ymm_c, ymm_c_permuted)  # Add halves
    VHADDPS(ymm_c, ymm_c, ymm_c)  # Horizontal add (reduces to 2 elements)
    VHADDPS(ymm_c, ymm_c, ymm_c)  # Final reduction (1 element)

    # Convert from similarity to distance: 1 - result
    ymm_one = YMMRegister()
    VXORPS(ymm_one, ymm_one, ymm_one)  # Zero
    # Set to 1.0 (would need proper initialization)
    VSUBPS(ymm_c, ymm_one, ymm_c)  # Negate

    RETURN(ymm_c.as_xmm)  # Return in XMM register

# Compile and load
python_function = asm_function.finalize(abi.detect()).encode().load()
metric = CompiledMetric(
    pointer=python_function.loader.code_address,
    kind=MetricKind.IP,
    signature=MetricSignature.ArrayArray
)

index = Index(ndim=ndim, metric=metric)
```

## Clustering and Sub-clustering

USearch can perform K-Nearest Neighbors clustering using the index structure itself, which is much faster than traditional methods for large datasets.

### Basic Clustering

```python
from usearch.index import Index
import numpy as np

# Create and populate index
index = Index(ndim=256, metric='cos')
vectors = np.random.rand(10000, 256).astype(np.float32)
keys = np.arange(10000)
index.add(keys, vectors)

# Perform clustering
clustering = index.cluster(
    min_count=10,   # Minimum members per cluster
    max_count=100,  # Maximum clusters to create
    threads=4       # Parallel processing
)

# Get cluster information
centroid_keys, cluster_sizes = clustering.centroids_popularity
print(f"Created {len(centroid_keys)} clusters")
print(f"Cluster sizes: {cluster_sizes}")

# Get members of a specific cluster
first_cluster_centroid = centroid_keys[0]
members = clustering.members_of(first_cluster_centroid)
print(f"First cluster has {len(members)} members")
```

### Sub-clustering (Hierarchical Clustering)

```python
# Deepen into a specific cluster
sub_clustering = clustering.subcluster(
    centroid_key=centroid_keys[0],  # Focus on first cluster
    min_count=5,
    max_count=20,
    threads=4
)

# Get sub-cluster centroids
sub_centroids, sub_sizes = sub_clustering.centroids_popularity
print(f"Created {len(sub_centroids)} sub-clusters")
```

### Clustering Visualization

```python
import matplotlib.pyplot as plt

# Plot cluster size distribution
clustering.plot_centroids_popularity()
plt.show()

# Export as NetworkX graph for analysis
import networkx as nx
g = clustering.network

# Analyze graph properties
print(f"Nodes: {g.number_of_nodes()}")
print(f"Edges: {g.number_of_edges()}")
print(f"Connected components: {nx.number_connected_components(g)}")
```

### Performance Comparison

For 1 million points with 50,000 clusters:
- **USearch clustering**: ~seconds to minutes
- **SciPy K-Means**: ~minutes to hours
- **Speedup**: Up to 100x faster than conventional methods

## Joins and Semantic Matching

USearch supports approximate joins for fuzzy matching tasks, enabling semantic joins beyond traditional exact database joins.

### One-to-One Join (Stable Marriage)

```python
from usearch.index import Index
import numpy as np

# Create two indexes to join
index_a = Index(ndim=256, metric='cos')
index_b = Index(ndim=256, metric='cos')

# Populate with vectors
vectors_a = np.random.rand(1000, 256).astype(np.float32)
vectors_b = np.random.rand(1000, 256).astype(np.float32)

index_a.add(np.arange(1000), vectors_a)
index_b.add(np.arange(1000), vectors_b)

# Perform fuzzy join
pairs = index_a.join(index_b, max_proposals=0, exact=False)

# pairs is a dict: {key_from_a: key_from_b}
print(f"Created {len(pairs)} matched pairs")
for key_a, key_b in list(pairs.items())[:5]:
    print(f"  {key_a} ↔ {key_b}")
```

### One-to-Many and Many-to-Many Joins

```python
# Allow multiple matches per key
pairs_multi = index_a.join(index_b, max_proposals=5, exact=False)

# Returns dict with lists: {key_from_a: [key_from_b1, key_from_b2, ...]}
for key_a, matches_b in list(pairs_multi.items())[:3]:
    print(f"  {key_a} → {matches_b}")
```

### Join with Custom Scoring

```python
# Get distances along with matches
def custom_join_with_scores(index_a, index_b, top_k=5):
    """Join with distance scores"""
    results = {}
    
    for key_a in range(len(index_a)):
        vector_a = index_a[key_a]
        matches = index_b.search(vector_a, top_k)
        
        results[key_a] = [
            (match.key, match.distance) 
            for match in matches 
            if match.distance < 0.5  # Threshold filter
        ]
    
    return results

scored_pairs = custom_join_with_scores(index_a, index_b, top_k=10)
```

## Filtering and Predicates

Filter search results using predicate functions during graph traversal, avoiding post-filtering overhead.

### Python Filtering (Post-Processing)

Python bindings don't support inline predicates, but you can filter results:

```python
from usearch.index import Index
import numpy as np

index = Index(ndim=256, metric='cos')
vectors = np.random.rand(10000, 256).astype(np.float32)
index.add(np.arange(10000), vectors)

# Search with expansion to get more candidates
query = np.random.rand(256).astype(np.float32)
matches = index.search(query, 100, expansion=256)  # Get more candidates

# Filter results
def is_valid_key(key):
    return key % 2 == 0  # Only even keys

filtered_matches = [
    match for match in matches 
    if is_valid_key(match.key)
]

print(f"Filtered to {len(filtered_matches)} matches")
```

### C++ Filtering (Inline Predicates)

C++ supports true inline filtering during traversal:

```cpp
#include "usearch/index.hpp"

unum::usearch::index_dense_t<> index;

// Define predicate: only odd keys
auto is_odd = [](uint64_t key) { return key % 2 == 1; };

std::vector<float> query = {0.2f, 0.1f, 0.2f, 0.1f, 0.3f};
auto results = index.search(query, 10, is_odd);

// All returned keys satisfy the predicate
for (auto& match : results) {
    assert(match.key % 2 == 1);  // All keys are odd
}
```

### Rust Filtering

```rust
use usearch::index::*;

let mut index = IndexDense::<f32, uint64_t>::new(
    Config::new(MetricKind::Cos, ndim)
)?;

// Define predicate
let is_odd = |key: uint64_t| key % 2 == 1;

let query = vec![0.2, 0.1, 0.2, 0.1, 0.3];
let results = index.filtered_search(&query, 10, is_odd)?;

// Verify all keys are odd
assert!(results.keys.iter().all(|&key| key % 2 == 1));
```

## Multi-Index Parallel Search

For billion-scale applications, split data across multiple indexes and search in parallel.

### Creating Multi-Index

```python
from usearch.index import Indexes, Index
import numpy as np

# Create multiple smaller indexes
n_shards = 4
ndim = 256
indexes = [Index(ndim=ndim, metric='cos') for _ in range(n_shards)]

# Distribute vectors across shards
all_vectors = np.random.rand(100000, ndim).astype(np.float32)
vectors_per_shard = len(all_vectors) // n_shards

for i, idx in enumerate(indexes):
    start = i * vectors_per_shard
    end = start + vectors_per_shard if i < n_shards - 1 else len(all_vectors)
    shard_vectors = all_vectors[start:end]
    shard_keys = np.arange(start, end)
    idx.add(shard_keys, shard_vectors)

# Combine into multi-index
multi_index = Indexes(indexes=indexes)
```

### Parallel Search Across Shards

```python
# Search across all shards simultaneously
query = np.random.rand(ndim).astype(np.float32)
matches = multi_index.search(query, 10, threads=4)

# Results are merged and sorted by distance
print(f"Top match: key={matches[0].key}, distance={matches[0].distance}")
```

### Multi-Index from Disk

```python
# Create indexes in separate files
for i, idx in enumerate(indexes):
    idx.save(f"shard_{i}.usearch")

# Load multiple indexes from paths
multi_index = Indexes(
    paths=["shard_0.usearch", "shard_1.usearch", "shard_2.usearch", "shard_3.usearch"],
    view=True,  # Memory-map instead of loading into RAM
    threads=4
)

# Search without loading all indexes into memory
matches = multi_index.search(query, 10)
```

### Cost Optimization

Using `view=True` with multi-index can reduce cloud costs by 20x:
- **Without viewing**: Load all shards into RAM → expensive instance types
- **With viewing**: Memory-map from disk → cheaper storage-optimized instances

## Application Examples

### Molecular Similarity Search (RDKit)

```python
from usearch.index import Index, MetricKind
from rdkit import Chem
from rdkit.Chem import AllChem
import numpy as np

# Load molecules from SMILES strings
smiles_list = ['CCOC', 'CCO', 'CCC', 'CC', 'CCCC']
molecules = [Chem.MolFromSmiles(s) for s in smiles_list]

# Generate Morgan fingerprints
fp_generator = AllChem.GetRDKitFPGenerator()
fingerprints = np.vstack([
    np.array(fp_generator.GetFingerprint(mol)) 
    for mol in molecules 
])

# Pack bits for binary storage
fingerprints_packed = np.packbits(fingerprints, axis=1)

# Create index with Tanimoto metric
index = Index(ndim=fingerprints_packed.shape[1], metric=MetricKind.Tanimoto)
keys = np.arange(len(molecules))
index.add(keys, fingerprints_packed)

# Search for similar molecules
query_mol = Chem.MolFromSmiles('CCOC')  # Ethanol
query_fp = np.packbits([np.array(fp_generator.GetFingerprint(query_mol))], axis=0)
matches = index.search(query_fp, 5)

print("Similar molecules:")
for match in matches:
    print(f"  {smiles_list[match.key]}: distance={match.distance:.3f}")
```

### Geospatial Indexing with Custom Distance

```python
from numba import cfunc, types, carray
from usearch.index import Index, MetricKind, MetricSignature, CompiledMetric
import math

ndim = 2  # [latitude, longitude]

# Vincenty distance formula (more accurate than Haversine)
@cfunc(types.float32(
    types.CPointer(types.float32),
    types.CPointer(types.float32)
))
def vincenty_distance(a, b):
    a_arr = carray(a, ndim)
    b_arr = carray(b, ndim)
    
    lat1, lon1 = math.radians(a_arr[0]), math.radians(a_arr[1])
    lat2, lon2 = math.radians(b_arr[0]), math.radians(b_arr[1])
    
    # WGS-84 ellipsoid parameters
    a_ellipsoid = 6378137.0  # meters
    f_flattening = 1 / 298.257223563
    b_ellipsoid = (1 - f_flattening) * a_ellipsoid
    
    L = lon2 - lon1
    U1 = math.atan((1 - f_flattening) * math.tan(lat1))
    U2 = math.atan((1 - f_flattening) * math.tan(lat2))
    
    lambda_val = L
    for _ in range(100):
        sin_lambda, cos_lambda = math.sin(lambda_val), math.cos(lambda_val)
        sin_sigma = math.sqrt(
            (cos_U2 * sin_lambda) ** 2 + 
            (cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lambda) ** 2
        )
        if sin_sigma == 0: return 0.0
        
        cos_sigma = sin_U1 * sin_U2 + cos_U1 * cos_U2 * cos_lambda
        sigma = math.atan2(sin_sigma, cos_sigma)
        
        sin_alpha = cos_U1 * cos_U2 * sin_lambda / sin_sigma
        cos2_alpha = 1 - sin_alpha ** 2
        
        cos2_sigma_m = cos_sigma - 2 * sin_U1 * sin_U2 / cos2_alpha if cos2_alpha != 0 else 0
        C = f_flattening / 16 * cos2_alpha * (4 + f_flattening * (4 - 3 * cos2_alpha))
        
        lambda_prev = lambda_val
        lambda_val = L + (1 - C) * f_flattening * sin_alpha * (
            sigma + C * sin_sigma * (
                cos2_sigma_m + C * cos_sigma * (-1 + 2 * cos2_sigma_m ** 2)
            )
        )
        
        if abs(lambda_val - lambda_prev) <= 1e-12:
            break
    
    u2 = cos2_alpha * (a_ellipsoid ** 2 - b_ellipsoid ** 2) / (b_ellipsoid ** 2)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    
    delta_sigma = B * sin_sigma * (
        cos2_sigma_m + B / 4 * (
            cos_sigma * (-1 + 2 * cos2_sigma_m ** 2) - 
            B / 6 * cos2_sigma_m * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos2_sigma_m ** 2)
        )
    )
    
    s = b_ellipsoid * A * (sigma - delta_sigma)
    return s / 1000.0  # Convert to kilometers

# Create index with custom distance
metric = CompiledMetric(
    pointer=vincenty_distance.address,
    kind=MetricKind.Haversine,
    signature=MetricSignature.ArrayArray
)

index = Index(ndim=2, metric=metric, dtype='f32')

# Add locations: [latitude, longitude]
locations = {
    'New York': [40.7128, -74.0060],
    'London': [51.5074, -0.1278],
    'Tokyo': [35.6762, 139.6503],
    'Sydney': [-33.8688, 151.2093]
}

for i, (city, coords) in enumerate(locations.items()):
    index.add(i, np.array(coords, dtype=np.float32))

# Search for nearest cities to Paris
paris = np.array([48.8566, 2.3522], dtype=np.float32)
matches = index.search(paris, 3)

print("Nearest cities to Paris:")
for match in matches:
    city = list(locations.keys())[match.key]
    print(f"  {city}: {match.distance:.1f} km")
```

### Semantic Search Pipeline

```python
from usearch.index import Index
import numpy as np

class SemanticSearchEngine:
    def __init__(self, embedding_model, ndim=768):
        """
        Initialize semantic search with an embedding model.
        
        Args:
            embedding_model: Function that converts text to embeddings
            ndim: Dimensionality of embeddings
        """
        self.embedding_model = embedding_model
        self.index = Index(ndim=ndim, metric='cos', dtype='bf16')
        self.documents = {}  # Store original text
        
    def add_document(self, key: int, text: str):
        """Add a document to the search index."""
        embedding = self.embedding_model(text)
        self.index.add(key, embedding)
        self.documents[key] = text
        
    def add_batch(self, documents: list):
        """Add multiple documents efficiently."""
        keys = list(range(len(self.documents), len(self.documents) + len(documents)))
        embeddings = np.stack([self.embedding_model(doc) for doc in documents])
        
        self.index.add(keys, embeddings)
        for key, doc in zip(keys, documents):
            self.documents[key] = doc
            
    def search(self, query: str, top_k: int = 10):
        """Search for similar documents."""
        query_embedding = self.embedding_model(query)
        matches = self.index.search(query_embedding, top_k)
        
        results = []
        for match in matches:
            results.append({
                'key': match.key,
                'text': self.documents[match.key],
                'similarity': 1 - match.distance  # Convert distance to similarity
            })
            
        return results
        
    def save(self, path: str):
        """Save index to disk."""
        self.index.save(path)
        
    def load(self, path: str):
        """Load index from disk."""
        self.index.load(path)


# Usage example with a mock embedding function
def mock_embedding(text):
    """Replace with actual embedding model (e.g., sentence-transformers)."""
    # This is just a placeholder - use real embeddings in practice
    hash_val = hash(text) % 10000
    return np.array([((hash_val >> i) & 1) * 2 - 1 for i in range(768)], dtype=np.float32)

# Create search engine
search_engine = SemanticSearchEngine(mock_embedding, ndim=768)

# Add documents
documents = [
    "Machine learning is a subset of artificial intelligence",
    "Deep learning uses neural networks with many layers",
    "Natural language processing enables text understanding",
    "Computer vision allows machines to interpret images"
]
search_engine.add_batch(documents)

# Search
results = search_engine.search("neural networks and AI", top_k=3)
for result in results:
    print(f"Similarity: {result['similarity']:.3f}")
    print(f"  {result['text']}")
```

## Performance Tuning

### Benchmarking Your Index

```python
from usearch.index import Index, self_recall
import numpy as np
import time

index = Index(ndim=256, metric='cos')

# Populate with test data
n_vectors = 100_000
vectors = np.random.rand(n_vectors, 256).astype(np.float32)
keys = np.arange(n_vectors)
index.add(keys, vectors)

# Measure recall
stats = self_recall(index, exact=False)
print(f"Recall@1: {stats.recall_1:.4f}")
print(f"Visited nodes: {stats.visited_members}")
print(f"Computed distances: {stats.computed_distances}")

# Benchmark search speed
query = np.random.rand(256).astype(np.float32)
n_queries = 1000

start = time.time()
for _ in range(n_queries):
    index.search(query, 10)
elapsed = time.time() - start

print(f"Search throughput: {n_queries / elapsed:.0f} queries/second")
```

### Optimization Checklist

1. **Choose appropriate dtype**: Use `bf16` or `f16` for modern hardware
2. **Tune connectivity**: Lower (8) for speed, higher (32) for accuracy
3. **Adjust expansion factors**: Balance indexing time vs search quality
4. **Use multi-index**: For billion-scale, shard across multiple indexes
5. **Enable viewing**: Memory-map large indexes to reduce RAM usage
6. **Parallel processing**: Use `threads` parameter for batch operations
7. **Hardware acceleration**: Verify SIMD support with `hardware_acceleration` property
