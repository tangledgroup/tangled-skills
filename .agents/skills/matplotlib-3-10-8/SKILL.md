---
name: matplotlib-3-10-8
description: Comprehensive toolkit for Matplotlib 3.10.8, the Python plotting library for creating static, animated, and interactive visualizations. Use when generating plots (line, scatter, bar, histogram, contour, 3D), customizing figures/axes/colors/text, managing backends and output formats (PNG, SVG, PDF, PS), configuring rcParams, building subplots/gridspecs, animations, or integrating with Jupyter notebooks.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
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
  - https://github.com/matplotlib/matplotlib/tree/v3.10.8
  - https://matplotlib.org/3.10.8/api/index.html
  - https://matplotlib.org/3.10.8/gallery/index.html
  - https://matplotlib.org/3.10.8/users/index.html
---

# Matplotlib 3.10.8

## Overview

Matplotlib is the foundational Python plotting library for creating static, animated, and interactive visualizations. It produces publication-quality figures in a wide variety of formats and supports all major operating systems. Built on NumPy arrays, it provides both a high-level pyplot interface for quick scripting and a lower-level object-oriented API for fine-grained control.

Matplotlib 3.10.8 introduces support for constrained layout as the default, improved color handling with alpha tuples, enhanced animation writers (PillowWriter, FFMpegWriter), and refined subplot mosaic layouts. It works seamlessly with Jupyter notebooks, IPython, PyQt/PySide, Tkinter, wxPython, and headless environments.

## When to Use

- Generating 2D plots: line charts, scatter plots, bar charts, histograms, box plots, violin plots
- Creating gridded data visualizations: heatmaps (imshow), contour plots, pcolormesh
- Building statistical visualizations: ECDFs, hexbin, error bars, stackplots
- Producing 3D plots: surfaces, wireframes, scatter3d, bar3d
- Saving figures to PNG, SVG, PDF, PS, or PGF formats
- Customizing plot appearance through rcParams, style sheets, and colormaps
- Creating animations with FuncAnimation or ArtistAnimation
- Embedding Matplotlib in GUI applications (Qt, Tk, wx) or web servers
- Working with date/time data, custom tick locators/formatters
- Building complex multi-axis layouts with subplot_mosaic or GridSpec

## Core Concepts

### The Object Hierarchy

Everything visible in a Matplotlib figure is an **Artist**. The hierarchy is:

- **Figure** — the top-level container (window, canvas, or output file). Created via `plt.figure()` or `plt.subplots()`.
- **Axes** — a plotting area within a Figure. Each Axes has its own x/y axes (Axis objects), data region, title, labels, and legend. Most plotting methods live here.
- **Axis** — the tick-generating objects that control scale, limits, locators, and formatters.
- **Artist** — everything visible: Line2D, Text, Rectangle, Patch, Collection, Image, etc. Artists are drawn when the Figure is rendered.

### Two API Styles

**Object-oriented (OO) style** — recommended for most use cases:

```python
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(6, 4), layout='constrained')
ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
ax.set_xlabel('x label')
ax.set_ylabel('y label')
ax.set_title('Simple Plot')
plt.show()
```

**Pyplot (state-machine) style** — convenient for quick scripts:

```python
import matplotlib.pyplot as plt

plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
plt.xlabel('x label')
plt.ylabel('y label')
plt.title('Simple Plot')
plt.show()
```

The OO style is preferred because it avoids global state, supports multiple figures/axes cleanly, and makes customization explicit.

### Creating Figures and Axes

```python
# Empty figure, no axes
fig = plt.figure()

# Figure with a single Axes
fig, ax = plt.subplots()

# 2x2 grid of Axes
fig, axs = plt.subplots(2, 2)

# Complex layout with subplot_mosaic
fig, axs = plt.subplot_mosaic([['left', 'top'], ['left', 'bottom']])
```

The `layout='constrained'` parameter (default in 3.10) automatically adjusts spacing to prevent label overlap. Use `fig.subplots_adjust()` for manual control or `tight_layout()` for the legacy approach.

### Saving Figures

