# scipy.spatial - Spatial Data Structures and Algorithms

The `scipy.spatial` module provides spatial algorithms and data structures for tasks like nearest neighbor search, convex hulls, Delaunay triangulation, and distance computations.

## K-D Trees for Nearest Neighbor Search

### Building K-D Trees

```python
from scipy import spatial
import numpy as np

# Sample points in 2D
points = np.random.rand(1000, 2)

# Build k-d tree (efficient for nearest neighbor queries)
tree = spatial.KDTree(points)

# Query for nearest neighbor of a point
query_point = np.array([0.5, 0.5])
distance, index = tree.query(query_point)
print(f"Nearest neighbor: {points[index]}, distance: {distance}")

# Query for k nearest neighbors
distances, indices = tree.query(query_point, k=5)
nearest_points = points[indices]
```

### Batch Queries

```python
from scipy import spatial

# Multiple query points
query_points = np.random.rand(100, 2)

# Find nearest neighbor for each query point
distances, indices = tree.query(query_points, k=1)

# Find k nearest neighbors for each
k = 10
distances_k, indices_k = tree.query(query_points, k=k)

# distances_k shape: (100, 10)
# indices_k shape: (100, 10)
```

### Ball Tree (Alternative to K-D Tree)

```python
from scipy import spatial

# Ball tree works better for high-dimensional data or custom metrics
tree_ball = spatial.cKDTree(points)  # Optimized C implementation

# For non-Euclidean metrics, use BallTree
from sklearn.neighbors import BallTree  # SciPy doesn't have BallTree yet

# Query with different distance metric
distances, indices = tree_ball.query(query_points, k=5, 
                                     distance_upper_bound=0.5)  # Max distance filter
```

### Range Searches

```python
from scipy import spatial

# Find all points within radius r of query point
query_point = np.array([0.5, 0.5])
radius = 0.1

# Query ball (returns indices of points within radius)
indices_in_ball = tree.query_ball_point(query_point, r=radius)
points_in_ball = points[indices_in_ball]

# Query ball for multiple points
query_points = np.random.rand(10, 2)
all_indices = tree.query_ball_point(query_points, r=radius)

# Each element in all_indices is a list of indices for that query point
```

## Distance Computations

### Pairwise Distance Matrix

```python
from scipy.spatial import distance
import numpy as np

# Two sets of points
X = np.random.rand(5, 3)  # 5 points in 3D
Y = np.random.rand(7, 3)  # 7 points in 3D

# Euclidean distance matrix (5 x 7)
dist_euclidean = distance.cdist(X, Y, metric='euclidean')

# Other metrics: 'cityblock' (Manhattan), 'cosine', 'correlation', etc.
dist_manhattan = distance.cdist(X, Y, metric='cityblock')
dist_cosine = distance.cdist(X, Y, metric='cosine')
```

### Common Distance Metrics

```python
from scipy.spatial import distance
import numpy as np

a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# Euclidean distance
dist_eucl = distance.euclidean(a, b)

# Manhattan (city block) distance
dist_manhattan = distance.cityblock(a, b)

# Chebyshev distance (max coordinate difference)
dist_cheby = distance.chebyshev(a, b)

# Minkowski distance (generalization of Euclidean and Manhattan)
dist_minkowski = distance.minkowski(a, b, p=3)  # p=2 is Euclidean

# Cosine distance (1 - cosine similarity)
dist_cosine = distance.cosine(a, b)

# Hamming distance (fraction of differing components)
dist_hamming = distance.hamming(a, b)

# Jaccard distance (for binary vectors)
a_binary = np.array([1, 0, 1, 1])
b_binary = np.array([1, 1, 0, 1])
dist_jaccard = distance.jaccard(a_binary, b_binary)
```

### Pdist (Pairwise Distances within Single Set)

```python
from scipy.spatial import distance
import numpy as np

# Single set of points
points = np.random.rand(10, 3)  # 10 points in 3D

# Compute all pairwise distances (returns condensed form)
dist_condensed = distance.pdist(points, metric='euclidean')

# Convert to squareform (10 x 10 matrix)
dist_square = distance.squareform(dist_condensed)

# Different metrics
dist_correlation = distance.pdist(points, metric='correlation')
dist_pearson = distance.pdist(points, metric='pearsonr')
```

## Convex Hulls

### Computing Convex Hull

