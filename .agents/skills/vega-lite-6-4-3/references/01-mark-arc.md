# Arc Mark Reference

The `arc` mark renders pie charts, donut charts, and radial visualizations using polar coordinates.

## Basic Pie Chart

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A simple pie chart with embedded data.",
  "data": {
    "values": [
      {"category": "A", "value": 4},
      {"category": "B", "value": 6},
      {"category": "C", "value": 10},
      {"category": "D", "value": 3}
    ]
  },
  "mark": "arc",
  "encoding": {
    "theta": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

## Donut Chart

Use `innerRadius` on the mark to create a donut (ring) chart:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A donut chart with inner radius.",
  "data": {
    "values": [
      {"category": "A", "value": 4},
      {"category": "B", "value": 6},
      {"category": "C", "value": 10}
    ]
  },
  "mark": {"type": "arc", "innerRadius": 50},
  "encoding": {
    "theta": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

## Pie Chart with Labels

Layer text marks on arcs for labels:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Pie chart with percentage labels.",
  "data": {
    "values": [
      {"category": "A", "value": 4},
      {"category": "B", "value": 6},
      {"category": "C", "value": 10}
    ]
  },
  "layer": [
    {
      "mark": "arc",
      "encoding": {
        "theta": {"field": "value", "type": "quantitative"},
        "color": {"field": "category", "type": "nominal"}
      }
    },
    {
      "mark": "text",
      "encoding": {
        "theta": {"field": "value", "type": "quantitative"},
        "text": {"field": "category"},
        "color": {"value": "white"}
      }
    }
  ]
}
```

## Pyramid Chart

Use `radius` for a pyramid-style chart where both theta and radius encode data:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A pyramid chart using radius encoding.",
  "data": {
    "values": [
      {"category": "A", "value": 4, "group": "X"},
      {"category": "B", "value": 6, "group": "X"},
      {"category": "C", "value": 10, "group": "Y"}
    ]
  },
  "mark": "arc",
  "encoding": {
    "theta": {"field": "value", "type": "quantitative"},
    "radius": {"field": "group", "type": "nominal"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `theta` | Arc angle (proportional to quantitative field) |
| `theta2` | End angle for partial arcs |
| `radius` | Outer radius (nominal grouping or quantitative size) |
| `color` | Slice color (nominal categories) |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `innerRadius` | `0` | Inner radius in pixels (donut effect) |
| `outerRadius` | auto | Outer radius in pixels |
| `cornerRadius` | `0` | Corner rounding for arc edges |

## Gotchas

- Arc marks always use polar coordinates — there is no x/y axis.
- `theta` values are automatically normalized to sum to 360° (full circle). Use `"stack": "normalize"` explicitly if needed.
- For pie chart labels, the text mark's `theta` encoding aligns with arc slices.
- Donut charts (`innerRadius > 0`) work best when you have a center label or annotation.
