# Axes API Reference (matplotlib.axes)

## The Axes Class

The `Axes` represents one (sub-)plot in a figure. It contains the plotted data, axis ticks, labels, title, legend, etc. Its methods are the main interface for plotting.

### Basic Plotting Methods

#### Line Plots
```python
ax.plot(x, y)                              # Default: solid blue line
ax.plot(x, y, 'r--')                       # Red dashed line
ax.plot(x, y, 'bo-', label='data')         # Blue circles with solid line
ax.plot(x, y1, x, y2, x, y3)               # Multiple lines at once
```

#### Scatter Plots
```python
ax.scatter(x, y)                            # Default scatter
ax.scatter(x, y, c=z, cmap='viridis')       # Color by z values
ax.scatter(x, y, s=area, alpha=0.5)         # Size and transparency
ax.scatter(x, y, marker='^', c='red')       # Custom marker
```

#### Bar Charts
```python
ax.bar(x, height)                           # Vertical bars
ax.barh(y, width)                           # Horizontal bars
ax.bar(x, height, width=0.5, bottom=0)      # Custom width and position
ax.bar_label(container, labels=labels)      # Add labels on bars
```

#### Histograms
```python
ax.hist(data, bins=30, density=True)        # Histogram with normalization
ax.hist([data1, data2], bins=20, label=['A','B'])  # Multiple histograms
ax.stairs(values, edges)                     # Stair plot from bin edges
ax.hist2d(x, y, bins=50)                    # 2D histogram (heatmap)
```

#### Pie Charts
```python
ax.pie(sizes, labels=['A','B','C'], colors=['r','g','b'])
ax.pie(sizes, explode=[0.05, 0, 0], autopct='%1.1f%%')
```

#### Stem Plots
```python
ax.stem(x, y)                               # Stem plot
ax.stem(x, y, linefmt='C-', markerfmt='bo') # Custom formatting
```

#### Error Bars
```python
ax.errorbar(x, y, yerr=err, xerr=err2, fmt='o', capsize=5)
```

#### Box Plots
```python
ax.boxplot(data, notch=True, vert=True)
ax.bxp(boxstats, positions=[1, 2, 3])       # From pre-computed stats
```

#### Violin Plots
```python
vp = ax.violinplot(data, showmeans=True)
# Access violin parts: vp['bodies'], vp['cmins'], 'cmaxes', 'means'
```

### Specialized Plot Types

#### Contour Plots
```python
ax.contour(x, y, z)                         # Line contours
ax.contourf(x, y, z)                        # Filled contours
CS = ax.contour(X, Y, Z)
ax.clabel(CS, inline=True, fontsize=10)     # Add labels on contour lines
```

#### 2D Array Display
```python
ax.imshow(data)                              # Image display with colormap
ax.matshow(data)                             # Matrix-style (black background)
ax.pcolor(x, y, z)                           # Pseudocolor (edges at cell centers)
ax.pcolormesh(x, y, z)                       # Faster pcolor variant
ax.pcolorfast(x, y, z)                       # Fastest pseudocolor
ax.spy(Z, precision=0.1)                     # Visualize sparse matrix pattern
```

#### Filled Regions
```python
ax.fill(x, y)                                # Fill below curve to y=0
ax.fill_between(x, y1, y2)                  # Fill between two curves
ax.fill_betweenx(y, x1, x2, where=(x>0))    # Conditional fill
```

#### Vector Fields
```python
ax.quiver(x, y, u, v)                        # Arrow field
ax.quiverkey(Q, X, Y, U, label='5 m/s')     # Add quiver key/legend
ax.barbs(x, y, u, v)                         # Meteorological barbs
ax.streamplot(x, y, u, v)                    # Stream lines for 2D vector field
```

#### Spectral Analysis
```python
ax.psd(x, NFFT=256, Fs=2)                   # Power spectral density
ax.csd(x, y, NFFT=256)                      # Cross-spectral density
ax.magnitude_spectrum(x)                     # Magnitude spectrum
ax.angle_spectrum(x)                         # Angle spectrum
ax.phase_spectrum(x)                         # Phase spectrum
ax.specgram(x, NFFT=256, Fs=2)              # Spectrogram (time-frequency)
ax.acorr(x)                                  # Autocorrelation
ax.xcorr(x, y)                               # Cross-correlation
```

#### Other Plots
```python
ax.stackplot(x, y1, y2)                      # Stacked area plot
ax.hexbin(x, y, gridsize=50, cmap='YlOrRd')  # Hexagonal binning
ax.violinplot(data)                          # Violin plot
ax.eventplot(positions, orientation='vertical')
ax.scatter(x, y, c=colors, marker=markers)   # Categorical scatter
```

