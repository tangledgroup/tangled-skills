# Axes, Legends & Title

## Contents
- Axis Properties
- Axis Orientation
- Custom Axis Encodings
- Legend Properties
- Legend Orientation
- Custom Legend Encodings
- Title

## Axis Properties

Axes visualize spatial scale mappings using ticks, grid lines, and labels. Supports Cartesian (rectangular) coordinates.

| Property | Type | Description |
|----------|------|-------------|
| `scale` | String | **Required.** Name of the backing scale |
| `orient` | String | **Required.** Axis orientation (`left`, `right`, `top`, `bottom`) |
| `bandPosition` | Number | Interpolation fraction for band scale tick position (0=left edge, 0.5=center) |
| `domain` | Boolean | Include domain/baseline (default: true) |
| `domainCap` | String | Domain line cap: `"butt"` (default), `"round"`, `"square"` (≥5.11) |
| `domainColor` | Color | Domain line color |
| `domainDash` | Number[] | Stroke dash pattern (or [] for solid, ≥5.0) |
| `domainDashOffset` | Number | Dash start offset (≥5.0) |
| `domainOpacity` | Number | Domain opacity (≥4.1) |
| `domainWidth` | Number | Domain stroke width |
| `encode` | Object | Custom mark encodings for axis elements |
| `format` | String / TimeMultiFormat | Label format specifier (d3-format or d3-time-format) |
| `formatType` | String | Format type override: `"number"`, `"time"`, `"utc"` (≥5.1, UTC ≥5.8) |
| `grid` | Boolean | Include grid lines (default: false) |
| `gridCap` | String | Grid line cap (≥5.11) |
| `gridColor` | Color | Grid line color |
| `gridDash` | Number[] | Grid dash pattern |
| `gridDashOffset` | Number | Grid dash start offset (≥5.0) |
| `gridOpacity` | Number | Grid opacity |
| `gridScale` | String | Scale for grid lines (default: same as ticks/labels) |
| `gridWidth` | Number | Grid stroke width |
| `labels` | Boolean | Include labels (default: true) |
| `labelAlign` | String | Horizontal text alignment override |
| `labelAngle` | Number | Label angle in degrees |
| `labelBaseline` | String | Vertical baseline: `alphabetic`, `top`, `middle`, `bottom`, `line-top`, `line-bottom` (≥5.10) |
| `labelBound` | Boolean / Number | Hide labels exceeding axis range (false=none, true=1px, number=pixel tolerance) |
| `labelColor` | Color | Label text color |
| `labelFlush` | Boolean / Number | Flush-align labels at axis ends |
| `labelFlushOffset` | Number | Offset for flush-adjusted labels (default: 0) |
| `labelFont` | String | Label font name |
| `labelFontSize` | Number | Label font size |
| `labelFontStyle` | String | Font style (≥5.0) |
| `labelFontWeight` | String / Number | Font weight |
| `labelLimit` | Number | Max label length in pixels |
| `labelLineHeight` | Number | Line height for multi-line labels (≥5.10) |
| `labelOffset` | Number | Label position offset (≥5.10) |
| `labelOpacity` | Number | Label opacity (≥4.1) |
| `labelOverlap` | Boolean / String | Overlap strategy: false, true/"parity" (every other), "greedy" |
| `labelPadding` | Number | Padding between labels and ticks |
| `labelSeparation` | Number | Min separation for non-overlapping (≥5.0) |
| `minExtent` | Number / Value | Minimum extent in pixels for tick/label area |
| `maxExtent` | Number / Value | Maximum extent in pixels |
| `offset` | Number / Value | Orthogonal offset from chart edge |
| `position` | Number / Value | Anchor position (default: 0) |
| `ticks` | Boolean | Include ticks (default: true) |
| `tickBand` | String | Band scale tick style: `"center"` (default), `"extent"` (≥5.8) |
| `tickCap` | String | Tick mark cap (≥5.11) |
| `tickColor` | Color | Tick color |
| `tickCount` | Number / String / Object | Desired number of ticks; for time scales: `"month"`, `{"interval":"month","step":3}` |
| `tickDash` | Number[] | Tick dash pattern (≥5.0) |
| `tickDashOffset` | Number | Tick dash start offset (≥5.0) |
| `tickMinStep` | Number | Minimum step between ticks in domain units (≥5.0) |
| `tickExtra` | Boolean | Extra tick at initial axis position for band scales |
| `tickOffset` | Number | Tick/label/gridline offset (≥5.10) |
| `tickOpacity` | Number | Tick opacity (≥4.1) |
| `tickRound` | Boolean | Round pixel positions to integers |
| `tickSize` | Number | Tick length in pixels |
| `tickWidth` | Number | Tick stroke width |
| `title` | String / String[] | Axis title; ≥5.7 accepts string array for multi-line |
| `titleAnchor` | String | Title anchor: `"start"`, `"middle"`, `"end"`, or null (auto, ≥5.0) |
| `titleAlign` | String | Title horizontal alignment: `"left"`, `"center"`, `"right"` |
| `titleAngle` | Number | Title angle in degrees |
| `titleBaseline` | String | Title vertical baseline |
| `titleColor` | Color | Title text color |
| `titleFont` | String | Title font name |
| `titleFontSize` | Number | Title font size |
| `titleFontStyle` | String | Font style (≥5.0) |
| `titleFontWeight` | String / Number | Title font weight |
| `titleLimit` | Number | Max title length in pixels |
| `titleLineHeight` | Number | Line height for multi-line titles (≥5.7) |
| `titleOpacity` | Number | Title opacity (≥4.1) |
| `titlePadding` | Number / Value | Padding between labels and title |
| `titleX` | Number | Custom X position of title |
| `titleY` | Number | Custom Y position of title |
| `translate` | Number | Coordinate space translation (default: 0.5 for pixel alignment, ≥5.8) |
| `values` | Array[] | Explicit tick/label values from scale domain |
| `zindex` | Number | Layering z-index (default: 0; axes behind marks) |

