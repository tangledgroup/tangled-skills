# Customization

## rcParams

Runtime configuration (rcParams) controls default appearance of all Matplotlib elements. All settings are stored in `matplotlib.rcParams`.

### Setting rcParams at Runtime

```python
import matplotlib as mpl
import matplotlib.pyplot as plt

# Direct assignment
mpl.rcParams['lines.linewidth'] = 2
mpl.rcParams['lines.linestyle'] = '--'
mpl.rcParams['font.size'] = 12
mpl.rcParams['axes.titlesize'] = 14

# Using rc() for grouped settings
mpl.rc('lines', linewidth=2, linestyle='--')
mpl.rc('font', family='serif', size=12)
mpl.rc('axes', titlesize=14, labelsize=12)
```

### Changing the Color Cycle

```python
from cycler import cycler

# Custom color cycle
mpl.rcParams['axes.prop_cycle'] = cycler(color=['r', 'g', 'b', 'y'])

# Multiple properties
mpl.rcParams['axes.prop_cycle'] = cycler(
    color=['#1f77b4', '#ff7f0e', '#2ca02c'],
    linestyle=['-', '--', '-.']
)
```

### Temporary rc Settings

Using `rc_context` as a context manager:

```python
with mpl.rc_context({'lines.linewidth': 3, 'lines.linestyle': ':'}):
    plt.plot(data)
# Settings revert automatically after the block
```

As a decorator:

```python
@mpl.rc_context({'lines.linewidth': 3, 'lines.linestyle': '-'})
def plotting_function():
    plt.plot(data)
```

Restore defaults:

```python
mpl.rcdefaults()
```

## Style Sheets

Style sheets are portable rcParam configurations for visual appearance. They cannot set non-style params like `backend`.

### Built-in Styles

```python
# List available styles
import matplotlib.style as mpls
print(mpls.available)
# Common styles: 'default', 'classic', 'ggplot', 'grayscale',
# 'seaborn-v0_8', 'Solarize_Light2', '_mpl-gallery', '_mpl-gallery-nogrid'

# Apply a style
plt.style.use('seaborn-v0_8')

# Multiple styles (later takes precedence)
plt.style.use(['classic', 'ggplot'])

# Temporary style
with plt.style.context('ggplot'):
    plt.plot(data)
```

### Creating Custom Style Sheets

Create a file `mystyle.mplstyle`:

```
lines.linewidth: 2
lines.markeredgewidth: 0.5
axes.grid: True
axes.facecolor: #FAFAFA
figure.facecolor: white
font.size: 11
```

Then use it:

```python
plt.style.use('/path/to/mystyle.mplstyle')
```

Or register it:

```python
import matplotlib.style as mpls
mpls.core.create_library_from_dir('/path/to/styles/')
plt.style.use('mystyle')
```

## matplotlibrc File

The `matplotlibrc` file sets permanent defaults. Location order (first found wins):

1. Current working directory
2. `~/.config/matplotlib/matplotlibrc`
3. Matplotlib data directory

Example `matplotlibrc`:

```
backend : QtAgg
figure.figsize : 8, 6
figure.dpi : 100
lines.linewidth : 1.5
font.size : 12
axes.grid : True
savefig.dpi : 300
savefig.bbox : tight
```

## Key rcParams Groups

### Figure

```
figure.figsize : [6.4, 4.8]     # Default figure size in inches
figure.dpi : 100                # Dots per inch
figure.facecolor : white
figure.edgecolor : white
figure.max_open_warning : 20
```

### Axes

```
axes.facecolor : white
axes.edgecolor : black
axes.grid : False
axes.axisbelow : line           # Draw grid below 'line', 'patch', or 'line'
axes.labelsize : medium
axes.titlesize : large
axes.prop_cycle : cycler(...)   # Default property cycle
```

### Lines

```
lines.linewidth : 1.5
lines.linestyle : -
lines.color : C0                # First color in cycle
lines.marker : None
lines.markersize : 6
lines.markeredgewidth : 0.8
```

### Fonts

```
font.family : sans-serif
font.serif : DejaVu Serif, ...
font.sans-serif : DejaVu Sans, ...
font.monospace : DejaVu Sans Mono, ...
font.size : 10.0
```

### Savefig

```
savefig.dpi : figure            # Use figure DPI or explicit value
savefig.facecolor : auto        # Match figure facecolor
savefig.edgecolor : auto
savefig.format : png
savefig.bbox : standard
```

## Common Customization Patterns

### Publication-Ready Figure

```python
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams.update({
    'figure.figsize': (6.4, 4.8),
    'figure.dpi': 150,
    'font.size': 10,
    'axes.labelsize': 10,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'lines.linewidth': 1.5,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

fig, ax = plt.subplots(layout='constrained')
ax.plot(x, y)
fig.savefig('publication.png')
```

### Dark Theme

```python
mpl.rcParams.update({
    'figure.facecolor': '#1a1a2e',
    'axes.facecolor': '#16213e',
    'axes.edgecolor': '#0f3460',
    'axes.labelcolor': 'white',
    'xtick.color': 'white',
    'ytick.color': 'white',
    'text.color': 'white',
    'grid.color': '#0f3460',
})
```

### High Contrast for Presentations

```python
mpl.rcParams.update({
    'figure.figsize': (12, 7),
    'font.size': 16,
    'axes.labelsize': 18,
    'axes.titlesize': 20,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'lines.linewidth': 3,
    'lines.markersize': 10,
})
```
