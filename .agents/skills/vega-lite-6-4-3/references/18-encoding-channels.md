# Encoding Channels Reference

Encoding channels map data fields to visual properties. Every Vega-Lite spec uses encodings to define how data appears visually.

## Position Channels

### `x` and `y`

Primary position on horizontal and vertical axes:

```vega-lite
"encoding": {
  "x": {"field": "Horsepower", "type": "quantitative"},
  "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
}
```

### `x2` and `y2`

Secondary position for ranged marks (bar, area, rect, rule):

```vega-lite
"encoding": {
  "y": {"aggregate": "min", "field": "people"},
  "y2": {"aggregate": "max", "field": "people"}
}
```

## Color Channels

### `color`

General color encoding (fill for most marks, stroke for line/point/rule):

```vega-lite
"color": {"field": "Origin", "type": "nominal"}
```

### `fill` and `stroke`

Explicit fill or stroke (overrides `color`):

```vega-lite
"encoding": {
  "fill": {"field": "category", "type": "nominal"},
  "stroke": {"value": "black"}
}
```

## Size and Shape

### `size`

Pixel area for points/circles/squares, font size for text, bar width:

```vega-lite
"size": {"field": "Displacement", "type": "quantitative"}
```

### `shape`

Symbol shape for point marks only:

```vega-lite
"shape": {"field": "Origin", "type": "nominal"}
```

Available shapes: `circle`, `square`, `cross`, `diamond`, `triangle-up`, `triangle-down`, `star`, `yen`, `plus`, `x`.

## Opacity and Order

### `opacity`

Transparency from 0 (invisible) to 1 (opaque):

```vega-lite
"opacity": {"value": 0.5}
```

### `order`

Drawing/stacking order:

```vega-lite
"order": {"field": "priority", "type": "quantitative"}
```

## Polar Channels

### `theta` and `radius`

Polar coordinates for arc and text marks:

```vega-lite
"encoding": {
  "theta": {"field": "value", "type": "quantitative"},
  "color": {"field": "category", "type": "nominal"}
}
```

## Text and Tooltip

### `text`

Text content for text marks:

```vega-lite
"text": {"aggregate": "mean", "field": "Horsepower", "format": ".2f"}
```

### `tooltip`

Hover tooltip content:

```vega-lite
"encoding": {
  "x": {"field": "Horsepower"},
  "y": {"field": "Miles_per_Gallon"},
  "tooltip": [
    {"field": "Horsepower"},
    {"field": "Miles_per_Gallon"},
    {"field": "Origin"}
  ]
}
```

Or use the mark property: `"mark": {"type": "point", "tooltip": true}`.

## Special Channels

### `detail`

Splits data into separate groups without visual encoding (creates independent mark groups):

```vega-lite
"detail": {"field": "symbol", "type": "nominal"}
```

Useful for connecting lines per group without coloring them differently.

### `key`

Data key for interaction binding (selections, parameters).

## Longitude/Latitude (Geographic)

For geographic projections:

```vega-lite
"encoding": {
  "longitude": {"field": "Longitude", "type": "quantitative"},
  "latitude": {"field": "Latitude", "type": "quantitative"}
}
```

## Encoding Channel Properties

Each encoding channel accepts an object with these properties:

| Property | Description |
|---|---|
| `field` | Data field name |
| `type` | Data type (`quantitative`, `ordinal`, `nominal`, `temporal`) |
| `aggregate` | Aggregation function (`sum`, `mean`, `count`, `min`, `max`, etc.) |
| `bin` | Binning (`true`, `false`, or bin config) |
| `timeUnit` | Time unit truncation (`year`, `month`, `yearmonth`, `yearmonthdate`) |
| `value` | Constant value (alternative to `field`) |
| `scale` | Scale configuration |
| `axis` | Axis configuration (x/y only) |
| `legend` | Legend configuration (color/size/shape only) |
| `sort` | Sorting (`"ascending"`, `"descending"`, field name, `-field`) |
| `title` | Label override for axis/legend |
| `format` | Display format string |
| `stack` | Stacking behavior (`"layer0"`, `"center"`, `"normalize"`, `null`) |

## Gotchas

- `type` is required when using `field`. It determines the scale type and visual treatment.
- `value` bypasses the data field entirely — use for constant styling (e.g., `"color": {"value": "red"}`).
- `aggregate` and `bin` can be combined: `{"aggregate": "count", "bin": true}` creates a histogram.
- `detail` does not produce visual output but splits data into separate mark groups — essential for multi-line charts with the same color.
- Channel properties like `scale`, `axis`, and `legend` override global `config` settings.
