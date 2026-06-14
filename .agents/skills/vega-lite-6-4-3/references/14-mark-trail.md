# Trail Mark Reference

The `trail` mark renders connected lines that preserve the original data order (unlike `line`, which sorts by x-axis). Use trails for GPS traces, time-series with irregular sampling, or any sequence where order matters.

## Basic Trail Chart

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Stock prices as trails preserving data order.",
  "data": {"url": "data/stocks.csv"},
  "mark": "trail",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"},
    "color": {"field": "symbol", "type": "nominal"}
  }
}
```

## Trail with Variable Width

Use `size` to encode a third dimension:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Trail with variable line width.",
  "data": {"url": "data/stocks.csv"},
  "mark": "trail",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"},
    "size": {"field": "price", "type": "quantitative"},
    "color": {"field": "symbol", "type": "nominal"}
  }
}
```

## Comet Trail

Combine with opacity for a comet-tail effect:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Comet trail visualization.",
  "data": {"url": "data/stocks.csv"},
  "mark": {"type": "trail", "opacity": 0.5},
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"},
    "color": {"field": "symbol", "type": "nominal"},
    "size": {"field": "price", "type": "quantitative"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position coordinates (connected in data order) |
| `color` | Trail color (separate trails per group) |
| `size` | Line width in pixels |
| `opacity` | Transparency |
| `detail` | Splits into separate trails without visual encoding |
| `order` | Drawing order |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `point` | `false` | Overlay point markers on data values |
| `tension` | `0` | Catmull-Rom spline tension |
| `orient` | auto | `"horizontal"` or `"vertical"` |

## Gotchas

- Unlike `line`, `trail` does **not** sort points by x-axis — it connects them in the order they appear in the data. Use `order` encoding to control connection sequence.
- Trail marks are path-based (like line and area), supporting `point` overlay and `tension` for smoothing.
- For GPS/trajectory data, ensure the source data is already sorted before encoding.
- `trail` is useful when x-axis values can repeat or go backward (e.g., a robot moving in loops).
- Use `detail` to split a single dataset into multiple trails without adding a visual encoding.
