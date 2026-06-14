# Text Mark Reference

The `text` mark renders text labels and annotations. Use it for data labels, axis annotations, titles within charts, and rich tooltips.

## Basic Text Labels

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Text labels showing mean horsepower by origin.",
  "data": {"url": "data/cars.json"},
  "width": 50,
  "mark": "text",
  "encoding": {
    "y": {"field": "Origin", "type": "ordinal"},
    "text": {"aggregate": "mean", "field": "Horsepower", "type": "quantitative", "format": ".2f"}
  }
}
```

## Data Labels on Bar Chart

Layer text on bars:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Bar chart with value labels.",
  "data": {
    "values": [
      {"category": "A", "value": 4},
      {"category": "B", "value": 6},
      {"category": "C", "value": 10}
    ]
  },
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"field": "category", "type": "nominal"},
        "y": {"field": "value", "type": "quantitative"}
      }
    },
    {
      "mark": "text",
      "encoding": {
        "x": {"field": "category", "type": "nominal"},
        "y": {"field": "value", "type": "quantitative"},
        "text": {"field": "value", "type": "quantitative"},
        "dy": {"value": -10}
      }
    }
  ]
}
```

## Text with Formatting

Use `format` for number/date formatting:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Text with formatted numbers.",
  "data": {
    "values": [
      {"label": "Revenue", "value": 1234567},
      {"label": "Cost", "value": 987654}
    ]
  },
  "mark": "text",
  "encoding": {
    "y": {"field": "label", "type": "nominal"},
    "text": {"field": "value", "format": "$,.0f"}
  }
}
```

## Text in Polar Coordinates

Text on arc marks (pie chart labels):

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Pie chart with text labels.",
  "data": {
    "values": [
      {"category": "A", "value": 4},
      {"category": "B", "value": 6},
      {"category": "C", "value": 10}
    ]
  },
  "mark": "text",
  "encoding": {
    "theta": {"field": "value", "type": "quantitative"},
    "text": {"field": "category"},
    "color": {"value": "white"}
  }
}
```

## Key Channels

| Channel | Role |
|---|---|
| `x`, `y` | Position coordinates |
| `text` | Text content (field or aggregate) |
| `color` | Text color |
| `size` | Font size in pixels |
| `angle` | Rotation angle in degrees |
| `theta`, `radius` | Polar position for arc-aligned text |
| `dy`, `dx` | Offset from anchor position |

## Mark Properties

| Property | Default | Description |
|---|---|---|
| `align` | `"center"` | Horizontal alignment (`left`, `center`, `right`) |
| `baseline` | `"alphabetic"` | Vertical baseline (`top`, `middle`, `bottom`, `line-top`, `line-bottom`) |
| `fontSize` | `11` | Font size in pixels |
| `font` | — | Font family string |
| `fontWeight` | `"normal"` | Font weight (`bold`, `normal`, numeric) |
| `limit` | — | Maximum text width (truncates with ellipsis) |
| `lineHeight` | — | Line height for multiline text |

## Text Formatting

| Format | Example | Output |
|---|---|---|
| `.2f` | `123.456` | `123.46` |
| `$,.0f` | `1234567` | `$1,234,567` |
| `.1%` | `0.857` | `85.7%` |
| `%Y-%m-%d` | Date object | `2024-01-15` |
| `%b %Y` | Date object | `Jan 2024` |

## Gotchas

- Text marks do not wrap automatically — use `limit` to constrain width and get ellipsis truncation.
- The `text` encoding channel can reference a field, an aggregate, or a constant value.
- Use `dy` (not `y`) for vertical offset from the anchor position — this avoids conflicts with the y-axis scale.
- For multiline text, include `\n` in the data values and set `lineHeight`.
- Text in polar coordinates uses `theta`/`radius` channels and aligns with arc marks.
