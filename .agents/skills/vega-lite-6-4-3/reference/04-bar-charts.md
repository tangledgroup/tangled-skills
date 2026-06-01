# Bar Charts

Bar marks display quantitative values as rectangular bars. They support simple bars, stacked bars, grouped bars, ranged bars (Gantt), and more.

## Basic Syntax

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "bar",
  "encoding": {
    "x": {"field": "Origin", "type": "nominal"},
    "y": {"aggregate": "count", "type": "quantitative"}
  }
}
```

## Bar Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `orient` | string | `"vertical"` (default) or `"horizontal"` |
| `align` | number | Text alignment within bar (0-1) |
| `baseline` | string | Baseline for text marks on bars |
| `width` / `height` | number | Bar dimensions |
| `binSpacing` | number | Gap between bars (default 1); set to 0 for no gaps |
| `cornerRadius` | number | Radius of all corners |
| `cornerRadiusEnd` | number | Radius at the end (value) corner |
| `cornerRadiusTopLeft` / `TopRight` / `BottomLeft` / `BottomRight` | number | Individual corner radii |

## Bar Config

| Property | Type | Description |
|----------|------|-------------|
| `continuousBandSize` | number | Band size for bars on continuous scales (default 18) |
| `discreteBandSize` | number | Band size for bars on discrete scales (uses step-based sizing) |
| `minBandSize` | number | Minimum band size |

## Chart Patterns

### Simple Bar Chart

Map a quantitative field to one axis, nominal/ordinal to the other:

```json
{
  "data": {"values": [{"a": "A", "b": 28}, {"a": "B", "b": 55}]},
  "mark": "bar",
  "encoding": {
    "x": {"field": "a", "type": "nominal"},
    "y": {"field": "b", "type": "quantitative"}
  }
}
```

### 1D Bar (Single Dimension)

Only one positional encoding — aggregates all data into a single bar:

```json
{
  "data": {"url": "data/population.json"},
  "transform": [{"filter": "datum.year == 2000"}],
  "mark": "bar",
  "encoding": {
    "x": {"aggregate": "sum", "field": "people", "title": "population"}
  }
}
```

### Aggregate Bars

Use `aggregate` on the quantitative axis. Grouping is by the other encoded field:

```json
{
  "data": {"url": "data/population.json"},
  "transform": [{"filter": "datum.year == 2000"}],
  "mark": "bar",
  "encoding": {
    "y": {"field": "age"},
    "x": {"aggregate": "sum", "field": "people", "title": "population"}
  }
}
```

### Grouped Bars (Offset)

Use `xOffset` or `yOffset` to group bars side-by-side:

```json
{
  "data": {"values": [
    {"category": "A", "group": "x", "value": 0.1},
    {"category": "A", "group": "y", "value": 0.6}
  ]},
  "mark": "bar",
  "encoding": {
    "x": {"field": "category"},
    "y": {"field": "value", "type": "quantitative"},
    "xOffset": {"field": "group"},
    "color": {"field": "group"}
  }
}
```

### Stacked Bars (Default with Color)

Adding `color` creates stacked bars by default:

```json
{
  "data": {"url": "data/population.json"},
  "transform": [
    {"filter": "datum.year == 2000"},
    {"calculate": "datum.sex == 2 ? 'Female' : 'Male'", "as": "gender"}
  ],
  "mark": "bar",
  "encoding": {
    "y": {"aggregate": "sum", "field": "people"},
    "x": {"field": "age"},
    "color": {"field": "gender"}
  }
}
```

### Normalized (100%) Stacked Bars

Set `stack: "normalize"` on the quantitative encoding:

```json
{
  "encoding": {
    "y": {"aggregate": "sum", "field": "people", "stack": "normalize"},
    "x": {"field": "age"},
    "color": {"field": "gender"}
  }
}
```

Other stack modes: `"zero"` (default), `"center"` (streamgraph-style).

### Layered Bars (No Stacking)

Set `stack: null` and use semi-transparent opacity:

```json
{
  "mark": {"type": "bar", "opacity": 0.7},
  "encoding": {
    "y": {"aggregate": "sum", "field": "people", "stack": null},
    "x": {"field": "age"},
    "color": {"field": "gender"}
  }
}
```

### Temporal Bars

With temporal x-axis, bars use `continuousBandSize` config for width. Cast to `"ordinal"` type for discrete scale:

```json
{
  "mark": "bar",
  "encoding": {
    "x": {"timeUnit": "month", "field": "date", "type": "ordinal"},
    "y": {"aggregate": "count"}
  }
}
```

Center bars within time intervals using `bandPosition: 0.5`.

### Rounded Corners

```json
{
  "mark": {"type": "bar", "cornerRadiusEnd": 4}
}
```

Or individual corners: `cornerRadiusTopLeft`, `cornerRadiusTopRight`, etc.

### Negative Values

Hide axis domain and use conditional grid for zero baseline:

```json
{
  "encoding": {
    "x": {"axis": {"domain": false, "ticks": false}},
    "y": {"axis": {
      "gridColor": {
        "condition": {"test": "datum.value === 0", "value": "black"},
        "value": "#ddd"
      }
    }}
  }
}
```

### Ranged Bars (Gantt Charts)

Use `x2` or `y2` for ranged bars:

```json
{
  "data": {"values": [
    {"task": "A", "start": 1, "end": 3},
    {"task": "B", "start": 3, "end": 8}
  ]},
  "mark": "bar",
  "encoding": {
    "y": {"field": "task", "type": "ordinal"},
    "x": {"field": "start", "type": "quantitative"},
    "x2": {"field": "end"}
  }
}
```

### Binned Bars (Pre-binned Data)

When data is already binned with start/end fields:

```json
{
  "encoding": {
    "x": {"field": "bin_start", "bin": {"binned": true, "step": 2}},
    "x2": {"field": "bin_end"},
    "y": {"field": "count", "type": "quantitative"}
  }
}
```

### Histograms

Map a binned quantitative field to x, aggregate count to y:

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "bar",
  "encoding": {
    "x": {"field": "Horsepower", "bin": true},
    "y": {"aggregate": "count"}
  }
}
```

Set `binSpacing: 0` on the mark for no gaps between bars.

### Bullet Charts

Use ranged bars with a measure bar overlaid:

```json
{
  "layer": [
    {"mark": "bar", "encoding": {"y": {"field": "category"}, "x": {"field": "target"}, "x2": {"field": "max"}}},
    {"mark": "bar", "encoding": {"y": {"field": "category"}, "x": {"field": "actual"}}}
  ]
}
```

### Population Pyramids

Diverging stacked bars — negative values on one side, positive on the other.

### Relative Bar Width

Set `width` as proportion of band for temporal bars:

```json
{
  "mark": "bar",
  "encoding": {
    "x": {"timeUnit": "month", "field": "date"},
    "width": {"value": 0.7}
  }
}
```

### Configuring Bars Globally

```json
{
  "config": {
    "bar": {"cornerRadius": 3, "continuousBandSize": 12}
  }
}
```
