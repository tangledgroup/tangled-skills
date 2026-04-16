---
name: matplotlib-3-10-8
description: Comprehensive toolkit for Matplotlib 3.10.8, the Python plotting library for creating static, animated, and interactive visualizations. Use when generating plots (line, scatter, bar, histogram, contour, 3D), customizing figures/axes/colors/text, managing backends and output formats (PNG, SVG, PDF, PS), configuring rcParams, building subplots/gridspecs, animations, or integrating with Jupyter notebooks.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "3.10.8"
tags:
  - plotting
  - visualization
  - charts
  - graphs
  - data-visualization
  - figures
category: data-science
external_references:
  - https://github.com/matplotlib/matplotlib/tree/v3.10.8/doc
---

# Matplotlib 3.10.8

## Overview

Matplotlib is the foundational Python plotting library for creating a wide variety of static, animated, and interactive visualizations. It provides both a quick plotting interface via `pyplot` (MATLAB-like state machine) and an object-oriented API for fine-grained control over every element in a figure. Matplotlib serves as the visualization backend for pandas, seaborn, scikit-learn, and many other data science libraries.

## When to Use

Use this skill when:
- Creating line plots, scatter plots, bar charts, histograms, contour plots, or 3D visualizations
- Customizing figure appearance: colors, colormaps, tick labels, legends, annotations
- Configuring subplot layouts with `subplots`, `GridSpec`, `subplot_mosaic`, or `SubFigure`
- Saving figures to multiple formats (PNG, SVG, PDF, PS, JPG, TIFF)
- Setting up interactive backends for Jupyter notebooks or GUI applications
- Creating animations using the `animation` module
- Customizing axes: scales (log, symlog, datetime), limits, ticks, tick formatters
- Working with collections, patches, paths, and custom artists
- Configuring global defaults via `rcParams` or style sheets

## Core Concepts

### The Figure-Axes Architecture

Every matplotlib figure follows a hierarchical structure:

```
Figure                    # Top-level container
├── Axes (or subplots)    # Individual plot area(s)
│   ├── XAxis / YAxis     # Axis objects with ticks, labels
│   ├── Title             # Plot title
│   ├── Legend            # Legend box
│   └── Artists           # Lines, patches, text, images on the axes
├── Figure-level artists  # Text, colorbars, legends at figure level
└── SubFigures            # Nested logical figures (SubFigure)
```

### Two API Styles

**1. Pyplot State Machine (implicit)** — Quick, MATLAB-like plotting:

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2, 100)
plt.plot(x, x**2, 'r-', label='$y=x^2$')
plt.xlabel('x')
plt.ylabel('y')
plt.title('Simple Plot')
plt.legend()
plt.show()
```

**2. Object-Oriented (explicit, recommended)** — Full control:

```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()
x = np.linspace(0, 2, 100)
ax.plot(x, x**2, 'r-', label='$y=x^2$')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Simple Plot')
ax.legend()
plt.show()
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `matplotlib.pyplot` | State-based plotting interface (pyplot) |
| `matplotlib.figure.Figure` | Top-level container for all plot elements |
| `matplotlib.axes.Axes` | The plotted data area with axes, ticks, labels |
| `matplotlib.artist.Artist` | Base class for all visible elements |
| `matplotlib.lines.Line2D` | Line objects (markers, colors, linestyles) |
| `matplotlib.patches` | Shapes: Rectangle, Circle, Polygon, FancyBboxPatch |
| `matplotlib.path.Path` | Vector paths with vertices and codes |
| `matplotlib.collections.Collection` | Groups of similar artists (e.g., scatter points) |
| `matplotlib.colors` | Color specification, normalization, colormaps |
| `matplotlib.ticker` | Tick location and formatting logic |
| `matplotlib.scale.ScaleBase` | Axis scale types (linear, log, symlog, datetime) |
| `matplotlib.transforms.Transform` | Coordinate transformation system |
| `matplotlib.gridspec.GridSpec` | Programmatic subplot layout |
| `matplotlib.animation` | Animation framework (FuncAnimation) |
| `matplotlib.style` | Style sheets for consistent appearance |

### Color Specification

Colors can be specified in multiple ways:

