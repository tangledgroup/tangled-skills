# Square Mark Reference

The `square` mark renders filled square markers, similar to `circle` but with a square shape. Used in scatter plots and matrix visualizations.

## Basic Scatter Plot with Squares

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot with square markers.",
  "data": {"url": "data/cars.json"},
  "mark": "square",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

## Colored Squares

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot with colored squares.",
  "data": {"url": "data/cars.json"},
  "mark": "square",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "color": {"field": "Origin", "type": "nominal"},
    "size": {"field": "Displacement", "type": "quantitative"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position coordinates |
| `color` | Fill color |
| `size` | Area of the square in pixels |
| `opacity` | Transparency (0–1) |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `filled` | `true` | Square marks are filled by default |
| `strokeWidth` | `1.5` | Border width in pixels |

## Gotchas

- `square` is always filled (like `circle`). Use `point` with `shape: "square"` for stroke-only squares.
- `size` encodes the **area** of the square, not its side length.
- Unlike `point`, `square` does not support the `shape` encoding channel — it's always a square.
- Choose between `circle`, `square`, and `point` based on visual distinction needs in multi-series plots.
