# 3D Plotting

## Overview

The `mplot3d` toolkit provides 3D plotting capabilities. Import the 3D projection before creating 3D plots:

```python
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Registers the 3D projection
```

In practice, you typically create 3D axes using `projection='3d'`:

```python
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Or with subplots
fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
```

## 3D Line Plots

```python
import numpy as np

z = np.linspace(0, 15, 1000)
x = np.sin(z)
y = np.cos(z)

fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
ax.plot(x, y, z, label='helix')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.legend()
```

## 3D Scatter Plots

```python
np.random.seed(42)
x = np.random.randn(100)
y = np.random.randn(100)
z = np.random.randn(100)
colors = np.random.rand(100)
sizes = 50 * np.random.rand(100)

fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
sc = ax.scatter(x, y, z, c=colors, s=sizes, cmap='viridis', alpha=0.6)
fig.colorbar(sc, ax=ax, shrink=0.6)
```

## 3D Surface Plots

```python
X = np.linspace(-5, 5, 100)
Y = np.linspace(-5, 5, 100)
X, Y = np.meshgrid(X, Y)
Z = np.sin(np.sqrt(X**2 + Y**2))

fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
surf = ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none', alpha=0.9)
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
```

### Surface Plot Options

- `cmap` — colormap for the surface
- `edgecolor` — color of mesh edges (`'none'` for smooth appearance)
- `rstride`, `cstride` — row/column stride (skip points for performance)
- `antialiased` — smooth shading
- `linewidth` — width of mesh lines

## 3D Wireframe Plots

```python
fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
ax.plot_wireframe(X, Y, Z, color='cyan', linewidth=0.5, rstride=5, cstride=5)
```

## 3D Tri-Surface

For unstructured triangular data:

```python
from mpl_toolkits.mplot3d import Axes3D

# Random triangulated surface
x = np.random.rand(100)
y = np.random.rand(100)
z = np.random.rand(100)

fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
ax.plot_trisurf(x, y, z, cmap='viridis', linewidth=0.2)
```

## 3D Bar Plots

```python
x = [1, 2, 3, 4]
y = [1, 2, 3, 4]
x, y = np.meshgrid(x, y)
x = x.flatten()
y = y.flatten()
z = np.zeros(16)

dx = dy = 0.6
dz = np.random.rand(16) * 5

fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
ax.bar3d(x, y, z, dx, dy, dz, shade=True, color='steelblue')
```

## 3D Contour Plots

```python
fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
contours = ax.contour(X, Y, Z, levels=20, cmap='viridis')
ax.contour(X, Y, Z, zdir='z', offset=-2, cmap='viridis')  # Project onto plane
ax.set_zlim(-2, Z.max())
```

## Voxels (Volumetric Data)

```python
# Create a 3D grid of filled cubes
data = np.zeros((10, 10, 10), dtype=bool)
data[3:7, 3:7, 3:7] = True
data[4:6, 4:6, 4:6] = False  # Hollow center

fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
ax.voxels(data, edgecolor='black')
```

## 3D Quiver (Vector Field)

```python
X, Y, Z = np.meshgrid(np.linspace(-1, 1, 5),
                       np.linspace(-1, 1, 5),
                       np.linspace(-1, 1, 5))
U = V = W = np.ones((5, 5, 5))

fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
ax.quiver(X, Y, Z, U, V, W, length=0.1, normalize=True)
```

## Camera Angles

Control the viewing angle of 3D plots:

```python
ax.view_init(elev=30, azim=45)
# elev — elevation angle in degrees (default ~30)
# azim — azimuth angle in degrees (default ~-60)
```

## 3D Plot Considerations

- 3D plots are rendered as 2D projections — use `view_init()` to find the best angle
- For large datasets, reduce points with `rstride`/`cstride` or subsampling
- Use `alpha < 1.0` for semi-transparent surfaces to see through overlapping geometry
- The z-axis scale may differ from x/y — use `ax.set_box_aspect([1,1,1])` for equal scaling
