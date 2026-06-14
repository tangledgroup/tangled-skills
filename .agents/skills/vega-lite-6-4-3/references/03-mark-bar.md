# Bar Mark Reference

The `bar` mark renders bar charts — one of the most common chart types. Supports vertical, horizontal, grouped, and stacked variants.

## Basic Bar Chart

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A simple bar chart of population by age group.",
  "data": {
    "values": [
      {"age": "0-9", "people": 20},
      {"age": "10-19", "people": 35},
      {"age": "20-29", "people": 45},
      {"age": "30-39", "people": 30}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "age", "type": "ordinal"},
    "y": {"field": "people", "type": "quantitative"}
  }
}
```

## Aggregated Bar Chart

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Bar chart with aggregation.",
  "data": {"url": "data/cars.json"},
  "mark": "bar",
  "encoding": {
    "x": {"field": "Cylinders", "type": "ordinal"},
    "y": {"aggregate": "mean", "field": "Horsepower", "type": "quantitative"}
  }
}
```

## Horizontal Bar Chart

Swap x and y encodings:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Horizontal bar chart.",
  "data": {
    "values": [
      {"country": "US", "gdp": 21},
      {"country": "CN", "gdp": 14},
      {"country": "JP", "gdp": 5}
    ]
  },
  "mark": "bar",
  "encoding": {
    "y": {"field": "country", "type": "nominal"},
    "x": {"field": "gdp", "type": "quantitative", "title": "GDP (trillion USD)"}
  }
}
```

## Stacked Bar Chart

Add a `color` encoding for automatic stacking:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Stacked bar chart of population by age and gender.",
  "data": {"url": "data/population.json"},
  "transform": [{"filter": "datum.year == 2000"}],
  "mark": "bar",
  "encoding": {
    "x": {"field": "age", "type": "ordinal"},
    "y": {"aggregate": "sum", "field": "people", "type": "quantitative"},
    "color": {"field": "gender", "type": "nominal"}
  }
}
```

## Grouped (Dodged) Bar Chart

Use `xOffset` (or `yOffset`) to dodge bars within groups — this automatically disables stacking:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Grouped bar chart.",
  "data": {"url": "data/population.json"},
  "transform": [{"filter": "datum.year == 2000"}],
  "mark": "bar",
  "encoding": {
    "x": {"field": "age", "type": "ordinal"},
    "y": {"aggregate": "sum", "field": "people", "type": "quantitative"},
    "color": {"field": "gender", "type": "nominal"},
    "xOffset": {"field": "gender", "type": "nominal"}
  }
}
```

## Bar Chart with Error Bars

Layer error bars using `layer`. The `errorbar` composite mark computes bounds automatically:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Bar chart with error bars.",
  "data": {"url": "data/cars.json"},
  "encoding": {
    "x": {"field": "Cylinders", "type": "nominal"},
    "xOffset": {"field": "Origin", "type": "nominal"}
  },
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "y": {"aggregate": "mean", "field": "Acceleration", "type": "quantitative"},
        "color": {"field": "Origin", "type": "nominal"}
      }
    },
    {
      "mark": "errorbar",
      "encoding": {
        "y": {"field": "Acceleration", "type": "quantitative"}
      }
    }
  ]
}
```

## Bar Chart with Rounded Corners

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Bar chart with rounded corners.",
  "data": {
    "values": [
      {"category": "A", "value": 4},
      {"category": "B", "value": 6},
      {"category": "C", "value": 10}
    ]
  },
  "mark": {"type": "bar", "cornerRadiusTopLeft": 3, "cornerRadiusTopRight": 3},
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position and size of bars |
| `x2`, `y2` | Secondary position for ranged bars |
| `color` | Bar color (stacking groups when nominal) |
| `size` | Bar width/height override |
| `opacity` | Transparency |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `cornerRadiusTopLeft` | `0` | Top-left corner radius in pixels |
| `cornerRadiusTopRight` | `0` | Top-right corner radius |
| `cornerRadiusBottomLeft` | `0` | Bottom-left corner radius |
| `cornerRadiusBottomRight` | `0` | Bottom-right corner radius |
| `cornerRadiusEnd` | `0` | End corner(s) for the bar direction |
| `binSpacing` | `1` | Gap between binned bars (0 for no gap) |

## Gotchas

- Bars stack automatically when a third encoding (like `color`) is present. Use `"stack": null` to disable stacking and get dodged/grouped bars.
- For grouped bars, use `xOffset`/`yOffset` with the grouping field.
- The default `binSpacing` of 1 leaves small gaps between binned bars. Set to `0` for continuous appearance.
- Bar marks are rect-based, so they support `continuousBandSize`, `discreteBandSize`, and `minBandSize` config properties.
- For horizontal bars, use `cornerRadiusEnd` or the right/bottom corner properties depending on orientation.
