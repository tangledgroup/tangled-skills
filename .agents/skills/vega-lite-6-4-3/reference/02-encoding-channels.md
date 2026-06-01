# Encoding Channels

The `encoding` object maps data fields, constant values, or datum expressions to visual channels. Each channel definition is one of three forms:

| Form | Pattern | Purpose |
|------|---------|---------|
| Field Definition | `{field, type}` | Map a data field through a scale |
| Value Definition | `{value: ...}` | Constant visual value (bypasses scale) |
| Datum Definition | `{datum: ...}` | Constant data value through a scale |

## Channel Groups

### Position Channels

`x`, `y` — mark position or bar/area width/height. `x2`, `y2` — ranged marks (span).

| Property | Description |
|----------|-------------|
| `scale` | Scale customization (type, domain, range, zero, nice, clamp) |
| `axis` | Axis guide customization |
| `sort` | Sort order of scale domain |
| `stack` | Stacking offset type (`"zero"`, `"normalize"`, `"center"`, `"wiggle"`) |
| `impute` | Imputation for missing values |

**Note**: `x2`/`y2` share scales and axes with `x`/`y`; they don't have independent scale/axis/sort/stack.

### Position Offset Channels

`xOffset`, `yOffset` — additional offset to position (grouped bars, jittering).

Supports `scale` and `sort`. Step size controlled via `width`/`height` with `"for": "offset"`.

### Polar Position Channels

`theta`, `radius`, `theta2`, `radius2` — arc mark angles and radii. Supports `scale`, `stack`, `sort`.

### Geographic Position Channels

`longitude`, `latitude`, `longitude2`, `latitude2` — geographic coordinates with projection.

### Mark Property Channels

| Channel | Encodes | Default Scale |
|---------|---------|---------------|
| `color` (alias: `fill`/`stroke`) | Fill or stroke color | ordinal for nominal, linear for quantitative |
| `opacity` | Mark opacity | linear |
| `fillOpacity` | Fill opacity specifically | linear |
| `strokeOpacity` | Stroke opacity specifically | linear |
| `size` | Mark area/width/font-size | linear (min/max varies by mark) |
| `shape` | Point marker shape | ordinal |
| `angle` | Rotation angle | linear |
| `strokeWidth` | Stroke line width | linear |
| `strokeDash` | Dash pattern | ordinal |

Supports `scale`, `legend`, and `condition`.

### Text and Tooltip Channels

`text` — rendered text labels. `tooltip` — hover tooltip display.

Supports `format`, `formatType`, `condition`. Multiple field definitions as array for multi-field tooltips.

### Other Channels

| Channel | Purpose |
|---------|---------|
| `href` | Hyperlink URL (mark becomes clickable) |
| `description` | ARIA accessibility text (SVG only) |
| `detail` | Grouping without visual encoding |
| `key` | Object constancy for data transitions |
| `order` | Stacking/drawing order, z-order |
| `facet`, `row`, `column` | Small multiples faceting |

## Field Definitions

Every field definition requires:

```json
{
  "field": "Horsepower",
  "type": "quantitative"
}
```

### Data Types

| Type | Description | Default Scale (x/y) |
|------|-------------|---------------------|
| `quantitative` | Continuous numeric (ratio/interval) | linear |
| `temporal` | Date/time values | time |
| `ordinal` | Ranked order without magnitude | band/point |
| `nominal` | Categorical names, no order | band/point |
| `geojson` | GeoJSON shapes | — |

### Inline Transforms

Field definitions support inline data transforms:

| Property | Purpose |
|----------|---------|
| `aggregate` | `"count"`, `"sum"`, `"mean"`, `"min"`, `"max"`, `"median"`, etc. |
| `bin` | Bin quantitative data (`true`, `{binned: true}`, or `{maxbins, extent}`) |
| `timeUnit` | Extract time components (`"year"`, `"month"`, `"day"`, `"hour"`, `"yearmonth"`, etc.) |
| `sort` | Sort order of domain values |
| `band` | Band position within interval (0-1, default 0) |
| `title` | Override axis/legend title |

## Scales

Scales transform data domains to visual ranges. Vega-Lite auto-creates scales for position and mark property channels.

### Scale Types by Data Type and Channel

| Channel | Nominal/Ordinal | Quantitative | Temporal |
|---------|-----------------|--------------|----------|
| x, y | band (bar/rect) / point (others) | linear | time |
| size, opacity | point | linear | time |
| color | ordinal | linear (ramp scheme) | linear |
| shape | ordinal | N/A | N/A |

### Continuous Scale Types

