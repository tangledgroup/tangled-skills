# Arc Charts

Arc marks are circular arcs defined by a center point plus angular and radial extents. They are used for pie charts, donut charts, and other radial visualizations.

## Basic Syntax

```json
{
  "data": {"values": [
    {"category": 1, "value": 4},
    {"category": 2, "value": 6}
  ]},
  "mark": "arc",
  "encoding": {
    "theta": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

## Arc Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `radius` / `radius2` | number | Inner/outer radius of arc |
| `innerRadius` / `outerRadius` | number | Alternative radius properties |
| `theta` / `theta2` | number | Start/end angle in radians |
| `cornerRadius` | number | Corner radius for rounded arcs |
| `padAngle` | number | Padding between arc segments (radians) |
| `radiusOffset` / `radius2Offset` | number | Radius offset |
| `thetaOffset` / `theta2Offset` | number | Angle offset |

## Chart Patterns

### Pie Chart

```json
{
  "data": {"values": [
    {"category": 1, "value": 4},
    {"category": 2, "value": 6},
    {"category": 3, "value": 10}
  ]},
  "mark": "arc",
  "encoding": {
    "theta": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

### Donut Chart

Set `innerRadius` to non-zero:

```json
{
  "mark": {"type": "arc", "innerRadius": 50},
  "encoding": {
    "theta": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

### Pie Chart with Labels

Layer text marks on top of arcs:

```json
{
  "layer": [
    {
      "mark": "arc",
      "encoding": {
        "theta": {"field": "value", "stack": true},
        "color": {"field": "category"}
      }
    },
    {
      "mark": "text",
      "encoding": {
        "theta": {"field": "value", "stack": true},
        "text": {"field": "category"}
      }
    }
  ]
}
```

**Note**: Add `stack: true` to theta in the text layer to align with arc stacking.

### Pie Chart with Tooltips

```json
{
  "mark": {"type": "arc", "tooltip": true},
  "encoding": {
    "theta": {"field": "value"},
    "color": {"field": "category"}
  }
}
```

### Normalized Pie (Percentage Tooltips)

Use `stack: "normalize"` for percentage tooltips:

```json
{
  "encoding": {
    "theta": {"field": "value", "stack": "normalize"}
  }
}
```

### Ordinal Theta

Map ordinal fields to theta:

```json
{
  "encoding": {
    "theta": {"field": "category", "type": "ordinal"}
  }
}
```

### Pyramid Arcs

Diverging arcs showing positive/negative values.

### Radial Histograms

Histogram data mapped to arc angles:

```json
{
  "mark": "arc",
  "encoding": {
    "theta": {"field": "value", "bin": true},
    "radius": {"aggregate": "count"}
  }
}
```

### Radial Arcs (Layer Shorthand)

Combine arcs with other marks in layers.

### Faceted Pie Charts

Theta resolves to independent scales by default in facets, preserving ratios:

```json
{
  "facet": {"column": {"field": "region"}},
  "spec": {
    "mark": "arc",
    "encoding": {
      "theta": {"field": "value"},
      "color": {"field": "category"}
    }
  }
}
```

### Arc Config

```json
{
  "config": {
    "arc": {"cornerRadius": 3, "padAngle": 0.02}
  }
}
```
