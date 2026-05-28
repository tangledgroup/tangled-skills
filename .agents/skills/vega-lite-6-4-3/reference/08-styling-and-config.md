# Styling and Configuration

## Contents

- Axis
- Legend
- Header
- Title
- Format
- Config Overview
- Mark Config
- Style Config
- Scale Config
- Gradient
- Invalid Data Handling

## Axis

Control axis appearance via encoding field definition or config.

### Axis Properties

| Property | Type | Description |
|----------|------|-------------|
| `orient` | String | `"bottom"`, `"left"`, `"right"`, `"top"`. Auto-derived from channel |
| `title` | String \| Null | Axis title. `null` removes title |
| `titleColor` / `titleFont` / `titleFontSize` / `titleFontWeight` | — | Title styling |
| `titleAngle` / `titleX` / `titleY` | Number | Title position |
| `label` | Boolean | Show labels. Default: `true` |
| `labelAlign` / `labelBaseline` | String | Label text alignment and baseline |
| `labelColor` / `labelFont` / `labelFontSize` / `labelFontWeight` | — | Label styling |
| `labelAngle` | Number | Rotation angle in degrees. Use for long labels (e.g., `0` or `-45`) |
| `labelFlush` / `labelFlushOffset` | Number \| Boolean | Align first/last label to axis edge |
| `labelLimit` | Number | Max pixel width for labels (truncates with ellipsis) |
| `labelOverlap` | Boolean | Remove overlapping labels. Default: `true` |
| `labelPadding` | Number | Padding between label and axis. Default: `2` |
| `tickCount` | Number | Approximate number of ticks. Default: `max(0, round(rangeStep/tickMinStep)-1)` |
| `tickMinStep` / `tickMaxStep` | Number | Min/max pixel distance between ticks |
| `tickRound` | Boolean | Round tick values to integers. Default: `true` |
| `tickSize` / `tickBand` | Number \| String | Tick length in pixels. `"extent"` fills full band |
| `grid` / `gridColor` / `gridWidth` / `gridDash` / `gridOpacity` | — | Grid line styling |
| `domain` / `domainColor` / `domainWidth` / `domainDash` | — | Axis domain line styling |
| `format` | String \| Object | Number/time format pattern |
| `values` | Array | Explicit tick values |
| `zindex` | Number | Z-order for layering |
| `offset` | Number | Offset from scale range edge |
| `hideOverlappingLabels` | Boolean | Deprecated, use `labelOverlap` instead |
| `stackOffset` | String | Stack offset for stacked axes: `"zero"`, `"center"`, `"normalize"` |

### Axis Config

```json
{
  "config": {
    "axis": {"grid": false, "labelFontSize": 12},
    "axisX": {"labelAngle": -45},
    "axisY": {"title": null}
  }
}
```

## Legend

Control legend appearance for mark property channels.

### Legend Properties

| Property | Type | Description |
|----------|------|-------------|
| `orient` | String | `"left"`, `"right"`, `"top"`, `"bottom"`, or corner values like `"top-left"` |
| `title` | String \| Null | Legend title. `null` removes title |
| `label` | Boolean | Show labels. Default: `true` |
| `labelColor` / `labelFont` / `labelFontSize` / `labelFontWeight` | — | Label styling |
| `labelOverlap` / `labelLimit` | Boolean \| Number | Overlap control and max width |
| `format` | String | Format pattern for labels |
| `values` | Array | Explicit legend values (subset or reorder) |
| `direction` | String | `"horizontal"` or `"vertical"` (default) |
| `padding` | Number | Padding between legend items |
| `columns` / `rows` | Number | Layout columns/rows |
| `gradient` | Boolean \| Number | Show gradient for continuous color. Length in pixels or `true` |
| `stroke` / `fill` / `opacity` | — | Symbol styling |
| `symbolSize` / `symbolType` / `symbolOffset` | — | Legend symbol appearance |
| `zindex` | Number | Z-order |
| `offset` | Number | Offset from view edge |

### Legend Types

- **Color legend**: gradient bar for continuous, swatches for discrete
- **Size legend**: circles of increasing size
- **Shape legend**: shape symbols with labels
- **StrokeDash legend**: dash pattern samples

## Header

Control facet header labels.

### Header Properties

| Property | Type | Description |
|----------|------|-------------|
| `title` | Boolean \| Null | Show title. `null` removes it |
| `label` | Boolean | Show labels. Default: `true` |
| `labelColor` / `labelFont` / `labelFontSize` / `labelFontWeight` | — | Label styling |
| `labelLimit` / `labelOverlap` | Number \| Boolean | Truncation and overlap |
| `format` | String | Format pattern |
| `orient` | String | Header orientation |
| `columns` / `rows` | Number | Grid layout for facet headers |
| `bounds` | String | `"full"` (default) or `"flush"` |
| `stripe` | Boolean | Alternate background colors. Default: `false` |
| `stripSize` | Number | Stripe band size |

## Title

Plot-level title.

### Title Properties

