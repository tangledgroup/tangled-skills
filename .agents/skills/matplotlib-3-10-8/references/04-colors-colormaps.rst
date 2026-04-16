# Colors & Colormaps Reference

## Color Specification

Colors in matplotlib can be specified in multiple ways:

### Named Colors
```python
ax.plot(x, 'red')                    # Full name
ax.plot(x, 'r')                      # Short name
ax.plot(x, 'C0')                     # Cycle color (default blue)
ax.plot(x, 'C1')                     # Second cycle color (orange)
```

Available named colors include: `blue`, `green`, `red`, `cyan`, `magenta`, `yellow`, `black`, `white`, plus CSS color names (`salmon`, `coral`, `steelblue`).

### RGB / RGBA Tuples
```python
ax.plot(x, (0.2, 0.4, 0.6))          # RGB in [0, 1] range
ax.plot(x, (0.2, 0.4, 0.6, 0.8))     # RGBA with alpha
```

### Hex Strings
```python
ax.plot(x, '#FF5733')                # Hex color
ax.plot(x, '#FF573380')              # With alpha (RRGGBBAA)
```

### Color Cycle
Matplotlib uses a default color cycle: `['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']` (tab10).

Access cycle colors: `plt.rcParams['axes.prop_cycler']`.

## Colormaps

### Getting Colormaps
```python
# By name
cmap = plt.get_cmap('viridis')
cmap = plt.cm.viridis                # Same thing

# From registry
all_cmaps = plt.colormaps            # dict of all registered colormaps
cmap = all_cmaps['plasma']

# Listed colormap (can sample N colors)
colors = cmap(5)                     # Returns 5 RGBA values
colors = cmap(np.linspace(0, 1, 10)) # Sample at specific positions
```

### Built-in Colormap Categories

**Sequential (perceptually uniform):**
- `viridis` — Default colormap (v3.2+)
- `plasma`
- `inferno`
- `magma`
- `cividis` — Colorblind-friendly alternative to viridis

**Diverging:**
- `coolwarm`
- `seismic`
- `RdBu_r`, `bwr`, `PiYG`
- `Spectral` (legacy, avoid for new code)

**Cyclic / Qualitative:**
- `twilight` — Cyclic
- `hsv` — Rainbow (qualitative, not perceptually uniform)
- `nipy_spectral`
- `gist_ncar`

**Tab colors (discrete):**
- `tab10`, `tab20`, `tab20b`, `tab20c`

**Matlab-like:**
- `jet` — Legacy, not recommended for new plots
- `hot`, `cool`, `spring`, `summer`, `autumn`, `winter`, `copper`, `pink`, `prism`

### Colormap Registration and Customization

```python
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

# Create custom colormap from colors
custom_cmap = ListedColormap(['red', 'green', 'blue'], name='custom')
plt.register_cmap(name='my_cmap', cmap=custom_cmap)

# Create from color transitions
cmap = LinearSegmentedColormap.from_list('my_cmap', ['white', 'blue', 'black'])

# Reverse a colormap
reversed_cmap = plt.cm.viridis_r
```

### Color Normalization

```python
from matplotlib.colors import Normalize, LogNorm, SymLogNorm, PowerNorm

# Linear normalization (default: maps data min/max to 0/1)
norm = Normalize(vmin=0, vmax=100)

# Logarithmic normalization
norm = LogNorm(vmin=1, vmax=1000)

# Symmetric log (good for data crossing zero)
norm = SymLogNorm(linthresh=0.1, vmin=-100, vmax=100)

# Power law normalization
norm = PowerNorm(gamma=0.5, vmin=0, vmax=100)

# Apply to plotting
im = ax.imshow(data, cmap='viridis', norm=LogNorm())
```

### Colormaps in Plotting Functions

```python
# imshow
ax.imshow(data, cmap='plasma')
ax.imshow(data, cmap='plasma', norm=LogNorm())
im = ax.imshow(data)
fig.colorbar(im, ax=ax, label='Intensity')

# contour / contourf
ax.contour(X, Y, Z, levels=20, cmap='viridis')
CS = ax.contour(X, Y, Z)
ax.clabel(CS, inline=True, fontsize=8)

# pcolormesh
ax.pcolormesh(x, y, z, cmap='coolwarm', shading='auto')

# scatter
ax.scatter(x, y, c=z, cmap='viridis', norm=LogNorm())
```

### Colorbar

```python
im = ax.imshow(data, cmap='viridis')
cbar = fig.colorbar(im, ax=ax)                    # Vertical colorbar
cbar = fig.colorbar(im, ax=ax, orientation='h')  # Horizontal
cbar.set_label('Intensity')                       # Label colorbar
fig.colorbar(im, ax=ax, shrink=0.8)               # Shrink size

# Multiple colorbars
sm1 = ax.scatter(x1, y1, c=z1, cmap='viridis')
sm2 = ax.scatter(x2, y2, c=z2, cmap='plasma')
fig.colorbar(sm1, ax=ax, location='left')
fig.colorbar(sm2, ax=ax, location='right')
```

### Setting Default Colormap

```python
# Set globally
plt.rcParams['image.cmap'] = 'viridis'

# Set for current figure
plt.set_cmap('plasma')
```
