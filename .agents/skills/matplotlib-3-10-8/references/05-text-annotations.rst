# Text & Annotations Reference

## Text Rendering

### Basic Text
```python
ax.text(x, y, 'Hello')              # Text at data coordinates
ax.text(0.5, 0.5, 'Centered',       # Relative to axes
        transform=ax.transAxes)
ax.text(0.5, 0.95, 'Figure Title',  # Relative to figure
        transform=fig.transFigure,
        ha='center')
```

### Text Properties
```python
ax.text(x, y, 'text',
        fontsize=14,                   # Font size in points
        fontweight='bold',             # 'normal', 'bold', 'light', etc.
        fontstyle='italic',            # 'normal' or 'italic'
        family='serif',                # 'serif', 'sans-serif', 'monospace', etc.
        color='red',                   # Text color
        bbox=dict(facecolor='white',  # Bounding box
                  edgecolor='black',
                  alpha=0.8))
```

### Horizontal and Vertical Alignment
```python
ax.text(x, y, 'text',
        ha='center', va='center')     # Horizontal/vertical alignment
# ha options: 'left', 'right', 'center'
# va options: 'bottom', 'top', 'center', 'baseline', 'center_baseline'
```

### LaTeX Math Text
Matplotlib has built-in TeX equation rendering (does not require a full TeX installation):

```python
ax.text(x, y, r'$\alpha_i = \beta_i$', fontsize=16)
ax.set_xlabel(r'$t$ [s]', fontsize=14)
ax.set_title(r'$f(x) = e^{i\pi x}$')
```

Common LaTeX symbols: `$\alpha$', `$\beta$', `$\gamma$', `$\infty$', `$\pm$', `$\leq$', `$\geq$', `$\approx$', `$\sum$', `$\int$', `$\sqrt{}$', `$\frac{}{}$`.

For full TeX rendering (requires LaTeX installed):
```python
plt.rcParams['text.usetex'] = True    # Requires pdflatex
```

### Text Positioning Transforms
| Transform | Coordinate System |
|-----------|------------------|
| `ax.transData` | Data coordinates (default) |
| `ax.transAxes` | Axes fraction [0,1] x [0,1] |
| `fig.transFigure` | Figure fraction [0,1] x [0,1] |
| `ax.inverted_transData` | Reverse data transform |

## Annotations

### annotate() Method
```python
ax.annotate('annotation text',
            xy=(x, y),              # Point to annotate (arrow tip)
            xytext=(xx, yy),        # Text position
            xycoords='data',        # Coordinate system for xy
            textcoords='offset points',  # Coordinate system for text
            arrowprops=dict(arrowstyle='->', color='red'))
```

### Arrow Styles
```python
# Simple arrow
arrowprops = dict(arrowstyle='->', color='gray')

# Fancy arrow with connection style
arrowprops = dict(arrowstyle='->,head_width=0.4,head_length=0.8',
                  connectionstyle='arc3,rad=0.2', color='blue')

# Filled arrow
arrowprops = dict(arrowstyle='-|>', fc='red', ec='red')

# Connection styles
connectionstyle='arc3,rad=0'      # Straight line
connectionstyle='arc3,rad=0.5'    # Curved arc
connectionstyle='angle,angleA=90,angleB=0,rad=10'  # Angle-based
connectionstyle='angle3'          # Perpendicular angle
```

### Available Arrow Styles (arrowstyle)
`'-|>'`, `'->'`, `'-['`, `'-]'`, `'->|<'`, `<|-`, `|-|>`, `<->`, `<|-|>`, `fancy`, `simple`, `wedge`.

### Bounding Boxes for Annotations
```python
from matplotlib.patches import FancyBboxPatch, BoxStyle

# Fancy box around annotation
bbox_props = dict(boxstyle="round,pad=0.3", fc="cyan", ec="b", lw=2)
ax.annotate("Fancy Box", xy=(0.5, 0.5), xytext=(0.7, 0.7),
            bbox=bbox_props)

# Rounded box
bbox_props = dict(boxstyle="round4", fc="lightyellow", ec="orange")

# Crossed out text
ax.annotate('crossed', xy=(0.3, 0.3),
            bbox=dict(boxstyle='round', fc='white'),
            ma='center', family='monospace')
```

### Table in Axes
```python
from matplotlib.table import Table

table_data = [['A', 'B'], ['1', '2']]
ax_table = ax.table(cellText=table_data, loc='bottom',
                    cellLoc='center')
ax_table.set_fontsize(10)
ax_table.scale(1.5, 2)

# Color cells
for (i, j), val in np.ndenumerate(table_data):
    if val == 'B':
        ax_table[(i, j)].set_facecolor('lightblue')
```

### FancyArrowPatch
```python
from matplotlib.patches import FancyArrowPatch

arrow = FancyArrowPatch((0.1, 0.1), (0.9, 0.9),
                        arrowstyle='->', mutation_scale=20,
                        color='red', linewidth=2)
ax.add_patch(arrow)
```

### TextPath and Custom Fonts
```python
from matplotlib.path import Path
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch

tp = TextPath((0, 0), 'A', size=1, prop={'weight': 'bold'})
patch = PathPatch(tp, transform=ax.transData)
ax.add_patch(patch)
```

### MathText Symbols Reference
| Symbol | LaTeX | Result |
|--------|-------|--------|
| `$\alpha$` | `\alpha` | α |
| `$\beta$` | `\beta` | β |
| `$\infty$` | `\infty` | ∞ |
| `$\pm$` | `\pm` | ± |
| `$\leq$` | `\leq` | ≤ |
| `$\geq$` | `\geq` | ≥ |
| `$\sum_{i=0}^n$` | `\sum_{i=0}^n` | Σ |
| `$\int_0^1$` | `\int_0^1` | ∫ |
| `$\sqrt{x}$` | `\sqrt{x}` | √x |
| `$\frac{a}{b}$` | `\frac{a}{b}` | a/b |
| `$\vec{v}$` | `\vec{v}` | v⃗ |
