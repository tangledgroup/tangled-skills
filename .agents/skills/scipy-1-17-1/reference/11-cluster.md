# scipy.cluster - Clustering Algorithms

The `scipy.cluster` module provides clustering algorithms including k-means, vector quantization, and hierarchical clustering. These are essential for data analysis, pattern recognition, and dimensionality reduction.

## Vector Quantization (K-Means Clustering)

### Basic K-Means with vq

```python
from scipy import cluster
import numpy as np

# Generate sample data
np.random.seed(42)
data = np.random.rand(100, 2) * 10

# Initialize centroids (k=3 clusters)
centroids_initial = np.array([[2, 2], [8, 2], [5, 8]])

# K-means clustering
codebook, distortion = cluster.vq.kmeans(data, centroids_initial)

print(f"Centroids:\n{codebook}")
print(f"Distortion (within-cluster sum of squares): {distortion}")

# Assign each point to nearest centroid
labels, distances = cluster.vq.vq(data, codebook)

print(f"Cluster labels: {labels[:10]}...")  # First 10 labels
```

### K-Means++ Initialization (Better Starting Points)

```python
from scipy import cluster
import numpy as np

data = np.random.rand(200, 3) * 10

# Use k-means++ for better initialization
k = 4
centroids_init, _ = cluster.vq.whiten(data, return_parameters=True)
centroids_kmeanspp = cluster.vq.kmeans(data, centroids_init[:k])

# Alternative: Multiple random restarts
best_centroids = None
best_distortion = np.inf

for _ in range(10):  # 10 restarts
    init_centroids = data[np.random.choice(len(data), k, replace=False)]
    centroids, distortion = cluster.vq.kmeans(data, init_centroids)
    
    if distortion < best_distortion:
        best_distortion = distortion
        best_centroids = centroids
```

### Determining Optimal Number of Clusters

```python
from scipy import cluster
import numpy as np
import matplotlib.pyplot as plt

data = np.random.rand(200, 2) * 10

# Elbow method: Plot distortion vs k
k_range = range(2, 11)
distortions = []

for k in k_range:
    init_centroids = data[np.random.choice(len(data), k, replace=False)]
    centroids, distortion = cluster.vq.kmeans(data, init_centroids, iter=20)
    distortions.append(distortion)

# Plot to find elbow point
plt.plot(k_range, distortions, 'bo-')
plt.xlabel('Number of clusters (k)')
plt.ylabel('Distortion')
plt.title('Elbow Method for Optimal k')
```

### Using Transformed Data (Whitening)

```python
from scipy import cluster
import numpy as np

data = np.random.rand(100, 3) * 10

# Whiten data (remove correlations, scale to unit variance)
data_white, parameters = cluster.vq.whiten(data, return_parameters=True)

# Perform k-means on whitened data
k = 3
init_centroids = data_white[np.random.choice(len(data_white), k, replace=False)]
centroids_white, distortion = cluster.vq.kmeans(data_white, init_centroids)

# Transform centroids back to original space
centroids_original = cluster.vq.unwhiten(centroids_white, parameters)
```

## Hierarchical Clustering

### Linkage Methods

```python
from scipy import cluster
import numpy as np

# Sample data (observations in rows)
data = np.random.rand(50, 2) * 10

# Compute linkage matrix
linkage_single = cluster.hierarchy.linkage(data, method='single')
linkage_complete = cluster.hierarchy.linkage(data, method='complete')
linkage_average = cluster.hierarchy.linkage(data, method='average')
linkage_ward = cluster.hierarchy.linkage(data, method='ward')  # Ward's minimum variance

# Linkage matrix columns: [idx1, idx2, distance, sample_count]
print(f"Linkage matrix shape: {linkage_ward.shape}")
print(f"First merge: {linkage_ward[0]}")
```

### Linkage Method Comparison

| Method | Description | Best For |
|--------|-------------|----------|
| `single` | Minimum distance between clusters | Chain-like clusters |
| `complete` | Maximum distance between clusters | Compact, spherical clusters |
| `average` | Average distance between clusters | Balanced approach |
| `ward` | Minimize within-cluster variance | Equal-sized clusters (recommended) |
| `centroid` | Distance between cluster centroids | General purpose |
| `median` | Median-based clustering | Robust to outliers |

