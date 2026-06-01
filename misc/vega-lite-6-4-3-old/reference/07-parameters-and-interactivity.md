# Parameters and Interactivity

## Contents

- Parameters Overview
- Value Parameters
- Expr Parameters
- Selection Parameters
- Point Selections
- Interval Selections
- Bind
- Using Selections in Encodings
- Interactive Patterns

## Parameters Overview

Parameters are named variables that map user input to data queries or computed values. Defined in the `params` array at spec or layer level.

```json
{
  "params": [
    {"name": "highlight", "select": {"type": "point", "on": "pointerover"}},
    {"name": "brush", "select": "interval"}
  ],
  ...
}
```

Three parameter types: `value` (constant), `expr` (computed), and `select` (user interaction).

## Value Parameters

Simple constant variables:

```json
{
  "params": [
    {"name": "baseline", "value": 0}
  ]
}
```

Reference in expressions: `param.baseline`.

## Expr Parameters

Computed parameters using Vega expressions:

```json
{
  "params": [
    {
      "name": "meanPrice",
      "value": {"expr": "aggregate(data('source-0'), 'price', mean)"}
    }
  ]
}
```

## Selection Parameters

Map user interaction to data queries. Two types: `point` (discrete selection) and `interval` (range/brush selection).

### Point Selections

Select individual data points on click, hover, or other events.

```json
{
  "params": [
    {
      "name": "highlight",
      "select": {
        "type": "point",
        "on": "pointerover"
      }
    },
    {
      "name": "select",
      "select": "point"
    }
  ]
}
```

### Point Selection Properties

| Property | Type | Description |
|----------|------|-------------|
| `type` | String | `"point"` or `"single"` (single selection, replaces previous) |
| `on` | String | Vega event stream: `"click"`, `"pointerover"`, `"dblclick"`, etc. Default: `"click"` |
| `fields` | String[] | Fields to include in selection. If omitted, all encoding fields are used |
| `encodings` | String[] | Encoding channels to include: `["x"]`, `["x", "y"]` |
| `clear` | Boolean \| String | Clear selection on event. Default: `true` for `"click"`, `false` otherwise |
| `toggle` | Boolean \| String | Toggle behavior: `"shift"` (default, shift-click to add), `"ctrl"`, `"meta"`, `false` (no toggle) |
| `empty` | Boolean | Whether empty selection is allowed. Default: `true` |
| `nearest` | Boolean | Select nearest data point. Default: `false` |
| `resolve` | String | `"global"` (default), `"union"`, or `"intersect"` for multi-view resolution |
| `persist` | Boolean | Persist selection across views. Default: `true` |

### Interval Selections

Select a range of data by dragging/brushing.

```json
{
  "params": [
    {
      "name": "brush",
      "select": "interval"
    }
  ]
}
```

### Interval Selection Properties

| Property | Type | Description |
|----------|------|-------------|
| `type` | String | `"interval"` |
| `on` | String | Vega event stream. Default: `"mousedown > mousemove!mousedown > mouseup"` |
| `encodings` | String[] | Channels the brush applies to: `["x"]`, `["y"]`, `["x", "y"]` |
| `translate` | Boolean \| String[] | Enable dragging to translate. Default: `true` |
| `zoom` | Boolean \| String | Enable zooming: `"wheel"` or `false`. Default: `false` |
| `extent` | Object \| String | Brush extent constraints. `"view"` (default) or object with `{"x": [min, max], "y": [min, max]}` |
| `empty` | String | Behavior when no selection: `"none"` (default), `"all"`, or `"reset"` |
| `resolve` | String | `"global"` (default), `"union"`, or `"intersect"` |
| `brush` | Object | Brush style: `{"stroke": ..., "fill": ...}` |
| `size` | Number | Size of interval selection indicator. Default: `2` |
| `interval` | String | Interval modifier key for zoom/translate: `"shift"`, `"ctrl"`, `"meta"` |
| `value` | Object | Initial brush value: `{"x": [55, 160], "y": [13, 37]}` |
| `bind` | String \| Object | Bind to input element or `"scales"` for pan/zoom |

## Bind

