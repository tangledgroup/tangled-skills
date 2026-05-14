# API Reference Summary

## pyplot Module (matplotlib.pyplot)

The `pyplot` module provides the state-machine interface. Most functions have equivalent Axes methods.

### Figure Management

```python
plt.figure(figsize=(8, 6), dpi=100)     # Create new figure
plt.subplots(2, 2, layout='constrained')  # Figure + grid of axes
plt.subplot_mosaic(grid)                  # Complex layout
plt.gcf()                                 # Get current figure
plt.clf()                                 # Clear current figure
plt.close()                               # Close figure(s)
plt.show(block=True)                      # Display figures
```

### Plotting Functions

```python
# Lines and markers
plt.plot(x, y)           # Line plot
plt.scatter(x, y)        # Scatter plot
plt.stem(x, y)           # Stem plot
plt.step(x, y)           # Step plot
plt.fill_between(x, y1, y2)   # Filled area

# Bar charts
plt.bar(x, height)       # Vertical bars
plt.barh(y, width)       # Horizontal bars

# Statistical
plt.hist(x, bins=30)     # Histogram
plt.boxplot(data)        # Box plot
plt.violinplot(data)     # Violin plot
plt.errorbar(x, y, yerr=err)  # Error bars
plt.hexbin(x, y)         # Hexagonal binning
plt.pie(x)               # Pie chart
plt.ecdf(x)              # Empirical CDF

# Gridded data
plt.imshow(Z)            # Image display
plt.contour(X, Y, Z)     # Contour lines
plt.contourf(X, Y, Z)    # Filled contours
plt.pcolormesh(X, Y, Z)  # Pseudocolor plot
plt.quiver(X, Y, U, V)   # Vector arrows
plt.streamplot(X, Y, U, V)  # Streamlines

# Text
plt.text(x, y, 'text')
plt.xlabel('label')
plt.ylabel('label')
plt.title('title')
plt.legend()
plt.annotate('text', xy=(x,y))

# Saving
plt.savefig('filename.png', dpi=150, bbox_inches='tight')
```

### Axis Configuration

```python
plt.xlim(0, 100)
plt.ylim(-1, 1)
plt.xscale('log')
plt.yscale('linear')
plt.xticks([0, 25, 50], ['A', 'B', 'C'])
plt.yticks(np.arange(0, 1.1, 0.2))
plt.grid(True, alpha=0.3)
```

## Axes Methods (matplotlib.axes.Axes)

The `Axes` class is the primary interface for most plotting operations.

### Data Plotting

- `plot()`, `scatter()`, `bar()`, `barh()`, `bar_label()`
- `hist()`, `hist2d()`, `boxplot()`, `violinplot()`
- `errorbar()`, `stem()`, `eventplot()`, `ecdf()`
- `pie()`, `stackplot()`, `stairs()`, `hexbin()`
- `imshow()`, `matshow()`, `pcolor()`, `pcolormesh()`
- `contour()`, `contourf()`, `clabel()`
- `tripcolor()`, `triplot()`, `tricontour()`, `tricontourf()`
- `quiver()`, `streamplot()`, `barbs()`
- `fill_between()`, `fill_betweenx()`, `fill()`
- `vlines()`, `hlines()`, `axhline()`, `axvline()`
- `axhspan()`, `axvspan()`, `axline()`
- `specgram()`, `psd()`, `cohre()`, `csd()`

### Text and Annotations

- `text()`, `annotate()`, `table()`
- `set_xlabel()`, `set_ylabel()`, `set_title()`
- `legend()`, `get_legend_handles_labels()`

### Axis Configuration

- `set_xlim()`, `set_ylim()`, `set_xscale()`, `set_yscale()`
- `set_xticks()`, `set_yticks()`, `set_xticklabels()`, `set_yticklabels()`
- `tick_params()`, `ticklabel_format()`, `locator_params()`
- `minorticks_on()`, `minorticks_off()`
- `set_aspect()`, `set_box_aspect()`
- `invert_xaxis()`, `invert_yaxis()`
- `margins()`, `relim()`, `autoscale()`

