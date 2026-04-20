# Unsupervised Learning & Dimensionality Reduction

## Clustering Algorithms

### K-Means

```python
from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=3, init='k-means++', n_init=10, random_state=42)
labels = kmeans.fit_predict(X)
centers = kmeans.cluster_centers_
```

- `n_clusters`: number of clusters (default 8)
- `init`: 'k-means++' (recommended), 'random'
- `n_init`: number of runs with different centroids (default 10 in 1.8+)
- `algorithm`: 'lloyd' (EM, default), 'elkan' (faster for dense data)
- Fast convergence but sensitive to initialization
- Requires specifying k; use elbow method or silhouette score to choose

**Finding optimal k:**
```python
from sklearn.metrics import silhouette_score

silhouettes = []
for k in range(2, 11):
    km = KMeans(n_clusters=k, random_state=42).fit(X)
    silhouettes.append(silhouette_score(X, km.labels_))
```

### Mini-Batch K-Means

```python
from sklearn.cluster import MiniBatchKMeans

mbk = MiniBatchKMeans(n_clusters=3, batch_size=1024, n_init=10)
labels = mbk.fit_predict(X)
```

- Faster than KMeans for very large datasets
- Uses mini-batches for stochastic gradient descent
- Trade-off: slightly lower quality for much faster training

### Hierarchical Clustering

```python
from sklearn.cluster import AgglomerativeClustering

agg = AgglomerativeClustering(n_clusters=3, linkage='ward')
labels = agg.fit_predict(X)
```

- `linkage`: 'ward' (default), 'complete', 'average', 'single'
- 'ward': minimizes variance within clusters
- 'complete': uses maximum distance between clusters
- 'average': uses average pairwise distances
- 'single': uses minimum distance (chaining effect)
- `n_clusters` or `distance_threshold` (mutually exclusive)
- Produces dendrogram for visual interpretation

### DBSCAN (Density-Based)

```python
from sklearn.cluster import DBSCAN

dbscan = DBSCAN(eps=0.5, min_samples=5)
labels = dbscan.fit_predict(X)
# -1 indicates noise points
```

- `eps`: maximum distance between two samples in the same neighborhood
- `min_samples`: minimum samples to form a dense region
- **No need to specify number of clusters**
- Finds arbitrarily shaped clusters
- Identifies noise/outliers (labelled as -1)
- Sensitive to eps and min_samples

### OPTICS

```python
from sklearn.cluster import OPTICS

optics = OPTICS(min_samples=5, eps=0.5)
labels = optics.fit_predict(X)
```

- Similar to DBSCAN but creates a clustering hierarchy
- Better for datasets with varying densities
- Use `Xi` parameter or `cluster_method='dbscan'` for flat clusters

### Spectral Clustering

```python
from sklearn.cluster import SpectralClustering

spec = SpectralClustering(n_clusters=3, affinity='rbf')
labels = spec.fit_predict(X)
```

- Works well when clusters are not convex
- `affinity`: 'rbf' (default), 'nearest_neighbors', 'precomputed'
- Computationally expensive: O(n³) for eigenvalue decomposition
- Good for image segmentation

### Affinity Propagation

```python
from sklearn.cluster import AffinityPropagation

ap = AffinityPropagation(damping=0.9, random_state=42)
labels = ap.fit_predict(X)
```

- No need to specify number of clusters
- Exchanges messages between points to find exemplars
- `damping`: factor for damping message updates (0.5-1.0)
- Can be slow for large datasets

### MeanShift

```python
from sklearn.cluster import MeanShift

ms = MeanShift()
labels = ms.fit_predict(X)
centers = ms.cluster_centers_
```

- Discovers clusters by finding dense regions
- Automatically determines number of clusters
- `bandwidth`: kernel bandwidth (None = auto-detect)
- Can be slow for large datasets

## Dimensionality Reduction

### Principal Component Analysis (PCA)

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=0.95)  # keep 95% variance
X_reduced = pca.fit_transform(X)
print(f"Original: {X.shape[1]} -> Reduced: {X_reduced.shape[1]}")
```

- `n_components`: int (keep k components), float (fraction of variance), or None (all)
- `explained_variance_`: variance explained by each component
- `explained_variance_ratio_`: percentage of variance
- `singular_values_`: singular values of the input data
- Linear projection; assumes orthogonal axes

**PCA with sparse data:**
```python
from sklearn.decomposition import TruncatedSVD

svd = TruncatedSVD(n_components=50)
X_reduced = svd.fit_transform(X_sparse)
```

### Incremental PCA

```python
from sklearn.decomposition import IncrementalPCA

ipca = IncrementalPCA(n_components=50, batch_size=200)
# Fit in batches for large datasets that don't fit in memory
for batch in get_batches(X):
    ipca.partial_fit(batch)