| Property | Type | Description |
|----------|------|-------------|
| `text` | String | **Required.** Title text |
| `align` | String | `"left"`, `"right"`, `"center"` (default) |
| `anchor` | String | `"start"`, `"middle"` (default), `"end"` |
| `baseline` | String | Text baseline |
| `color` / `font` / `fontSize` / `fontWeight` | — | Typography |
| `lineHeight` | Number | Line height for multi-line titles |
| `limit` | Number | Max pixel width (truncates) |
| `orient` | String | `"alpha"` (default, above), `"middle"`, `"delta"` (below) |
| `offset` / `x` / `y` | Number | Position offset |
| `angle` | Number | Rotation in radians |
| `dx` / `dy` | Number | Additional offset |
| `className` | String | CSS class name |

## Format

### Number Format

Uses D3's number format pattern:

```json
"format": ".2f"    // 2 decimal places
"format": "$,.2f"  // Currency with commas
"format": ".1%"    // Percentage
"format": ".2s"    // SI suffix (1.5k, 2.3M)
```

### Time Format

Uses D3's time format pattern:

```json
"format": "%Y"           // Year (2024)
"format": "%b"           // Month abbreviation (Jan)
"format": "%m/%d/%Y"     // Date (01/15/2024)
"format": "%H:%M"        // Time (14:30)
```

### Dynamic Time Format

Auto-select format based on temporal granularity:

```json
{
  "format": {
    "year": "%Y",
    "month": "%b '%y",
    "day": "%b %d"
  }
}
```

## Config Overview

The `config` object sets default properties at the top level. Only one `config` per spec (top-level only).

### Top-Level Config

| Property | Description |
|----------|-------------|
| `fieldTitle` | Function or template for generating field titles |
| `format` | Default number/time format |

### Guide Configurations

| Property | Description |
|----------|-------------|
| `axis` / `axisX` / `axisY` | Default axis properties |
| `legend` / `legendColor` / `legendOpacity` / `legendSize` / `legendShape` / `legendStrokeDash` | Default legend properties |
| `header` / `headerRow` / `headerColumn` | Default header properties |
| `title` | Default title properties |

### Mark Configurations

| Property | Description |
|----------|-------------|
| `mark` | Global mark defaults |
| `area` / `bar` / `circle` / `line` / `point` / `rect` / `rule` / `geoshape` / `square` / `text` / `tick` | Per-mark defaults |

### Scale Config

| Property | Description |
|----------|-------------|
| `scale` | Global scale defaults |
| `range` | Default color ranges |
| `invalid` | Output value for invalid data in scales |
| `bandPaddingInner` / `bandPaddingOuter` | Default band padding |

### View Config

| Property | Description |
|----------|-------------|
| `view` | View background defaults |
| `continuousWidth` / `continuousHeight` | Default sizes for continuous views (default: 300) |
| `discreteWidth` / `discreteHeight` | Default sizes for discrete views |
| `step` | Default step size for discrete fields |

### Style Config

Define named styles:

```json
{
  "config": {
    "style": {
      "label": {"dy": -5, "align": "right", "dx": -5},
      "triangle": {"shape": "triangle-up", "strokeWidth": 2}
    }
  }
}
```

Built-in styles: `"guide-label"`, `"guide-title"`, `"group-title"`.

### Projection Config

```json
{
  "config": {
    "projection": {"type": "albersUsa", "scale": 1000}
  }
}
```

### Selection Config

```json
{
  "config": {
    "selection": {"interval": {"translate": true, "zoom": false}}
  }
}
```

### ARIA Config

```json
{
  "config": {
    "aria": true
  }
}
```

## Gradient

Define gradients for fill/stroke colors.

### Linear Gradient

```json
{
  "fill": {
    "gradient": "linear",
    "x1": 0, "y1": 0, "x2": 0, "y2": 1,
    "stops": [
      {"offset": 0, "color": "#ffffb7"},
      {"offset": 0.5, "color": "#43a2ca"},
      {"offset": 1, "color": "#3b528b"}
    ]
  }
}
```

### Radial Gradient

```json
{
  "fill": {
    "gradient": "radial",
    "r1": 0, "r2": 1, "x1": 0.5, "y1": 0.5, "x2": 0.5, "y2": 0.5,
    "stops": [
      {"offset": 0, "color": "#ffffb7"},
      {"offset": 1, "color": "#3b528b"}
    ]
  }
}
```

## Invalid Data Handling

Control how `null` and `NaN` values are represented.

### Mark-Level Invalid Mode

Set on mark definition:

| Mode | Description |
|------|-------------|
| `"filter"` | Exclude invalid values from marks and scales |
| `"break-paths-filter-domains"` | Break paths at invalid values, exclude from scale domains |
| `"break-paths-show-domains"` | Break paths, hide non-path invalid, include in scale domains |
| `"show"` or `null` | Show all, invalid maps to zero or minimum |
| `"break-paths-show-path-domains"` (default) | Break paths for line/area/trail, filter for others |

### Scale Invalid Output

```json
{
  "config": {
    "scale": {"invalid": "#999"}
  }
}
```

Sets the visual output for invalid values in scales. When defined, all values are considered "valid" (no filtering or path breaking occurs).
