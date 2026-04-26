# Unsupervised Learning

## Clustering

### K-Means

```python
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=3, random_state=0, n_init="auto").fit(X)
labels = kmeans.labels_
centers = kmeans.cluster_centers_
inertia = kmeans.inertia_  # within-cluster sum of squares
```

Use `KMeans++.x` initialization (default) for better convergence. For large datasets, use `MiniBatchKMeans`.

### Agglomerative Clustering

Hierarchical bottom-up clustering:

```python
from sklearn.cluster import AgglomerativeClustering
model = AgglomerativeClustering(n_clusters=3, linkage="ward").fit(X)
labels = model.labels_
```

Linkage options: `"ward"` (default), `"complete"`, `"average"`, `"single"`.

### DBSCAN

Density-based clustering that finds arbitrarily shaped clusters:

```python
from sklearn.cluster import DBSCAN
model = DBSCAN(eps=0.5, min_samples=5).fit(X)
labels = model.labels_  # -1 indicates noise points
core_sample_indices = model.core_sample_indices_
```

### HDBSCAN

Hierarchical version of DBSCAN that is more robust to parameter choice:

```python
from sklearn.cluster import HDBSCAN
model = HDBSCAN(min_cluster_size=5).fit(X)
labels = model.labels_
probabilities = model.probability_  # stability of each point's cluster assignment
```

### Mean Shift

```python
from sklearn.cluster import MeanShift
model = MeanShift(bandwidth=2.0).fit(X)
labels = model.labels_
centers = model.cluster_centers_
```

### Spectral Clustering

Uses eigenvectors of a similarity matrix:

```python
from sklearn.cluster import SpectralClustering
model = SpectralClustering(n_clusters=3, random_state=0).fit(X)
labels = model.labels_
```

### BIRCH

Balanced Iterative Reducing and Clustering using Hierarchies — efficient for large datasets:

```python
from sklearn.cluster import Birch
model = Birch(n_clusters=3).fit(X)
labels = model.labels_
```

### Affinity Propagation

```python
from sklearn.cluster import AffinityPropagation
model = AffinityPropagation(random_state=0).fit(X)
labels = model.labels_
exemplars = model.cluster_centers_indices_
```

## Gaussian Mixture Models

Model data as a mixture of Gaussian distributions:

```python
from sklearn.mixture import GaussianMixture
gmm = GaussianMixture(n_components=3, random_state=0).fit(X)
labels = gmm.predict(X)
probas = gmm.predict_proba(X)  # soft assignments
aicc = gmm.aic(X)
bic = gmm.bic(X)
```

Covariance types: `"full"`, `"tied"`, `"diag"`, `"spherical"`.

Version 1.8: `GaussianMixture` with `init_params="random"` or `"random_from_data"` and `warm_start=False` now supports Array API inputs.

## Manifold Learning

### t-SNE

Non-linear dimensionality reduction for visualization:

```python
from sklearn.manifold import TSNE
X_embedded = TSNE(n_components=2, random_state=0).fit_transform(X)
```

Version 1.8: `TSNE` now supports PCA initialization with sparse input matrices.

### UMAP

```python
# Requires umap-learn package
from sklearn.manifold import MDS
X_embedded = MDS(n_components=2, random_state=0).fit_transform(X)
```

Version 1.8 major feature: `MDS` now supports arbitrary distance metrics via `metric` and `metric_params` parameters, and initialization via classical MDS via the `init` parameter. The old `dissimilarity` parameter was deprecated.

### Classical MDS

New in version 1.8 — performs classical MDS (eigendecomposition of the double-centered distance matrix):

```python
from sklearn.manifold import ClassicalMDS
X_embedded = ClassicalMDS(n_components=2).fit_transform(distance_matrix)
```

### Isomap

Preserves geodesic distances on a manifold:

```python
from sklearn.manifold import Isomap
X_embedded = Isomap(n_components=2, n_neighbors=5).fit_transform(X)
```

### Locally Linear Embedding (LLE)

```python
from sklearn.manifold import LocallyLinearEmbedding
lle = LocallyLinearEmbedding(n_components=2, n_neighbors=10).fit_transform(X)
```

## Decomposition (Matrix Factorization)

### Principal Component Analysis (PCA)