### Cutting the Dendrogram

```python
from scipy import cluster
import numpy as np

data = np.random.rand(50, 2) * 10

# Compute linkage
linkage = cluster.hierarchy.linkage(data, method='ward')

# Cut dendrogram at specific number of clusters
k = 4
labels = cluster.hierarchy.fcluster(linkage, t=k, criterion='maxclust')

# Alternative: Cut at distance threshold
labels_distance = cluster.hierarchy.fcluster(linkage, t=5.0, criterion='distance')

# Alternative: Inconsistent cutoff
inconsistency = cluster.hierarchy.inconsistent(linkage)
labels_incon = cluster.hierarchy.fcluster(linkage, t=2.0, criterion='inconsistent', 
                                          incons_matrix=inconsistency)
```

### Dendrogram Visualization

```python
from scipy import cluster
import numpy as np
import matplotlib.pyplot as plt

data = np.random.rand(30, 2) * 10

# Compute linkage
linkage = cluster.hierarchy.linkage(data, method='ward')

# Plot dendrogram
plt.figure(figsize=(12, 6))
dendrogram = cluster.hierarchy.dendrogram(linkage, 
                                          color_threshold=0.7 * max(linkage[:, 2]),
                                          leaf_rotation=90,
                                          leaf_font_size=8)

# Add horizontal line at cutoff
k = 5
cutoff_height = cluster.hierarchy.fcluster(linkage, t=k, criterion='maxclust')
plt.axhline(y=linkage[np.argmin(linkage[:, 2] >= max(linkage[:, 2]) * 0.7), 2], 
            color='r', linestyle='--')

plt.title('Hierarchical Clustering Dendrogram')
plt.xlabel('Sample Index')
plt.ylabel('Distance')
plt.show()
```

### Cluster Statistics and Analysis

```python
from scipy import cluster
import numpy as np

data = np.random.rand(100, 3) * 10

# Compute linkage
linkage = cluster.hierarchy.linkage(data, method='ward')

# Get cluster labels for k clusters
k = 5
labels = cluster.hierarchy.fcluster(linkage, t=k, criterion='maxclust')

# Compute cluster statistics
unique_labels = np.unique(labels)
for label in unique_labels:
    cluster_mask = labels == label
    cluster_points = data[cluster_mask]
    
    print(f"Cluster {label}:")
    print(f"  Size: {len(cluster_points)}")
    print(f"  Centroid: {cluster_points.mean(axis=0)}")
    print(f"  Std dev: {cluster_points.std(axis=0)}")
```

### Cophenetic Correlation (Quality Measure)

```python
from scipy import cluster
import numpy as np

data = np.random.rand(50, 2) * 10

# Compute pairwise distances
from scipy.spatial.distance import pdist
distances = pdist(data)

# Compute linkage
linkage = cluster.hierarchy.linkage(data, method='ward')

# Cophenetic correlation (how well dendrogram preserves original distances)
cophenetic_dist = cluster.hierarchy.cophenetic(linkage)
correlation = np.corrcoef(distances, cophenetic_dist)[0, 1]

print(f"Cophenetic correlation: {correlation:.3f}")
# Values close to 1 indicate good clustering
```

### Comparing Clusterings

```python
from scipy import cluster
import numpy as np
from sklearn.metrics import adjusted_rand_score, silhouette_score

data = np.random.rand(100, 2) * 10

# Get clusters from different methods
linkage = cluster.hierarchy.linkage(data, method='ward')
labels_hierarchical = cluster.hierarchy.fcluster(linkage, t=5, criterion='maxclust')

# K-means
from scipy.cluster.vq import kmeans, vq
centroids, _ = kmeans(data, 5)
labels_kmeans, _ = vq(data, centroids)

# Compare clusterings
ari = adjusted_rand_score(labels_hierarchical, labels_kmeans)
print(f"Adjusted Rand Index: {ari:.3f}")

# Silhouette score (higher is better, max=1)
from sklearn.metrics import silhouette_score
silhouette_hier = silhouette_score(data, labels_hierarchical)
silhouette_km = silhouette_score(data, labels_kmeans)
print(f"Silhouette (hierarchical): {silhouette_hier:.3f}")
print(f"Silhouette (k-means): {silhouette_km:.3f}")
```

