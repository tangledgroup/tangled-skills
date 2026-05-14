# Axes and Layouts

## Introduction to Axes

An **Axes** is the primary plotting area within a Figure. It contains:
- Two or three **Axis** objects (x, y, and optionally z)
- Ticks and tick labels for data scaling
- A title (`set_title()`), x-label (`set_xlabel()`), and y-label (`set_ylabel()`)
- All the Artists representing plotted data

The Axes methods are the main interface for configuring plots: adding data, controlling axis scales and limits, adding labels, legends, and grids.

## Creating Multiple Axes

### Using subplots()

```python
# Single axes
fig, ax = plt.subplots()

# 2x2 grid — axs is a 2D array
fig, axs = plt.subplots(2, 2, figsize=(8, 6), layout='constrained')
axs[0, 0].plot(x, y1)
axs[1, 1].scatter(x, y2)

# Squeeze=False keeps single-row as 2D array
fig, axs = plt.subplots(1, 3, squeeze=False)
```

### Using subplot_mosaic()

For complex non-uniform layouts:

```python
grid = [
    ['heatmap', 'histogram_y'],
    ['histogram_x', 'histogram_y'],
]
fig, axs = plt.subplot_mosaic(grid, figsize=(8, 6), layout='constrained')
axs['heatmap'].imshow(data)
axs['histogram_x'].hist(data.flatten())
```

### Using GridSpec

For precise control over axis placement:

```python
import matplotlib.gridspec as gridspec

fig = plt.figure(layout='constrained')
gs = gridspec.GridSpec(2, 3, figure=fig)
ax1 = fig.add_subplot(gs[0, :])     # Top row, all columns
ax2 = fig.add_subplot(gs[1, :2])    # Bottom-left, 2 columns
ax3 = fig.add_subplot(gs[1, 2])     # Bottom-right
```

### Manual Axes Placement

```python
fig = plt.figure()
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])  # [left, bottom, width, height] in figure fraction
```

## Constrained Layout vs Tight Layout

**Constrained layout** (default in 3.10) — recommended approach:

```python
fig, axs = plt.subplots(2, 2, layout='constrained')
# Automatically adjusts spacing to prevent overlap
```

**Tight layout** (legacy, mildly discouraged):

```python
fig, axs = plt.subplots(2, 2)
fig.tight_layout()
# Must be called after all artists are added
```

Constrained layout is preferred because it:
- Works automatically during figure construction
- Handles nested layouts (subfigures, inset axes)
- Respects `set_in_layout(False)` for artists that should not affect spacing

## Twin Axes

For plots with dual y-axes:

```python
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()  # Share x-axis, independent y-axis

ax1.plot(x, y1, 'b-', label='Temperature')
ax1.set_ylabel('Temperature (°C)', color='blue')
ax2.plot(x, y2, 'r-', label='Pressure')
ax2.set_ylabel('Pressure (hPa)', color='red')
```

## Shared Axes

```python
# Share x-axis across subplots
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
ax1.plot(x, y1)
ax2.plot(x, y2)
# Only bottom axis shows ticks/labels

# Share both axes
fig, axs = plt.subplots(2, 2, sharex=True, sharey=True)
```

## Inset Axes

```python
fig, ax = plt.subplots()
ax.plot(x, y)

# Create inset
ax_inset = ax.inset_axes([0.6, 0.55, 0.35, 0.35])  # [x, y, w, h] in axes fraction
ax_inset.plot(x, y)
ax_inset.set_xlim(2, 4)
ax_inset.set_ylim(-1, 1)

# Show zoom indicator
ax.indicate_inset_zoom(ax_inset, edgecolor='red')
```

## Colorbar Placement

```python
# Standard colorbar
im = ax.imshow(data, cmap='viridis')
fig.colorbar(im, ax=ax)

# Horizontal colorbar
fig.colorbar(im, ax=ax, orientation='horizontal', pad=0.08)

# Dedicated axes for colorbar
fig, (ax, cax) = plt.subplots(1, 2, gridspec_kw={'width_ratios': [1, 0.05]})
im = ax.imshow(data)
fig.colorbar(im, cax=cax)
```

## Axis Configuration

### Setting Limits and Scales

```python
ax.set_xlim(0, 100)
ax.set_ylim(-1, 1)
ax.set_xscale('log')   # 'linear', 'log', 'symlog', 'logit'
ax.set_yscale('log')
ax.invert_xaxis()
```

### Ticks and Labels

```python
# Set tick positions
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_yticks(np.arange(0, 1.1, 0.2))

# Set tick labels
ax.set_xticklabels(['Low', 'Med', 'High', 'VHigh', 'Max'])

# Tick formatting
ax.ticklabel_format(style='scientific', axis='y')
ax.tick_params(axis='both', which='major', direction='inout', length=6)

# Minor ticks
ax.minorticks_on()
```

### Using Locators and Formatters

```python
from matplotlib.ticker import AutoLocator, FixedLocator, StrMethodFormatter, LogFormatterSciNotation
from matplotlib.dates import MonthLocator, DateFormatter
import matplotlib.dates as mdates

# Fixed tick positions
ax.xaxis.set_major_locator(FixedLocator([0, 25, 50, 75, 100]))

# Scientific notation
ax.yaxis.set_major_formatter(StrMethodFormatter('{x:.2e}'))

# Date formatting
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
```

## Aspect Ratio

```python
ax.set_aspect('equal')       # Equal scaling on both axes
ax.set_aspect(0.5)           # Custom aspect ratio
ax.set_box_aspect(1.0)       # Fixed box aspect regardless of data
ax.set_adjustable('datalim') # Adjust based on data limits
```

## Clearing and Resetting

```python
ax.clear()   # Remove all artists, reset axes
ax.cla()     # Alias for clear()
```
