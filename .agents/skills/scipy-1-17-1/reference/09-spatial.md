# Spatial Data Structures and Algorithms (scipy.spatial)

## Delaunay Triangulation

Subdivides points into non-overlapping triangles where no point lies inside any triangle's circumcircle:

```python
from scipy.spatial import Delaunay
import numpy as np

points = np.array([[0, 0], [0, 1.1], [1, 0], [1, 1]])
tri = Delaunay(points)

# Triangle vertex indices
print(tri.simplices)

# Neighboring triangles
print(tri.neighbors)

# Find which simplex contains a point
point_region = tri.find_simplex(query_points)
```

Works in higher dimensions (tetrahedra in 3D, etc.) via Qhull.

## Voronoi Diagrams

Dual of Delaunay triangulation — partitions space into regions closest to each input point:

```python
from scipy.spatial import Voronoi
vor = Voronoi(points)
```

## Convex Hull

```python
from scipy.spatial import ConvexHull
hull = ConvexHull(points)
print(hull.volume)
print(hull.area)
print(hull.vertices)  # vertices on the hull
```

## k-D Trees (Nearest Neighbor Search)

Efficient nearest-neighbor queries in multi-dimensional space:

```python
from scipy.spatial import KDTree
import numpy as np

points = np.random.rand(1000, 3)
tree = KDTree(points)

# Find nearest neighbor
dist, idx = tree.query(query_point, k=1)

# Find k nearest neighbors
dists, indices = tree.query(query_points, k=5)

# Find all points within radius
indices = tree.query_ball_point(query_point, r=0.1)
```

## Distance Computations (scipy.spatial.distance)

Comprehensive distance metrics:

```python
from scipy.spatial import distance
import numpy as np

u = np.array([1, 2, 3])
v = np.array([4, 5, 6])

# Euclidean distance
d = distance.euclidean(u, v)

# Manhattan distance
d = distance.cityblock(u, v)

# Cosine distance
d = distance.cosine(u, v)

# Full distance matrix from a collection of vectors
D = distance.pdist(points, metric='euclidean')
D_square = distance.squareform(D)
```

Supported metrics: euclidean, cityblock, cosine, correlation, braycurtis, chebyshev, minkowski, jensenshannon, mahalanobis, and many more.

## Rotations (scipy.spatial.transform.Rotation)

Represent 3D rotations with multiple representations:

```python
from scipy.spatial.transform import Rotation as R
import numpy as np

# From Euler angles
rot = R.from_euler('zyx', [0, 0.5, 0.3], degrees=True)

# From quaternion
rot = R.from_quat([0, 0.707, 0, 0.707])

# From rotation matrix
rot = R.from_matrix([[1, 0, 0], [0, 0, -1], [0, 1, 0]])

# Apply rotation to vectors
vectors = np.array([[1, 0, 0], [0, 1, 0]])
rotated = rot.apply(vectors)

# Convert between representations
print(rot.as_euler('zyx', degrees=True))
print(rot.as_quat())
print(rot.as_matrix())

# Composition
rot_combined = rot1 * rot2

# Interpolation (slerp)
rot_interp = rot.slerp([0, 0.5, 1])
```

### New in 1.17

- `Rotation` and `RigidTransform` extended from 0D/1D to N-D arrays with standard broadcasting
- `shape` property added
- `shape` argument to `identity()` constructors
- `axis` argument to `mean()`
- `from_matrix` gained `assume_valid` for performance
- `as_euler`/`as_davenport` gained `suppress_warnings`
- Array API standard compatible backend

## Rigid Transforms

Combines rotation and translation:

```python
from scipy.spatial.transform import RigidTransform
import numpy as np

rot = R.from_euler('z', 90, degrees=True)
transformation = RigidTransform(rotation=rot, translation=[1, 0, 0])
transformed_points = transformation.apply(points)
```

## Geometric Spherical Linear Interpolation

```python
from scipy.spatial import geometric_slerp

# Interpolate between two points on a sphere
midpoint = geometric_slerp(start_point, end_point, 0.5)

# New in 1.17: extrapolation support (t outside [0, 1])
extrapolated = geometric_slerp(start_point, end_point, -1.0)
```
