# Pyplot API Reference (matplotlib.pyplot)

## Overview

`pyplot` is a state-based interface to matplotlib, providing a MATLAB-like way of plotting. It maintains a "current figure" and "current axes" that are implicitly used by stateful functions.

The explicit object-oriented API (`fig, ax = plt.subplots()`) is recommended for complex plots, but `pyplot` remains the standard for quick exploration and simple scripts.

### Quick Start (Pyplot)

```python
import matplotlib.pyplot as plt
import numpy as np

x = np.arange(0, 5, 0.1)
y = np.sin(x)
plt.plot(x, y)
plt.show()
```

### Key Pyplot Functions by Category

#### Figure Management
| Function | Description |
|----------|-------------|
| `plt.figure()` | Create new figure (or get current) |
| `plt.gcf()` | Get current figure |
| `plt.gca()` | Get current axes |
| `plt.subplots(nrows, ncols)` | Create figure with subplots |
| `plt.subplot_mosaic(mosaic)` | Named subplot layout |
| `plt.subplot2grid(shape, loc)` | Subplot at grid position |
| `plt.close(fig)` | Close figure |
| `plt.clf()` | Clear current figure |
| `plt.cla()` | Clear current axes |

#### Adding Data (Plotting)
| Function | Description |
|----------|-------------|
| `plt.plot(x, y)` | Line plot |
| `plt.scatter(x, y)` | Scatter plot |
| `plt.bar(x, height)` | Bar chart |
| `plt.hist(data, bins)` | Histogram |
| `plt.pie(sizes)` | Pie chart |
| `plt.contour(X, Y, Z)` / `contourf` | Contour plots |
| `plt.imshow(data)` | Image display |
| `plt.pcolormesh(x, y, z)` | Pseudocolor mesh |
| `plt.hexbin(x, y)` | Hexagonal binning |
| `plt.fill_between(x, y1, y2)` | Filled region |
| `plt.errorbar(x, y, yerr)` | Error bars |
| `plt.boxplot(data)` | Box plot |
| `plt.violinplot(data)` | Violin plot |
| `plt.stem(y)` | Stem plot |
| `plt.barbs(x, y, u, v)` | Meteorological barbs |
| `plt.streamplot(x, y, u, v)` | Stream lines |
| `plt.quiver(x, y, u, v)` | Arrow field |
| `plt.specgram(x)` | Spectrogram |
| `plt.acorr(x)` | Autocorrelation |

#### Axis Configuration
| Function | Description |
|----------|-------------|
| `plt.xlabel(label)` / `plt.ylabel()` | Axis labels |
| `plt.title(title)` | Plot title |
| `plt.xlim(lo, hi)` / `plt.ylim()` | Axis limits |
| `plt.xticks(ticks, labels)` / `plt.yticks()` | Tick positions/labels |
| `plt.xscale('log')` / `plt.yscale()` | Axis scales |
| `plt.grid(True)` | Grid lines |
| `plt.legend(loc='best')` | Legend |
| `plt.colorbar(im)` | Colorbar for image/contour |
| `plt.autoscale()` | Auto-scale axes |
| `plt.tick_params(**kwargs)` | Tick appearance |

#### Layout
| Function | Description |
|----------|-------------|
| `plt.tight_layout()` | Auto-adjust subplot spacing |
| `plt.subplots_adjust(**kw)` | Manual subplot adjustment |
| `plt.suptitle(title)` | Figure-level title |
| `plt.subplot_tool(fig)` | Interactive subplot editor |

#### Configuration
| Function | Description |
|----------|-------------|
| `plt.style.use('ggplot')` | Apply style sheet |
| `plt.rc('lines', linewidth=2)` | Set rc parameter |
| `plt.rc_context({...})` | Temporary rc settings context |
| `plt.rcdefaults()` | Reset all rc parameters |

#### Output
| Function | Description |
|----------|-------------|
| `plt.savefig('file.png')` | Save figure to file |
| `plt.show()` | Display figure interactively |
| `plt.pause(interval)` | Pause for animation |
| `plt.ion()` / `plt.ioff()` | Toggle interactive mode |

### Colormaps and Colors

```python
# Get colormap
cmap = plt.get_cmap('viridis')
colors = plt.cm.viridis(np.linspace(0, 1, 10))

# Set default colormap
plt.set_cmap('plasma')

# Built-in color shortcut functions (set colormap for current image)
plt.viridis()   # Equivalent to plt.set_cmap('viridis')
plt.plasma()
plt.inferno()
plt.magma()
plt.cividis()
plt.jet()
plt.hsv()
plt.cool()
plt.hot()

# Available colormaps registry
all_cmaps = plt.colormaps  # dict of all registered colormaps

# Color sequences (for cycling)
colors = plt.color_sequences  # Named color palettes
```

### Interactive Mode

```python
plt.ion()                          # Enable interactive mode
fig, ax = plt.subplots()
for i in range(10):
    ax.plot(range(i), np.random.rand(i))
    fig.canvas.draw()
    fig.canvas.flush_events()
plt.ioff()                         # Disable interactive mode

# Or use plt.pause for animation
for i in range(10):
    plt.plot(range(i), 'o-')
    plt.pause(0.1)
```

### XKCD Mode

```python
with plt.xkcd():
    plt.plot([1, 2, 3], [1, 4, 2])
    plt.title('Hand-drawn style')
    plt.show()
```

### Connecting Events

```python
def on_click(event):
    print(f'Clicked at {event.xdata}, {event.ydata}')

cid = plt.connect('button_press_event', on_click)
plt.disconnect(cid)
```