| Type | Description | Extra Properties |
|------|-------------|------------------|
| `linear` | Proportional mapping | — |
| `log` | Logarithmic (strictly positive/negative) | `base` |
| `pow` | Power transform | `exponent` |
| `sqrt` | Square root (pow with exponent 0.5) | — |
| `symlog` | Symmetric log (supports zero/negative) | `constant` |
| `time` | Temporal, local timezone | — |
| `utc` | Temporal, UTC | — |

### Discrete Scale Types

| Type | Description |
|------|-------------|
| `ordinal` | Lookup table from domain to range |
| `band` | Uniform bands for bar charts; supports `step`, `paddingInner`, `paddingOuter` |
| `point` | Zero-width bands for scatterplots; supports `step` |

### Discretizing Scale Types

| Type | Description |
|------|-------------|
| `bin-linear` | Binned linear for size/opacity (auto-assigned) |
| `bin-ordinal` | Binned ordinal for color (auto-assigned); supports `bins` |
| `quantile` | Equal-count groups from sample domain |
| `quantize` | Uniform domain segments to discrete range |
| `threshold` | Arbitrary threshold boundaries |

### Common Scale Properties

| Property | Type | Description |
|----------|------|-------------|
| `type` | string | Scale type |
| `domain` | array \| object | Custom domain values or `{data, field}` |
| `domainMin` / `domainMax` | number | Clamp one end of domain |
| `domainMid` | number | Midpoint for diverging scales |
| `range` | array | Output visual values |
| `rangeMin` / `rangeMax` | number | Override one end of range |
| `scheme` | string \| object | Named color scheme (e.g., `"viridis"`, `"tableau10"`) |
| `zero` | boolean | Include zero in quantitative scales (default true) |
| `nice` | boolean \| number | Extend domain to nice round numbers |
| `clamp` | boolean | Clamp output to range |
| `interpolate` | string | Interpolation (`"linear"`, `"catmull-rom"`, etc.) |
| `round` | boolean | Round output values |
| `reverse` | boolean | Reverse domain order |
| `padding` / `paddingInner` / `paddingOuter` | number | Band scale padding |
| `align` | number | Band scale alignment (0-1) |

### Diverging Scales

Piecewise/diverging scales: specify multi-element `domain` with matching multi-element `range`:

```json
{
  "scale": {
    "domain": [-1, 0, 1],
    "range": ["red", "white", "blue"]
  }
}
```

### Disabling Scales

Set `scale: null` to directly encode data values (e.g., raw CSS color names from data).

### Default Color Schemes

| Field Type | Default Scheme | Vega Name |
|------------|---------------|-----------|
| Nominal | Categorical | `"tableau10"` |
| Ordinal | Sequential | `"blues"` |
| Quantitative (rect) | Heatmap | `"viridis"` |
| Quantitative (other) | Ramp | `"blues"` |

Customize via `scheme`, `range` array, or `config.range`.

### Scale Config

Global defaults via `config.scale`: padding (`bandPaddingInner`, `continuousPadding`, etc.), range (`minSize`, `maxSize`, `minOpacity`, etc.), `zero`, `clamp`, `round`, `invalid`.

Named ranges via `config.range` — override defaults for `category`, `diverging`, `heatmap`, `ordinal`, `ramp`, `symbol`.

## Sort Orders

The `sort` property controls the order of scale domains.

### Continuous Fields

- `"ascending"` (default)
- `"descending"`

### Discrete Fields

| Value | Description |
|-------|-------------|
| `"ascending"` / `"descending"` | Natural JS sort order |
| `"x"`, `"-y"` | Sort by another encoding channel (`-` prefix = descending) |
| `{field, op, order}` | Sort by a data field with aggregation (e.g., `{field: "people", op: "sum"}`) |
| `[...]` | Custom array specifying preferred order |
| `null` | No sorting (preserve data order) |

Sort arrays can be partial — unspecified values follow original order. For time units, month/day names are accepted (case-insensitive).

## Axis Configuration

Axes visualize position scales. Auto-created for `x`/`y`. Set `axis: null` to hide.

### Key Properties

| Group | Properties |
|-------|-----------|
| General | `orient`, `offset`, `position`, `minExtent`, `maxExtent`, `style`, `aria`, `description`, `bandPosition`, `zindex` |
| Domain | `domain`, `domainColor`, `domainWidth`, `domainDash`, `domainCap` |
| Grid | `grid`, `gridColor`, `gridWidth`, `gridDash`, `gridOpacity` |
| Ticks | `ticks`, `tickCount`, `tickSize`, `tickBand`, `tickColor`, `tickExtra` |
| Labels | `format`, `formatType`, `labelAngle`, `labelOverlap`, `labelExpr`, `labelFont`, `labelFontSize`, `labelLimit` |
| Title | `title`, `titleAlign`, `titleFont`, `titleFontSize`, `titlePadding` |

