# Interactivity Reference

Vega-Lite supports interactive selections and parameters for brushing, linking, highlighting, and dynamic filtering.

## Point Selection

Select individual data points on click:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Scatter plot with point selection.",
  "data": {"url": "data/cars.json"},
  "params": [
    {"name": "select", "select": {"type": "point", "toggle": "ctrl"}}
  ],
  "mark": "circle",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "color": {
      "condition": {"param": "select", "value": "#1f77b4"},
      "value": "#cccccc"
    }
  }
}
```

## Interval Selection (Brushing)

Drag to select a range of data:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Brush selection on scatter plot.",
  "data": {"url": "data/cars.json"},
  "params": [
    {
      "name": "brush",
      "select": {
        "type": "interval",
        "encodings": ["x", "y"]
      }
    }
  ],
  "mark": "circle",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "color": {
      "condition": {"param": "brush", "value": "#1f77b4"},
      "value": "#cccccc"
    }
  }
}
```

## Brush and Link (Cross-Filtering)

Use a brush view to filter another view:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Brush and link between two views.",
  "data": {"url": "data/cars.json"},
  "params": [
    {"name": "brush", "select": {"type": "interval", "encodings": ["x"]}}
  ],
  "layer": [
    {
      "mark": "circle",
      "encoding": {
        "x": {"field": "Horsepower", "type": "quantitative"},
        "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
        "color": {
          "condition": {"param": "brush", "value": "#1f77b4"},
          "value": "#cccccc"
        }
      }
    },
    {
      "mark": "bar",
      "encoding": {
        "x": {"field": "Origin", "type": "nominal"},
        "y": {"aggregate": "count"},
        "opacity": {
          "condition": {"param": "brush", "value": 1},
          "value": 0.2
        }
      }
    }
  ]
}
```

## Nearest Selection

Highlight nearest data point on hover:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Nearest point highlight on hover.",
  "data": {"url": "data/cars.json"},
  "params": [
    {
      "name": "hover",
      "select": {"type": "single", "nearest": true, "on": "mouseenter"}
    }
  ],
  "mark": "circle",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "color": {
      "condition": {"param": "hover", "value": "#d62728"},
      "value": "#1f77b4"
    },
    "size": {
      "condition": {"param": "hover", "value": 100},
      "value": 30
    }
  }
}
```

## Toggle Selection

Multi-select with toggle behavior:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Toggle selection for multi-select.",
  "data": {"url": "data/cars.json"},
  "params": [
    {
      "name": "filter",
      "select": {"type": "point", "fields": ["Origin"], "toggle": false}
    }
  ],
  "mark": "circle",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "opacity": {
      "condition": {"param": "filter", "value": 1},
      "value": 0.1
    }
  }
}
```

## Parameters with Bind

Bind parameters to UI controls:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Slider parameter for filtering.",
  "data": {"url": "data/cars.json"},
  "params": [
    {
      "name": "hpRange",
      "select": {"type": "interval", "encodings": ["x"]},
      "bind": {"input": "range", "min": 40, "max": 250, "step": 10}
    }
  ],
  "mark": "circle",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

## Selection Types

| Type | Description |
|---|---|
| `point` | Select individual data points |
| `interval` | Drag to select a rectangular range |
| `single` | Select one item at a time |
| `multi` | Select multiple items (shift-click) |

## Selection Properties

| Property | Description |
|---|---|
| `encodings` | Which encodings the selection applies to (`["x"]`, `["x", "y"]`) |
| `fields` | Data fields for point selection |
| `toggle` | Key for toggling (`"ctrl"`, `"shift"`, `false`) |
| `on` | Trigger event (`"click"`, `"mouseenter"`, `"dblclick"`) |
| `clear` | Clear selection on event (`true`, `"click"`) |
| `nearest` | Snap to nearest data point |
| `empty` | Default state (`"none"`, `"all"`) |

## Condition Expressions

Conditions enable dynamic encoding based on selection state:

```vega-lite
"color": {
  "condition": {"param": "brush", "value": "#1f77b4"},
  "value": "#cccccc"
}
```

Pattern: selected items get the `condition` value, unselected get the default `value`.

## Gotchas

- Selections require Vega 5.x — ensure compatible versions of vega and vega-lite.
- The `params` array defines named selections; reference them by name in `condition` expressions.
- `toggle: "ctrl"` requires holding Ctrl to add/remove from selection; `toggle: false` replaces selection on each click.
- For brush-and-link across concatenated views, define `params` at the top level (not inside individual views).
- `nearest: true` works best with `on: "mouseenter"` for hover highlighting.
- Selections can reference specific encodings (`encodings: ["x"]`) to limit the selection scope to one axis.
