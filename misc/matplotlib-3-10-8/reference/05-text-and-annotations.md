# Text and Annotations

## Adding Text

### Basic Text

```python
ax.text(x, y, 'Label')
ax.text(x, y, 'Label', fontsize=12, fontweight='bold', color='red')
ax.text(x, y, 'Label', ha='center', va='bottom')  # Horizontal/vertical alignment
```

### Axis Labels and Titles

```python
ax.set_xlabel('X Label (units)', fontsize=12)
ax.set_ylabel('Y Label (units)', fontsize=12)
ax.set_title('Plot Title', fontsize=14, fontweight='bold')
ax.set_title('Subtitle', loc='left', fontsize=10, fontstyle='italic')
```

Title locations: `'center'` (default), `'left'`, `'right'`.

### Figure-Level Text

```python
fig.suptitle('Main Figure Title', fontsize=16, y=0.98)
fig.text(0.5, 0.02, 'Figure caption', ha='center')
```

## Text Properties

```python
ax.text(x, y, 'Text',
        fontsize=12,           # Size in points
        fontweight='bold',     # 'normal', 'bold', 'light', or numeric (100-900)
        fontstyle='italic',    # 'normal', 'italic', 'oblique'
        family='serif',        # 'serif', 'sans-serif', 'cursive', 'fantasy', 'monospace'
        color='darkblue',
        ha='center',           # Horizontal alignment: 'left', 'center', 'right'
        va='top',              # Vertical alignment: 'bottom', 'center', 'top'
        rotation=45,           # Degrees
        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5),
        )
```

## Annotations

### Basic Annotation

```python
ax.annotate('Peak',
            xy=(x_peak, y_peak),       # Point being annotated
            xytext=(x_text, y_text),   # Text position
            arrowprops=dict(arrowstyle='->', color='red'))
```

### Annotation Styles

```python
# Simple arrow
ax.annotate('Note', xy=(1, 1), xytext=(2, 3),
            arrowprops=dict(arrowstyle='->'))

# Curved arrow
ax.annotate('Note', xy=(1, 1), xytext=(2, 3),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3'))

# Fancy arrow
ax.annotate('Note', xy=(1, 1), xytext=(2, 3),
            arrowprops=dict(arrowstyle='fancy', color='blue', lw=2))

# No arrow (just text at offset)
ax.annotate('Label', xy=(1, 1), xytext=(0.5, 0.5),
            textcoords='offset points')
```

### Arrow Styles

- `->` — simple arrow
- `-|>` — arrow with bar
- `fancy` — fancy arrow
- `simple` — filled triangle
- `wedge` — wedge shape
- `->,head_length=10,head_width=5` — customizable

### Annotation Boxes

```python
ax.annotate('Important', xy=(1, 1), xytext=(2, 2),
            arrowprops=dict(arrowstyle='->'),
            bbox=dict(boxstyle='round,pad=0.5',
                      facecolor='lightyellow',
                      edgecolor='orange',
                      alpha=0.8))
```

Box styles: `'round'`, `'square'`, `'circle'`, `'larrow'`, `'rarrow'`, `'dbox'`.

## Mathematical Expressions (Mathtext)

Matplotlib supports a LaTeX-like syntax for mathematical expressions using the `$...$` delimiters:

```python
ax.set_title(r'$\alpha > \beta$')
ax.text(0.5, 0.5, r'$\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}$')
ax.set_xlabel(r'$\Delta x_i$ (m/s$^2$)')
```

### Common Mathtext Elements

```python
# Greek letters
r'$\alpha, \beta, \gamma, \delta, \epsilon, \theta, \lambda, \mu, \sigma, \omega$'

# Superscripts and subscripts
r'$x_i^2$, $E = mc^2$'

# Fractions
r'$\frac{a}{b}$'

# Operators
r'$\sum_{i=0}^{n}, \int_0^1, \prod, \infty, \pm, \times, \div$'

# Relations
r'$\leq, \geq, \neq, \approx, \sim, \propto$'

# Arrows
r'$\rightarrow, \leftarrow, \Rightarrow, \Leftrightarrow$'

# Brackets
r'$\left(\frac{a}{b}\right)$'
```

### Using Full LaTeX Rendering

For full LaTeX rendering (requires LaTeX installed):

```python
import matplotlib as mpl
mpl.rcParams['text.usetex'] = True
ax.set_title(r'$\sum_{i=1}^{N} x_i^2$')  # Rendered by system LaTeX
```

Or use the PGF backend for high-quality output:

```python
mpl.rcParams['text.usetex'] = False
mpl.rcParams['text.preamble'] = [r'\usepackage{amsmath}']
```

## Fonts

### Font Configuration

```python
import matplotlib.font_manager as fm

# List available fonts
for f in fm.fontManager.ttflist:
    print(f.name)

# Use a specific font
ax.text(x, y, 'Text', fontname='DejaVu Sans')
ax.text(x, y, 'Text', family='monospace')

# Load custom font
prop = fm.FontProperties(fname='/path/to/font.ttf')
ax.text(x, y, 'Custom Font Text', fontproperties=prop)
```

### Font Cache

Matplotlib maintains a font cache. To refresh it:

```python
fm._rebuild()  # Rebuild font cache
```

## Legends

```python
# Basic legend
ax.plot(x, y1, label='Series A')
ax.plot(x, y2, label='Series B')
ax.legend()

# Legend with location
ax.legend(loc='upper right')
ax.legend(loc='best')  # Automatic best position

# Legend outside the plot
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

# Custom legend
ax.legend(title='Data Series', fontsize=10, framealpha=0.9)

# Multiple legends
leg1 = ax.legend(handles=[line1], loc='upper right')
ax.add_artist(leg1)
ax.legend(handles=[line2, line3], loc='lower left')
```

Legend locations: `'best'`, `'upper right'`, `'upper left'`, `'lower left'`, `'lower right'`, `'right'`, `'center left'`, `'center right'`, `'lower center'`, `'upper center'`, `'center'`.

## Text Rotation and Alignment

```python
# Rotate x-axis tick labels
plt.xticks(rotation=45, ha='right')
fig.autofmt_xdate()  # Auto-rotate date labels

# Rotated text with proper alignment
ax.text(x, y, 'Rotated', rotation=30, rotation_mode='anchor',
        ha='center', va='center')
```