### Conditional Axis Properties

Use conditional values based on tick data (`label`, `value`, `index`):

```json
{
  "axis": {
    "gridDash": [{"test": "datum.index === 0 || datum.index === 1", "value": [6, 3]}, {"value": null}]
  }
}
```

### Axis Config

`config.axis` — all axes. `config.axisX/Y/Left/Right/Top/Bottom` — orientation-specific. `config.axisBand/Quantitative/Temporal` — type-specific. Combined: `config.axisXTemporal`. Supports `disable`.

Precedence (highest to lowest): field-level axis > style config > orientation+type config > type config > orientation config > general config.

## Legend Configuration

Legends visualize mark property scales. Auto-created for `color`, `opacity`, `size`, `shape`. Set `legend: null` to hide.

### Key Properties

| Group | Properties |
|-------|-----------|
| General | `orient`, `offset`, `type` (`"gradient"` / `"symbol"`), `direction`, `padding`, `cornerRadius` |
| Gradient | `gradientLength`, `gradientThickness`, `gradientOpacity` |
| Symbols | `symbolType`, `symbolSize`, `symbolFillColor`, `symbolStrokeColor` |
| Layout | `columns`, `columnPadding`, `rowPadding`, `clipHeight`, `gridAlign` |
| Labels | `labelFont`, `labelFontSize`, `labelLimit`, `labelExpr` |
| Title | `title`, `titleFont`, `titleFontSize` |

### Legend Config

`config.legend` — all legends. Supports `disable`, `gradientDirection`, `symbolDirection`, `unselectedOpacity`.

## Format Strings

`format` and `formatType` control display formatting for text, tooltips, axes, legends, headers.

### Quantitative Fields

Use [d3-format](https://github.com/d3/d3-format) specifiers: `".2f"` (2 decimal places), `".2s"` (SI prefix), `"%"` (percentage), `",.2f"` (comma-separated).

### Temporal Fields

**Dynamic format** — object keyed by Vega time units:

```json
{"format": {"year": "%Y", "month": "%b %Y", "date": "%b %d, %Y"}}
```

**Static format** — single [d3-time-format](https://github.com/d3/d3-time-format) specifier: `"%Y-%m-%d"`, `"%b '%y"`.

`formatType`: `"plain"` (default), `"locale"`.

## Conditional Encoding

For mark property, text, and tooltip channels, `condition` enables parameter-driven or test-driven encoding:

### Parameter-based Condition

```json
{
  "color": {
    "condition": {
      "param": "brush",
      "field": "Category",
      "type": "nominal"
    },
    "value": "grey"
  }
}
```

Properties: `param` (selection parameter name), `empty` (boolean, how to treat empty selection).

### Test-based Condition

```json
{
  "color": {
    "condition": {
      "test": "datum.value > 50",
      "value": "red"
    },
    "field": "Category",
    "type": "nominal"
  }
}
```

Properties: `test` (expression string referencing `datum`).

### Two Patterns

1. **Conditional field + value else**: `condition` has `{param/test, field, type}`, outer is `value`
2. **Conditional value + field else**: `condition` has `{param/test, value}`, outer is `field`/`type`

Multiple conditions can be chained as arrays.

## Datum and Value Definitions

### Datum

Maps a constant data value through a scale. Useful for annotations:

```json
{"y": {"datum": 200}}        // threshold line at y=200
{"x": {"datum": {"year": 2020}}}  // vertical line at year boundary
```

### Value

Maps a constant visual value directly (bypasses scale):

```json
{"color": {"value": "#ff6384"}}    // fixed color
{"shape": {"value": "diamond"}}    // fixed shape
{"size": {"value": 100}}          // fixed mark size
```

Equivalent to setting mark definition properties, but `value` can be combined with `condition`.

## Band Position

`bandPosition` adjusts position within a band scale interval (0 = start, 0.5 = center, 1 = end). Useful for centering lines/bars within time intervals:

```json
{"x": {"field": "date", "timeUnit": "month", "bandPosition": 0.5}}
```

## Header Configuration

Headers provide titles and labels for faceted plots. Customizable per row/column/facet field.

### Key Properties

| Group | Properties |
|-------|-----------|
| Labels | `labelFont`, `labelFontSize`, `labelOrient`, `labelExpr`, `labelLimit` |
| Title | `titleFont`, `titleFontSize`, `titleOrient`, `titleAlign` |

### Header Config

`config.header` — all headers. `config.headerRow/Column/Facet` — type-specific.
