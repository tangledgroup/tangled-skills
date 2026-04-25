# Transforms & Artists Reference

## Artist Base Classes

### The Artist Hierarchy

All visible elements in matplotlib inherit from `matplotlib.artist.Artist`:

```
Artist (base class)
├── Patch (filled shapes)
│   ├── Rectangle
│   ├── Circle
│   ├── Ellipse
│   ├── Polygon
│   ├── FancyBboxPatch
│   └── Wedge
├── Line2D (lines, curves)
├── Text (text labels)
├── Image (raster images)
├── AxesImage (imshow output)
├── QuadMesh (pcolormesh output)
├── ContourSet (contour/contourf output)
├── Collection (groups of similar artists)
│   ├── PathCollection (scatter plots)
│   ├── LineCollection (many lines)
│   ├── PatchCollection (many patches)
│   └── Poly3DCollection (3D polygons)
├── Axes (plot area)
├── Figure (top-level container)
├── Axis (x-axis or y-axis)
├── Legend
├── Colorbar
└── Table
```

### Adding Custom Artists

```python
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch
from matplotlib.lines import Line2D
import matplotlib.patheffects as path_effects

# Add a patch
rect = Rectangle((0.1, 0.1), 0.3, 0.2, transform=ax.transAxes,
                 fill=True, facecolor='lightblue', alpha=0.5)
ax.add_patch(rect)

# Add text with outline effect
text = ax.text(0.5, 0.5, 'Highlighted Text', ha='center', va='center')
text.set_path_effects([path_effects.Stroke(linewidth=3, foreground='white'),
                       path_effects.Normal()])

# Add a line
line = Line2D([0, 1], [0, 1], transform=ax.transAxes, color='red', linestyle='--')
ax.add_line(line)

# Remove artist
ax.remove(rect)
```

### Property Cycles

```python
# Default property cycle defines colors, linestyles, markers for new artists
from cycler import cycler

ax.set_prop_cycle(cycler('color', ['r', 'g', 'b']) +
                  cycler('linestyle', ['-', '--', '-.']))

# Access current prop cycle
cycle = ax._get_lines.prop_cycler
```

## Transform System

### Coordinate Transforms

Matplotlib uses a transform hierarchy for coordinate systems:

```python
# Data coordinates (default)
ax.transData          # Maps data units to display pixels

# Axes fraction [0,1] x [0,1]
ax.transAxes          # Relative to axes box

# Figure fraction [0,1] x [0,1]
fig.transFigure       # Relative to figure

# Display/pixel coordinates
ax.transScale() + ax.transLimit()  # Full transform chain

# Blended transforms (mix coordinate systems)
blended = matplotlib.transforms.blended_transform_factory(
    ax.transData,   # x in data coords
    ax.transAxes    # y in axes fraction
)
```

### Common Transform Usage

```python
from matplotlib.transforms import blended_transform_factory

# X-axis ticks in data coordinates, Y-axis labels in axes fraction
trans = blended_transform_factory(ax.transData, ax.transAxes)
ax.text(0.5, 1.02, 'Time (s)', transform=trans, ha='center')
```

### Transform Composition

```python
from matplotlib.transforms import Affine2D, CompositeGenericTransform

# Create a custom transform chain
t = Affine2D().scale(2).translate(10, 20) + ax.transData
line.set_transform(t)

# Rotate around center
from matplotlib.transforms import Affine2D
center = (x_center, y_center)
rotate = Affine2D().rotate_deg_around(*center, angle) + ax.transData
```

### Custom Transforms

```python
from matplotlib.transforms import Transform

class MyTransform(Transform):
    input_dims = 2
    output_dims = 2

    def transform(self, xy):
        x, y = xy.T
        return np.vstack([x**2, y]).T

    def transform_inverse(self, xy):
        x, y = xy.T
        return np.vstack([np.sqrt(np.abs(x)), np.sign(y) * np.sqrt(np.abs(y))]).T

    def inverted(self):
        return MyTransformInverse()

ax.transData + MyTransform()   # Chain with existing transforms
```

## Path and PathCollection

### Creating Paths

