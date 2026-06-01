# Mark Basics

Marks are the visual building blocks of a visualization. The `mark` property specifies the mark type and its styling.

## String vs Object Form

```json
// String form — simplest
"mark": "bar"

// Object form — with properties
"mark": {
  "type": "bar",
  "cornerRadius": 3,
  "tooltip": true
}
```

Properties in the mark definition are **overridden** by encoding channels. For example, `mark.color` is overridden if `encoding.color` maps a field.

## Primitive Mark Types (11)

| Mark | Visual Role | Key Encodings |
|------|-------------|---------------|
| `area` | Filled region under a line | `x`, `y`, `y2` (ranged) |
| `bar` | Rectangular bars | `x`, `y`, stacking, `cornerRadius` |
| `circle` | Circular points (scatterplots) | `x`, `y`, `size`, `color` |
| `line` | Connected segments | `x`, `y`, interpolation, `strokeDash` |
| `point` | Point markers (various shapes) | `x`, `y`, `shape`, `filled` |
| `rect` | Rectangles (heatmaps, mosaics) | `x`, `y`, `x2`, `y2` |
| `rule` | Lines at a single position | `x` or `y`, `x2`/`y2` (ranged) |
| `square` | Square points | `x`, `y`, `size` |
| `text` | Text labels/annotations | `x`, `y`, `text`, `align`, `baseline` |
| `tick` | Tick marks/dot plots | `x` or `y`, `thickness` |
| `geoshape` | GeoJSON polygons/lines | geographic data, `projection` |

## Composite Mark Types (3)

| Mark | Composed Of | Purpose |
|------|-------------|---------|
| `boxplot` | rule + rect + point | Statistical box-and-whisker display |
| `errorbar` | rule + tick | Error range visualization |
| `errorband` | area | Shaded error/confidence region |

## General Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `type` | string | Mark type name (required in object form) |
| `cursor` | string | CSS cursor on hover (`"pointer"`, `"crosshair"`, etc.) |
| `style` | string \| array | Named style from `config.style` |
| `tooltip` | boolean \| array | Show default tooltip; `true` shows all fields |
| `clip` | boolean | Clip marks to enclosing group bounds |
| `invalid` | string | Handling of invalid data (`"filter"` or `"break"`) |
| `order` | number | Drawing order (higher = on top) |
| `aria` | boolean | Generate ARIA attributes for accessibility |
| `description` | string | Default mark description text |

## Position and Offset Properties

Set constant positions directly on the mark definition (bypasses encoding):

| Property | Type | Description |
|----------|------|-------------|
| `x`, `y` | number | Constant position |
| `x2`, `y2` | number | Ranged mark end position |
| `width`, `height` | number | Mark dimensions |
| `xOffset`, `yOffset` | number | Position offset |
| `x2Offset`, `y2Offset` | number | Ranged position offset |

## Color Properties

| Property | Type | Description |
|----------|------|-------------|
| `filled` | boolean | Whether mark is filled (default varies by mark) |
| `color` | string | Shorthand for both `fill` and `stroke` |
| `fill` | string | Interior color |
| `stroke` | string | Outline color |
| `opacity` | number | Overall opacity (0-1) |
| `fillOpacity` | number | Fill opacity (0-1) |
| `strokeOpacity` | number | Stroke opacity (0-1) |
| `blend` | string | CSS blend mode (`"multiply"`, `"screen"`, etc.) |

## Stroke Style Properties

| Property | Type | Description |
|----------|------|-------------|
| `strokeWidth` | number | Stroke line width in pixels |
| `strokeCap` | string | Line cap (`"butt"`, `"round"`, `"square"`) |
| `strokeDash` | array | Dash pattern `[dash, gap]` (e.g., `[6, 4]`) |
| `strokeDashOffset` | number | Dash offset |
| `strokeJoin` | string | Corner join (`"miter"`, `"round"`, `"bevel"`) |
| `strokeMiterLimit` | number | Miter limit for sharp corners |

## Hyperlink Properties

| Property | Type | Description |
|----------|------|-------------|
| `href` | string | URL to navigate to on click; auto-sets `cursor: "pointer"` |

## Mark Config

Global defaults via `config`:

```json
{
  "config": {
    "mark": {"opacity": 0.8},           // all marks
    "bar": {"cornerRadius": 3},         // bar-specific
    "point": {"filled": true, "size": 100}  // point-specific
  }
}
```

`config.mark` supports all standard properties except `type`, `style`, `clip`, `orient`. Mark-specific configs (e.g., `config.bar`) support that mark's full property set.

**Note**: Mark config does not support offset properties (`xOffset`, `yOffset`).

## Mark Style Config

Named styles for reusable mark themes:

```json
{
  "config": {
    "style": {
      "triangle": {
        "shape": "triangle-up",
        "strokeWidth": 2
      }
    }
  }
}
```

Invoke with `"mark": {"type": "point", "style": "triangle"}`.

### Built-in Style Names

| Name | Applies To |
|------|-----------|
| `"guide-label"` | Axis, legend, header labels |
| `"guide-title"` | Axis, legend, header titles |
| `"group-title"` | Chart titles |

Use style config to set `dx`/`dy` offsets for text mark labels on other marks.