### Adding Artists

- `add_line()`, `add_patch()`, `add_collection()`, `add_image()`
- `add_artist()`, `add_table()`, `add_container()`
- `add_subplot()`, `inset_axes()`
- `twinx()`, `twiny()`, `sharex()`, `sharey()`
- `secondary_xaxis()`, `secondary_yaxis()`

### Layout and Position

- `set_position()`, `get_position()`
- `set_title()`, `label_outer()`

## Artist Base Class (matplotlib.artist.Artist)

All visible objects inherit from `Artist`. Common methods:

```python
artist.set_visible(True/False)
artist.set_alpha(0.5)
artist.set_zorder(10)           # Drawing order
artist.set_clip_on(True)
artist.set_clip_path(path)
artist.set_transform(transform)
artist.set_label('name')        # For legend entries
artist.remove()                 # Remove from figure
artist.get_window_extent()      # Bounding box in display coords
```

## Figure Methods (matplotlib.figure.Figure)

```python
fig.add_subplot(2, 2, 1)        # Add axes at position
fig.subplots(2, 2)              # Grid of axes
fig.subplot_mosaic(grid)        # Complex layout
fig.add_axes([0.1, 0.1, 0.8, 0.8])  # Manual axes placement
fig.colorbar(im, ax=ax)         # Add colorbar
fig.suptitle('Title')           # Figure-level title
fig.text(0.5, 0.5, 'Text')      # Figure-level text
fig.savefig('plot.png')         # Save to file
fig.canvas.draw()               # Force redraw
```

## Axis Locators and Formatters (matplotlib.ticker)

### Locators (determine tick positions)

- `AutoLocator()` — automatic (default)
- `FixedLocator([0, 25, 50])` — fixed positions
- `MultipleLocator(5)` — every 5 units
- `MaxNLocator(nbins=10)` — max ~10 ticks
- `LogLocator()` — for log scales
- `LinearLocator(numticks=10)` — evenly spaced
- `NullLocator()` — no ticks

### Formatters (determine tick labels)

- `StrMethodFormatter('{x:.2f}')` — Python format string
- `FormatStrFormatter('%.2f')` — printf-style
- `FuncFormatter(func)` — custom function
- `LogFormatterSciNotation()` — scientific for log scales
- `NullFormatter()` — no labels
- `FixedFormatter(['A', 'B', 'C'])` — fixed labels

## Patches (matplotlib.patches)

```python
from matplotlib.patches import Rectangle, Circle, Polygon, Ellipse, FancyBboxPatch, Wedge, Arrow

rect = Rectangle((0, 0), 1, 1, facecolor='blue', alpha=0.5)
circle = Circle((0.5, 0.5), 0.3, facecolor='red')
arrow = Arrow(0, 0, 1, 1, width=0.2, facecolor='green')
ax.add_patch(rect)
```

## Collections (matplotlib.collections)

- `PolyCollection` — multiple polygons (used by scatter, pcolormesh)
- `LineCollection` — multiple line segments
- `PatchCollection` — multiple patches
- `PathCollection` — scatter plot backend

## Colormap API (matplotlib.colors)

```python
from matplotlib.colors import Normalize, LogNorm, SymLogNorm, BoundaryNorm, TwoSlopeNorm
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, to_rgba, to_hex
from matplotlib.colormaps import get_cmap, register_cmap

# Convert colors
rgba = to_rgba('red')
hex_str = to_hex((0.5, 0.5, 0.5))
```

## Event Handling (matplotlib.backend_bases)

Connect callbacks to figure events:

```python
def on_click(event):
    if event.inaxes is not None:
        print(f'Click at data coords: ({event.xdata:.2f}, {event.ydata:.2f})')

fig.canvas.mpl_connect('button_press_event', on_click)
```

Common events: `'button_press_event'`, `'button_release_event'`, `'motion_notify_event'`, `'key_press_event'`, `'key_release_event'`, `'resize_event'`, `'draw_event'`, `'close_event'`.
