# Scatterplots (Circle Marks)

Circle marks are like point marks but with shape fixed to `circle` and filled by default. They are the primary mark for scatterplots and bubble charts.

## Basic Syntax

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "circle",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

## Circle Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `size` | number | Default mark size (area in pixels) |

## Chart Patterns

### Simple Scatterplot

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "circle",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

### Bubble Charts

Add `size` encoding for a third dimension:

```json
{
  "mark": "circle",
  "encoding": {
    "x": {"field": "life_expectancy", "type": "quantitative"},
    "y": {"field": "income", "type": "quantitative"},
    "size": {"field": "population", "type": "quantitative"},
    "color": {"field": "continent", "type": "nominal"}
  }
}
```

### Binned Scatterplots

Use `bin` to aggregate data into cells:

```json
{
  "mark": "circle",
  "encoding": {
    "x": {"field": "Horsepower", "bin": {"maxbins": 20}},
    "y": {"field": "Miles_per_Gallon", "bin": {"maxbins": 20}},
    "color": {"aggregate": "count"}
  }
}
```

### GitHub Punchcard

Temporal day-of-week vs. hour with binned data:

```json
{
  "mark": "circle",
  "encoding": {
    "x": {"timeUnit": "day", "field": "date", "type": "ordinal"},
    "y": {"timeUnit": "hours", "field": "date", "type": "ordinal"},
    "color": {"aggregate": "count"}
  }
}
```

### Wilkinson Dot Plots

Stacked dot plots showing distributions:

```json
{
  "transform": [{"window": [{"op": "count", "as": "cumcount"}]}],
  "mark": "circle",
  "encoding": {
    "x": {"field": "category"},
    "y": {"field": "cumcount", "type": "quantitative"},
    "color": {"field": "category"}
  }
}
```

### Quantile/Quantize/Threshold Scales

Use discretizing scale types for color encoding:

```json
{
  "encoding": {
    "color": {"field": "value", "scale": {"type": "quantile"}}
  }
}
```

| Scale Type | Behavior |
|-----------|----------|
| `quantile` | Equal-count groups from sample domain |
| `quantize` | Uniform domain segments to discrete range |
| `threshold` | Arbitrary threshold boundaries |

### Opacity Encoding

```json
{
  "encoding": {
    "opacity": {"field": "value", "type": "quantitative"}
  }
}
```

### Flatten Transform for Scatterplots

Use `flatten` to unpivot wide data:

```json
{
  "transform": [{"flatten": ["field1", "field2"]}],
  "encoding": {
    "x": {"field": "field1"},
    "y": {"field": "field2"}
  }
}
```

### Circle Config

```json
{
  "config": {
    "circle": {"size": 50, "opacity": 0.7}
  }
}
```