```python
from matplotlib.path import Path
from matplotlib.patches import PathPatch

# Define path vertices and codes
verts = [
    (0.1, 0.1),    # vertex 0
    (0.9, 0.1),    # vertex 1
    (0.5, 0.9),    # vertex 2
    (0.1, 0.1),    # vertex 3 (close)
]
codes = [
    Path.MOVETO,   # Start at vertex 0
    Path.LINETO,   # Line to vertex 1
    Path.LINETO,   # Line to vertex 2
    Path.CLOSEPOLY,# Close path back to vertex 0
]

path = Path(verts, codes)
patch = PathPatch(path, facecolor='blue', alpha=0.5)
ax.add_patch(patch)
```

### Path Codes Reference

| Code | Value | Description |
|------|-------|-------------|
| `Path.STOP` | 0 | End of path |
| `Path.MOVETO` | 1 | Move to point |
| `Path.LINETO` | 2 | Draw line to point |
| `Path.CURVE3` | 3 | Quadratic Bezier curve |
| `Path.CURVE4` | 4 | Cubic Bezier curve |
| `Path.CLOSEPOLY` | 79 | Close path to MOVETO |

### PathCollection (Scatter Plots)

```python
# Scatter plots are internally PathCollections
scat = ax.scatter(x, y, s=100, c='red')
scat.set_offsets(new_positions)     # Update positions
scat.set_sizes(new_sizes)          # Update sizes
scat.set_facecolors(new_colors)    # Update colors
```

## Blending and Compositing

### Artist Alpha and Z-order

```python
# Transparency
ax.plot(x, y, alpha=0.5)           # 50% transparent
rect.set_alpha(0.3)                # Set patch transparency

# Z-order (draw order — higher = on top)
ax.plot(x1, y1, zorder=1)
ax.plot(x2, y2, zorder=2)          # Draws on top
patch.set_zorder(10)               # Bring to front
```

### Blending Modes

```python
# Set blend mode for an artist
line.set_figure(fig)
line.set_alpha(0.5)                # Normal blending (alpha compositing)
```

## GridSpec and Layout

### GridSpec

```python
from matplotlib.gridspec import GridSpec

fig = plt.figure(figsize=(10, 8))
gs = GridSpec(3, 3, figure=fig)

# Span multiple cells
ax1 = fig.add_subplot(gs[0, :])      # Top row, all columns
ax2 = fig.add_subplot(gs[1, :-1])    # Middle row, first two columns
ax3 = fig.add_subplot(gs[1:, -1])    # Right column, rows 2-3
ax4 = fig.add_subplot(gs[2, 0])      # Bottom-left corner

# Nested GridSpecs
gs_inner = gs[1, :-1].subgridspec(2, 1)
ax5 = fig.add_subplot(gs_inner[0])
ax6 = fig.add_subplot(gs_inner[1])
```

### Constrained Layout (v3.3+)

```python
# Automatic layout adjustment
fig, axes = plt.subplots(2, 2, constrained_layout=True)

# Or after creation
fig.set_layout_engine('constrained')

# Fine-tune with subplot_kw
fig, axes = plt.subplots(2, 2, constrained_layout=True,
                         gridspec_kw={'wspace': 0.3, 'hspace': 0.3})
```

### Subplot Parameters

```python
fig, axes = plt.subplots(nrows=2, ncols=2,
                         figsize=(10, 8),
                         sharex=True,    # Share x-axis
                         sharey=True,    # Share y-axis
                         squeeze=False)  # Always return array of Axes

# Access specific subplot
ax = axes[0, 1]

# Iterate over all subplots
for ax in axes.flat:
    ax.grid(True)
```

### subplot_mosaic (v3.4+)

```python
# Named layout using ASCII art
mosaic = """
AAAAB
CCDDD
EEEEE
"""
fig, axes = plt.subplot_mosaic(mosaic, figsize=(10, 8))

# Access by name
axes['A'].plot([1,2,3])
axes['CCC'].bar(['a','b'], [1,2])

# Custom figure and shared axes
fig, axes = plt.subplot_mosaic(mosaic, sharex='all', figsize=(10, 6))
```

### SubFigures (v3.4+)

```python
fig = plt.figure(figsize=(10, 8))
sfigs = fig.subfigures(2, 1)

# Each subfigure works like a mini Figure
ax1 = sfigs[0].add_subplot()
ax1.plot([1, 2, 3])

ax2 = sfigs[1].add_subplot()
ax2.bar(['A','B'], [3,7])
```
