# Tick Marks

Tick marks represent each data point as a short line. They are useful for displaying value distributions, dot plots, and strip charts.

## Basic Syntax

```json
{
  "data": {"url": "data/seattle-weather.csv"},
  "mark": "tick",
  "encoding": {
    "x": {"field": "precipitation", "type": "quantitative"}
  }
}
```

## Tick Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `orient` | string | `"vertical"` or `"horizontal"` |
| `cornerRadius` | number | Corner radius for rounded ticks |

## Tick Config

| Property | Type | Description |
|----------|------|-------------|
| `bandSize` | number | Band size on discrete scales |
| `thickness` | number | Tick line thickness in pixels |

## Chart Patterns

### Dot Plot (1D Distribution)

Single quantitative axis shows distribution:

```json
{
  "data": {"url": "data/seattle-weather.csv"},
  "mark": "tick",
  "encoding": {
    "x": {"field": "precipitation", "type": "quantitative"}
  }
}
```

### Custom Thickness

```json
{
  "mark": {"type": "tick", "thickness": 3},
  "encoding": {"x": {"field": "value"}}
}
```

### Grouped Ticks

Add a grouping dimension:

```json
{
  "mark": "tick",
  "encoding": {
    "x": {"field": "value", "type": "quantitative"},
    "y": {"field": "category", "type": "nominal"},
    "color": {"field": "category"}
  }
}
```

### Histogram Ticks

Use `bin` to create histogram-style ticks:

```json
{
  "mark": "tick",
  "encoding": {
    "x": {"field": "value", "bin": true},
    "y": {"aggregate": "count"}
  }
}
```

### Strip Charts (1D with Height)

Show distribution along one axis with categorical grouping:

```json
{
  "mark": "tick",
  "encoding": {
    "x": {"field": "value", "type": "quantitative"},
    "y": {"field": "category", "type": "nominal"}
  }
}
```

### Strip with Band Positioning

```json
{
  "mark": "tick",
  "encoding": {
    "x": {"field": "value", "bandPosition": 0.5}
  }
}
```

### Sort Ticks

Control sort order:

```json
{
  "encoding": {
    "x": {"field": "value", "sort": "descending"}
  }
}
```

### Timeunit Ticks

Temporal aggregation with ticks:

```json
{
  "mark": "tick",
  "encoding": {
    "x": {"timeUnit": "month", "field": "date"},
    "y": {"aggregate": "count"}
  }
}
```

### Width Band

Control tick band width:

```json
{
  "config": {
    "tick": {"bandSize": 10, "thickness": 2}
  }
}
```

### Tick Config

```json
{
  "config": {
    "tick": {"orient": "horizontal", "cornerRadius": 2}
  }
}
```