Bind parameters to HTML input elements or scale interactions.

### Input Element Binding

```json
{
  "params": [
    {
      "name": "year",
      "value": 1980,
      "bind": {"input": "range", "min": 1950, "max": 2010, "step": 1}
    }
  ]
}
```

### Input Types

| Type | Description |
|------|-------------|
| `select` | Dropdown select |
| `radio` | Radio buttons |
| `checkbox` | Checkbox (for boolean params) |
| `range` | Slider input |

### Legend Binding

Bind parameter to legend interactions:

```json
{
  "params": [
    {
      "name": "filter",
      "select": {"type": "point", "fields": ["category"]},
      "bind": "legend"
    }
  ]
}
```

### Scale Binding (Pan/Zoom)

```json
{
  "params": [
    {
      "name": "grid",
      "select": "interval",
      "bind": "scales"
    }
  ]
}
```

Enables pan (drag) and zoom (scroll wheel) on the entire view.

## Using Selections in Encodings

### Conditional Encoding

Change visual properties based on selection state:

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

Items inside `brush` selection show colored by Cylinders; items outside are grey.

### Multi-Condition

```json
{
  "encoding": {
    "strokeWidth": {
      "condition": [
        {"param": "select", "empty": false, "value": 2},
        {"param": "highlight", "empty": false, "value": 1}
      ],
      "value": 0
    }
  }
}
```

### Filter by Selection

```json
{
  "layer": [
    {
      "params": [{"name": "brush", "select": {"type": "interval", "encodings": ["x"]}}],
      "transform": [{"filter": {"param": "brush"}}],
      "mark": "bar",
      "encoding": {
        "x": {"field": "distance", "bin": {"maxbins": 20}},
        "y": {"aggregate": "count"}
      }
    }
  ]
}
```

### Test Predicate (Non-Selection Condition)

```json
{
  "encoding": {
    "color": {
      "condition": {"test": "datum.open < datum.close", "value": "#06982d"},
      "value": "#ae1325"
    }
  }
}
```

## Interactive Patterns

### Hover Highlighting

```json
{
  "params": [
    {"name": "hover", "select": {"type": "point", "on": "pointerover"}}
  ],
  "mark": "point",
  "encoding": {
    "color": {
      "condition": {"param": "hover", "field": "Origin", "type": "nominal"},
      "value": "#ccc"
    }
  }
}
```

### Brush and Link

```json
{
  "params": [
    {"name": "brush", "select": "interval"}
  ],
  "mark": "point",
  "encoding": {
    "color": {
      "condition": {"param": "brush", "field": "Cylinders", "type": "ordinal"},
      "value": "grey"
    }
  }
}
```

### Crossfilter (Multi-View Filtering)

Use `repeat` or `concat` with shared selection parameter:

```json
{
  "data": {"url": "data/flights-2k.json"},
  "repeat": {"column": ["distance", "delay", "time"]},
  "spec": {
    "layer": [
      {
        "params": [
          {"name": "brush", "select": {"type": "interval", "encodings": ["x"]}}
        ],
        "transform": [{"filter": {"param": "brush"}}],
        "mark": "bar",
        "encoding": {
          "x": {"field": {"repeat": "column"}, "bin": {"maxbins": 20}},
          "y": {"aggregate": "count", "axis": null}
        }
      }
    ]
  }
}
```

### Pan and Zoom

```json
{
  "params": [
    {"name": "grid", "select": "interval", "bind": "scales"}
  ],
  "mark": "circle",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative", "scale": {"domain": [75, 150]}},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative", "scale": {"domain": [20, 40]}}
  }
}
```

### Overview + Detail

Use `vconcat` with interval selection on overview, filtering detail view.

### Dynamic Color Legend

Bind a point selection to legend and use condition encoding:

```json
{
  "params": [
    {"name": "filter", "select": {"type": "point", "fields": ["Origin"]}, "bind": "legend"}
  ],
  "mark": "point",
  "encoding": {
    "color": {
      "condition": {"param": "filter", "field": "Origin", "type": "nominal"},
      "value": "#ddd"
    }
  }
}
```
