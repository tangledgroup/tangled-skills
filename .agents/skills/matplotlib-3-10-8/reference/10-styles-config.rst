# Styles & Configuration Reference

## rcParams

### Overview

`matplotlib.rcParams` is a dictionary-like object that controls all default settings for matplotlib. Changes affect all subsequent plots.

```python
import matplotlib as mpl

# Access current value
print(mpl.rcParams['figure.figsize'])      # [5.5, 4.5]
print(mpl.rcParams['lines.linewidth'])     # 1.5

# Set a value
mpl.rcParams['lines.linewidth'] = 2.0
mpl.rcParams['axes.grid'] = True

# Update multiple at once
mpl.rcParams.update({
    'figure.figsize': (10, 6),
    'savefig.dpi': 300,
    'font.size': 12,
})

# Reset to defaults
mpl.rcParams.update(mpl.rcParamsDefault)
```

### Key rcParams Categories

#### Figure Settings (`figure.*`)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `figure.figsize` | `[5.5, 4.5]` | Figure size in inches |
| `figure.dpi` | `100` | Dots per inch |
| `figure.facecolor` | `'white'` | Background color |
| `figure.edgecolor` | `'white'` | Edge color |
| `figure.frameon` | `True` | Draw figure frame |
| `figure.max_open_warning` | `20` | Warning threshold for open figures |
| `figure.raise_window` | `True` | Raise window on show |

#### Axes Settings (`axes.*`)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `axes.facecolor` | `'white'` | Axes background color |
| `axes.edgecolor` | `'black'` | Axes border color |
| `axes.linewidth` | `0.8` | Border line width |
| `axes.grid` | `False` | Show grid |
| `axes.grid.axis` | `'both'` | Grid axis |
| `axes.axisbelow` | `'line'` | Grid below artists |
| `axes.titlesize` | `'large'` | Title font size |
| `axes.labelsize` | `'medium'` | Label font size |
| `axes.labelweight` | `'normal'` | Label font weight |
| `axes.linewidth` | `0.8` | Border width |
| `axes.spines.top` | `True` | Show top spine |
| `axes.spines.right` | `True` | Show right spine |
| `axes.spines.bottom` | `True` | Show bottom spine |
| `axes.spines.left` | `True` | Show left spine |
| `axes.prop_cycle` | tab10 colors | Default color cycle |
| `axes.xmargin` | `0.05` | X-axis margin fraction |
| `axes.ymargin` | `0.05` | Y-axis margin fraction |

#### Lines Settings (`lines.*`)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `lines.linewidth` | `1.5` | Line width in points |
| `lines.linestyle` | `'-'` | Line style: `-`, `--`, `-.`, `:` |
| `lines.color` | `'C0'` | Default line color |
| `lines.marker` | `None` | Marker type |
| `lines.markersize` | `6.0` | Marker size in points |
| `lines.markeredgewidth` | `1.0` | Marker edge width |

#### Text Settings (`text.*`)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `text.color` | `'black'` | Default text color |
| `text.hinting` | `'auto'` | Font hinting mode |
| `text.usetex` | `False` | Use external TeX renderer |

#### Font Settings (`font.*`)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `font.family` | `'sans-serif'` | Font family |
| `font.size` | `10.0` | Default font size in points |
| `font.serif` | `['DejaVu Serif']` | Serif font list |
| `font.sans-serif` | `['DejaVu Sans']` | Sans-serif font list |
| `font.monospace` | `['DejaVu Sans Mono']` | Monospace font list |
| `font.weight` | `'normal'` | Default font weight |
| `font.style` | `'normal'` | Default font style |

#### Savefig Settings (`savefig.*`)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `savefig.dpi` | `80` | Dots per inch for saving |
| `savefig.facecolor` | `'auto'` | Figure facecolor when saving |
| `savefig.edgecolor` | `'auto'` | Edge color when saving |
| `savefig.bbox` | `None` | Bounding box: `'tight'` or `'clip'` |
| `savefig.pad_inches` | `0.1` | Padding around tight bbox |
| `savefig.transparent` | `False` | Transparent background |
| `savefig.format` | `'png'` | Default output format |

#### Image Settings (`image.*`)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `image.cmap` | `'viridis'` | Default colormap |
| `image.interpolation` | `'nearest'` | Interpolation method |
| `image.aspect` | `'equal'` | Aspect ratio for images |
| `image.lut` | `256` | Lookup table size |

#### Legend Settings (`legend.*`)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `legend.loc` | `'best'` | Default legend location |
| `legend.frameon` | `True` | Draw legend frame |
| `legend.fancybox` | `True` | Rounded corners on frame |
| `legend.shadow` | `False` | Shadow behind legend |
| `legend.framealpha` | `0.8` | Frame transparency |
| `legend.edgecolor` | `'0.75'` | Frame edge color |

