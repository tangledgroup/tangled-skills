# Transformations

## Coordinate Systems

Matplotlib uses a transformation pipeline to convert between different coordinate systems. Understanding these is essential for precise placement of artists and annotations.

### Available Coordinate Systems

- **Display coordinates** — pixels on the screen (origin at bottom-left of figure)
- **Figure coordinates** — fraction of figure size (0,0 = bottom-left, 1,1 = top-right)
- **Axes coordinates** — fraction of axes area (0,0 = bottom-left, 1,1 = top-right)
- **Data coordinates** — the actual data values on the axes

### Transform Objects

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()

# Key transform objects
ax.transData         # Data → Display
ax.transAxes         # Axes fraction → Display
fig.transFigure      # Figure fraction → Display
ax.get_xaxis_transform()   # x in data coords, y in axes coords
ax.get_yaxis_transform()   # x in axes coords, y in data coords
```

## Using Transforms

### Placing Text in Mixed Coordinates

```python
# x in data coordinates, y in axes coordinates (top of plot)
ax.text(x_value, 0.95, 'Label',
        transform=ax.get_yaxis_transform(),
        ha='center', va='top')

# x in axes coordinates, y in data coordinates
ax.text(0.05, y_value, 'Label',
        transform=ax.get_xaxis_transform(),
        ha='left', va='center')
```

### Anchoring Annotations

Keep annotation text at a fixed position relative to the axes regardless of zoom:

```python
# Arrow points to data coordinate, text stays in axes fraction
ax.annotate('Peak',
            xy=(x_peak, y_peak),           # Data coordinates
            xycoords='data',
            xytext=(0.7, 0.8),             # Axes fraction
            textcoords='axes fraction',
            arrowprops=dict(arrowstyle='->'))
```

### Coordinate System Names

Use string names instead of transform objects:

```python
ax.annotate('Note',
            xy=(1, 1),
            xycoords='data',
            xytext=(50, 50),
            textcoords='offset points',    # Offset from xy in pixels
            arrowprops=dict(arrowstyle='->'))
```

Available coordinate names:
- `'data'` — data coordinates
- `'axes fraction'` — axes (0-1)
- `'figure fraction'` — figure (0-1)
- `'figure pixels'` — figure in pixels
- `'offset points'` — offset from xy point
- `'display'` — display (screen) pixels

## Compound Transforms

Combine transforms using `+` for composition:

```python
from matplotlib.transforms import Affine2D

# Scale and translate
transform = Affine2D().scale(1.5).translate(10, 20) + ax.transData

# Use with an artist
circle = plt.Circle((0, 0), 0.5, transform=transform)
ax.add_patch(circle)
```

### Common Transform Operations

```python
from matplotlib.transforms import Affine2D, BboxTransformTo, ScaledTranslation

# Translation in display units
offset = ScaledTranslation(dx/dpi*72, dy/dpi*72, fig.dpi_scale_trans)
new_transform = original_transform + offset

# Scale transform
scale = Affine2D().scale(2.0, 0.5)
```

## Bbox (Bounding Box) Transforms

```python
from matplotlib.transforms import Bbox

# Define a bounding box
bbox = Bbox([[0, 0], [100, 100]])

# Transform to fit within axes
transform = BboxTransformTo(bbox)
```

## Practical Examples

### Fixed-Size Markers Independent of Data Scale

```python
from matplotlib.transforms import Affine2D

# Marker size in display units (points), not data units
size_in_points = 10
transform = ax.transData + Affine2D().scale(size_in_points/72, size_in_points/72)
```

### Drawing a Rectangle Over Part of the Axes

```python
from matplotlib.patches import Rectangle

# Rectangle in axes coordinates (covers right half, bottom third)
rect = Rectangle((0.5, 0), 0.5, 0.33,
                 transform=ax.transAxes,
                 facecolor='yellow', alpha=0.3)
ax.add_patch(rect)
```

### Inset with Blended Transform

```python
# x in data coords, y in axes fraction
inset_x = ax.inset_axes([0.6, 0.55, 0.35, 0.35])
inset_x.plot(x, y)
inset_x.set_xlim(2, 4)
ax.indicate_inset_zoom(inset_x, edgecolor='red')
```

### OffsetBox Annotations (for annotations that stay fixed)

```python
from matplotlib.offsetbox import AnnotationBbox, TextArea

# Fixed-size annotation box
text_box = TextArea("Fixed size label", textprops=dict fontsize=12))
ab = AnnotationBbox(text_box, (x, y),
                    xycoords='data',
                    box_alignment=(0, 0.5),
                    arrowprops=dict(arrowstyle='->'))
ax.add_artist(ab)
```
