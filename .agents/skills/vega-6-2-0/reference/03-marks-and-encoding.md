# Marks & Encoding

## Contents
- Mark Types
- Top-Level Mark Properties
- Encode Sets
- Visual Encoding
- From (Data Source)
- Faceting
- Reactive Geometry
- Value References
- Production Rules

## Mark Types

Vega supports 12 graphical mark types:

| Type | Description |
|------|-------------|
| `rect` | Rectangles (bar charts, timelines) |
| `line` | Stroked lines (change over time) |
| `area` | Filled areas with horizontal/vertical alignment |
| `symbol` | Plotting symbols (circles, squares, etc.) |
| `arc` | Circular arcs (pie/donut slices) |
| `text` | Text labels with configurable fonts/alignment/angle |
| `group` | Container for other marks, sub-plots, small multiples |
| `path` | Arbitrary paths or polygons (SVG path syntax) |
| `rule` | Line segments (axis ticks, grid lines) |
| `shape` | Variant of path for faster cartographic drawing |
| `image` | Images, icons, photographs |
| `trail` | Lines that change size based on data |

## Top-Level Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `type` | String | **Required.** Mark type (one of the 12 above) |
| `from` | Object | Data source for this mark set |
| `encode` | Encode | Visual encoding rules |
| `interactive` | Boolean / Signal | If false, marks don't generate events (default: true) |
| `key` | Field | Data field as unique key for object constancy with transitions |
| `name` | String | Unique name; also used as CSS class on SVG group element |
| `clip` | Boolean / Object / Signal | Clip marks to region. `true` = enclosing group bounds. Object: `{path: "..."}` or `{sphere: "projName"}` |
| `sort` | Compare | Sort comparator for rendering order (evaluated after encodings) |
| `transform` | Transform[] | Post-encoding transforms on scenegraph items |
| `style` | String / String[] | Named style collections from config; applied to enter encoding |
| `zindex` | Number | Layering z-index relative to other marks/axes/legends (default: 0) |
| `role` | String | Metadata string for layout guidance; do not set unless targeting specific layout effects |
| `on` | Trigger[] | Triggers modifying mark properties on signal changes |
| `aria` | Boolean | Include ARIA attributes for SVG output (default: true, ≥5.11) |
| `description` | String | Text description for ARIA accessibility (≥5.11) |

## Encode Sets

Mark property definitions are organized into named encoding sets:

| Set | When Evaluated |
|-----|---------------|
| `enter` | When a mark item is first instantiated from new data |
| `update` | For all existing (non-exiting) mark instances, on every update |
| `exit` | When backing data is removed and the mark exits the scene |
| `hover` | When mouse hovers over a mark item (requires hover processing enabled) |

Custom encoding sets with arbitrary names are also allowed. Invoke them via `View.run()` or signal event handlers with an `"encode"` directive.

### Example Encode Block

```json
{
  "type": "rect",
  "from": {"data": "table"},
  "encode": {
    "enter": {
      "x": {"scale": "xscale", "field": "category"},
      "width": {"scale": "xscale"},
      "y": {"scale": "yscale", "field": "value"},
      "y2": {"scale": "yscale", "value": 0},
      "fill": {"value": "steelblue"}
    },
    "update": {
      "fillOpacity": {"value": 1}
    },
    "hover": {
      "fill": {"value": "darkblue"},
      "fillOpacity": {"value": 0.8}
    },
    "exit": {
      "y": {"scale": "yscale", "value": 0},
      "opacity": {"value": 0}
    }
  }
}
```

## Visual Encoding

Each mark type supports standardized encoding channels. Common channels include:

| Channel | Description | Example Types |
|---------|-------------|---------------|
| `x` / `y` | Position coordinates | All marks |
| `x2` / `y2` | Secondary position (for rules, rects) | rect, rule, trail |
| `width` / `height` | Dimension sizes | rect, group |
| `fill` | Fill color | rect, arc, area, path, shape |
| `stroke` | Stroke color | line, path, shape, rule, text |
| `strokeWidth` | Stroke width | All stroked marks |
| `opacity` / `fillOpacity` / `strokeOpacity` | Transparency | All marks |
| `text` | Label text | text mark |
| `shape` | Symbol shape | symbol mark |
| `size` | Size/area/radius | symbol, trail, image |
| `angle` | Rotation angle | symbol, text, rect |

## From (Data Source)

### Basic Data Source
```json
"from": {"data": "table"}
```

### Faceting
Splits a data source among multiple group mark items:

```json
"from": {
  "data": "source",
  "facet": {
    "name": "facets",
    "groupby": ["category"]
  }
}
```

| Property | Type | Description |
|----------|------|-------------|
| `name` | String | **Required.** Name of generated facet data source |
| `data` | String | **Required.** Source dataset name |
| `field` | Field | For pre-faceted data: field containing array of sub-values |
| `groupby` | Field / Field[] | For data-driven facets: fields to partition by |
| `aggregate` | Object | Optional aggregate params (fields, ops, as, cross) |

### Reactive Geometry
Marks can serve as backing data for other marks. The source mark must have a `name` property:

```json
{
  "name": "baseMarks",
  "type": "point",
  "from": {"data": "source"},
  "encode": {...}
},
{
  "type": "text",
  "from": {"data": "baseMarks"},
  "encode": {
    "update": {
      "x": {"field": "x", "offset": 4},
      "y": {"field": "y"},
      "text": {"field": "datum.label"}
    }
  }
}
```

## Value References

Specify mark property values:

| Syntax | Description |
|--------|-------------|
| `{"value": "left"}` | Literal constant |
| `{"field": "amount"}` | Data field value |
| `{"scale": "yscale", "field": "amount"}` | Scale-transformed data field |
| `{"signal": "hypot(datum.a, datum.b)"}` | Signal expression value |

## Production Rules

Conditional "if-then-else" chains for visual properties:

```json
"fill": [
  {
    "test": "indata('selectedPoints', 'key', datum.key)",
    "scale": "c",
    "field": "species"
  },
  {"value": "grey"}
]
```

The first rule whose `test` expression evaluates to true is used. The final element without a `test` serves as the "else" default (defaults to `null` if omitted).