### Using rc_context for Temporary Settings

```python
import matplotlib as mpl

# Temporary settings using context manager
with mpl.rc_context({'lines.linewidth': 3, 'axes.facecolor': 'white'}):
    plt.plot(x, y)       # Uses linewidth=3
# Back to original settings outside context

# Or with nested contexts
with mpl.rc_context():
    mpl.rcParams['figure.figsize'] = (10, 6)
    with mpl.rc_context():
        mpl.rcParams['lines.linewidth'] = 2
        plt.plot(x, y)
```

### Using plt.rc() for Specific Categories

```python
# Set multiple params in one category
plt.rc('lines', linewidth=2.5, markersize=8)
plt.rc('font', family='serif', size=14)
plt.rc('axes', grid=True, labelsize=12)

# Reset a specific category
plt.rcdefaults()          # Reset all
plt.rcdefaults('lines')   # Reset only lines category
```

## Style Sheets

### Built-in Styles

```python
import matplotlib.pyplot as plt

# List available styles
print(plt.style.available)

# Common built-in styles:
plt.style.use('classic')       # Matplotlib 2.0 default
plt.style.use('seaborn-v0_8-whitegrid')
plt.style.use('ggplot')        # ggplot-like appearance
plt.style.use('bmh')           # Bayesian Methods for Hackers style
plt.style.use('dark_background')
plt.style.use('fivethirtyeight')
plt.style.use('grayscale')
plt.style.use('fast')          # Fast rendering (no antialiasing)
plt.style.use(['seaborn-v0_8-whitegrid', 'ggplot'])  # Combine styles
```

### Applying Styles

```python
# Global style (affects all subsequent plots)
plt.style.use('ggplot')

# Temporary style using context manager
with plt.style.context('dark_background'):
    plt.plot(x, y)

# Apply to a specific figure
fig = plt.figure()
with fig.autofmt_xdate():
    pass  # Use figure-specific settings
```

### Creating Custom Style Sheets

```python
# Save current state as a style sheet
plt.style.export('my_style.mplstyle')

# Or write manually (mplstyle format):
# lines.linewidth: 2.0
# axes.facecolor: white
# font.size: 12
```

### matplotlibrc File

The `matplotlibrc` file is the persistent configuration file. It can be located at:
- `~/.config/matplotlib/matplotlibrc` (Linux/macOS)
- `%USERPROFILE%\.matplotlib\matplotlibrc` (Windows)
- Or specified via `MPLCONFIGDIR` environment variable

```ini
# Example matplotlibrc
figure.figsize: 10, 6
figure.dpi: 150
savefig.dpi: 300
savefig.format: pdf
axes.grid: True
axes.grid.axis: y
lines.linewidth: 2.0
font.size: 14
text.usetex: False
image.cmap: viridis
```

Find the config directory:
```python
import matplotlib
print(matplotlib.get_configdir())
```

## Figure Saving

### savefig() Parameters

```python
fig.savefig('output.png',
            dpi=300,              # Resolution (dots per inch)
            format='png',         # Output format
            bbox_inches='tight',  # Crop to content
            pad_inches=0.1,       # Padding around tight bbox
            transparent=False,    # Transparent background
            facecolor='auto',     # Background color
            edgecolor='auto',     # Edge color
            metadata={            # PDF/PNG metadata
                'Author': 'Name',
                'Title': 'Plot Title'
            })
```

### Supported Output Formats

| Format | Extension | Type | Notes |
|--------|-----------|------|-------|
| PNG | `.png` | Raster | Default, supports transparency |
| SVG | `.svg` | Vector | Scalable, great for web |
| PDF | `.pdf` | Vector | Publication-ready |
| PS | `.ps` | Vector | PostScript |
| EPS | `.eps` | Vector | Encapsulated PostScript |
| JPG/JPEG | `.jpg` | Raster | No transparency |
| TIFF | `.tiff` | Raster | High-quality raster |
| RAW | `.raw` | Raster | Raw RGBA buffer |

### Multi-page PDF

```python
from matplotlib.backends.backend_pdf import PdfPages

with PdfPages('multipage.pdf') as pdf:
    fig1, ax1 = plt.subplots()
    ax1.plot([1,2,3])
    pdf.savefig(fig1)
    plt.close(fig1)

    fig2, ax2 = plt.subplots()
    ax2.bar(['A','B'], [1,2])
    pdf.savefig(fig2)
    plt.close(fig2)
```

### DPI and Resolution

```python
# Figure-level DPI
fig.set_dpi(150)

# Save at different resolution than display
plt.figure(dpi=100)       # Screen: 100 DPI
plt.savefig('print.png', dpi=300)  # Print: 300 DPI

# Override savefig DPI (uses figure DPI by default)
plt.savefig('output.png', dpi='figure')  # Use figure's DPI
```
