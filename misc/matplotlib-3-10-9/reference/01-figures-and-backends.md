# Figures and Backends

## What Is a Backend?

Backends handle the rendering of Matplotlib figures — either displaying them on screen (interactive) or writing to files (non-interactive). The "frontend" is the user-facing plotting code; the "backend" does the actual drawing work.

Matplotlib supports many use cases: interactive Python shells with pop-up windows, Jupyter notebooks with inline plots, GUI embedding (PyQt, PyGObject, Tkinter), batch scripts generating images, and web application servers serving dynamic graphs.

## Backend Types

**User interface backends** (interactive) — for PyQt/PySide, GTK4/GTK3, Tkinter, wxPython, or macOS/Cocoa.

**Hardcopy backends** (non-interactive) — for writing image files:

- **Agg** — PNG raster graphics using the Anti-Grain Geometry engine (high quality)
- **PDF** — Portable Document Format (vector)
- **PS** — PostScript / EPS (vector)
- **SVG** — Scalable Vector Graphics (vector)
- **PGF** — PGF/TikZ output for LaTeX documents
- **Cairo** — PNG, PS, PDF, SVG via the Cairo library (requires pycairo or cairocffi)

## Selecting a Backend

Three methods, listed by precedence (last wins):

1. `rcParams["backend"]` in matplotlibrc file
2. `MPLBACKEND` environment variable
3. `matplotlib.use()` function call

```python
# Method 1: matplotlibrc file
# backend : qtagg

# Method 2: Environment variable
# export MPLBACKEND=qtagg

# Method 3: Programmatic (must be before any figure creation)
import matplotlib
matplotlib.use('QtAgg')
```

**Automatic detection**: Without explicit configuration, Matplotlib auto-detects in this order: MacOSX → QtAgg → GTK4Agg → Gtk3Agg → TkAgg → WxAgg → Agg. The Agg fallback is non-interactive (file-only).

## Interactive Backends

- **QtAgg** — Agg rendering in a Qt canvas (requires PyQt or PySide)
- **GTK4Agg / GTK3Agg** — Agg rendering in a GTK canvas
- **TkAgg** — Agg rendering in a Tkinter canvas
- **WxAgg** — Agg rendering in a wxPython canvas
- **macosx** — Native macOS backend (vector-based, no Agg)

## Viewing Figures

### Jupyter Notebooks

Default inline backend produces static plots:

```python
%matplotlib inline  # Static images (default in Jupyter)
```

For interactive plots in notebooks:

```python
%matplotlib widget   # ipympl backend (JupyterLab, notebook >= 7)
%matplotlib notebook # Legacy notebook backend (notebook < 7)
```

### Standalone Scripts

Figures appear in a GUI window when `plt.show()` is called. The call blocks until the window is closed. The toolbar provides Zoom, Pan, and Save tools.

```python
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 2])
plt.show()  # Blocks until window closes
```

### Headless Environments

On servers without a display, use the Agg backend:

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [1, 4, 2])
fig.savefig('output.png')
# plt.show() would fail here — save instead
```

## Creating Figures

```python
import matplotlib.pyplot as plt

# Empty figure
fig = plt.figure(figsize=(8, 6), dpi=100)

# Figure with single Axes
fig, ax = plt.subplots(figsize=(8, 6))

# Grid of Axes
fig, axs = plt.subplots(2, 3, figsize=(12, 8))

# Complex layout
fig, axs = plt.subplot_mosaic([['A', 'B'], ['A', 'C']])
```

### Figure Options

- `figsize` — (width, height) in inches
- `dpi` — pixels per inch
- `facecolor` — background color
- `layout='constrained'` — automatic spacing adjustment (default in 3.10)
- `constrained_layout=True` — legacy equivalent

### Subfigures

For nested layouts where subgroups of axes don't share the same grid:

```python
fig = plt.figure(layout='constrained', facecolor='lightgray')
fig.suptitle('Figure')
figL, figR = fig.subfigures(1, 2)
figL.set_facecolor('thistle')
axL = figL.subplots(2, 1, sharex=True)
axL[1].set_xlabel('x [m]')
figL.suptitle('Left subfigure')
```

## Saving Figures

```python
# Basic save
fig.savefig('plot.png')

# High-quality vector output
fig.savefig('plot.svg', bbox_inches='tight')

# Publication-ready PDF
fig.savefig('plot.pdf', dpi=300, bbox_inches='tight')

# Control appearance
fig.savefig('plot.png',
            dpi=150,
            facecolor='white',
            edgecolor='none',
            bbox_inches='tight',
            pad_inches=0.1)
```

Key parameters:
- `bbox_inches='tight'` — trim whitespace around the figure
- `dpi` — resolution for raster formats
- `facecolor` / `edgecolor` — background and border colors
- `format` — explicit format override

## Environment Variables

- `MPLBACKEND` — set the backend (e.g., `export MPLBACKEND=Agg`)
- `MPLCONFIGDIR` — override the matplotlib configuration directory
- `MPLDATA_DIR` — override the matplotlib data directory

Note: Setting `MPLBACKEND` globally in `.bashrc` is discouraged as it can cause unexpected behavior. Use it per-script instead: `MPLBACKEND=Agg python script.py`.