```python
from scipy.spatial import ConvexHull
import numpy as np

# Random points in 2D
points_2d = np.random.rand(20, 2)

# Compute convex hull
hull = ConvexHull(points_2d)

# Hull vertices (indices into points array)
hull_vertices = hull.vertices
hull_points = points_2d[hull_vertices]

# Hull simplices (triangles in 2D, tetrahedra in 3D)
hull_simplices = hull.simplices

# Volume and surface area
print(f"Volume: {hull.volume}")
print(f"Surface area: {hull.area}")
```

### 3D Convex Hull

```python
from scipy.spatial import ConvexHull
import numpy as np

# Random points in 3D
points_3d = np.random.rand(50, 3)

# Compute convex hull
hull_3d = ConvexHull(points_3d)

# Hull facets (triangles on surface)
facets = hull_3d.simplices  # Each row is a triangle (3 vertex indices)

# Volume and surface area
print(f"3D Volume: {hull_3d.volume}")
print(f"Surface Area: {hull_3d.area}")

# Equation of each facet plane
equations = hull_3d.equations  # [normal_x, normal_y, normal_z, offset]
```

### Point in Convex Hull Test

```python
from scipy.spatial import ConvexHull
import numpy as np

points = np.random.rand(20, 2)
hull = ConvexHull(points)

# Test if point is inside hull
test_point = np.array([0.5, 0.5])

# Method 1: Check if point is on correct side of all facets
def point_in_hull(point, hull):
    return np.all(np.dot(hull.equations[:, :-1], point) + 
                  hull.equations[:, -1] <= 0)

is_inside = point_in_hull(test_point, hull)
```

## Delaunay Triangulation

### 2D Delaunay Triangulation

```python
from scipy.spatial import Delaunay
import numpy as np

# Random points in 2D
points_2d = np.random.rand(20, 2)

# Compute Delaunay triangulation
tri = Delaunay(points_2d)

# Triangles (each row is 3 vertex indices)
triangles = tri.simplices

# Find which triangle contains a point
test_point = np.array([0.5, 0.5])
triangle_index = tri.find_simplex(test_point)  # -1 if outside hull

# Voronoi diagram (dual of Delaunay)
voronoi = tri.voronoi_regions  # Available in newer SciPy versions
```

### 3D Delaunay Triangulation

```python
from scipy.spatial import Delaunay
import numpy as np

# Random points in 3D
points_3d = np.random.rand(30, 3)

# Compute Delaunay triangulation
tri_3d = Delaunay(points_3d)

# Tetrahedra (each row is 4 vertex indices)
tetrahedra = tri_3d.simplices

# Find which tetrahedron contains a point
test_point = np.array([0.5, 0.5, 0.5])
tet_index = tri_3d.find_simplex(test_point)
```

### Point Location and Interpolation

```python
from scipy.spatial import Delaunay
import numpy as np

# Points with values (for interpolation)
points = np.random.rand(20, 2)
values = np.sin(points[:, 0] * 10) * np.cos(points[:, 1] * 10)

# Create Delaunay triangulation
tri = Delaunay(points)

# Interpolate at new points (linear interpolation within triangles)
from scipy.interpolate import LinearNDInterpolator

interpolator = LinearNDInterpolator(points, values)
new_points = np.random.rand(100, 2)
interpolated_values = interpolator(new_points)
```

## Spatial Transformations

### Rotation Transforms

```python
from scipy.spatial.transform import Rotation as R
import numpy as np

# Create rotation from Euler angles (intrinsic rotations)
rot_euler = R.from_euler('zyx', [90, 45, 0], degrees=True)

# Create rotation from quaternion
rot_quat = R.from_quat([0, 0, 0, 1])  # Identity quaternion

# Create rotation from axis-angle
rot_axis_angle = R.from_rotvec([np.pi/2, 0, 0])  # 90° around x-axis

# Apply rotation to vector
vector = np.array([1, 0, 0])
rotated_vector = rot_euler.apply(vector)

# Get rotation matrix
rotation_matrix = rot_euler.as_dcm()  # Direction cosine matrix

# Compose rotations
rot1 = R.from_euler('z', 90, degrees=True)
rot2 = R.from_euler('y', 45, degrees=True)
rot_composed = rot1 * rot2  # rot2 applied first, then rot1
```

### Common Rotation Representations