```python
fig.savefig('plot.png')           # PNG (raster)
fig.savefig('plot.svg')           # SVG (vector)
fig.savefig('plot.pdf')           # PDF (vector)
fig.savefig('plot.eps')           # Encapsulated PostScript
fig.savefig('plot.png', dpi=300)  # High-resolution PNG
```

Key `savefig` parameters: `dpi`, `bbox_inches='tight'`, `pad_inches`, `facecolor`, `format`.

## Usage Examples

### Line Plots with Multiple Series

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 2, 100)
fig, ax = plt.subplots(figsize=(6, 4), layout='constrained')
ax.plot(x, x, label='linear')
ax.plot(x, x**2, label='quadratic')
ax.plot(x, x**3, label='cubic')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Multiple Lines')
ax.legend()
plt.show()
```

### Scatter Plot with Data Keyword

```python
np.random.seed(42)
data = {'a': np.arange(50), 'c': np.random.randint(0, 50, 50)}
data['b'] = data['a'] + 10 * np.random.randn(50)
data['d'] = np.abs(data['a']) * 100

fig, ax = plt.subplots(figsize=(5, 3), layout='constrained')
ax.scatter('a', 'b', c='c', s='d', data=data)
ax.set_xlabel('entry a')
ax.set_ylabel('entry b')
```

### Bar Chart with Error Bars

```python
categories = ['A', 'B', 'C', 'D']
values = [30, 45, 25, 60]
errors = [3, 5, 2, 7]

fig, ax = plt.subplots(layout='constrained')
ax.bar(categories, values, yerr=errors, capsize=5, color='steelblue')
ax.set_ylabel('Value')
ax.set_title('Bar Chart with Error Bars')
```

### Subplot Mosaic Layout

```python
import matplotlib.pyplot as plt

grid = [
    ['top_left', 'top_right'],
    ['bottom_left', 'top_right'],
]
fig, axs = plt.subplot_mosaic(grid, figsize=(8, 6), layout='constrained')
for name, ax in axs.items():
    ax.text(0.5, 0.5, name.replace('_', '\n'), ha='center', va='center', fontsize=14)
```

## Advanced Topics

**Figures and Backends**: Output backends (Agg, QtAgg, GTK4Agg, SVG, PDF, PS), interactive vs non-interactive, backend selection, Jupyter integration → [Figures and Backends](reference/01-figures-and-backends.md)

**Axes, Subplots, and Layouts**: GridSpec, subplot_mosaic, constrained layout, tight_layout, twin axes, shared axes, inset axes, colorbar placement → [Axes and Layouts](reference/02-axes-and-layouts.md)

**Plot Types Reference**: Complete catalog of plotting methods — line, scatter, bar, histogram, contour, imshow, pcolormesh, pie, boxplot, violin, quiver, streamplot, hexbin, ECDF, stairs → [Plot Types](reference/03-plot-types.md)

**Colors and Colormaps**: Color specification formats (RGB, hex, named, xkcd, Tableau), colormaps (sequential, diverging, qualitative, cyclic), normalization, alpha blending, custom colorbars → [Colors and Colormaps](reference/04-colors-and-colormaps.md)

**Text, Annotations, and Math**: Text placement, annotations with arrows, mathematical expressions (LaTeX-like syntax), font management, text properties, mathtext rendering → [Text and Annotations](reference/05-text-and-annotations.md)

**Customization and rcParams**: Runtime rc settings, style sheets (built-in and custom), matplotlibrc configuration, rc_context for temporary changes, cycler for property cycles → [Customization](reference/06-customization.md)

**Transformations**: Data coordinates, display coordinates, axes coordinates, blended transforms, compound transforms, offsetbox annotations → [Transformations](reference/07-transformations.md)

**Animations**: FuncAnimation, ArtistAnimation, blitting for performance, saving to MP4/GIF via PillowWriter and FFMpegWriter → [Animations](reference/08-animations.md)

**3D Plotting**: mplot3d toolkit, 3D line/scatter/surface/wireframe plots, volumetric data (voxels), tri-surface, contour3D → [3D Plotting](reference/09-3d-plotting.md)

**API Reference Summary**: pyplot module functions, Axes methods, Artist base class, Figure methods, Axis locators and formatters, patches, collections → [API Reference](reference/10-api-reference.md)