### Spans and Lines

```python
ax.axhline(y=0.5)                            # Horizontal line across axes
ax.axvline(x=0.5)                            # Vertical line across axes
ax.axhspan(ymin, ymax)                       # Horizontal span (shaded region)
ax.axvspan(xmin, xmax)                       # Vertical span
ax.axline((0, 0), slope=1)                   # Infinite line through point with slope
```

### Text and Annotations

```python
ax.text(x, y, 'text')                        # Text at data coordinates
ax.annotate('text', xy=(x, y), xytext=(xx, yy),
            arrowprops=dict(arrowstyle='->'))  # Annotated text with arrow
ax.table(cell_text, loc='bottom')            # Table in axes
ax.arrow(x, y, dx, dy)                       # Arrow from (x,y) by (dx,dy)
```

### Axis Configuration

#### Limits and Direction
```python
ax.set_xlim(0, 10)
ax.get_xlim()                                # Returns (min, max)
ax.set_ylim(-1, 1)
ax.invert_xaxis()                            # Reverse x-axis direction
ax.invert_yaxis()
ax.set_xbound(lower=0, upper=10)             # Set axis bounds (allows auto-scaling within)
```

#### Scales
```python
ax.set_xscale('linear')                      # Linear (default)
ax.set_xscale('log')                         # Logarithmic
ax.set_xscale('symlog', linthresh=1)         # Symmetric log
ax.set_xscale('logit')                       # Logit scale (0-1)
ax.set_yscale('log')
```

#### Ticks and Tick Labels
```python
# Manual tick placement
ax.set_xticks([0, 2, 4, 6, 8])
ax.set_xticklabels(['A', 'B', 'C', 'D', 'E'])
ax.set_yticks(ticks, labels=labels)

# Automatic tick locators and formatters
from matplotlib.ticker import (AutoLocator, AutoMinorLocator,
                                LogFormatterMathtext, FormatStrFormatter,
                                ScalarFormatter, FuncFormatter)
ax.xaxis.set_major_locator(AutoLocator())
ax.xaxis.set_minor_locator(AutoMinorLocator(5))
ax.yaxis.set_major_formatter(FormatStrFormatter('%.1f'))

# Custom formatter
ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:.2e}'))

# Tick appearance
ax.tick_params(axis='both', which='major', labelsize=12, direction='out')
ax.minorticks_on()
ax.minorticks_off()
```

#### Labels and Title
```python
ax.set_xlabel('X Label', fontsize=14, fontweight='bold')
ax.set_ylabel('Y Label')
ax.set_title('Plot Title', fontsize=16)
ax.get_title()                               # Get current title
```

#### Legend
```python
ax.legend(loc='upper right')                 # Auto-legend from labeled artists
ax.legend(handles, labels, loc='best')       # Manual legend
ax.legend(frameon=True, fancybox=True, shadow=True)
ax.get_legend().get_frame().set_alpha(0.8)   # Legend frame transparency
```

#### Grid
```python
ax.grid(True, which='major', axis='both')    # Enable grid
ax.grid(False, which='minor')                # Disable minor grid
ax.grid(axis='y')                            # Y-grid only
```

### Layout and Aspect

```python
# Autoscaling
ax.autoscale()                               # Auto-scale all axes
ax.autoscale_view(scalex=True, scaley=True)  # View limits only
ax.relim()                                   # Recompute data limits

# Margins
ax.margins(x=0.1, y=0.1)                     # Add margin around data
ax.set_xmargin(0.05)
ax.get_xmargin()

# Aspect ratio
ax.set_aspect('equal')                       # Equal data units
ax.set_aspect('auto')                        # Fill axes box
ax.set_box_aspect(1.5)                       # Box aspect ratio
ax.set_adjustable('datalim')                 # Adjust axes to fit data
```

### Property Cycle

```python
# Set default color/style cycle for new artists
ax.set_prop_cycle(color=['red', 'green', 'blue'] + plt.rcParams['axes.prop_cycler']['linestyle'])
ax.set_prop_cycle(['C0', 'C1', 'C2'], ['-', '--', '-.'])
```

### Axis Object Access

```python
ax.xaxis                                   # XAxis object
ax.yaxis                                   # YAxis object
ax.xaxis.get_major_locator()
ax.xaxis.get_major_formatter()
ax.xaxis.set_tick_params(labelrotation=45)  # Rotate x tick labels
```
