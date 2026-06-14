# Errorbar Mark Reference

The `errorbar` composite mark renders error bars showing uncertainty around aggregate values. It compiles to layered `rule` (stem) and `tick` (end cap) marks.

## Basic Error Bar (Confidence Interval)

The `errorbar` mark computes error bounds automatically from the data:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Error bars with confidence intervals for barley yield by variety.",
  "data": {"url": "data/barley.json"},
  "mark": "errorbar",
  "encoding": {
    "x": {"field": "yield", "type": "quantitative", "scale": {"zero": false}},
    "y": {"field": "variety", "type": "ordinal"}
  }
}
```

## Error Bar with CI Extent

Explicitly set confidence interval extent:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Error bars with explicit CI extent.",
  "data": {"url": "data/cars.json"},
  "mark": {"type": "errorbar", "extent": "ci"},
  "encoding": {
    "y": {"field": "Miles_per_Gallon", "type": "quantitative", "scale": {"zero": false}},
    "x": {"timeUnit": "year", "field": "Year"}
  }
}
```

## Error Bar with Ticks

Add tick marks at the ends of error bars:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Error bars with tick marks at ends.",
  "data": {"url": "data/cars.json"},
  "mark": {"type": "errorbar", "extent": "ci", "ticks": true},
  "encoding": {
    "y": {"field": "Miles_per_Gallon", "type": "quantitative", "scale": {"zero": false}},
    "x": {"timeUnit": "year", "field": "Year"}
  }
}
```

## Manual Error Bars (Min/Max Range)

For custom error ranges, use a layer of `rule` + `tick` marks:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Manual error bars showing min-max range.",
  "data": {"url": "data/population.json"},
  "transform": [{"filter": "datum.year == 2000"}],
  "layer": [
    {
      "mark": "rule",
      "encoding": {
        "x": {"field": "age", "type": "ordinal"},
        "y": {"aggregate": "min", "field": "people", "type": "quantitative", "title": "population"},
        "y2": {"aggregate": "max", "field": "people"}
      }
    },
    {
      "mark": "tick",
      "encoding": {
        "x": {"field": "age", "type": "ordinal"},
        "y": {"aggregate": "min", "field": "people"},
        "size": {"value": 5}
      }
    },
    {
      "mark": "tick",
      "encoding": {
        "x": {"field": "age", "type": "ordinal"},
        "y": {"aggregate": "max", "field": "people"},
        "size": {"value": 5}
      }
    },
    {
      "mark": "point",
      "encoding": {
        "x": {"field": "age", "type": "ordinal"},
        "y": {"aggregate": "mean", "field": "people"},
        "size": {"value": 2}
      }
    }
  ]
}
```

## Horizontal Error Bars

Swap x and y for horizontal error bars:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Horizontal error bars.",
  "data": {"url": "data/population.json"},
  "transform": [{"filter": "datum.year == 2000"}],
  "layer": [
    {
      "mark": "rule",
      "encoding": {
        "y": {"field": "age", "type": "ordinal"},
        "x": {"aggregate": "min", "field": "people", "type": "quantitative", "title": "population"},
        "x2": {"aggregate": "max", "field": "people"}
      }
    },
    {
      "mark": "tick",
      "encoding": {
        "y": {"field": "age", "type": "ordinal"},
        "x": {"aggregate": "min", "field": "people"},
        "size": {"value": 5}
      }
    },
    {
      "mark": "tick",
      "encoding": {
        "y": {"field": "age", "type": "ordinal"},
        "x": {"aggregate": "max", "field": "people"},
        "size": {"value": 5}
      }
    },
    {
      "mark": "point",
      "encoding": {
        "y": {"field": "age", "type": "ordinal"},
        "x": {"aggregate": "mean", "field": "people"},
        "size": {"value": 2}
      }
    }
  ]
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position of the error bar (quantitative field for automatic computation) |
| `color` | Error bar color |
| `opacity` | Transparency |
| `tooltip` | Hover tooltip content |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `extent` | `"ci"` | Error extent (`"ci"` for confidence interval, `"stdev"` for standard deviation) |
| `ticks` | `false` | Show tick marks at error bar ends |
| `tickSize` | auto | Width of the end ticks |
| `strokeWidth` | `1.5` | Line thickness |

## Gotchas

- The `errorbar` composite mark computes errors automatically from raw data — it does not use `yError`/`xError` encoding channels.
- For manual/custom error ranges (pre-computed min/max), build error bars manually using `layer` with `rule` + `tick` marks and `y`/`y2` or `x`/`x2` encodings.
- Use `"scale": {"zero": false}` when error ranges don't meaningfully include zero.
- Set `extent: "stdev"` for standard deviation-based error bars instead of confidence intervals.
- The `ticks` property adds end-cap marks; `tickSize` controls their width.
