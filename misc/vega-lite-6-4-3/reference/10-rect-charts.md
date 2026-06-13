# Rect Charts

Rect marks represent arbitrary rectangles. They are the primary mark for heatmaps and mosaic plots.

## Basic Syntax

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "rect",
  "encoding": {
    "x": {"field": "Cylinders", "type": "ordinal"},
    "y": {"field": "Origin", "type": "nominal"},
    "color": {"aggregate": "mean", "field": "Horsepower"}
  }
}
```

## Rect Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `orient` | string | `"vertical"` or `"horizontal"` |
| `align` | number | Text alignment within rect (0-1) |
| `baseline` | string | Baseline for text marks on rects |
| `width` / `height` | number | Rect dimensions |
| `cornerRadius` | number | Corner radius |
| `binSpacing` | number | Gap between rects (default 1) |

## Rect Config

| Property | Type | Description |
|----------|------|-------------|
| `continuousBandSize` | number | Band size on continuous scales |
| `discreteBandSize` | number | Band size on discrete scales |
| `minBandSize` | number | Minimum band size |

## Chart Patterns

### Simple Heatmap

Discrete fields on both axes, color encoding:

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "rect",
  "encoding": {
    "x": {"field": "Cylinders", "type": "ordinal"},
    "y": {"field": "Origin", "type": "nominal"},
    "color": {"aggregate": "mean", "field": "Horsepower"}
  },
  "config": {"axis": {"grid": true, "tickBand": "extent"}}
}
```

### Binned Heatmap

Bin quantitative fields on both axes:

```json
{
  "mark": "rect",
  "encoding": {
    "x": {"field": "Horsepower", "bin": true},
    "y": {"field": "Miles_per_Gallon", "bin": true},
    "color": {"aggregate": "count"}
  }
}
```

### Weather Heatmap

Temporal + ordinal axes:

```json
{
  "mark": "rect",
  "encoding": {
    "x": {"timeUnit": "day", "field": "date", "type": "ordinal"},
    "y": {"timeUnit": "month", "field": "date", "type": "ordinal"},
    "color": {"aggregate": "mean", "field": "temp"}
  }
}
```

### Mosaic Plots

Proportional rectangles showing multi-dimensional data:

```json
{
  "mark": "rect",
  "encoding": {
    "x": {"field": "category1", "type": "nominal", "aggregate": "count"},
    "y": {"field": "category2", "type": "nominal", "aggregate": "count"},
    "color": {"field": "category1"}
  }
}
```

### Labeled Mosaic Plots

Add text layer for labels:

```json
{
  "layer": [
    {"mark": "rect", "encoding": {"x": {"field": "cat1"}, "y": {"field": "cat2"}, "color": {"field": "cat1"}}},
    {"mark": "text", "encoding": {"x": {"field": "cat1"}, "y": {"field": "cat2"}, "text": {"aggregate": "count"}}}
  ]
}
```

### Lasagna Charts

Single-axis rects with color encoding (like horizontal heatmaps):

```json
{
  "mark": "rect",
  "encoding": {
    "y": {"field": "category", "type": "nominal"},
    "color": {"field": "value", "type": "quantitative"}
  }
}
```

### Ranged Rectangles (Annotations)

Use `x2`/`y2` for ranged rects:

```json
{
  "mark": "rect",
  "encoding": {
    "x": {"datum": 10},
    "x2": {"datum": 30},
    "y": {"scale": "y"},
    "y2": {"scale": "y"}
  }
}
```

### Rect Config

```json
{
  "config": {
    "rect": {"cornerRadius": 2, "binSpacing": 0}
  }
}
```
