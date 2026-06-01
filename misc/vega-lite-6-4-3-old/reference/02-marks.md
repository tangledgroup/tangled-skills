# Marks

## Contents

- Mark Types Overview
- Mark Definition Object
- General Mark Properties
- Position and Offset Properties
- Color Properties
- Stroke Style Properties
- Primitive Mark Types
- Composite Mark Types
- Mark Config and Style Config

## Mark Types Overview

Marks are the basic visual building blocks. One mark instance is generated per input data element (except `line` and `area` which represent multiple elements as contiguous shapes).

**Primitive marks** (11): `area`, `bar`, `circle`, `line`, `point`, `rect`, `rule`, `square`, `text`, `tick`, `geoshape`, `trail`

**Composite marks** (3): `boxplot`, `errorband`, `errorbar` — macros for complex layered graphics.

Specify as a string (`"bar"`) or a mark definition object (`{"type": "bar", "tooltip": true}`).

## Mark Definition Object

```json
{
  "mark": {
    "type": "bar",
    "tooltip": true,
    "cornerRadius": 3
  }
}
```

If mark property encoding channels are specified, they override mark definition properties.

## General Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `type` | String | **Required.** Mark type name |
| `aria` | Boolean | Include ARIA attributes (SVG only). Default: `true` |
| `cursor` | String | CSS cursor type over the mark |
| `description` | String | Text description for ARIA accessibility |
| `style` | String \| String[] | Style name(s). Default: mark's name (e.g., `"bar"`) |
| `tooltip` | Boolean \| Object \| Null | Tooltip content. `true` or `{"content": "encoding"}` uses all encoding fields. `{"content": "data"}` uses highlighted data point fields. Default: `null` |
| `clip` | Boolean | Clip to enclosing group's width/height |
| `invalid` | String \| Null | Invalid data mode: `"filter"`, `"break-paths-filter-domains"`, `"break-paths-show-domains"`, `"show"`/`null`, `"break-paths-show-path-domains"` (default) |
| `order` | Null \| Boolean | For line/trail: `null` or `false` uses original data order |

## Position and Offset Properties

| Property | Type | Description |
|----------|------|-------------|
| `x` / `y` | Number \| String | Coordinates, or width/height of horizontal/vertical bar/area. `"width"`/`"height"` for plot dimensions |
| `x2` / `y2` | Number \| String | Ranged coordinates for `area`, `bar`, `rect`, `rule` |
| `width` / `height` | Number \| Object | Fixed pixel size or `{band: 0.5}` for relative band size |
| `xOffset` / `yOffset` | Number | Offset from x/y position |
| `x2Offset` / `y2Offset` | Number | Offset from x2/y2 position |

## Color Properties

| Property | Type | Description |
|----------|------|-------------|
| `filled` | Boolean | Use color as fill instead of stroke. Default: `false` for point/line/rule/geoshape; `true` otherwise |
| `color` | Color \| Gradient | Default color. Default: `"#4682b4"` |
| `fill` | Color \| Gradient \| Null | Fill color (overrides `color`). Default: none |
| `stroke` | Color \| Gradient \| Null | Stroke color (overrides `color`). Default: none |
| `blend` | String | CSS mix-blend-mode. Default: `"source-over"` |
| `opacity` | Number | Overall opacity [0,1]. Default: `0.7` for non-aggregate point/tick/circle/square; `1` otherwise |
| `fillOpacity` | Number | Fill opacity. Default: `1` |
| `strokeOpacity` | Number | Stroke opacity. Default: `1` |

## Stroke Style Properties

| Property | Type | Description |
|----------|------|-------------|
| `strokeCap` | String | Line ending: `"butt"` (default), `"round"`, `"square"` |
| `strokeDash` | Number[] | Alternating stroke/space lengths for dashes |
| `strokeDashOffset` | Number | Offset into dash array |
| `strokeJoin` | String | Join method: `"miter"` (default), `"round"`, `"bevel"` |
| `strokeMiterLimit` | Number | Miter limit for beveling |
| `strokeWidth` | Number | Stroke width in pixels |

## Primitive Mark Types

### Bar

Rectangular marks. Supports ranged bars via `x2`/`y2` (Gantt charts).

| Property | Type | Description |
|----------|------|-------------|
| `cornerRadius` | Number | Corner radius in pixels |
| `cornerRadiusTopLeft` / `TopRight` / `BottomLeft` / `BottomRight` | Number | Individual corner radii |
| `orient` | String \| Null | `"vertical"`, `"horizontal"`, or `null` (auto) |

### Area

Filled area marks. Supports ranged areas via `y2`.

| Property | Type | Description |
|----------|------|-------------|
| `orient` | String \| Null | `"vertical"` (default), `"horizontal"`, or `null` (auto) |
| `interpolate` | String | Line interpolation: `"linear"` (default), `"step-before"`, `"step-after"`, `"basis"`, `"monotone"`, etc. |
| `tension` | Number | Cardinal/basis/catmull-rom spline tension [0,1] |

### Line

Connected line marks.

| Property | Type | Description |
|----------|------|-------------|
| `interpolate` | String | `"linear"` (default), `"step-before"`, `"step-after"`, `"basis"`, `"monotone"`, `"catmull-rom"`, `"cardinal"`, `"bundle"` |
| `tension` | Number | Spline tension [0,1] |
| `orient` | String \| Null | `"vertical"`, `"horizontal"`, or `null` (auto) |
| `shortPaths` | String | How to handle short paths: `"line"` (default) or `"point"` |

### Trail

Like `line` but supports varying stroke width via `size` channel.

