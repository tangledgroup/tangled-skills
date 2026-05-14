# Plot Types

## Pairwise Data

### Line Plots

```python
ax.plot(x, y)                          # Basic line
ax.plot(x, y, 'r--', linewidth=2)      # Red dashed, thick
ax.plot(x, y1, label='A')              # With legend entry
ax.plot(x, y1, x, y2)                  # Multiple lines at once
```

Format string shorthand: `'[color][marker][linestyle]'` — e.g., `'ro--'` = red circles with dashed line.

### Scatter Plots

```python
ax.scatter(x, y)
ax.scatter(x, y, c=colors, s=sizes, cmap='viridis', alpha=0.6)
ax.scatter(x, y, c=z, vmin=0, vmax=100, cmap='plasma')  # Color by z-value
```

### Bar Charts

```python
# Vertical bars
ax.bar(categories, values, color='steelblue', edgecolor='black')

# Horizontal bars
ax.barh(categories, values, color='coral')

# Stacked bars
ax.bar(x, y1, label='A')
ax.bar(x, y2, bottom=y1, label='B')

# Grouped bars
width = 0.35
ax.bar(x - width/2, y1, width, label='A')
ax.bar(x + width/2, y2, width, label='B')

# Bar labels
bars = ax.bar(categories, values)
ax.bar_label(bars, fmt='%d')
```

### Stem Plots

```python
ax.stem(x, y, linefmt='b-', markerfmt='bo', basefmt='k-')
```

### Fill Between

```python
# Area between two curves
ax.fill_between(x, y1, y2, alpha=0.3)

# Confidence band
ax.fill_between(x, mean - std, mean + std, alpha=0.2, color='gray')

# Horizontal fill
ax.fill_betweenx(y, x1, x2, alpha=0.3)

# Simple polygon fill
ax.fill(x, y, alpha=0.3)
```

### Stackplot

```python
ax.stackplot(years, app1, app2, app3, labels=['A', 'B', 'C'], alpha=0.8)
```

### Stairs (Step Histogram)

```python
ax.stairs(values, edges)  # Step-style histogram outline
```

## Statistical Distributions

### Histograms

```python
ax.hist(data, bins=30, edgecolor='black')
ax.hist([data1, data2], bins=30, label=['A', 'B'], stacked=True)
ax.hist2d(x, y, bins=50, cmap='Blues')  # 2D histogram
```

### Box Plots

```python
ax.boxplot(data_list, labels=categories)
ax.boxplot(data, vert=False)                    # Horizontal
ax.boxplot(data, patch_artist=True, boxprops=dict(facecolor='lightblue'))
```

### Violin Plots

```python
parts = ax.violinplot(data, showmeans=True, showmedians=True)
for pc in parts['bodies']:
    pc.set_facecolor('lightblue')
    pc.set_edgecolor('black')
```

### Error Bars

```python
ax.errorbar(x, y, yerr=errors, fmt='o', capsize=5)
ax.errorbar(x, y, xerr=x_err, yerr=y_err, fmt='s')
```

### ECDF (Empirical Cumulative Distribution Function)

```python
result = ax.ecdf(data)
result.lines[0].set_label('Data')
```

### Event Plot

```python
ax.eventplot(positions, orientation='horizontal', lineoffsets=1)
```

### Hexbin

```python
ax.hexbin(x, y, C=values, gridsize=30, cmap='Blues', mincnt=1)
```

### Pie Charts

```python
labels = ['A', 'B', 'C', 'D']
sizes = [30, 25, 25, 20]
ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
```

## Gridded Data

### imshow

```python
im = ax.imshow(data, cmap='viridis', interpolation='nearest')
im = ax.imshow(data, extent=[x0, x1, y0, y1], origin='lower')
# Add colorbar
fig.colorbar(im, ax=ax)
```

### pcolormesh

```python
ax.pcolormesh(X, Y, Z, cmap='viridis', shading='auto')
ax.pcolormesh(x_edges, y_edges, Z, cmap='plasma', vmin=0, vmax=100)
```

### Contour Plots

```python
# Line contours
cs = ax.contour(X, Y, Z, levels=10, colors='black')
ax.clabel(cs, inline=True, fmt='%1.1f')

# Filled contours
cf = ax.contourf(X, Y, Z, levels=20, cmap='RdYlBu_r')
fig.colorbar(cf, ax=ax)
```

### Vector Fields

```python
# Quiver (arrows)
ax.quiver(X, Y, U, V, color='red')
ax.quiverkey(q, X=0.9, Y=1.02, U=1, label='1 m/s', labelpos='E')

# Streamplot (streamlines)
ax.streamplot(X, Y, U, V, density=2, colormap='viridis')

# Barbs (wind barbs)
ax.barbs(X, Y, U, V)
```

### Spy (Sparse Matrix Pattern)

```python
ax.spy(sparse_matrix, marker='o', markersize=2)
```

## Irregularly Gridded Data

```python
# Triangular mesh plots
ax.triplot(x, y, triangles, 'b-')
ax.tricontour(x, y, z, levels=10)
ax.tricontourf(x, y, z, cmap='viridis', levels=20)
ax.tripcolor(x, y, z, cmap='plasma', shading='flat')
```

## Spectral Analysis

```python
# Power spectral density
ax.psd(data, NFFT=256, Fs=2, linewidth=2)

# Cross-spectral density
ax.csd(data1, data2, NFFT=256, Fs=2)

# Coherence
ax.cohere(data1, data2, NFFT=256, Fs=2)

# Spectrogram
ax.specgram(data, NFFT=256, Fs=2, noverlap=128)

# Autocorrelation
ax.acorr(data, maxlags=40)
```

## Reference Lines and Shapes

```python
# Horizontal/vertical lines
ax.axhline(y=0, color='black', linestyle='--')
ax.axvline(x=5, color='red', linestyle=':')
ax.axline((0, 0), slope=1, color='gray')

# Horizontal/vertical spans
ax.axhspan(ymin=0, ymax=1, alpha=0.2, color='green')
ax.axvspan(xmin=2, xmax=4, alpha=0.2, color='blue')

# Vertical/horizontal lines at specific positions
ax.vlines(x=[1, 3, 5], ymin=0, ymax=10, colors='red')
ax.hlines(y=[2, 4, 6], xmin=0, xmax=10, colors='blue')
```

## Date/Time Plotting

```python
import matplotlib.dates as mdates

ax.plot(dates, values)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
fig.autofmt_xdate()  # Rotate and align date labels
```