```python
# Named colors
ax.plot(x, 'red')
ax.plot(x, 'C0')  # Cycle color (blue by default)

# RGB / RGBA tuples (0-1 range)
ax.plot(x, (0.2, 0.4, 0.6, 0.8))

# Hex strings
ax.plot(x, '#FF5733')

# Colormap lookup
cmap = plt.get_cmap('viridis')
color = cmap(0.5)  # Returns RGBA tuple
```

### Colormaps

Matplotlib provides built-in colormaps accessible via `plt.cm.<name>` or `plt.get_cmap('<name>')`:

- **Sequential**: `viridis`, `plasma`, `inferno`, `magma`, `cividis`
- **Diverging**: `coolwarm`, `seismic`, `RdBu_r`, `bwr`
- **Cyclic**: `twilight`, `hsv` (qualitative)
- **Qualitative**: `tab10`, `tab20`, `Set1`, `Pastel1`

```python
# Set default colormap for subsequent plots
plt.set_cmap('viridis')

# Use with imshow/contour/pcolormesh
im = ax.imshow(data, cmap='plasma', norm=LogNorm(vmin=1, vmax=100))
fig.colorbar(im, ax=ax)
```

### rcParams Configuration

Global defaults are controlled via `matplotlib.rcParams`:

```python
import matplotlib as mpl

# View current settings
print(mpl.rcParams['figure.figsize'])  # [5.5, 4.5]

# Set a parameter
mpl.rcParams['figure.dpi'] = 150
mpl.rcParams['axes.grid'] = True
mpl.rcParams['lines.linewidth'] = 2

# Use rc_context for temporary settings
with mpl.rc_context({'lines.linewidth': 3, 'axes.facecolor': 'white'}):
    plt.plot(x, y)  # Uses linewidth=3 temporarily

# Reset all defaults
mpl.rcParams.update(mpl.rcParamsDefault)
```

Key rcParams categories: `figure.*`, `axes.*`, `lines.*`, `patch.*`, `text.*`, `font.*`, `savefig.*`, `image.*`, `legend.*`.

### Backends

Matplotlib supports multiple rendering backends:

**Interactive (GUI) backends:**
| Backend | GUI Framework |
|---------|--------------|
| `tkagg` | Tkinter (default on many systems) |
| `macosx` | macOS native |
| `qtagg` / `qt5agg` | PyQt/PySide |
| `gtk3agg` / `gtk4agg` | GTK3/GTK4 |
| `wx` | wxPython |
| `nbagg` / `notebook` | Jupyter notebook |
| `webagg` | Browser-based (port 8080) |

**Non-interactive (headless) backends:**
| Backend | Purpose |
|---------|---------|
| `agg` | Anti-aliased raster (PNG output, default) |
| `svg` | Vector SVG output |
| `pdf` | PDF output |
| `ps` | PostScript output |
| `cairo` | Cairo rendering |
| `pgf` | PGF/TikZ output |
| `template` | Custom backend templates |

Switch backends before importing pyplot:

```python
import matplotlib
matplotlib.use('Agg')  # Must be called BEFORE pyplot import
import matplotlib.pyplot as plt
```

Or set via environment variable: `MPLBACKEND=Agg` or `matplotlibrc`.

## Installation / Setup

```bash
# Via pip
pip install matplotlib

# Via conda
conda install matplotlib

# With extras (for some backends)
pip install matplotlib[dev]
```

Required dependencies: NumPy, Python 3.10+. Optional: freetype, libpng, kiwisolver, cycler, pillow, pyparsing.

## Usage Examples

### Basic Plotting

```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots()
x = np.linspace(0, 2, 100)
ax.plot(x, x, label='linear')
ax.plot(x, x**2, label='quadratic')
ax.plot(x, x**3, label='cubic')
ax.set_xlabel('x label')
ax.set_ylabel('y label')
ax.set_title("Simple Plot")
ax.legend()
plt.show()
```

### Multiple Subplots

```python
fig, axes = plt.subplots(2, 2, figsize=(10, 8))
for i, ax in enumerate(axes.flat):
    x = np.random.randn(100)
    if i == 0:
        ax.hist(x, bins=20)
        ax.set_title('Histogram')
    elif i == 1:
        ax.scatter(x, x+np.random.randn(100))
        ax.set_title('Scatter')
    elif i == 2:
        ax.bar(['A','B','C'], [3,7,5])
        ax.set_title('Bar')
    else:
        ax.stem([1,3,5,7,4])
        ax.set_title('Stem')
fig.tight_layout()
plt.show()
```

### Advanced Styling

