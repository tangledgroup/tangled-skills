# Text Marks

Text marks represent each data point as text labels. They are used for annotations, labels on other marks, and text-based visualizations.

## Basic Syntax

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "text",
  "encoding": {
    "y": {"field": "Origin", "type": "ordinal"},
    "text": {"aggregate": "mean", "field": "Horsepower", "format": ".2f"}
  }
}
```

## Text Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `angle` | number | Rotation angle in degrees |
| `align` | string | `"left"`, `"center"`, `"right"` |
| `baseline` | string | `"top"`, `"middle"`, `"bottom"`, `"alphabetic"`, etc. |
| `dir` | string | Text direction (`"ltr"` or `"rtl"`) |
| `dx` / `dy` | number | Offset in pixels |
| `ellipsis` | string | Ellipsis character for overflow |
| `font` | string | Font family |
| `fontSize` | number | Font size in pixels |
| `fontStyle` | string | `"normal"` or `"italic"` |
| `fontWeight` | string \| number | `"normal"`, `"bold"`, or numeric (100-900) |
| `limit` | number | Maximum text length in pixels |
| `lineHeight` | number | Line height multiplier |
| `radius` / `theta` | number | Polar position for radial text |
| `text` | string | Constant text value |

## Chart Patterns

### Text Table Heatmap

Text marks as a table display:

```json
{
  "layer": [
    {
      "mark": "rect",
      "encoding": {
        "x": {"field": "Cylinders"},
        "y": {"field": "Origin"},
        "color": {"aggregate": "mean", "field": "Horsepower"}
      }
    },
    {
      "mark": "text",
      "encoding": {
        "x": {"field": "Cylinders"},
        "y": {"field": "Origin"},
        "text": {"aggregate": "mean", "field": "Horsepower", "format": ".1f"}
      }
    }
  ]
}
```

### Labels on Bars

Offset text marks above bars:

```json
{
  "layer": [
    {
      "mark": "bar",
      "encoding": {"x": {"field": "category"}, "y": {"field": "value"}}
    },
    {
      "mark": {"type": "text", "dy": -5},
      "encoding": {
        "x": {"field": "category"},
        "y": {"field": "value"},
        "text": {"field": "value", "format": ".0f"}
      }
    }
  ]
}
```

### Colored Scatterplot with Text

Show initial characters instead of points:

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "text",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "text": {"field": "Origin"},
    "color": {"field": "Origin"}
  }
}
```

### Geo Text

Text at geographic coordinates:

```json
{
  "data": {"url": "data/us-10m.json"},
  "mark": "text",
  "encoding": {
    "longitude": {"field": "lon"},
    "latitude": {"field": "lat"},
    "text": {"field": "name"}
  }
}
```

### Format Strings

Control number and date formatting:

```json
{
  "encoding": {
    "text": {
      "aggregate": "mean",
      "field": "Horsepower",
      "format": ".2f"
    }
  }
}
```

Common formats: `".2f"` (2 decimals), `",.0f"` (comma-separated integers), `"%"` (percentage), `".2s"` (SI prefix).

### Text Config

```json
{
  "config": {
    "text": {"fontSize": 12, "color": "#333"}
  }
}
```