## Advanced Hierarchical Clustering

### Using Custom Distance Metrics

```python
from scipy import cluster
from scipy.spatial.distance import pdist, squareform
import numpy as np

data = np.random.rand(50, 3) * 10

# Compute distance matrix with custom metric
dist_matrix = pdist(data, metric='cosine')

# Convert to condensed form (already in this format from pdist)
# Linkage works directly with condensed distance matrix
linkage_cosine = cluster.hierarchy.linkage(dist_matrix, method='ward')

# For square distance matrix, use form='squareform'
dist_square = squareform(dist_matrix)
```

### Partial Clustering (Large Datasets)

```python
from scipy import cluster
import numpy as np

# For very large datasets, use partial clustering
data_large = np.random.rand(10000, 5) * 10

# Compute linkage with optimization
linkage_optimized = cluster.hierarchy.linkage(data_large, method='ward', 
                                              optimize='tour')  # 'tour', 'centroid', or 'inplace'

# Or use subset for initial clustering
subset_indices = np.random.choice(len(data_large), 1000, replace=False)
data_subset = data_large[subset_indices]
linkage_subset = cluster.hierarchy.linkage(data_subset, method='ward')
```

### Inconsistent Coefficients

```python
from scipy import cluster
import numpy as np

data = np.random.rand(50, 2) * 10

# Compute linkage
linkage = cluster.hierarchy.linkage(data, method='average')

# Compute inconsistency coefficients
inconsistency = cluster.hierarchy.inconsistent(linkage, d=3, depth=None)

# Columns: [mean, std, max_depth, sample_count]
print(f"Inconsistency matrix shape: {inconsistency.shape}")

# Use inconsistency to cut dendrogram
labels = cluster.hierarchy.fcluster(linkage, t=1.5, criterion='inconsistent',
                                    incons_matrix=inconsistency)
```

## Troubleshooting

### K-Means Convergence Issues

```python
from scipy import cluster
import numpy as np

data = np.random.rand(100, 2) * 10

# Increase iterations for better convergence
centroids, distortion = cluster.vq.kmeans(data, init_centroids, iter=100)

# Check for empty clusters (distortion doesn't decrease)
# Use multiple restarts
best_result = None
best_distortion = np.inf

for i in range(20):
    init = data[np.random.choice(len(data), k, replace=False)]
    centroids, distortion = cluster.vq.kmeans(data, init, iter=50)
    
    if distortion < best_distortion:
        best_distortion = distortion
        best_result = centroids
```

### Memory Issues with Large Datasets

```python
# For large datasets, use mini-batch k-means from sklearn
from sklearn.cluster import MiniBatchKMeans

mb_kmeans = MiniBatchKMeans(n_clusters=10, batch_size=100)
labels = mb_kmeans.fit_predict(data_large)

# Or process in chunks
chunk_size = 1000
for i in range(0, len(data), chunk_size):
    chunk = data[i:i+chunk_size]
    # Process chunk...
```

### Choosing Between K-Means and Hierarchical

```python
# Use k-means when:
# - You know the number of clusters
# - Dataset is large (>1000 points)
# - Clusters are spherical and similar size

# Use hierarchical when:
# - You want to explore different cluster counts
# - Dataset is moderate size (<5000 points)
# - Cluster hierarchy is meaningful
# - You want dendrogram visualization
```

## See Also

- [`scipy.spatial`](references/10-spatial.md) - Distance computations and spatial trees
- [`sklearn.cluster`](https://scikit-learn.org/stable/modules/clustering.html) - Extended clustering algorithms
- [`scikit-learn`](https://scikit-learn.org/) - Machine learning with better k-means implementations
