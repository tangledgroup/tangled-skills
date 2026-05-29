# Charts

## Contents
- Chart Creation Pattern
- Available Chart Types
- Data References and Categories
- Axes Configuration
- Secondary Axis
- Chart Layout and Styling
- Advanced: Gauge Charts

## Chart Creation Pattern

All charts follow the same pattern:

```python
from openpyxl import Workbook
from openpyxl.chart import BarChart, Reference

wb = Workbook()
ws = wb.active
for i in range(10):
    ws.append([i])

values = Reference(ws, min_col=1, min_row=1, max_col=1, max_row=10)
chart = BarChart()
chart.add_data(values)
ws.add_chart(chart, "E15")
wb.save("chart.xlsx")
```

Anchor `"E15"` sets the top-left corner. Default size is ~15 x 7.5 cm. Adjust with `chart.width` and `chart.height`.

## Available Chart Types

| Import | Type | Description |
|--------|------|-------------|
| `AreaChart`, `AreaChart3D` | Area | Filled area under line; `grouping="standard"`, `"stacked"`, `"percentStacked"` |
| `BarChart`, `BarChart3D` | Bar/Column | `chart.type = "col"` (vertical) or `"bar"` (horizontal); stacked: `overlap=100` |
| `BubbleChart` | Bubble | Third dimension via `zvalues`; multiple series |
| `LineChart`, `LineChart3D` | Line | Standard, stacked, percentStacked; `DateAxis` for date x-axis |
| `ScatterChart` | Scatter | X/Y values plotted against each other; use `Series(xvalues=...)` |
| `PieChart`, `PieChart3D`, `ProjectedPieChart` | Pie | Single series; `DataPoint(idx=0, explosion=20)` to slice out segments |
| `DoughnutChart` | Doughnut | Like pie with ring; supports multiple concentric rings |
| `RadarChart` | Radar | Standard or filled; compare aggregate values of multiple series |
| `StockChart` | Stock | High-low-close or open-high-low-close; data order matters (H/L/C or O/H/L/C) |
| `SurfaceChart`, `SurfaceChart3D` | Surface | 3D by default; 2D wireframe/contour via rotation and perspective settings |

## Data References and Categories

```python
from openpyxl.chart import Reference, Series

# Reference to a cell range
data = Reference(ws, min_col=2, min_row=1, max_row=7, max_col=3)
cats = Reference(ws, min_col=1, min_row=2, max_row=7)

# Add data with titles from first row
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)

# For scatter charts, use Series with xvalues
xvalues = Reference(ws, min_col=1, min_row=2, max_row=7)
yvalues = Reference(ws, min_col=2, min_row=1, max_row=7)
series = Series(yvalues, xvalues=xvalues, title_from_data=True)
chart.series.append(series)

# For bubble charts, add zvalues
size = Reference(ws, min_col=3, min_row=2, max_row=5)
series = Series(values=yvalues, xvalues=xvalues, zvalues=size, title="2013")
chart.series.append(series)
```

## Axes Configuration

### Titles and labels

```python
chart.title = "Sales by Quarter"
chart.y_axis.title = 'Units Sold'
chart.x_axis.title = 'Quarter'
chart.legend = None  # Hide legend
```

### Axis limits and scaling

```python
chart.x_axis.scaling.min = 0
chart.x_axis.scaling.max = 11
chart.y_axis.scaling.min = 0
chart.y_axis.scaling.max = 1.5

# Logarithmic scale
chart.y_axis.scaling.logBase = 10

# Reverse axis orientation
chart.y_axis.crosses = "max"
```

### Date axis

```python
from openpyxl.chart.axis import DateAxis

chart.x_axis = DateAxis()
```

## Secondary Axis

Create a second chart sharing the x-axis but with separate y-axis:

```python
from openpyxl.chart import BarChart, LineChart, Reference

c1 = BarChart()
v1 = Reference(ws, min_col=1, min_row=1, max_col=7)
c1.add_data(v1, titles_from_data=True, from_rows=True)
c1.y_axis.title = 'Series 1'
c1.x_axis.title = 'Days'

c2 = LineChart()
v2 = Reference(ws, min_col=1, min_row=2, max_col=7)
c2.add_data(v2, titles_from_data=True, from_rows=True)
c2.y_axis.axId = 200  # Different axis ID
c2.y_axis.title = "Series 2"

# Position y-axis on right
c1.y_axis.crosses = "max"

# Combine charts
c1 += c2
ws.add_chart(c1, "D4")
```

## Chart Layout and Styling

### Size and position

```python
chart.width = 400   # Width in pixels (approx)
chart.height = 250  # Height in pixels (approx)
ws.add_chart(chart, "E1")  # Anchor cell
```

### Legend position

```python
chart.legend.position = 'r'  # 'r', 'l', 't', 'b', 'tr' (right, left, top, bottom, top-right)
```

### Chart style and shape

```python
chart.style = 10    # Preset style number
chart.shape = 4     # Shape variant
```

### Data point styling

```python
from openpyxl.chart.series import DataPoint

# Explode first slice of pie chart
slice = DataPoint(idx=0, explosion=20)
chart.series[0].data_points = [slice]

# Style individual bar
from openpyxl.drawing.fill import PatternFillProperties, ColorChoice
dp = DataPoint(idx=2, graphically=PatternFillProperties(ColorChoice("FF0000")))
chart.series[0].data_points = [dp]
```

### Gridlines

```python
chart.y_axis.majorGridlines = None  # Remove gridlines
```

## Advanced: Gauge Charts

Gauge charts combine a `DoughnutChart` and `PieChart`:

- Doughnut with 4 slices (3 visible colors + 1 invisible half)
- Pie chart with 3 slices (first and third invisible, second acts as needle)
- Uses graphical properties on individual data points

See openpyxl documentation for full gauge chart example code.
