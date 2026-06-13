# Point Marks

Point marks represent each data point with a symbol. They are the most versatile scatterplot mark, supporting various shapes, colors, sizes, and encodings.

## Basic Syntax

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "point",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

## Point Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `shape` | string | Marker shape (default `"circle"`) |
| `size` | number | Default mark size (area in pixels) |

### Available Shapes

`"circle"`, `"square"`, `"cross"`, `"diamond"`, `"triangle-up"`, `"triangle-right"`, `"triangle-down"`, `"triangle-left"`, `"star"`, `"wedge"` (pie slice), `"wedge-t"`, `"line"`, `"arrow"`.

## Chart Patterns

### 1D Points (Dot Plot)

Single positional encoding:

```json
{
  "data": {"values": [1, 2, 3, 5, 8, 13]},
  "mark": "point",
  "encoding": {"x": {"field": "data", "type": "quantitative"}}
}
```

### 2D Scatterplot

```json
{
  "mark": "point",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

### Filled Points

By default, points are stroked (transparent inside). Set `filled: true`:

```json
{
  "mark": {"type": "point", "filled": true}
}
```

### Bubble Charts

Add `size` encoding:

```json
{
  "mark": "point",
  "encoding": {
    "x": {"field": "life_expectancy"},
    "y": {"field": "income"},
    "size": {"field": "population"},
    "color": {"field": "continent"}
  }
}
```

### Color Encodings

**Quantitative color** (continuous scale):

```json
{"color": {"field": "value", "type": "quantitative"}}
```

**Ordinal color** (categorical):

```json
{"color": {"field": "category", "type": "nominal"}}
```

**Diverging color scheme**:

```json
{
  "encoding": {
    "color": {
      "field": "value",
      "scale": {"scheme": "redyellowblue", "domainMid": 0}
    }
  }
}
```

### Shape Encodings

**Custom shapes from data**:

```json
{
  "encoding": {
    "shape": {"field": "category", "type": "nominal"}
  }
}
```

**Constant shape with color**:

```json
{
  "mark": {"type": "point", "shape": "diamond"},
  "encoding": {"color": {"field": "category"}}
}
```

### Wind Vector Maps

Use `angle` encoding with wedge shapes:

```json
{
  "mark": {"type": "point", "shape": "wedge", "filled": true},
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "angle": {"field": "direction", "type": "quantitative"},
    "size": {"field": "speed", "type": "quantitative"}
  }
}
```

### Log Scale

```json
{
  "encoding": {
    "x": {"field": "value", "scale": {"type": "log"}}
  }
}
```

### Jittering (Random Offset)

Add random offset to discrete scales:

```json
{
  "transform": [{"calculate": "random()", "as": "jitter"}],
  "encoding": {
    "x": {"field": "category"},
    "xOffset": {"field": "jitter"}
  }
}
```

### Hyperlinks

Encode `href` for clickable points:

```json
{
  "encoding": {
    "x": {"field": "x"},
    "y": {"field": "y"},
    "href": {"field": "url"}
  }
}
```

### Overlapping Points

Use `opacity` or `bin` to handle overplotting:

```json
{
  "mark": {"type": "point", "opacity": 0.3}
}
```

### Q-Q Plots (Quantile-Quantile)

Compare distributions:

```json
{
  "transform": [
    {"window": [{"op": "quantile", "field": "value1", "as": "q1"}]},
    {"window": [{"op": "quantile", "field": "value2", "as": "q2"}]}
  ],
  "mark": "point",
  "encoding": {
    "x": {"field": "q1"},
    "y": {"field": "q2"}
  }
}
```

### Invalid Data Handling

Use conditional color for null/invalid values:

```json
{
  "encoding": {
    "color": {
      "condition": {"test": "isValid(datum.value)", "field": "category"},
      "value": "grey"
    }
  }
}
```

### Geo Points

Map geographic coordinates:

```json
{
  "mark": "point",
  "encoding": {
    "longitude": {"field": "lon"},
    "latitude": {"field": "lat"},
    "color": {"field": "category"}
  }
}
```

### Point Config

```json
{
  "config": {
    "point": {"filled": true, "size": 100, "opacity": 0.7}
  }
}
```
