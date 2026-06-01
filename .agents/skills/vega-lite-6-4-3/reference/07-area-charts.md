# Area Charts

Area marks represent data as filled regions, often showing change over time. They support stacking, gradients, and ranged areas.

## Basic Syntax

```json
{
  "data": {"url": "data/unemployment-across-industries.json"},
  "mark": "area",
  "encoding": {
    "x": {"timeUnit": "yearmonth", "field": "date"},
    "y": {"aggregate": "sum", "field": "count"}
  }
}
```

## Area Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `orient` | string | `"vertical"` or `"horizontal"` |
| `baseline` | string \| number | Baseline of area (`"zero"` default, or explicit value) |
| `align` | number | Alignment within band (0-1) |
| `interpolate` | string | Line interpolation method (same as line marks) |
| `tension` | number | Cubic spline tension (0-1) |
| `line` | boolean \| object | Overlay a line on the area |
| `point` | boolean \| object | Overlay point markers |

## Chart Patterns

### Simple Area Chart

```json
{
  "data": {"url": "data/unemployment-across-industries.json"},
  "mark": "area",
  "encoding": {
    "x": {"timeUnit": "yearmonth", "field": "date"},
    "y": {"aggregate": "sum", "field": "count"}
  }
}
```

### Area with Overlay Line and Points

```json
{
  "mark": {"type": "area", "line": true, "point": true},
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"}
  }
}
```

### Gradient Fill

Set `color` to a gradient object:

```json
{
  "mark": {
    "type": "area",
    "line": {"color": "darkgreen"},
    "color": {
      "x1": 1, "y1": 1, "x2": 1, "y2": 0,
      "gradient": "linear",
      "stops": [
        {"offset": 0, "color": "white"},
        {"offset": 1, "color": "darkgreen"}
      ]
    }
  }
}
```

### Stacked Area Charts

Add `color` to create stacked areas:

```json
{
  "mark": "area",
  "encoding": {
    "x": {"timeUnit": "yearmonth", "field": "date"},
    "y": {"aggregate": "sum", "field": "count"},
    "color": {"field": "series"}
  }
}
```

### Normalized Stacked Area (100%)

```json
{
  "encoding": {
    "y": {"aggregate": "sum", "field": "count", "stack": "normalize"}
  }
}
```

### Streamgraph (Centered Stack)

```json
{
  "encoding": {
    "y": {"aggregate": "sum", "field": "count", "stack": "center"}
  }
}
```

### Ranged Areas (y2)

Use `y2` for ranged areas (e.g., temperature ranges, confidence intervals):

```json
{
  "mark": "area",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "ci0", "type": "quantitative"},
    "y2": {"field": "ci1"}
  }
}
```

### Density Areas

Use `density` transform with stacked areas:

```json
{
  "transform": [{"density": "value", "bandwidth": 20}],
  "mark": "area",
  "encoding": {
    "x": {"field": "value", "type": "quantitative"},
    "y": {"field": "density", "type": "quantitative"},
    "color": {"field": "series"}
  }
}
```

### Horizon Charts

Multi-colored area bands showing magnitude and direction.

### Vertical Areas

```json
{
  "mark": {"type": "area", "orient": "horizontal"},
  "encoding": {
    "x": {"field": "value", "type": "quantitative"},
    "y": {"field": "category", "type": "nominal"}
  }
}
```

### Area Config

```json
{
  "config": {
    "area": {"opacity": 0.7, "interpolate": "monotone"}
  }
}
```
