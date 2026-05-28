# Encoding Channels

## Contents

- Channel Definition Types
- Position Channels
- Position Offset Channels
- Polar Position Channels
- Geographic Position Channels
- Mark Property Channels
- Text and Tooltip Channels
- Hyperlink, Description, Detail, Key, Order Channels
- Facet Channels

## Channel Definition Types

Each encoding channel maps to one of three definition types:

### Field Definition

Maps a data field to the channel. Supports inline transforms (`aggregate`, `bin`, `timeUnit`):

```json
"x": {"field": "Horsepower", "type": "quantitative"}
"y": {"aggregate": "mean", "field": "price", "type": "quantitative"}
"x": {"bin": true, "field": "IMDB Rating"}
"x": {"timeUnit": "month", "field": "date", "type": "ordinal"}
```

Common field definition properties:

| Property | Type | Description |
|----------|------|-------------|
| `field` | String | **Required** (except for `aggregate: "count"`). Field name. Use dots/brackets for nested objects (`"foo.bar"`) |
| `type` | String | `"quantitative"`, `"temporal"`, `"ordinal"`, `"nominal"`, or `"geojson"`. Auto-inferred in many cases |
| `aggregate` | String | Aggregation: `"sum"`, `"mean"`, `"median"`, `"min"`, `"max"`, `"count"`, `"distinct"`, `"variance"`, `"stddev"`, `"argmin"`, `"argmax"` |
| `bin` | Boolean \| Object \| String | `true` for auto-bin, object for params, `"binned"` for pre-binned data |
| `timeUnit` | String \| Object | Time extraction: `"year"`, `"month"`, `"day"`, `"yearmonth"`, `"monthdate"`, etc. |
| `sort` | Sort | Sort order (see position channels) |
| `title` | String \| Null | Override default axis/legend title. `null` removes title |
| `format` | String \| Object | Format specifier for text/axis labels |

### Value Definition

Maps a constant visual value:

```json
"color": {"value": "steelblue"}
"size": {"value": 100}
```

### Datum Definition

Maps a constant data value through a scale:

```json
"y": {"datum": 0, "type": "quantitative"}
```

## Position Channels

Determine mark position or bar/area width/height. Auto-generate scale and axis.

| Channel | Description |
|---------|-------------|
| `x` / `y` | Primary position coordinates |
| `x2` / `y2` | Ranged end coordinates for `area`, `bar`, `rect`, `rule` |
| `xError` / `yError` | Error extent start (for errorbar/errorband) |
| `xError2` / `yError2` | Error extent end |

Position field definitions support:

| Property | Type | Description |
|----------|------|-------------|
| `scale` | Scale \| Null | Scale configuration. `null` disables scale (raw data values used) |
| `axis` | Axis \| Null | Axis configuration. `null` removes axis |
| `sort` | Sort | Sort order. `"ascending"`/`"descending"`, channel string (`"-x"`), field definition, array of values, or `null` |
| `stack` | String \| Boolean \| Null | `"zero"`/`true` (stacked), `"normalize"` (percentage), `"center"` (streamgraph), `null`/`false` (layered). Default: `zero` for bar/area/arc with unaggregated non-position field; `null` otherwise |
| `impute` | ImputeParams \| Null | Impute missing values. Uses other position channel as key, color field as groupby |

## Position Offset Channels

Additional offset from primary position:

| Channel | Description |
|---------|-------------|
| `xOffset` / `yOffset` | Additional x/y offset (used for grouped bar charts) |

Supports `scale`, `sort` properties.

### Grouped Bar Chart Example

```json
{
  "mark": "bar",
  "encoding": {
    "x": {"field": "year", "type": "ordinal"},
    "y": {"aggregate": "sum", "field": "people"},
    "xOffset": {"field": "gender", "type": "nominal"}
  }
}
```

## Polar Position Channels

For `arc` and `text` marks on polar coordinates:

| Channel | Description |
|---------|-------------|
| `theta` | Arc length (radians) or start angle. 0 = up/north, increasing clockwise |
| `theta2` | End angle for ranged arcs |
| `radius` | Outer radius in pixels |
| `radius2` | Inner radius in pixels |

Supports `scale`, `stack`, `sort` properties similar to position channels.

## Geographic Position Channels

For marks with geographic projection:

| Channel | Description |
|---------|-------------|
| `longitude` / `latitude` | Primary geographic coordinates |
| `longitude2` / `latitude2` | Ranged end coordinates |

Requires `projection` property at spec level.

## Mark Property Channels

Map data to visual properties of marks. Auto-generate scale and legend.

| Channel | Description |
|---------|-------------|
| `color` | Fill or stroke color based on mark's `filled` property |
| `fill` | Fill color (higher precedence than `color`) |
| `stroke` | Stroke color (higher precedence than `color`) |
| `opacity` | Overall opacity |
| `fillOpacity` / `strokeOpacity` | Fill/stroke opacity |
| `size` | Mark size: pixel area for point/circle/square, bar/tick thickness, font size for text. Unsupported for line/area/rect (use `trail` instead) |
| `shape` | Point shape or geoshape field |
| `strokeWidth` | Stroke width in pixels |
| `strokeDash` | Dash pattern array |
| `angle` | Rotation angle for point/text marks |

Mark property field definitions support:

| Property | Type | Description |
|----------|------|-------------|
| `scale` | Scale \| Null | Scale configuration |
| `legend` | Legend \| Null | Legend configuration. `null` removes legend |
| `condition` | Condition[] | Conditional encoding rules based on parameters or predicates |

## Text and Tooltip Channels

| Channel | Description |
|---------|-------------|
| `text` | Text content for `text` marks |
| `tooltip` | Tooltip text on hover. Can be field definition, value, array of fields, or `null` to disable |

Support `format`, `formatType` (`"number"` / `"time"`), and `condition` properties.

### Multiple Field Tooltips

```json
{
  "tooltip": [
    {"field": "Beak Length (mm)", "type": "quantitative"},
    {"field": "Species", "type": "nominal"}
  ]
}
```

## Hyperlink, Description, Detail, Key, Order Channels

| Channel | Description |
|---------|-------------|
| `href` | URL to load on click. Sets cursor to `"pointer"` |
| `description` | ARIA text description (SVG output) |
| `detail` | Additional grouping field(s) without visual mapping. For line/area: groups lines by field. For aggregate: adds group-by |
| `key` | Unique key for data binding during transitions |
| `order` | Stack order, line point order, or z-order (layering). Array of fields for multi-field ordering |

### Detail Channel Example

```json
{
  "mark": "line",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"},
    "detail": {"field": "symbol", "type": "nominal"}
  }
}
```

## Facet Channels

Split a single plot into trellis (small multiples):

| Channel | Description |
|---------|-------------|
| `facet` | Flexible facet (auto-arranged grid) |
| `row` | Vertical facet |
| `column` | Horizontal facet |

Supports `header`, `sort`, `title`, `format` properties. Use `columns` property to set number of columns for flexible facet.
