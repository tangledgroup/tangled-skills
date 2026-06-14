# Boxplot Mark Reference

The `boxplot` composite mark renders box-and-whisker plots showing median, quartiles, and outliers. It compiles to layered primitive marks (rule, rect, point).

## Basic Vertical Boxplot

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Vertical boxplot of penguin body mass.",
  "data": {"url": "data/penguins.json"},
  "mark": "boxplot",
  "encoding": {
    "y": {"field": "Body Mass (g)", "type": "quantitative", "scale": {"zero": false}}
  }
}
```

## Boxplot by Group

Add a categorical encoding to compare distributions:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Boxplot of body mass by species.",
  "data": {"url": "data/penguins.json"},
  "mark": "boxplot",
  "encoding": {
    "x": {"field": "Species", "type": "nominal"},
    "y": {"field": "Body Mass (g)", "type": "quantitative", "scale": {"zero": false}},
    "color": {"field": "Species", "type": "nominal"}
  }
}
```

## Horizontal Boxplot

Swap x and y encodings:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Horizontal boxplot.",
  "data": {"url": "data/penguins.json"},
  "mark": "boxplot",
  "encoding": {
    "x": {"field": "Body Mass (g)", "type": "quantitative", "scale": {"zero": false}},
    "y": {"field": "Species", "type": "nominal"}
  }
}
```

## Boxplot with Min/Max Whiskers

Use mark object form to customize whisker extent:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Boxplot with min-max whiskers.",
  "data": {"url": "data/penguins.json"},
  "mark": {"type": "boxplot", "extent": "min-max"},
  "encoding": {
    "y": {"field": "Body Mass (g)", "type": "quantitative", "scale": {"zero": false}}
  }
}
```

## Boxplot with Custom Mid-Tick Color

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Boxplot with styled median tick.",
  "data": {"url": "data/penguins.json"},
  "mark": {
    "type": "boxplot",
    "midTickColor": "red"
  },
  "encoding": {
    "y": {"field": "Body Mass (g)", "type": "quantitative", "scale": {"zero": false}}
  }
}
```

## Pre-Aggregated Boxplot

When data is already aggregated:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Pre-aggregated boxplot.",
  "data": {
    "values": [
      {"group": "A", "q1": 20, "median": 30, "q3": 40, "min": 10, "max": 50}
    ]
  },
  "mark": {"type": "boxplot", "extent": "min-max"},
  "encoding": {
    "y": {"field": "median", "type": "quantitative"},
    "yError": {"field": "q3", "type": "quantitative"},
    "yError2": {"field": "q1", "type": "quantitative"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position (categorical axis for groups, quantitative for distribution) |
| `color` | Box color per group |
| `opacity` | Transparency |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `extent` | `1.5` | Whisker extent (IQR multiplier, or `"min-max"`) |
| `midTickColor` | auto | Color of the median tick mark |
| `size` | auto | Box width |

## Gotchas

- Boxplot is a composite mark — it compiles to multiple primitive marks (rule for whiskers, rect for box, point for outliers).
- Set `"scale": {"zero": false}` on the quantitative axis when values don't meaningfully start at zero.
- The `extent` property controls whisker length: `1.5` (default) uses 1.5× IQR; `"min-max"` extends to data extremes.
- Boxplot automatically detects and plots outliers beyond the whisker extent as individual points.
- For pre-aggregated data, you can replicate boxplots manually using `layer` with `rect`, `rule`, and `point` marks.
