# Backends Reference

## Overview

Matplotlib uses a "backend" architecture to support different output targets. The backend is responsible for rendering the figure and handling user interaction.

### Two Categories of Backends

**Interactive (GUI) backends** — Used when displaying figures in a window:
- `tkagg` — Tkinter (default on many systems)
- `macosx` — macOS native
- `qtagg` / `qt5agg` — PyQt5/PyQt6/PySide2/PySide6
- `gtk3agg` / `gtk4agg` — GTK3/GTK4
- `wx` — wxPython
- `nbagg` / `notebook` — Jupyter notebook (ipympl)
- `webagg` — Browser-based

**Non-interactive (headless) backends** — Used for generating files:
- `agg` — Anti-aliased raster (PNG, default on most systems)
- `svg` — Vector SVG output
- `pdf` — PDF output
- `ps` — PostScript output
- `cairo` — Cairo rendering (SVG, PS, PDF)
- `pgf` — PGF/TikZ output
- `template` — Custom backend templates

## Switching Backends

### Method 1: matplotlib.use() — Before pyplot import

```python
import matplotlib
matplotlib.use('Agg')              # Must be called BEFORE importing pyplot
import matplotlib.pyplot as plt
```

### Method 2: Environment Variable

```bash
MPLBACKEND=Agg python script.py
MPLBACKEND=tkagg python -c "import matplotlib.pyplot as plt; plt.show()"
```

### Method 3: matplotlibrc Configuration

In `~/.config/matplotlib/matplotlibrc`:
```ini
backend: Agg
```

### Method 4: Runtime Switching (limited)

```python
# Note: switching backends at runtime is not always safe
import matplotlib.pyplot as plt
plt.switch_backend('Agg')          # May not work after figure creation
```

## Backend-specific Details

### Agg Backend

The `Agg` (Anti-Grain Geometry) backend is the default non-interactive backend. It provides high-quality raster rendering.

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 7, 2])
fig.savefig('output.png', dpi=150)
```

### SVG Backend

For vector graphics output:

```python
import matplotlib
matplotlib.use('SVG')
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 7, 2])
fig.savefig('output.svg', bbox_inches='tight')
```

### PDF Backend

For publication-quality PDF:

```python
import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 7, 2])
fig.savefig('output.pdf', bbox_inches='tight')
```

### WebAgg Backend (Browser-based)

```python
import matplotlib
matplotlib.use('module://matplotlib.backends.backend_webagg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 7, 2])
plt.show()    # Opens in browser at http://localhost:8080
```

### TkAgg Backend (Tkinter)

```python
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 7, 2])
plt.show()    # Opens in Tkinter window
```

### Qt Backend (PyQt/PySide)

```python
# Force specific Qt binding
import matplotlib
matplotlib.use('Qt5Agg')     # PyQt5 or PySide2
matplotlib.use('Qt6Agg')     # PyQt6 or PySide6

# Or let matplotlib auto-detect
matplotlib.use('QtAgg')      # Uses preferred Qt binding

import matplotlib.pyplot as plt
plt.show()
```

### macOS Backend

The `macosx` backend provides native macOS window management:

```python
import matplotlib
matplotlib.use('macosx')
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 7, 2])
plt.show()
```

### Jupyter Notebook Backend

For interactive plots in Jupyter:

```python
# In a Jupyter notebook cell:
%matplotlib inline            # Static images (default)
%matplotlib widget            # Interactive (requires ipympl)
%matplotlib notebook          # Legacy interactive
```

Or programmatically:
```python
import matplotlib
matplotlib.use('module://ipympl.backend_nbagg')
import matplotlib.pyplot as plt
```

## Backend Registry API

```python
from matplotlib.backends import backend_registry

# List available backends
all_backends = backend_registry.list_builtin()
interactive = backend_registry.list_builtin(backend_registry.BackendFilter.INTERACTIVE)
non_interactive = backend_registry.list_builtin(backend_registry.BackendFilter.NON_INTERACTIVE)

# Check if a backend is valid
is_valid = backend_registry.is_valid_backend('Agg')

# Get GUI framework for a backend
gui_framework = backend_registry.get_gui_framework('tkagg')  # 'tk'
```

## Configuring Backends Programmatically

### Custom Backend Loader

```python
import matplotlib.backends.backend_tkagg as backend_tkagg
matplotlib.use(backend_tkagg)
```

### Entry Points for External Backends

External packages can register backends via entry points. A package can provide:

```python
# In setup.py or pyproject.toml:
# [options.entry_points]
# matplotlib.backends =
#     my_backend = my_package.backend_module
```

Then use with:
```python
matplotlib.use('my_backend')
```

## Common Issues and Solutions

### "No module named 'tkinter'" on Linux
```bash
sudo apt-get install python3-tk    # Debian/Ubuntu
sudo dnf install python3-tkinter   # Fedora/RHEL
```

### Qt backend not available
```bash
pip install PyQt5    # or: pip install PyQt6
# or: pip install PySide6
```

### Headless server (no display)
```python
import matplotlib
matplotlib.use('Agg')     # Force non-interactive backend
import matplotlib.pyplot as plt
```

Or set environment variable:
```bash
export MPLBACKEND=Agg
```
