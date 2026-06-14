# Line Mark Reference

The `line` mark renders connected line segments, ideal for time series and trend visualization. Lines are sorted by the x-axis value by default.

## Basic Line Chart

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Google stock price over time.",
  "data": {"url": "data/stocks.csv"},
  "transform": [{"filter": "datum.symbol==='GOOG'"}],
  "mark": "line",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"}
  }
}
```

## Multi-Line Chart

Add a `color` encoding to show multiple series:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Stock prices of multiple companies.",
  "data": {"url": "data/stocks.csv"},
  "mark": "line",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"},
    "color": {"field": "symbol", "type": "nominal"}
  }
}
```

## Line with Points

Use mark object form to overlay data points:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Line chart with data points.",
  "data": {"url": "data/stocks.csv"},
  "transform": [{"filter": "datum.symbol==='GOOG'"}],
  "mark": {"type": "line", "point": true},
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"}
  }
}
```

## Smooth Interpolation

Control curve style:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Smooth line chart.",
  "data": {"url": "data/stocks.csv"},
  "transform": [{"filter": "datum.symbol==='GOOG'"}],
  "mark": {"type": "line", "interpolate": "monotone"},
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"}
  }
}
```

## Line with Reference Rule

Layer a horizontal reference line:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Line chart with reference line.",
  "data": {"url": "data/stocks.csv"},
  "transform": [{"filter": "datum.symbol==='GOOG'"}],
  "layer": [
    {
      "mark": "line",
      "encoding": {
        "x": {"field": "date", "type": "temporal"},
        "y": {"field": "price", "type": "quantitative"}
      }
    },
    {
      "mark": {"type": "rule", "color": "red"},
      "encoding": {
        "y": {"aggregate": "mean", "field": "price"}
      }
    }
  ]
}
```

## Step Interpolation

For data that changes at discrete intervals:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Step line chart.",
  "data": {"url": "data/stocks.csv"},
  "transform": [{"filter": "datum.symbol==='GOOG'"}],
  "mark": {"type": "line", "interpolate": "step-before"},
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position coordinates (line connects points sorted by x) |
| `color` | Line color (separate lines per group) |
| `opacity` | Transparency |
| `size` | Line width in pixels |
| `detail` | Splits into separate paths without visual encoding |
| `order` | Drawing order of overlapping lines |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `interpolate` | `"linear"` | Curve style (`monotone`, `basis`, `step-before`, `step-after`, `step-center`) |
| `point` | `false` | Overlay point markers on data values |
| `tension` | `0` | Catmull-Rom spline tension (0 = fully interpolated, 1 = no interpolation) |
| `orient` | auto | `"horizontal"` or `"vertical"` |

## Gotchas

- Lines are sorted by x-axis value. Use `trail` mark if you need to preserve the original data order.
- When multiple groups share the same `x` value, each group gets its own line (via `color` encoding).
- The `point` property adds transparent points by default for tooltip/selection interaction. Use `{"point": {}}` for visible filled points.
- For time series with gaps, use `timeUnit` transforms to aggregate to consistent intervals.
- Line marks are path-based (like area and trail), so they support the same interpolation properties.
