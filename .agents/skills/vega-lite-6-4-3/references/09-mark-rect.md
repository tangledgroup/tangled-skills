# Rect Mark Reference

The `rect` mark renders rectangles, commonly used for heatmaps, mosaic plots, and matrix visualizations.

## Heatmap

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Heatmap of mean horsepower by origin and cylinders.",
  "data": {"url": "data/cars.json"},
  "mark": "rect",
  "encoding": {
    "y": {"field": "Origin", "type": "nominal"},
    "x": {"field": "Cylinders", "type": "ordinal"},
    "color": {"aggregate": "mean", "field": "Horsepower", "type": "quantitative"}
  },
  "config": {"axis": {"grid": true, "tickBand": "extent"}}
}
```

## Binned Heatmap (2D Histogram)

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "2D histogram as a heatmap.",
  "data": {"url": "data/cars.json"},
  "mark": "rect",
  "encoding": {
    "x": {"field": "Horsepower", "bin": true, "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "bin": true, "type": "quantitative"},
    "color": {"aggregate": "count", "type": "quantitative"}
  }
}
```

## Mosaic Plot

Use `x2` and `y2` for proportional rectangles:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Mosaic plot of car origins.",
  "data": {"url": "data/cars.json"},
  "mark": "rect",
  "encoding": {
    "x": {"field": "Origin", "type": "nominal"},
    "y": {"field": "Cylinders", "type": "ordinal"},
    "x2": {"aggregate": "count", "type": "quantitative"},
    "color": {"field": "Origin", "type": "nominal"}
  }
}
```

## Heatmap with Labels

Layer text on rectangles:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Heatmap with count labels.",
  "data": {"url": "data/cars.json"},
  "layer": [
    {
      "mark": "rect",
      "encoding": {
        "y": {"field": "Origin", "type": "nominal"},
        "x": {"field": "Cylinders", "type": "ordinal"},
        "color": {"aggregate": "count", "type": "quantitative"}
      }
    },
    {
      "mark": "text",
      "encoding": {
        "y": {"field": "Origin", "type": "nominal"},
        "x": {"field": "Cylinders", "type": "ordinal"},
        "text": {"aggregate": "count", "type": "quantitative"}
      }
    }
  ]
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position of the rectangle corner |
| `x2`, `y2` | Opposite corner (defines width/height) |
| `color` | Fill color (typically quantitative for heatmaps) |
| `opacity` | Transparency |
| `size` | Width/height override |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `binSpacing` | `0` | Gap between binned rectangles |
| `continuousBandSize` | `5` | Bar size on continuous scales |
| `discreteBandSize` | auto | Bar size on discrete scales |
| `minBandSize` | `0.25` | Minimum band size |

## Gotchas

- Rect marks are rect-based like bar, sharing `binSpacing`, `continuousBandSize`, and `discreteBandSize` properties.
- For heatmaps, set `"config": {"axis": {"tickBand": "extent"}}` to remove gaps between cells.
- The `x2`/`y2` channels define the full extent of a rectangle, enabling mosaic plots and Gantt charts.
- Rect marks do not stack — each rectangle is independent.
- For temporal heatmaps (e.g., weather by day/month), use `timeUnit` on x or y axes.
