# Tick Mark Reference

The `tick` mark renders small line segments (ticks), commonly used for strip plots, dot plots, and simple 1D distributions.

## Basic Strip Plot

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Strip plot of horsepower by cylinders.",
  "data": {"url": "data/cars.json"},
  "mark": "tick",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Cylinders", "type": "ordinal"}
  }
}
```

## Tick Histogram

Use `bin` for a histogram-like display:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Tick histogram of horsepower.",
  "data": {"url": "data/cars.json"},
  "mark": "tick",
  "encoding": {
    "x": {"field": "Horsepower", "bin": true, "type": "quantitative"},
    "y": {"aggregate": "count", "type": "quantitative"}
  }
}
```

## Grouped Ticks

Add color for grouped strip plots:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Grouped tick plot.",
  "data": {"url": "data/cars.json"},
  "mark": "tick",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Origin", "type": "nominal"},
    "color": {"field": "Cylinders", "type": "ordinal"}
  }
}
```

## Dot Plot with Ticks

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Dot plot using tick marks.",
  "data": {"url": "data/cars.json"},
  "mark": {"type": "tick", "thickness": 3},
  "encoding": {
    "x": {"aggregate": "mean", "field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Origin", "type": "nominal"},
    "color": {"field": "Origin", "type": "nominal"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position of the tick |
| `color` | Tick color (grouping) |
| `size` | Tick width/height |
| `opacity` | Transparency |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `thickness` | `1` | Thickness of the tick mark |
| `bandSize` | 3/4 of step | Width of ticks relative to band |
| `binSpacing` | `0` | Gap between binned ticks |
| `continuousBandSize` | `5` | Size on continuous scales |
| `discreteBandSize` | auto | Size on discrete scales |

## Gotchas

- Tick marks stack by default when a third encoding creates groups. Use `"stack": null` to disable.
- `thickness` controls the stroke width of individual ticks; `bandSize` controls the total width relative to the axis step.
- For strip plots with many overlapping points, reduce opacity or use `jitter` transforms.
- Tick marks are rect-based like bar and rect, sharing sizing properties.
- Use `tick` for lightweight distributions where `bar` would be too heavy visually.
