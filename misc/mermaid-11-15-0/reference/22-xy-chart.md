# XY Chart

## Contents
- Bar Charts
- Line Charts
- Axes Configuration
- Orientation
- Theme Variables
- Displaying Values on Bars (v11.14.0+)

## Overview

XY charts support bar and line charts with configurable axes.

```mermaid
xychart
    title "Sales Revenue"
    x-axis [jan, feb, mar, apr, may, jun]
    y-axis "Revenue ($)" 0 --> 10000
    bar [5000, 6000, 7500, 8200, 9500, 10500]
    line [5000, 6000, 7500, 8200, 9500, 10500]
```

## Bar Charts

```mermaid
xychart
    title "Monthly Sales"
    x-axis [Q1, Q2, Q3, Q4]
    y-axis 0 --> 100
    bar [65, 80, 72, 90]
```

## Line Charts

```mermaid
xychart
    title "Growth Trend"
    x-axis [2020, 2021, 2022, 2023]
    y-axis 0 --> 100
    line [20, 40, 65, 85]
```

Multiple series:

```mermaid
xychart
    x-axis [A, B, C]
    line [1, 2, 3]
    bar [2, 3, 4]
```

## Axes

### X-Axis

Categorical (text labels) or numeric range:

```
x-axis [cat1, cat2, cat3]    ' categorical
x-axis 0 --> 100             ' numeric range
```

### Y-Axis

Numeric range only:

```
y-axis "Label" 0 --> 100
y-axis "Label"        ' auto-range from data
```

Both axes are optional — Mermaid auto-generates ranges from data.

## Orientation

```mermaid
xychart horizontal
    x-axis [A, B, C]
    bar [10, 20, 30]
```

Valid: `vertical` (default), `horizontal`.

## Configuration

```mermaid
---
config:
  xyChart:
    width: 700
    height: 500
    chartOrientation: vertical
    plotReservedSpacePercent: 50
    showDataLabel: false
    showDataLabelOutsideBar: false
    xAxis:
      showLabel: true
      labelFontSize: 14
      showTitle: true
      titleFontSize: 16
      showTick: true
      tickLength: 5
      showAxisLine: true
    yAxis:
      showLabel: true
---
xychart
    bar [10, 20, 30]
```

## Displaying Values on Bars (v11.14.0+)

Show data labels inside or outside bars:

```mermaid
---
config:
  xyChart:
    showDataLabel: true
    showDataLabelOutsideBar: false
---
xychart
    x-axis [A, B, C]
    bar [10, 20, 30]
```

## Theme Variables

```mermaid
---
config:
  themeVariables:
    xyChart:
      titleColor: '#ff0000'
      titleFontSize: '24px'
      xAxisLabelColor: '#333'
      yAxisLabelColor: '#333'
      plotColor: '#000'
      axisColor: '#999'
---
xychart
    bar [10, 20, 30]
```
