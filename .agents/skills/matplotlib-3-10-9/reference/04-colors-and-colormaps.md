# Colors and Colormaps

## Color Specification Formats

Matplotlib recognizes multiple formats for specifying colors:

### RGB/RGBA Tuples

```python
(0.1, 0.2, 0.5)        # RGB, floats in [0, 1]
(0.1, 0.2, 0.5, 0.3)   # RGBA with alpha
```

### Hex Strings

```python
'#0f0f0f'       # 6-digit hex RGB
'#0f0f0f80'     # 8-digit hex RGBA
'#abc'          # Shorthand = '#aabbcc'
'#fb1'          # Shorthand = '#ffbb11'
```

### Grayscale Strings

```python
'0'    # Black
'0.5'  # Medium gray
'1'    # White
```

### Single-Character Shorthands

```
b — blue      g — green     r — red
c — cyan      m — magenta   y — yellow
k — black     w — white
```

Note: These shades differ from X11/CSS4 colors for better visibility.

### Named Colors

```python
'red'              # X11/CSS4 color name
'aquamarine'       # Any valid CSS4 name
'xkcd:sky blue'    # xkcd survey color (prefix required)
'tab:blue'         # Tableau T10 palette (default cycle)
```

Tableau T10 colors: `tab:blue`, `tab:orange`, `tab:green`, `tab:red`, `tab:purple`, `tab:brown`, `tab:pink`, `tab:gray`, `tab:olive`, `tab:cyan`.

### Cycle Index Colors

```python
'C0'   # First color in the property cycle
'C1'   # Second color
'C9'   # Tenth color
```

### Alpha Tuple (3.8+)

```python
('green', 0.3)     # Green with 30% opacity
('#f00', 0.9)      # Red hex with 90% opacity
```

### Special Values

```python
'none'   # Fully transparent (equivalent to RGBA (0,0,0,0))
```

## Transparency (Alpha Blending)

Alpha ranges from 0 (fully transparent) to 1 (fully opaque). The blending formula is:

```
RGB_result = RGB_background * (1 - alpha) + RGB_foreground * alpha
```

```python
ax.plot(x, y, color='red', alpha=0.5)
ax.scatter(x, y, alpha=0.3, s=100)
```

## Colormaps

Matplotlib provides several categories of colormaps:

### Sequential

For data with an intrinsic order (low → high):
- `viridis` (default), `plasma`, `inferno`, `magma`
- `Blues`, `Greens`, `Oranges`, `Reds`
- `Greys`, `Purples`, `YlGnBu`, `PuOr`

### Diverging

For data with a meaningful midpoint:
- `RdBu_r`, `RdYlBu_r`, `Sseismic`, `coolwarm`
- `PiYG`, `PRGn`, `BrBG`, `Spectral_r`

### Qualitative (Categorical)

For discrete categories without ordering:
- `tab10` (default), `Set1`, `Set2`, `Set3`
- `Pastel1`, `Pastel2`, `Paired`, `Dark2`, `Accent`, `Tab20`

### Cyclic

For periodic data (angles, time of day):
- `twilight`, `hsv`, `nipy_spectral`

### Using Colormaps

```python
# In plotting functions
im = ax.imshow(data, cmap='viridis')
sc = ax.scatter(x, y, c=z, cmap='plasma', vmin=0, vmax=100)

# Access colormap programmatically
from matplotlib.colormaps import get_cmap
cmap = get_cmap('viridis')
colors = cmap(np.linspace(0, 1, 100))

# Reverse a colormap
im = ax.imshow(data, cmap='viridis_r')

# Get colors from colormap
color_at_05 = cmap(0.5)
```

## Colormap Normalization

Control how data values map to colormap colors:

```python
import matplotlib.colors as mcolors

# Linear (default)
norm = mcolors.Normalize(vmin=0, vmax=100)
ax.imshow(data, cmap='viridis', norm=norm)

# Logarithmic
norm = mcolors.LogNorm(vmin=1, vmax=1000)
ax.pcolormesh(X, Y, Z, norm=norm)

# Symmetric log (for data with zero crossing)
norm = mcolors.SymLogNorm(linthresh=1.0, linscale=1, vmin=-100, vmax=100)

# Power law
norm = mcolors.PowerNorm(gamma=0.5)

# Discrete (binned) colors
bounds = [0, 25, 50, 75, 100]
norm = mcolors.BoundaryNorm(bounds, ncolors=256)

# Two-slope linear
norm = mcolors.TwoSlopeNorm(vmin=-1, vcenter=0, vmax=1)
```

## Creating Custom Colormaps

```python
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import numpy as np

# From a list of colors
colors = ['red', 'yellow', 'green', 'blue']
cmap = ListedColormap(colors)

# From RGB values
cdict = {
    'red':   [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
    'green': [(0.0, 0.0, 0.0), (1.0, 1.0, 1.0)],
    'blue':  [(0.0, 1.0, 1.0), (1.0, 0.0, 0.0)],
}
cmap = LinearSegmentedColormap.from_list('custom', cdict, N=256)

# Interpolated from color list
cmap = LinearSegmentedColormap.from_list(
    'my_cmap', ['darkblue', 'cyan', 'yellow', 'red'], N=256
)
```

## Colorbars

```python
im = ax.imshow(data, cmap='viridis')
cbar = fig.colorbar(im, ax=ax)
cbar.set_label('Intensity (a.u.)')

# Horizontal colorbar
fig.colorbar(im, ax=ax, orientation='horizontal', pad=0.08)

# Custom colorbar ticks
cbar = fig.colorbar(im, ax=ax, ticks=[0, 25, 50, 75, 100])
cbar.set_ticklabels(['Low', 'Med-Low', 'Med-High', 'High', 'Max'])

# Extended colorbar (with triangles at ends)
norm = mcolors.BoundaryNorm([0, 33, 66, 100], ncolors=256, extend='both')
im = ax.imshow(data, norm=norm)
fig.colorbar(im, ax=ax)
```

## Choosing Colormaps

Guidelines for selecting colormaps:

- **Default data**: Use `viridis` — perceptually uniform, colorblind-safe
- **Diverging data** (positive/negative): Use `RdBu_r` or `coolwarm`
- **Categorical data**: Use `tab10` or `Set3`
- **Publication quality**: Avoid `jet` (not perceptually uniform)
- **Print-friendly**: Use sequential single-hue maps like `Blues`