| Property | Type | Description |
|----------|------|-------------|
| `interpolate` | String | Same interpolation options as `line` |
| `tension` | Number | Spline tension [0,1] |

### Point

Individual point marks. Supports various shapes.

| Property | Type | Description |
|----------|------|-------------|
| `shape` | String | `"circle"` (default), `"square"`, `"cross"`, `"diamond"`, `"triangle-up"`, `"triangle-down"`, `"triangle-right"`, `"triangle-left"`, `"stroke"`, `"arrow"`, `"wedge"`, `"triangle"`, or custom SVG path |
| `size` | Number | Symbol size (pixel area) |

### Circle

Filled circle marks. Same properties as `point` plus standard color/position properties.

### Square

Filled square marks. Same as `circle` but rectangular shape.

### Rect

Rectangle marks. Supports ranged rects via `x2`/`y2`. Used for heatmaps.

| Property | Type | Description |
|----------|------|-------------|
| `orient` | String \| Null | `"vertical"`, `"horizontal"`, or `null` (auto) |

### Rule

Line segment marks. Supports ranged rules via `x2`/`y2`.

### Tick

Tick marks (1D bars). Used for dot plots and strip plots.

| Property | Property | Description |
|----------|------|-------------|
| `orient` | String \| Null | `"vertical"` (default), `"horizontal"`, or `null` |
| `thickness` | Number | Tick thickness in pixels. Default: `1` |

### Text

Text marks. Supports polar coordinates (`theta`, `radius`).

| Property | Type | Description |
|----------|------|-------------|
| `align` | String | `"left"`, `"right"`, `"center"` (default) |
| `baseline` | String | `"top"`, `"middle"` (default), `"bottom"`, `"alphabetic"`, `"hanging"`, `"ideographic"` |
| `angle` | Number | Rotation angle in radians |
| `dx` / `dy` | Number | Offset from text position |
| `font` | String | Font family |
| `fontSize` | Number | Font size in pixels |
| `fontWeight` | String \| Number | `"normal"`, `"bold"`, or numeric weight |
| `lineHeight` | Number | Line height for multi-line text |
| `color` | Color | Text color (also used as fill) |

### Geoshape

Geographic shape marks for rendering GeoJSON features.

| Property | Type | Description |
|----------|------|-------------|
| `fill` | Color | Default: `"#eee"` |
| `stroke` | Color | Default: `"#fff"` |

Requires `projection` at spec level and data with GeoJSON or TopoJSON format.

### Image

Image marks for embedding images.

| Property | Type | Description |
|----------|------|-------------|
| `aspect` | Boolean | Maintain aspect ratio. Default: `true` |
| `align` | String | `"left"`, `"right"`, `"center"` |
| `baseline` | String | `"top"`, `"middle"`, `"bottom"` |

### Arc

Arc marks for pie/donut charts. Uses polar channels (`theta`, `radius`).

| Property | Type | Description |
|----------|------|-------------|
| `innerRadius` | Number | Inner radius in pixels (for donut). Default: `0` |
| `outerRadius` | Number | Outer radius in pixels |
| `cornerRadius` | Number | Corner radius for rounded arcs |
| `padAngle` | Number | Padding between arcs in radians. Default: `0` |
| `startAngle` / `endAngle` | Number | Override arc start/end angles |

## Composite Mark Types

### Boxplot

Shows distribution with median, quartiles, and whiskers.

| Property | Type | Description |
|----------|------|-------------|
| `extent` | String \| Number[] | Whisker extent: `"minmax"` (default), `"iqr"`, or `[lower, upper]` as fraction of IQR |
| `size` | Number | Width of box. Default from band scale |
| `orient` | String \| Null | `"vertical"` (default), `"horizontal"`, or `null` |
| `box` | Mark | Customization for the box mark |
| `median` | Mark | Customization for median rule mark |
| `rule` | Mark | Customization for whisker rule marks |
| `tick` | Mark | Customization for quartile tick marks |
| `outliers` | Boolean \| Mark | Show outlier points. Default: `true` |

**Parts**: box (IQR rectangle), median (rule), rules (whiskers), ticks (quartile ends), outliers (points).

### Errorbar

Error bar marks showing confidence intervals or standard deviations.

| Property | Type | Description |
|----------|------|-------------|
| `extent` | String \| Number | Extent computation: `"ci"` (confidence interval), `"stdev"` (standard deviation), `"stderr"` (standard error), or numeric extent value |
| `extentOpacity` | Number | Opacity of the extent range. Default: `0.2` |
| `barWidth` | Number | Width of error bar caps. Default: `6` |
| `orient` | String \| Null | `"vertical"` (default), `"horizontal"`, or `null` |
| `bar` / `cap` | Mark | Customization for bar and cap marks |

### Errorband

Error band marks (filled area showing uncertainty).

| Property | Type | Description |
|----------|------|-------------|
| `extent` | String \| Number | Same extent options as errorbar |
| `orient` | String \| Null | `"vertical"` (default), `"horizontal"`, or `null` |
| `band` / `extent` | Mark | Customization for band and extent marks |

## Mark Config and Style Config

### Mark Config

Set default properties per mark type in the config:

```json
{
  "config": {
    "bar": {"cornerRadius": 3},
    "point": {"shape": "diamond"},
    "text": {"fontSize": 12}
  }
}
```

### Style Config

Define named styles and apply them to marks:

```json
{
  "config": {
    "style": {
      "label": {"dy": -5, "align": "right", "dx": -5}
    }
  }
}
```

Apply via `mark.style`: `{"type": "text", "style": "label"}`.

Built-in style names: `"guide-label"`, `"guide-title"`, `"group-title"`.