### Accessibility Properties (≥5.11)
| Property | Type | Description |
|----------|------|-------------|
| `aria` | Boolean | Include ARIA attributes for SVG (default: true) |
| `description` | String | Text description for ARIA (auto-generated if unspecified) |

### Axis Orientation
| Value | Description |
|-------|-------------|
| `left` | Y-axis along left edge |
| `right` | Y-axis along right edge |
| `top` | X-axis along top edge |
| `bottom` | X-axis along bottom edge |

## Custom Axis Encodings

The `encode` property supports encoding blocks for: `axis`, `ticks`, `grid`, `labels`, `title`, `domain`.

Each tick/grid/label data object provides: `label` (string), `value` (data value), `index` (fractional 0–1).

```json
{
  "orient": "bottom",
  "scale": "x",
  "title": "X-Axis",
  "encode": {
    "ticks": {"update": {"stroke": {"value": "steelblue"}}},
    "labels": {
      "interactive": true,
      "update": {
        "text": {"signal": "format(datum.value, '+,')"},
        "fill": {"value": "steelblue"},
        "angle": {"value": 50}
      },
      "hover": {"fill": {"value": "firebrick"}}
    }
  }
}
```

## Legend Properties

Legends visualize scale mappings for color, shape, and size. At least one of `size`, `shape`, `fill`, `stroke`, `strokeDash`, or `opacity` must be specified. Multiple scales must share the same domain.