X_reduced = ipca.transform(X)
```

- `partial_fit()`: incremental learning on mini-batches
- For datasets too large for standard PCA

### Randomized SVD

```python
from sklearn.decomposition import RandomizedPCA  # deprecated
# Use PCA with svd_solver='randomized' instead
pca = PCA(n_components=50, svd_solver='randomized')
X_reduced = pca.fit_transform(X)
```

- Faster than full SVD for large matrices
- Good approximation; useful when exact solution not needed

### Kernel PCA

```python
from sklearn.decomposition import KernelPCA

kpca = KernelPCA(n_components=2, kernel='rbf', gamma=0.1)
X_kernel = kpca.fit_transform(X)
```

- `kernel`: 'linear', 'poly', 'rbf', 'sigmoid', 'cosine', or callable
- Captures non-linear structure via kernel trick
- `gamma`: kernel coefficient for rbf/poly/sigmoid
- `alpha`: regularization parameter

### Sparse PCA

```python
from sklearn.decomposition import SparsePCA, SparseRandomProjection

spca = SparsePCA(n_components=5, alpha=1, random_state=42)
X_sparse_pca = spca.fit_transform(X)
```

- Produces sparse components (fewer non-zero coefficients per component)
- `alpha`: regularization strength for sparsity

### Non-Negative Matrix Factorization

```python
from sklearn.decomposition import NMF

nmf = NMF(n_components=10, init='random', solver='mu', max_iter=500, random_state=42)
W = nmf.fit_transform(X)  # basis matrix (non-negative)
H = nmf.components_       # coefficient matrix (non-negative)
```

- `init`: 'random' or 'nndsvd'
- `solver`: 'cd' (coordinate descent), 'mu' (multiplicative update)
- Components are non-negative; useful for parts-based representation
- Commonly used for text/topic modeling

### Factor Analysis

```python
from sklearn.decomposition import FactorAnalysis

fa = FactorAnalysis(n_components=5)
X_fa = fa.fit_transform(X)
```

- Statistical method assuming latent variables
- Models covariance structure
- `n_components`: number of latent factors
- Good for removing noise from data

### t-SNE (t-Distributed Stochastic Neighbor Embedding)

```python
from sklearn.manifold import TSNE

tsne = TSNE(n_components=2, perplexity=30, n_iter=1000, random_state=42)
X_embedded = tsne.fit_transform(X)
```

- `n_components`: output dimensionality (default 2)
- `perplexity`: balances local/global structure (5-50, typically 30)
- `n_iter`: number of optimization iterations
- Best for visualization; not for feature extraction
- Computationally expensive: O(n²)

### Isomap

```python
from sklearn.manifold import Isomap

isomap = Isomap(n_components=2, n_neighbors=5)
X_embedded = isomap.fit_transform(X)
```

- Preserves geodesic distances (manifold-aware)
- `n_neighbors`: number of neighbors for graph construction

### Locally Linear Embedding (LLE)

```python
from sklearn.manifold import LocallyLinearEmbedding

lle = LocallyLinearEmbedding(n_components=2, n_neighbors=5, method='standard')
X_embedded = lle.fit_transform(X)
```

- Preserves local neighborhood structure
- `method`: 'standard', 'ltsa', 'hessian', 'modified'
- Can fail if neighbors are not well-connected

### Multi-Dimensional Scaling (MDS)

```python
from sklearn.manifold import MDS

mds = MDS(n_components=2, dissimilarity='euclidean', random_state=42)
X_embedded = mds.fit_transform(X)
```

- Preserves pairwise distances in low-dimensional space
- `dissimilarity`: 'euclidean' or 'precomputed' (distance matrix)
- Metric MDS: preserves distances; Non-metric: preserves rank order

## Gaussian Mixture Models

```python
from sklearn.mixture import GaussianMixture

gmm = GaussianMixture(n_components=3, covariance_type='full', random_state=42)
labels = gmm.fit_predict(X)
```

- `n_components`: number of mixture components
- `covariance_type`: 'full', 'tied', 'diag', 'spherical'
- Uses Expectation-Maximization (EM) algorithm
- Soft clustering: each point has probabilities for each cluster
- `weights_`: mixing coefficients, `means_`: component means
- For array API support with random initialization: `init_params='random'`

## Biclustering

```python
from sklearn.cluster import SpectralBiclustering, SpectralCoclustering

sb = SpectralBiclustering(n_clusters=3, random_state=42)
row_labels = sb.fit_predict(X)
col_labels = sb.row_labels_
```

- Simultaneously clusters rows and columns
- Useful for gene expression data
- `SpectralCoclustering`: clusters rows and columns together (co-clusters)
