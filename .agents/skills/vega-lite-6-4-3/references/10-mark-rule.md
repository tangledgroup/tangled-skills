# Rule Mark Reference

The `rule` mark renders thin lines (rules), typically used for reference lines, thresholds, and error bar stems.

## Horizontal Reference Line

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Horizontal reference line at mean value.",
  "data": {"url": "data/cars.json"},
  "mark": {"type": "rule", "color": "red"},
  "encoding": {
    "y": {"aggregate": "mean", "field": "Horsepower", "type": "quantitative"}
  }
}
```

## Vertical Reference Line

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Vertical reference line.",
  "data": {"url": "data/cars.json"},
  "mark": {"type": "rule", "color": "red", "strokeDash": [4, 4]},
  "encoding": {
    "x": {"aggregate": "mean", "field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

## Ranged Rule (Error Bar Stem)

Use `y` and `y2` for a vertical rule spanning a range:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Ranged rules showing min-max per category.",
  "data": {"url": "data/population.json"},
  "transform": [{"filter": "datum.year == 2000"}],
  "mark": "rule",
  "encoding": {
    "x": {"field": "age", "type": "ordinal"},
    "y": {"aggregate": "min", "field": "people", "type": "quantitative"},
    "y2": {"aggregate": "max", "field": "people"}
  }
}
```

## Multiple Reference Lines

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Multiple horizontal rules by category.",
  "data": {"url": "data/cars.json"},
  "mark": {"type": "rule", "color": "red"},
  "encoding": {
    "y": {"aggregate": "mean", "field": "Horsepower", "type": "quantitative"},
    "color": {"field": "Origin", "type": "nominal"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Start position of the rule |
| `x2`, `y2` | End position (for ranged rules) |
| `color` | Rule color |
| `size` | Line width in pixels |
| `opacity` | Transparency |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `strokeDash` | — | Dash pattern `[on, off]` array |
| `strokeWidth` | `1.5` | Line thickness |
| `strokeCap` | `"butt"` | Line cap style (`round`, `square`) |

## Gotchas

- Rule marks are thin lines with no fill — use `bar` or `rect` for thick bands.
- Single-position rules (only `x` or `y`) span the entire axis range.
- Ranged rules (`x`/`x2` or `y`/`y2`) draw between two positions.
- Combine with `tick` marks at endpoints to create error bars.
- `strokeDash` creates dashed lines, useful for distinguishing reference lines from data lines.