```python
from sklearn.decomposition import PCA
pca = PCA(n_components=2).fit(X)
X_reduced = pca.transform(X)
X_original = pca.inverse_transform(X_reduced)
print(f"Explained variance: {pca.explained_variance_ratio_}")
```

For large datasets, use `IncrementalPCA` or `RandomizedPCA`.

Version 1.8: Input checks added to `inverse_transform` of `PCA` and `IncrementalPCA`.

### Kernel PCA

Non-linear extension of PCA using kernel trick:

```python
from sklearn.decomposition import KernelPCA
kpca = KernelPCA(n_components=2, kernel="rbf").fit(X)
X_reduced = kpca.transform(X)
```

### Independent Component Analysis (ICA)

```python
from sklearn.decomposition import FastICA
ica = FastICA(n_components=2, random_state=0).fit(X)
X_independent = ica.transform(X)
```

### Non-Negative Matrix Factorization (NMF)

```python
from sklearn.decomposition import NMF
model = NMF(n_components=2, random_state=0).fit(X_non_negative)
W = model.components_
H = model.transform(X_non_negative)
```

### Sparse Coding and Dictionary Learning

```python
from sklearn.decomposition import DictionaryLearning, SparseCoder
dict_model = DictionaryLearning(n_components=10, random_state=0).fit(X)
code = dict_model.transform(X)
# SparseCoder now follows the transformer API (version 1.8)
coder = SparseCoder(dictionary=dict_model.components_, algorithm="lasso_cd")
```

Version 1.8: `SparseCoder` now follows the transformer API with `fit` method that validates input and parameters. Dictionary learning methods with coordinate descent solver benefit from gap safe screening speed improvements.

## Covariance Estimation

### Empirical Covariance

```python
from sklearn.covariance import EmpiricalCovariance
emp_cov = EmpiricalCovariance().fit(X)
cov_matrix = emp_cov.covariance_
mahal_dist = emp_cov.mahalanobis(X_test)
```

### Ledoit-Wolf and OAS (Shrinkage)

```python
from sklearn.covariance import LedoitWolf, OAS
lw = LedoitWolf().fit(X)
oas = OAS().fit(X)
```

### Graphical Lasso (Sparse Inverse Covariance)

```python
from sklearn.covariance import GraphicalLasso, GraphicalLassoCV
model = GraphicalLasso(alpha=0.1).fit(X)
precisions = model.precision_
# With cross-validation
model_cv = GraphicalLassoCV().fit(X)
```

Version 1.8: Fixed uncontrollable randomness — now uses cyclic coordinate descent for `mode="cd"`. Benefits from gap safe screening speed improvements.

### Minimum Covariance Determinant (Robust)

```python
from sklearn.covariance import MinCovDet
mcd = MinCovDet(random_state=0).fit(X)
support_mask = mcd.support_  # boolean mask of inliers
```

Version 1.8: Added correction for consistency at the normal distribution, reducing bias.

## Novelty and Outlier Detection

### One-Class SVM

```python
from sklearn.svm import OneClassSVM
ocsvm = OneClassSVM(kernel="rbf", nu=0.1).fit(X_train)
predictions = ocsvm.predict(X_test)  # 1 for inliers, -1 for outliers
```

### Elliptic Envelope

Assumes Gaussian distribution:

```python
from sklearn.covariance import EllipticEnvelope
ee = EllipticEnvelope(contamination=0.1, random_state=0).fit(X_train)
predictions = ee.predict(X_test)
```

### Local Outlier Factor (LOF)

```python
from sklearn.neighbors import LocalOutlierFactor
lof = LocalOutlierFactor(n_neighbors=20, contamination=0.1)
predictions = lof.fit_predict(X)  # 1 for inliers, -1 for outliers
scores = lof.negative_outlier_factor_
```

## Density Estimation

Kernel Density Estimation:

```python
from sklearn.neighbors import KernelDensity
kde = KernelDensity(kernel="gaussian", bandwidth=0.5).fit(X)
log_densities = kde.score_samples(X_test)
densities = np.exp(log_densities)
```

## Biclustering

Simultaneous clustering of rows and columns:

```python
from sklearn.cluster import SpectralCoclustering
model = SpectralCoclustering(n_clusters=3, random_state=0).fit(data_matrix)
row_labels = model.labels_
column_labels = model.column_labels_
```
