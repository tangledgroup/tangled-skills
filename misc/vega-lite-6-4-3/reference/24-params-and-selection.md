# Parameters and Selections

Parameters are the building blocks of Vega-Lite's grammar of interaction. They can be simple variables or complex selections driven by user input.

## Parameter Basics

```json
{
  "params": [
    {"name": "myVar", "value": 42}
  ]
}
```

### Variable Parameters

Simple named values, reusable throughout the spec. Can be bound to input widgets.

```json
{
  "params": [{"name": "cornerRadius", "value": 5}]
}
```

Use in expressions: `"radius": {"expr": "cornerRadius"}`

### Expression Parameters

Derive parameter values from expressions:

```json
{
  "params": [{"name": "barSize", "expr": "height / 10"}]
}
```

Built-in parameters: `width`, `height`, `padding`, `autosize`, `background`.

## Selection Parameters

Data queries driven by user input (clicks, drags).

### Point Selections

Select individual data points:

```json
{
  "params": [{"name": "pts", "select": {"type": "point"}}]
}
```

**Properties:**

| Property | Description |
|----------|-------------|
| `toggle` | Modifier key to toggle (`"shiftKey"`, `"altKey"`, `false`) |
| `nearest` | Voronoi-based snapping to nearest mark |
| `on` | Event stream (e.g., `"pointerover"`, `"click"`, `"dblclick"`) |
| `clear` | Event to clear selection (default `"dblclick"`, or `false`) |

### Interval Selections

Drag out rectangular regions:

```json
{
  "params": [{"name": "brush", "select": {"type": "interval"}}]
}
```

**Properties:**

| Property | Description |
|----------|-------------|
| `mark` | Brush rectangle styling (`fill`, `stroke`, etc.) |
| `translate` | Pan behavior (default `true`, or custom event stream) |
| `zoom` | Resize behavior (default `"wheel!"`, or `false`) |
| `encodings` | Restrict selection to specific encodings (`["x"]`) |

## Using Parameters

### In Conditional Encoding

Highlight selected data:

```json
{
  "encoding": {
    "color": {
      "condition": {"param": "brush", "field": "Cylinders", "type": "ordinal"},
      "value": "grey"
    }
  }
}
```

### As Predicates

Filter data by selection:

```json
{"transform": [{"filter": {"param": "brush"}}]}
```

Empty selections contain all data by default. Set `{"param": "brush", "empty": false}` to exclude empty selections.

### In Expressions

Reference parameter values:

```json
{
  "mark": {
    "size": {"expr": "sel.Miles_per_Gallon * 10 || 75"},
    "opacity": {"expr": "opacityVar/100"}
  }
}
```

### Scale Domains

Drive scale domains from interval selections:

```json
{
  "encoding": {
    "x": {"scale": {"domain": {"param": "brush"}}}
  }
}
```

For multi-field selections, specify encoding: `{"param": "brush", "encoding": "x"}`.

## Selection Projection

Restrict selections to specific fields or encodings:

```json
{
  "params": [{
    "name": "brush",
    "select": {"type": "interval", "encodings": ["x"]}
  }]
}
```

**Point projection with fields:**

```json
{
  "params": [{"name": "pts", "select": {"type": "point", "fields": ["Cylinders", "Year"]}}]
}
```

## Binding

### Input Widgets

Bind variables/point selections to sliders, dropdowns:

```json
{
  "params": [{
    "name": "opacityVar",
    "value": 50,
    "bind": {"input": "range", "min": 1, "max": 100}
  }]
}
```

**Multi-field binding:**

```json
{
  "params": [{
    "name": "CylYr",
    "select": {"type": "point", "fields": ["Cylinders", "Year"]},
    "bind": {
      "Cylinders": {"input": "range", "min": 3, "max": 8, "step": 1},
      "Year": {"input": "range", "min": 1969, "max": 1981, "step": 1}
    }
  }]
}
```

### Legend Binding

```json
{
  "params": [{
    "name": "sel",
    "select": {"type": "point", "fields": ["Origin"]},
    "bind": "legend"
  }]
}
```

### Scale Binding (Pan/Zoom)

```json
{
  "params": [{
    "name": "region",
    "select": "interval",
    "bind": "scales"
  }]
}
```

## Resolution

For selections in facet/repeat views:

| Value | Behavior |
|-------|----------|
| `"global"` (default) | Single selection across all views |
| `"union"` | Per-view selections, highlight if in any |
| `"intersect"` | Per-view selections, highlight only if in all |

```json
{
  "params": [{
    "name": "brush",
    "select": {"type": "interval", "resolve": "union"}
  }]
}
```

## Initialization

Set initial selection values:

**Point selection:** `"value": [{"symbol": "AAPL"}]`

**Interval selection:** `"value": {"x": [55, 160], "y": [13, 37]}`

## Common Patterns

### Hover Highlight

```json
{
  "params": [{"name": "hover", "select": {"type": "point", "on": "pointerover"}}],
  "encoding": {
    "color": {"condition": {"param": "hover", "field": "Origin"}, "value": "grey"}
  }
}
```

### Paintbrush (Multi-Select)

```json
{
  "params": [{
    "name": "paintbrush",
    "select": {"type": "point", "on": "pointerover", "nearest": true}
  }]
}
```

### Overview + Detail

Bottom view has interval selection, top view uses it for scale domain:

```json
{
  "vconcat": [
    {"mark": "area", "encoding": {"x": {"scale": {"domain": {"param": "brush"}}}}},
    {
      "params": [{"name": "brush", "select": {"type": "interval", "encodings": ["x"]}}],
      "mark": "area"
    }
  ]
}
```

### Crossfilter

Selection in one view filters another via `{"filter": {"param": "brush"}}`.

### Dashboard (Linked Selections)

Same named selection across multiple views in hconcat/vconcat:

```json
{
  "hconcat": [
    {"params": [{"name": "brush", "select": {"type": "interval", "encodings": ["y"]}}], "mark": "bar"},
    {"params": [{"name": "brush", "select": {"type": "interval", "encodings": ["y"]}}], "mark": "bar"},
    {"params": [{"name": "brush", "select": "interval"}], "mark": "point"}
  ]
}
```

### Nearest Index Line

Vertical rule following cursor via `nearest`:

```json
{
  "params": [{
    "name": "index",
    "select": {"type": "point", "encodings": ["x"], "on": "pointermove", "nearest": true}
  }]
}
```

Layer with invisible points to trigger selection, then filter rule/text by `index`.

### Pan/Zoom SPLOM

Two selections: one for brushing (shift-key), one for pan/zoom (normal):

```json
{
  "params": [
    {
      "name": "brush",
      "select": {"type": "interval", "resolve": "union", "on": "[pointerdown[event.shiftKey], window:pointerup] > window:pointermove!"}
    },
    {"name": "grid", "select": {"type": "interval", "resolve": "global"}, "bind": "scales"}
  ]
}
```

### Line Hover (Transparent Layer)

Layer with thick transparent lines for easy hover trigger:

```json
{
  "layer": [
    {
      "params": [{"name": "hover", "select": {"type": "point", "fields": ["symbol"], "on": "pointerover"}}],
      "mark": {"type": "line", "strokeWidth": 8, "stroke": "transparent"}
    },
    {"mark": "line"}
  ]
}
```

## Selection Config

Set defaults globally:

```json
{
  "config": {
    "selection": {
      "point": {"toggle": "shiftKey"},
      "interval": {"translate": false, "zoom": false}
    }
  }
}
```