| Property | Type | Description |
|----------|------|-------------|
| `type` | String | `"symbol"`, `"gradient"`, or `"discrete"` (inferred if unspecified) |
| `direction` | String | `"vertical"` (default) or `"horizontal"` |
| `orient` | String | Position relative to chart (see Legend Orientation below) |
| `fill` / `stroke` / `shape` / `size` / `opacity` / `strokeDash` / `strokeWidth` | String | Name of scale for the visual channel |
| `encode` | Object | Custom mark encodings for legend elements |
| `format` | String / TimeMultiFormat | Label format specifier |
| `formatType` | String | Format type override: `"number"`, `"time"`, `"utc"` (≥5.1) |
| `gridAlign` | String | Symbol legend grid alignment: `"all"`, `"each"` (default), `"none"` |
| `clipHeight` | Number | Height to clip symbol entries |
| `columns` | Number | Number of columns (0=one per entry, ≥5.4) |
| `columnPadding` | Number | Horizontal padding between entries |
| `rowPadding` | Number | Vertical padding between entries |
| `cornerRadius` | Number | Legend corner radius |
| `fillColor` | Color | Background fill color |
| `offset` | Number / Value | Offset from chart/axes |
| `padding` | Number / Value | Padding inside legend border |
| `strokeColor` | Color | Border stroke color |
| `gradientLength` | Number | Primary axis length of gradient |
| `gradientOpacity` | Number | Gradient opacity (≥4.1) |
| `gradientThickness` | Number | Gradient thickness |
| `gradientStrokeColor` | Color | Gradient border color |
| `gradientStrokeWidth` | Number | Gradient border width |
| `labelAlign` / `labelBaseline` / `labelColor` / `labelFont` / `labelFontSize` | Various | Label text styling |
| `labelLimit` | Number | Max label length in pixels |
| `labelOffset` | Number | Label-symbol offset |
| `labelOpacity` | Number | Label opacity (≥4.1) |
| `labelOverlap` | Boolean / String | Overlap strategy: false, true/"parity", "greedy" |
| `labelSeparation` | Number | Min label separation (≥5.0) |
| `legendX` / `legendY` | Number | Custom position (orient="none" only, ≥5.4) |
| `symbolDash` | Number[] | Symbol outline dash (≥5.0) |
| `symbolDashOffset` | Number | Symbol dash offset (≥5.0) |
| `symbolFillColor` / `symbolStrokeColor` | Color | Symbol fill/stroke |
| `symbolLimit` | Number | Max symbol entries before ellipsis (≥5.7) |
| `symbolOffset` | Number | Horizontal symbol offset |
| `symbolOpacity` | Number | Symbol opacity (≥4.1) |
| `symbolSize` | Number | Default symbol area in px² |
| `symbolStrokeWidth` | Number | Default symbol stroke width |
| `symbolType` | String | Default shape type (e.g., `"circle"`) |
| `tickCount` | Number / String / Object | Desired tick count for quantitative legends |
| `tickMinStep` | Number | Minimum step between ticks (≥5.0) |
| `title` | String / String[] | Legend title; ≥5.7 accepts string array |
| `titleAnchor` / `titleAlign` / `titleBaseline` | Various | Title alignment |
| `titleColor` / `titleFont` / `titleFontSize` | Various | Title styling |
| `titleFontStyle` / `titleFontWeight` | String / Number | Title font (≥5.0) |
| `titleLimit` | Number | Max title length |
| `titleLineHeight` | Number | Multi-line title height (≥5.7) |
| `titleOpacity` | Number | Title opacity (≥4.1) |
| `titleOrient` | String | Title position relative to legend: `"top"` (default), `"left"`, `"bottom"`, `"right"` (≥5.0) |
| `titlePadding` | Number / Value | Padding between title and entries |
| `values` | Array[] | Explicit legend values from scale domain |
| `zindex` | Number | Layering z-index (default: 0) |

### Legend Orientation
| Value | Description |
|-------|-------------|
| `left` / `right` / `top` / `bottom` | Outside chart edges |
| `top-left` / `top-right` / `bottom-left` / `bottom-right` | Inside corners |
| `none` | No auto-layout; use `legendX`/`legendY` for custom positioning |

Multiple legends with same orient are ordered (vertically for left/right, horizontally for top/bottom).

### Custom Legend Encodings
Encoding blocks: `legend`, `title`, `labels`, `symbols`, `entries`, `gradient`.

Each symbol/label data object provides: `index` (integer), `label` (string), `value` (data value), `size` (symbol size, symbol legends only).

## Title

Title text to describe a visualization. Defined at the top level of the spec.

| Property | Type | Description |
|----------|------|-------------|
| `text` | String / Expression / Signal | Title text content |
| `align` | String | Text alignment: `"left"`, `"center"` (default), `"right"` |
| `anchor` | String | Anchor point: `"start"`, `"middle"`, `"end"` |
| `orient` | String | Position: `"top"` (default), `"bottom"` |
| `offset` | Number | Pixel offset from chart |
| `fontSize` | Number / Signal | Font size |
| `font` | String / Signal | Font family |
| `fontStyle` | String / Signal | Font style |
| `fontWeight` | String / Number / Signal | Font weight |
| `color` | Color / Signal / Array[] | Text color (array for multi-color) |
| `dy` | Number / Signal | Y offset adjustment |
| `dx` | Number / Signal | X offset adjustment |
| `lineHeight` | Number / Signal | Line height for multi-line titles (≥5.10) |
| `limit` | Number / Signal | Max title width in pixels |
| `ellipsis` | Boolean / Expression | Enable/disable text truncation (≥5.10) |
| `style` | String / String[] | Named styles from config |
| `aria` | Boolean | Include ARIA attributes (≥5.11) |
| `description` | String | ARIA description (≥5.11) |
