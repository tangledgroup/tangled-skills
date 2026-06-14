# Errorbar Mark Reference

The `errorbar` composite mark renders error bars showing uncertainty around aggregate values. It compiles to layered `rule` and `tick` marks.

## Basic Error Bar (Aggregate)

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Error bars showing min-max of population by age.",
  "data": {"url": "data/population.json"},
  "transform": [{"filter": "datum.year == 2000"}],
  "mark": "errorbar",
  "encoding": {
    "x": {"field": "age", "type": "ordinal"},
    "y": {"aggregate": "mean", "field": "people", "type": "quantitative"},
    "yError": {"ci": 0.95, "field": "people"}
  }
}
```

## Error Bars on Bar Chart

Layer errorbars on bars:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Bar chart with error bars.",
  "data": {"url": "data/cars.json"},
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"field": "Origin", "type": "nominal"},
        "y": {"aggregate": "mean", "field": "Horsepower"}
      }
    },
    {
      "mark": "errorbar",
      "encoding": {
        "x": {"field": "Origin", "type": "nominal"},
        "y": {"aggregate": "mean", "field": "Horsepower"},
        "yError": {"ci": 0.95, "field": "Horsepower"}
      }
    }
  ]
}
```

## Error Bars with Stdev

Use standard deviation instead of confidence intervals:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Error bars with standard deviation.",
  "data": {"url": "data/cars.json"},
  "mark": "errorbar",
  "encoding": {
    "x": {"field": "Origin", "type": "nominal"},
    "y": {"aggregate": "mean", "field": "Horsepower"},
    "yError": {"stdev": 1, "field": "Horsepower"}
  }
}
```

## Horizontal Error Bars

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Horizontal error bars.",
  "data": {"url": "data/cars.json"},
  "mark": "errorbar",
  "encoding": {
    "y": {"field": "Origin", "type": "nominal"},
    "x": {"aggregate": "mean", "field": "Horsepower"},
    "xError": {"ci": 0.95, "field": "Horsepower"}
  }
}
```

## Pre-Aggregated Error Bars

When data already has error values:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Pre-aggregated error bars.",
  "data": {
    "values": [
      {"group": "A", "mean": 30, "lower": 25, "upper": 35},
      {"group": "B", "mean": 40, "lower": 33, "upper": 47}
    ]
  },
  "mark": "errorbar",
  "encoding": {
    "x": {"field": "group", "type": "nominal"},
    "y": {"field": "mean", "type": "quantitative"},
    "yError": {"field": "upper"},
    "yError2": {"field": "lower"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position of the error bar center |
| `xError`, `yError` | Upper error bound |
| `xError2`, `yError2` | Lower error bound (asymmetric errors) |
| `color` | Error bar color |
| `opacity` | Transparency |

## Error Specifications

| Spec | Description |
|---|---|
| `{"ci": 0.95, "field": "x"}` | 95% confidence interval |
| `{"stdev": 1, "field": "x"}` | ±1 standard deviation |
| `{"field": "upper"}` | Direct field for upper bound |
| `{"field": "upper"}, {"field2": "lower"}` | Asymmetric bounds from fields |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `extent` | auto | Error extent specification |
| `tickSize` | auto | Width of the end ticks |
| `strokeWidth` | `1.5` | Line thickness |

## Gotchas

- Errorbar is a composite mark — it compiles to `rule` (stem) + `tick` (end caps).
- Use `yError`/`yError2` for asymmetric errors where upper and lower bounds differ.
- When layering errorbars on bars, the errorbar layer should come after the bar layer for proper z-ordering.
- For `ci` (confidence interval), Vega-Lite computes it from the data — ensure sufficient samples per group.
- Set `"scale": {"zero": false}` when error ranges don't meaningfully include zero.
