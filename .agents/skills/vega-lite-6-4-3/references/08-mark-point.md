# Point Mark Reference

The `point` mark renders stroke-only circular markers. Use `circle` for filled markers. Points are the default overlay on line and area marks.

## Basic Scatter Plot

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot with point marks.",
  "data": {"url": "data/cars.json"},
  "mark": "point",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

## Colored Scatter Plot

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot colored by origin.",
  "data": {"url": "data/cars.json"},
  "mark": "point",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "color": {"field": "Origin", "type": "nominal"}
  }
}
```

## Filled Points

Use `filled: true` on the mark:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Filled point marks.",
  "data": {"url": "data/cars.json"},
  "mark": {"type": "point", "filled": true},
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "color": {"field": "Origin", "type": "nominal"}
  }
}
```

## Variable Size and Shape

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot with size and shape encodings.",
  "data": {"url": "data/cars.json"},
  "mark": "point",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "size": {"field": "Displacement", "type": "quantitative"},
    "shape": {"field": "Origin", "type": "nominal"},
    "color": {"field": "Cylinders", "type": "ordinal"}
  }
}
```

## Dot Plot (1D)

Single-axis point plot:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Dot plot of mean horsepower by origin.",
  "data": {"url": "data/cars.json"},
  "mark": {"type": "point", "filled": true},
  "encoding": {
    "y": {"field": "Origin", "type": "nominal"},
    "x": {"aggregate": "mean", "field": "Horsepower", "type": "quantitative"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position coordinates |
| `color` | Stroke color (fill when `filled: true`) |
| `size` | Area of the point in pixels |
| `shape` | Symbol shape (`circle`, `square`, `cross`, `diamond`, `triangle-up`, etc.) |
| `opacity` | Transparency (0–1) |

## Available Shapes

| Shape | Description |
|---|---|
| `circle` | Circle (default) |
| `square` | Square |
| `cross` | Cross (+) |
| `diamond` | Diamond |
| `triangle-up` | Upward triangle |
| `triangle-down` | Downward triangle |
| `star` | Star |
| `yen` | Yen symbol |
| `plus` | Plus sign |
| `x` | X mark |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `filled` | `false` | Fill the point (stroke-only by default) |
| `strokeWidth` | `1.5` | Border width in pixels |

## Gotchas

- `point` is stroke-only by default; `circle` and `square` are filled. Use `{"filled": true}` to fill points.
- The `shape` encoding is only available for `point` marks (not `circle` or `square`).
- For dense scatter plots, reduce opacity (`"opacity": {"value": 0.3}`) to reveal overplotting density.
- `size` encodes the **area** of the point, not its diameter.
- Point marks are commonly used as overlays on line charts via `{"type": "line", "point": true}`.
