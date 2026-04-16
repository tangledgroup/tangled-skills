# 3D Toolkit Reference (mplot3d)

## Overview

The `mplot3d` toolkit provides 3D plotting capabilities for matplotlib. It is included in the standard distribution — no separate installation required.

### Import

```python
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
```

In recent versions, you can also specify 3D projection directly:

```python
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
```

## 3D Plot Types

### Surface Plots

```python
# Create meshgrid
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

# Surface plot
ax.plot_surface(X, Y, Z, cmap='viridis', edgecolor='none')

# With wireframe overlay
ax.plot_surface(X, Y, Z, cmap='plasma', alpha=0.8)
ax.plot_wireframe(X, Y, Z, rstride=5, cstride=5, color='white', alpha=0.3)

# Customizing surface appearance
ax.plot_surface(X, Y, Z, cmap='coolwarm', norm=plt.Normalize(vmin=-1, vmax=1),
                antialiased=True, shade=True)
```

### 3D Line and Scatter Plots

```python
# 3D line plot
theta = np.linspace(0, 4*np.pi, 200)
z = np.linspace(-2, 2, 200)
r = z**2 + 1
x = r * np.sin(theta)
y = r * np.cos(theta)
ax.plot(x, y, z, linewidth=2)

# 3D scatter plot
np.random.seed(42)
n = 100
xs = np.random.rand(n)
ys = np.random.rand(n)
zs = np.random.rand(n)
ax.scatter(xs, ys, zs, c=zs, cmap='viridis', s=50)

# Colored 3D scatter with varying sizes
sizes = np.random.rand(n) * 100
ax.scatter(xs, ys, zs, c=zs, s=sizes, alpha=0.7)
```

### 3D Contour Plots

```python
# 3D contour from surface data
ax.contour(X, Y, Z, cmap='viridis', zdir='z', offset=-2)
ax.contourf(X, Y, Z, cmap='plasma', zdir='z', offset=-2)

# Contour on x-z plane
ax.contour(X, Y, Z, zdir='x', offset=0, cmap='hot')

# 3D line contours
CS = ax.contour(X, Y, Z, zdir='z', offset=-2)
ax.clabel(CS, inline=True, fontsize=8)
```

### 3D Bar Charts

```python
# 3D bar chart
np.random.seed(42)
n_bins = 10
xs = np.arange(n_bins)
ys = np.random.rand(len(xs)) * 10
zs = np.random.rand(len(xs))
dx = dy = 0.5
dz = np.random.rand(len(xs)) * 10

ax.bar3d(xs, ys, zs, dx, dy, dz, color='b', alpha=0.7)

# Colored bars
colors = plt.cm.viridis(np.linspace(0, 1, len(xs)))
ax.bar3d(xs, ys, np.zeros_like(xs), dx, dy, dz, color=colors, alpha=0.7)
```

### 3D PolyCollection (Filled Polygons)

```python
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
import numpy as np

# Create vertices for a 3D shape
verts = [
    [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],   # bottom face
    [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],   # top face
    [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)],   # side faces...
]

poly = Poly3DCollection(verts, alpha=0.5)
poly.set_facecolor('cyan')
ax.add_collection3d(poly)
```

### Quiver (Arrow) Plots in 3D

```python
# 3D quiver plot
u = np.ones_like(X)
v = np.ones_like(Y)
w = np.ones_like(Z)
ax.quiver(X, Y, Z, u, v, w, length=0.1, normalize=True)
```

## 3D View Configuration

### Camera Angles

```python
# Set elevation and azimuth angles
ax.view_init(elev=30, azim=45)

# Rotate view interactively in GUI backends
# Use mouse to drag and rotate

# Programmatic rotation animation
for angle in range(0, 360, 10):
    ax.view_init(elev=30, azim=angle)
    fig.canvas.draw()
```

### View Angles Reference

| Angle | Range | Description |
|-------|-------|-------------|
| `elev` | -90 to 90 | Elevation angle (z-axis) |
| `azim` | -360 to 360 | Azimuth angle (rotation around z) |

Common presets:
```python
ax.view_init(elev=90, azim=0)     # Top-down view
ax.view_init(elev=0, azim=0)      # Side view from x-axis
ax.view_init(elev=0, azim=90)     # Side view from y-axis
ax.view_init(elev=30, azim=45)    # Default isometric-ish view
```

### 3D Axis Configuration

```python
# Set axis limits
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
ax.set_zlim(-1, 1)

# Set labels
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')

# Grid
ax.grid(True)

# Background color
ax.set_facecolor('white')
```

### 3D Tick Configuration

```python
from matplotlib.ticker import AutoLocator, FormatStrFormatter

ax.zaxis.set_major_locator(AutoLocator())
ax.zaxis.set_major_formatter(FormatStrFormatter('%.2f'))
```

## Example: Complete 3D Visualization

```python
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Create data
u = np.linspace(0, 2 * np.pi, 50)
v = np.linspace(0, np.pi, 50)
x = np.outer(np.sin(v), np.cos(u))
y = np.outer(np.sin(v), np.sin(u))
z = np.outer(np.cos(v), np.ones_like(u))

# Plot sphere
surf = ax.plot_surface(x, y, z, cmap='viridis', edgecolor='none', alpha=0.8)
fig.colorbar(surf, ax=ax, shrink=0.5)

# Add wireframe
ax.plot_wireframe(x, y, z, color='k', alpha=0.1, rstride=5, cstride=5)

# Set view
ax.view_init(elev=20, azim=45)
ax.set_title('3D Sphere')
plt.show()
```

## Polar 3D Plot (from mplot3d FAQ)

```python
# Create polar plot with radius as z
theta = np.linspace(0, 2*np.pi, 100)
r = np.linspace(0, 5, 50)
Theta, R = np.meshgrid(theta, r)
X = R * np.cos(Theta)
Y = R * np.sin(Theta)
Z = np.sin(R)

ax.plot_surface(X, Y, Z, cmap='viridis')
```
