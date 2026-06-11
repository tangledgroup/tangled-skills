# Trail Charts

Trail marks connect data points like lines but support **variable widths** determined by backing data. Unlike `line`, trails use `fill` (not `stroke`) for color and do not support interpolation methods.

## When to Use Trails vs Lines

| Feature | `line` | `trail` |
|---------|--------|---------|
| Variable width | No | Yes (via `size` encoding) |
| Interpolation | Many methods | None (straight segments only) |
| Color property | `stroke` | `fill` |
| Point overlay | Yes (`point: true`) | No |

## Trail Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `orient` | string | `"vertical"` or `"horizontal"` |

## Basic Syntax

```json
{
  "data": {"url": "data/path.json"},
  "mark": "trail",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "size": {"field": "width", "type": "quantitative"}
  }
}
```

## Chart Patterns

### Trail with Color Encoding

Encode a field in `color` (maps to `fill`) and `size` for variable-width trails:

```json
{
  "mark": "trail",
  "encoding": {
    "x": {"field": "x", "type": "quantitative"},
    "y": {"field": "y", "type": "quantitative"},
    "size": {"field": "size", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

### Comet Charts

Show change between two states with trails connecting them:

```json
{
  "data": {"url": "data/us-10m.json"},
  "transform": [{"filter": "datum.id !== '72'"}],
  "mark": "trail",
  "encoding": {
    "longitude": {"field": "lon", "type": "quantitative"},
    "latitude": {"field": "lat", "type": "quantitative"},
    "size": {"field": "pop", "type": "quantitative"}
  }
}
```

### Trail Config

```json
{
  "config": {
    "trail": {"fill": "#4682b4"}
  }
}
```
