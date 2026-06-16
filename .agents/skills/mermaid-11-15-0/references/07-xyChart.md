# XY Charts

Line, bar, area, and scatter charts with configurable axes.

## Syntax

```
xychart beta           %% "beta" keyword required
    title "Title"      %% Optional
    x-axis [Jan, Feb, Mar, Apr]
    y-axis "Values" 0 --> 100
    bar [10, 25, 45, 80]
    line [10, 25, 45, 80]
```

## Chart types

| Type | Syntax | Description |
| --- | --- | --- |
| Line | `line [...]` | Line chart |
| Bar | `bar [...]` | Bar chart |
| Area | `area [...]` | Area chart |
| Scatter | `scatter [...]` | Scatter plot |

Multiple chart types can be combined in one diagram.

## Axis configuration

### X-axis (categorical)

```
x-axis [Jan, Feb, Mar, Apr]
x-axis "Months" [Jan, Feb, Mar]
```

Accepts string array labels. Optional title.

### Y-axis (numerical range)

```
y-axis "Values" 0 --> 100
y-axis 0 --> 100
y-axis "Score" 0.0 --> 1.0
```

Format: `"title" min --> max`. Title optional. Supports decimals.

## Multiple data series

```
xychart beta
    x-axis [Q1, Q2, Q3, Q4]
    y-axis "Revenue" 0 --> 1000
    line [100, 300, 500, 800]
    bar [80, 250, 450, 700]
```

Each chart type keyword adds a new series.

## Legend (v11+)

Name a series by adding a quoted label to include it in the legend. Unnamed plots are omitted.

```
xychart beta
    x-axis [Jan, Feb, Mar]
    y-axis "Values" 0 --> 100
    line "Actual" [10, 50, 80]
    bar "Target" [20, 40, 60]
```

## Configuration

Under the `xyChart` config key:

| Option                  | Type    | Default     | Description                        |
|-------------------------|---------|-------------|------------------------------------|
| `width`                 | number  | `700`       | Chart width in pixels              |
| `height`                | number  | `500`       | Chart height in pixels             |
| `chartOrientation`      | string  | `vertical`  | `horizontal` or `vertical`         |
| `showLegend`            | boolean | `true`      | Show legend for named plots        |
| `legendFontSize`        | number  | `14`        | Legend font size                   |
| `showDataLabel`         | boolean | `false`     | Show value inside bars             |
| `showDataLabelOutsideBar` | boolean | `false`   | Show bar values outside the bar    |
| `plotReservedSpacePercent` | number  | `50`      | Minimum plot space (%)             |

### Axis config (`xAxis`, `yAxis`)

| Option        | Type    | Default | Description                        |
|---------------|---------|---------|------------------------------------|
| `showLabel`   | boolean | `true`  | Show tick values                   |
| `labelFontSize` | number  | `14`   | Label font size                    |
| `showTitle`   | boolean | `true`  | Show axis title                    |
| `titleFontSize` | number  | `16`   | Axis title font size               |
| `showTick`    | boolean | `true`  | Show tick marks                    |
| `tickLength`  | number  | `5`     | Tick length                        |
| `labelRotation` | number  | `0`    | Label rotation degrees (x-axis)    |

### Theme variables (`xyChart`)

| Variable           | Description                |
|--------------------|----------------------------|
| `backgroundColor`  | Chart background color     |
| `titleColor`       | Title text color           |
| `dataLabelColor`   | Data label color           |
| `legendTextColor`  | Legend text color          |
| `xAxisLabelColor`  | X-axis label color         |
| `xAxisTitleColor`  | X-axis title color         |
| `xAxisTickColor`   | X-axis tick color          |
| `xAxisLineColor`   | X-axis line color          |
| `yAxisLabelColor`  | Y-axis label color         |
| `yAxisTitleColor`  | Y-axis title color         |
| `yAxisTickColor`   | Y-axis tick color          |
| `yAxisLineColor`   | Y-axis line color          |
| `plotColorPalette` | Comma-separated colors     |

```yaml
---
config:
  xyChart:
    showDataLabel: true
    chartOrientation: horizontal
  themeVariables:
    xyChart:
      plotColorPalette: "#4e79a7,#f28e2b,#e15759"
---
```
