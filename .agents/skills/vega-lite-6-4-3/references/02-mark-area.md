# Area Mark Reference

The `area` mark renders filled area charts, useful for showing magnitude over a continuous dimension (typically time).

## Basic Area Chart

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Area chart of unemployment across industries.",
  "width": 300,
  "height": 200,
  "data": {"url": "data/unemployment-across-industries.json"},
  "mark": "area",
  "encoding": {
    "x": {"timeUnit": "yearmonth", "field": "date", "axis": {"format": "%Y"}},
    "y": {"aggregate": "sum", "field": "count", "title": "count"}
  }
}
```

## Stacked Area Chart

Add a `color` encoding to create stacked areas:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Stacked area chart by industry.",
  "data": {"url": "data/unemployment-across-industries.json"},
  "mark": "area",
  "encoding": {
    "x": {"timeUnit": "yearmonth", "field": "date"},
    "y": {"aggregate": "sum", "field": "count"},
    "color": {"field": "industry", "type": "nominal"}
  }
}
```

## Area with Line Overlay

Use mark object form to add a line on top of the area:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Area chart with line overlay.",
  "data": {"url": "data/unemployment-across-industries.json"},
  "mark": {"type": "area", "line": true},
  "encoding": {
    "x": {"timeUnit": "yearmonth", "field": "date"},
    "y": {"aggregate": "sum", "field": "count"}
  }
}
```

## Layered Area Chart (Non-Stacked)

Use `"stack": null` to overlay areas without stacking:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Layered (non-stacked) area chart.",
  "data": {"url": "data/unemployment-across-industries.json"},
  "mark": "area",
  "encoding": {
    "x": {"timeUnit": "yearmonth", "field": "date"},
    "y": {"aggregate": "sum", "field": "count"},
    "color": {"field": "industry", "type": "nominal"},
    "opacity": {"value": 0.3}
  },
  "config": {"area": {"stack": null}}
}
```

## Smooth Interpolation

Control the curve interpolation style:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Area chart with smooth interpolation.",
  "data": {"url": "data/unemployment-across-industries.json"},
  "mark": {"type": "area", "interpolate": "monotone"},
  "encoding": {
    "x": {"timeUnit": "yearmonth", "field": "date"},
    "y": {"aggregate": "sum", "field": "count"}
  }
}
```

## Gradient Fill

Use Vega's gradient syntax for filled areas:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Area chart with gradient fill.",
  "data": {"url": "data/unemployment-across-industries.json"},
  "mark": {
    "type": "area",
    "fill": {"gradient": "linear", "stops": [{"offset": 0, "color": "#4c78a8", "opacity": 0.8}, {"offset": 1, "color": "#4c78a8", "opacity": 0.1}]}
  },
  "encoding": {
    "x": {"timeUnit": "yearmonth", "field": "date"},
    "y": {"aggregate": "sum", "field": "count"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x` | Horizontal axis (typically temporal) |
| `y` | Vertical magnitude |
| `x2`, `y2` | Secondary position for ranged areas |
| `color` | Fill color (stacking groups when nominal) |
| `opacity` | Transparency for layered areas |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `interpolate` | `"linear"` | Curve interpolation (`monotone`, `basis`, `step`, etc.) |
| `line` | `false` | Overlay a line on the area boundary |
| `point` | `false` | Overlay points on data values |
| `orient` | auto | `"horizontal"` or `"vertical"` |

## Gotchas

- Area charts stack by default when a third encoding (like `color`) is present. Use `"stack": null` to disable.
- The `y` axis includes zero by default, which is usually correct for area charts.
- For smooth curves, use `interpolate: "monotone"` — it preserves monotonicity and avoids overshooting.
- Area marks are path-based (like line and trail), so they support `point` overlay for data point markers.
