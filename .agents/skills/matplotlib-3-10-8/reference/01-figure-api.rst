# Figure API Reference (matplotlib.figure)

## Figure Class

The `Figure` is the top-level container for all plot elements.

### Creation

```python
fig = plt.figure()                    # Default: 1 subplot, size [6.4, 4.8] inches
fig = plt.figure(figsize=(10, 6))     # Custom size in inches
fig = plt.figure(dpi=150)             # Custom dots per inch
fig, axes = plt.subplots(2, 3)        # Returns (Figure, Axes or array of Axes)
```

### Adding Axes and SubFigures

```python
# Add axes at specific position [left, bottom, width, height] in figure coords
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

# Add subplot with GridSpec
gs = fig.add_gridspec(3, 3)
ax = fig.add_subplot(gs[0, :-1])    # Top row spanning first two columns

# Use subplot_mosaic for named layouts
mosaic = """
AAAB
CCDD
"""
fig, axes = plt.subplot_mosaic(mosaic)
axes['A'].plot([1,2,3])

# SubFigures for nested layouts (v3.4+)
sfigs = fig.subfigures(2, 1)
ax = sfigs[0].add_subplot()
```

### Saving

```python
fig.savefig('output.png', dpi=300, bbox_inches='tight')
fig.savefig('output.pdf')            # Vector format
fig.savefig('output.svg')            # SVG vector format
fig.savefig('output.eps')            # Encapsulated PostScript
```

Key `savefig` parameters: `fname`, `dpi`, `format`, `bbox_inches`, `transparent`, `pad_inches`, `metadata`.

### Figure Geometry

```python
# Size in inches
w, h = fig.get_size_inches()
fig.set_size_inches(10, 6)
fig.set_figwidth(12)
fig.set_figheight(8)

# Dots per inch
fig.dpi = 150
fig.set_dpi(200)

# Layout engines (v3.3+)
fig.set_layout_engine('constrained')   # ConstrainedLayout (recommended)
fig.set_layout_engine('tight')         # tight_layout()
```

### Figure-level Elements

```python
# Figure-level text and titles
fig.suptitle('Main Title', fontsize=16, fontweight='bold')
fig.supxlabel('X Label', fontsize=12)
fig.supylabel('Y Label', fontsize=12)

# Align labels across subplots
fig.align_labels()
fig.align_xlabels()
fig.align_ylabels()
fig.align_titles()

# Auto-format x-axis dates
fig.autofmt_xdate(rotation=45, ha='right')

# Figure-level colorbar and legend
fig.colorbar(im, ax=axs)          # Colorbar spanning all axes
fig.legend(handles, labels)       # Figure-level legend
```

### Clearing

```python
fig.clear()                       # Remove all artists, keep figure
fig.clf()                         # Alias for clear()
```

### Interactive Events

```python
# Connect event handlers
cid = fig.canvas.mpl_connect('button_press_event', on_click)
cid = fig.canvas.mpl_connect('key_press_event', on_key)
cid = fig.canvas.mpl_connect('pick_event', on_pick)
fig.canvas.mpl_disconnect(cid)

# Get mouse coordinates
fig.ginput(3)                     # Click 3 points interactively

# Wait for button press
fig.waitforbuttonpress()
```

### SubFigure

A `SubFigure` is a logical figure inside a parent `Figure`, useful for nested layouts:

```python
parent_figs = fig.subfigures(2, 1)
ax = parent_figs[0].add_subplot()
# SubFigures share many Figure methods: add_subplot, subplots, etc.
```