```python
from scipy.spatial.transform import Rotation as R
import numpy as np

# Create rotation
rot = R.from_euler('zyx', [90, 45, 30], degrees=True)

# Convert to different representations
quat = rot.as_quat()  # Quaternion [x, y, z, w]
euler = rot.as_euler('zyx', degrees=True)  # Euler angles
matrix = rot.as_dcm()  # Rotation matrix (direction cosine matrix)
rotvec = rot.as_rotvec()  # Rotation vector (axis-angle)

# Create from different representations
rot_from_quat = R.from_quat(quat)
rot_from_matrix = R.from_dcm(matrix)
rot_from_rotvec = R.from_rotvec(rotvec)
```

### Spherical Coordinates

```python
from scipy.spatial.transform import SphericalRepresentation
import numpy as np

# Create spherical coordinates (lon, lat, distance)
spher = SphericalRepresentation(lon=[0, 90, 180], 
                                lat=[0, 45, 90], 
                                distance=[1, 1, 1], 
                                unit='deg')

# Convert to Cartesian
cartesian = spher.cartesian

# Create from Cartesian coordinates
from scipy.spatial.transform import CartesianRepresentation
cart = CartesianRepresentation(x=[1, 0, -1], y=[0, 1, 0], z=[0, 0, 1])
spher_from_cart = cart.spherical
```

## Voronoi Diagrams

### Computing Voronoi Diagram

```python
from scipy.spatial import Voronoi
import numpy as np

# Random points in 2D
points = np.random.rand(20, 2)

# Compute Voronoi diagram
vor = Voronoi(points)

# Voronoi vertices (corner points of cells)
vor_vertices = vor.vertices

# Regions (list of vertex indices for each cell)
vor_regions = vor.regions

# Some regions may be infinite (contain -1)
for i, region in enumerate(vor_regions):
    if -1 not in region and len(region) > 0:
        print(f"Point {i} has finite Voronoi cell with vertices: {region}")
```

### Extracting Voronoi Cells

```python
from scipy.spatial import Voronoi
import numpy as np

points = np.random.rand(20, 2)
vor = Voronoi(points)

def get_voronoi_cell(vor, point_index):
    """Get vertices of Voronoi cell for a specific point"""
    region_index = vor.point_region[point_index]
    vertex_indices = vor.regions[region_index]
    
    # Filter out infinite regions
    if -1 in vertex_indices:
        return None
    
    return vor.vertices[vertex_indices]

# Get cell for first point
cell_0 = get_voronoi_cell(vor, 0)
```

## Troubleshooting

### High-Dimensional Data Issues

```python
# K-D trees become inefficient in high dimensions (>20)
# Use alternative methods:

from sklearn.neighbors import NearestNeighbors  # Better for high-D

# Or use approximate nearest neighbor libraries
# - Annoy (Spotify)
# - FAISS (Facebook)
# - HNSW libraries
```

### Degenerate Cases in Convex Hull

```python
# Handle collinear points in 2D
points_collinear = np.array([[0, 0], [1, 1], [2, 2], [3, 3]])

try:
    hull = ConvexHull(points_collinear)
except Exception as e:
    print(f"Degenerate case: {e}")

# Solution: Add small perturbation
points_perturbed = points_collinear + np.random.randn(*points_collinear.shape) * 1e-10
hull = ConvexHull(points_perturbed)
```

### Infinite Voronoi Regions

```python
# Handle infinite Voronoi cells by clipping to bounding box
def clip_voronoi(vor, points, bbox=None):
    """Clip infinite Voronoi regions to bounding box"""
    if bbox is None:
        bbox = [points.min(axis=0), points.max(axis=0)]
    
    clipped_cells = []
    for i, region_idx in enumerate(vor.point_region):
        vertices_idx = vor.regions[region_idx]
        
        if -1 in vertices_idx:
            # Infinite region - clip to bbox
            # Complex logic needed here
            clipped_cells.append(None)  # Simplified
        else:
            clipped_cells.append(vor.vertices[vertices_idx])
    
    return clipped_cells
```

## See Also

- [`scipy.cluster`](references/11-cluster.md) - Clustering algorithms
- [`scikit-learn.neighbors`](https://scikit-learn.org/stable/modules/neighbors.html) - Nearest neighbor methods
- [`networkx`](https://networkx.org/) - Graph-based spatial analysis
