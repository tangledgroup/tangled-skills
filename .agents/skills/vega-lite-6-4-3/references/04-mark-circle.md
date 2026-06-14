# Circle Mark Reference

The `circle` mark renders filled circular points, typically used in scatter plots and bubble charts. Unlike `point` (stroke-only by default), `circle` is filled.

## Basic Scatter Plot

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot of horsepower vs miles per gallon.",
  "data": {"url": "data/cars.json"},
  "mark": "circle",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

## Colored Scatter Plot

Add a `color` encoding to group by category:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot colored by origin.",
  "data": {"url": "data/cars.json"},
  "mark": "circle",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "color": {"field": "Origin", "type": "nominal"}
  }
}
```

## Bubble Chart (Size Encoding)

Use `size` to encode a third quantitative dimension:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Bubble chart with size encoding.",
  "data": {"url": "data/cars.json"},
  "mark": "circle",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "size": {"field": "Displacement", "type": "quantitative"},
    "color": {"field": "Origin", "type": "nominal"}
  }
}
```

## Scatter Plot with Trend Line

Layer a line or rule for the trend:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot with regression line.",
  "data": {"url": "data/cars.json"},
  "layer": [
    {
      "mark": "circle",
      "encoding": {
        "x": {"field": "Horsepower", "type": "quantitative"},
        "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
        "opacity": {"value": 0.5}
      }
    },
    {
      "mark": "line",
      "encoding": {
        "x": {"field": "Horsepower", "type": "quantitative", "bin": true},
        "y": {"aggregate": "mean", "field": "Miles_per_Gallon"}
      }
    }
  ]
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position coordinates |
| `color` | Fill color |
| `size` | Area of the circle in pixels (not radius) |
| `opacity` | Transparency (0–1) |
| `shape` | Not applicable (circle is a fixed shape) |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `filled` | `true` | Circle marks are filled by default |
| `strokeWidth` | `1.5` | Border width in pixels |

## Gotchas

- `size` encodes the **area** of the circle, not its radius. The visual radius scales with the square root of the size value.
- `circle` is always filled; use `point` if you want stroke-only symbols.
- For very large datasets, consider using `sample` transform or reducing opacity to handle overplotting.
- Unlike `point`, `circle` does not support the `shape` encoding channel — it's always circular.