```python
import matplotlib as mpl
mpl.rcParams.update({
    'figure.figsize': (10, 6),
    'axes.facecolor': '#F5F5F5',
    'axes.edgecolor': 'black',
    'axes.linewidth': 1.5,
    'lines.linewidth': 2.5,
    'lines.markersize': 8,
    'font.size': 14,
    'legend.frameon': True,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 7, 2])
ax.grid(True, alpha=0.3)
plt.show()
```

### Saving Figures

```python
# PNG with transparency
fig.savefig('plot.png', dpi=150, transparent=True, bbox_inches='tight')

# SVG vector format
fig.savefig('plot.svg', format='svg')

# PDF for publications
fig.savefig('plot.pdf', bbox_inches='tight')

# Multi-page PDF (for multiple figures)
with plt.figure(), plt.plot([1,2,3]):
    pass  # Each plt.figure() adds a page when using PdfPages
```

### Annotations and Text

```python
ax.annotate('Local Max', xy=(np.pi/2, 1), xytext=(0.8, 0.9),
            arrowprops=dict(facecolor='red', shrink=0.05),
            fontsize=12, color='blue')

ax.text(0.5, 0.5, 'Centered Text', ha='center', va='center',
        transform=ax.transAxes, fontsize=16)
```

### 3D Plotting (mplot3d toolkit)

```python
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
x = np.outer(np.sin(v), np.cos(u))
y = np.outer(np.sin(v), np.sin(u))
z = np.outer(np.cos(v), np.ones_like(u))
ax.plot_surface(x, y, z, cmap='viridis')
plt.show()
```

### Animations

```python
from matplotlib.animation import FuncAnimation

fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = ax.plot([], [], 'ro')
ax.set_xlim(0, 2*np.pi)
ax.set_ylim(-1, 1)

def init():
    ln.set_data([], [])
    return ln,

def animate(i):
    xdata.append(i * 0.1)
    ydata.append(np.sin(i * 0.1))
    ln.set_data(xdata, ydata)
    return ln,

ani = FuncAnimation(fig, animate, init_func=init, frames=100, blit=True)
plt.show()
```

### Boxplot and Violin Plot

```python
data = [np.random.normal(0, std, 100) for std in range(1, 4)]
fig, ax = plt.subplots()
ax.boxplot(data, labels=['Group 1', 'Group 2', 'Group 3'])
ax.violinplot(data, showmeans=True)
plt.show()
```

### Hexbin and Heatmap-style Plots

```python
x = np.random.randn(10000)
y = np.random.randn(10000)
fig, ax = plt.subplots()
hb = ax.hexbin(x, y, gridsize=50, cmap='YlOrRd', mincnt=1)
fig.colorbar(hb, ax=ax)
plt.show()
```

### Style Sheets

```python
# Use built-in styles
plt.style.use('seaborn-v0_8-whitegrid')
plt.style.use('ggplot')
plt.style.use('classic')

# List available styles
print(plt.style.available)

# Apply temporarily
with plt.style.context('dark_background'):
    plt.plot(x, y)
```

## Advanced Topics

For detailed API reference and advanced topics, see the reference files:

- **Figure API** — Figure class, subfigures, layout engines, saving
- **Axes API** — All plotting methods (line, scatter, bar, hist, contour, etc.), axis configuration, appearance
- **Pyplot API** — State machine interface overview and function catalog
- **Colors & Colormaps** — Color specification, normalization, colormap registry
- **Text & Annotations** — Text rendering, LaTeX math, annotation arrows, bounding boxes
- **Animation** — FuncAnimation, blitting, writer backends (ffmpeg, pillow)
- **3D Toolkit (mplot3d)** — 3D axes, surfaces, wireframes, projections
- **Widgets & Interactive** — Sliders, buttons, checkboxes, range selectors, event handling
- **Transforms** — Coordinate systems, transformations, blending modes
- **Artist API** — Base classes for all visual elements, property cycles
- **Styles & Configuration** — rcParams, style sheets, matplotlibrc file
- **Backends** — All available backends, switching, configuration

## References

- GitHub repository: https://github.com/matplotlib/matplotlib/tree/v3.10.8
- API reference (v3.10.8): https://matplotlib.org/3.10.8/api/index.html
- User guide: https://matplotlib.org/3.10.8/users/index.html
- Tutorial gallery: https://matplotlib.org/3.10.8/gallery/index.html
