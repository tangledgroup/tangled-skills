# Line Charts

Line marks connect data points with a line, representing trajectories or change over time. One line mark represents multiple data elements as a single connected path.

## Basic Syntax

```json
{
  "data": {"url": "data/stocks.csv"},
  "transform": [{"filter": "datum.symbol==='GOOG'"}],
  "mark": "line",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"}
  }
}
```

## Line Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `orient` | string | `"vertical"` or `"horizontal"` |
| `interpolate` | string | Line interpolation method (see below) |
| `tension` | number | Cubic spline tension (0-1, default 0.7) |
| `point` | boolean \| object | Overlay point markers on the line |

### Interpolation Methods

| Value | Description |
|-------|-------------|
| `"linear"` (default) | Straight lines between points |
| `"linear-closed"` | Linear with closing segment |
| `"step"` / `"step-before"` / `"step-after"` | Step charts |
| `"basis"` / `"basis-open"` / `"basis-closed"` | B-spline interpolation |
| `"bundle"` | Bundled spline (use `tension` to control) |
| `"cardinal"` / `"cardinal-open"` / `"cardinal-closed"` | Cardinal spline |
| `"monotone"` | Monotone cubic spline (preserves monotonicity) |
| `"catmull-rom"` / `"-open"` / `"-closed"` | Catmull-Rom spline |
| `"natural"` | Natural cubic spline |

## Chart Patterns

### Simple Line Chart

Single line with temporal x and quantitative y:

```json
{
  "data": {"url": "data/stocks.csv"},
  "transform": [{"filter": "datum.symbol==='GOOG'"}],
  "mark": "line",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"}
  }
}
```

### Multi-Series Colored Lines

Add `color` to group data into separate line series:

```json
{
  "data": {"url": "data/stocks.csv"},
  "mark": "line",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"},
    "color": {"field": "symbol", "type": "nominal"}
  }
}
```

### Multi-Series with Detail (No Visual Encoding)

Use `detail` to group lines without mapping to visual properties:

```json
{
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"},
    "detail": {"field": "symbol"}
  }
}
```

### Varying Dash Patterns

Encode a field in `strokeDash` for multi-series with different dash styles:

```json
{
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"},
    "strokeDash": {"field": "symbol"}
  }
}
```

### Lines with Point Markers

Set `point: true` or a point definition object:

```json
{
  "mark": {"type": "line", "point": true}
}
```

Stroked (unfilled) points:

```json
{
  "mark": {"type": "line", "point": {"filled": false, "fill": "white"}}
}
```

### Imputing Missing Values

Use `impute` to fill gaps in time series:

```json
{
  "encoding": {
    "x": {"field": "a", "type": "quantitative"},
    "y": {"field": "b", "type": "quantitative", "impute": {"value": 0}},
    "color": {"field": "c", "type": "nominal"}
  }
}
```

Impute properties: `value`, `keyvals` (explicit key values), `method` (`"value"`, `"mean"`, `"max"`, `"min"`), `frame` (window bounds).

### Step Charts

```json
{
  "mark": {"type": "line", "interpolate": "step-after"}
}
```

Other step variants: `"step-before"`, `"step"`.

### Monotone Interpolation

Preserves monotonicity of data:

```json
{
  "mark": {"type": "line", "interpolate": "monotone"}
}
```

### Invalid Values (Breaks)

Data points with `null` or `NaN` cause breaks in the line:

```json
{
  "data": {"values": [
    {"x": 1, "y": 10}, {"x": 2, "y": 30},
    {"x": 3, "y": null},  // causes break
    {"x": 4, "y": 15}
  ]},
  "mark": "line",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"}
  }
}
```

To show isolated points, use `strokeCap: "square"` or overlay point marks.

### Connected Scatter Plots (Custom Path)

Use `order` channel to control path ordering:

```json
{
  "encoding": {
    "x": {"field": "Gas", "type": "quantitative"},
    "y": {"field": "Miles", "type": "quantitative"},
    "order": {"field": "Year", "type": "temporal"}
  }
}
```

### Slope Charts

Lines connecting two ordinal positions (e.g., before/after):

```json
{
  "mark": "line",
  "encoding": {
    "x": {"field": "period", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"},
    "color": {"field": "category"}
  }
}
```

### Bump Charts

Rankings over time — ordinal y-axis with lines:

```json
{
  "transform": [
    {"window": [{"op": "rank", "field": "value", "as": "rank"}], "groupBy": ["date"]}
  ],
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "rank", "type": "ordinal"},
    "color": {"field": "category"}
  }
}
```

### Domain Min/Max

Control visible range:

```json
{
  "encoding": {
    "x": {"field": "date", "scale": {"domainMin": "2019-01-01", "domainMax": "2020-12-31"}}
  }
}
```

### Line Config

```json
{
  "config": {
    "line": {"interpolate": "monotone", "tension": 0.5}
  }
}
```
