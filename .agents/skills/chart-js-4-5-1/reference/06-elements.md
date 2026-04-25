# Elements

Element options style **all datasets** of a type the same way. Set globally via `Chart.defaults.elements` or per-chart in `options.elements`.

## Point Configuration

Used in line, radar, and bubble charts.

Namespace: `options.elements.point`, global: `Chart.defaults.elements.point`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `radius` | number | `3` | Point radius |
| `pointStyle` | string/Image/Canvas | `'circle'` | Point style |
| `rotation` | number | `0` | Rotation in degrees |
| `backgroundColor` | Color | default bg | Fill color |
| `borderWidth` | number | `1` | Stroke width |
| `borderColor` | Color | default border | Stroke color |
| `hitRadius` | number | `1` | Extra radius for hit detection |
| `hoverRadius` | number | `4` | Radius when hovered |
| `hoverBorderWidth` | number | `1` | Stroke width when hovered |

### Point Styles
- `'circle'` — circle
- `'cross'` — cross (+)
- `'crossRot'` — rotated cross (×)
- `'dash'` — dashed line (—)
- `'line'` — single line (|)
- `'rect'` — rectangle
- `'rectRounded'` — rounded rectangle
- `'rectRot'` — rotated rectangle (diamond)
- `'star'` — star
- `'triangle'` — triangle
- `false` — no point
- `Image` / `HTMLCanvasElement` — custom image

## Line Configuration

Used in line and radar charts.

Namespace: `options.elements.line`, global: `Chart.defaults.elements.line`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `tension` | number | `0` | Bézier curve tension (0 = straight) |
| `backgroundColor` | Color | default bg | Line fill color |
| `borderWidth` | number | `3` | Stroke width |
| `borderColor` | Color | default border | Stroke color |
| `borderCapStyle` | string | `'butt'` | Line cap: `'butt'`, `'round'`, `'square'` |
| `borderDash` | number[] | `[]` | Dash pattern |
| `borderDashOffset` | number | `0` | Dash offset |
| `borderJoinStyle` | string | `'miter'` | Join: `'round'`, `'bevel'`, `'miter'` |
| `capBezierPoints` | boolean | `true` | Keep Bézier points inside chart |
| `cubicInterpolationMode` | string | `'default'` | Interpolation mode |
| `fill` | boolean/string | `false` | Fill area under line |
| `stepped` | boolean | `false` | Show as stepped line |

## Bar Configuration

Used in bar charts.

Namespace: `options.elements.bar`, global: `Chart.defaults.elements.bar`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `backgroundColor` | Color | default bg | Fill color |
| `borderWidth` | number | `0` | Stroke width |
| `borderColor` | Color | default border | Stroke color |
| `borderSkipped` | string | `'start'` | Skipped border side |
| `borderRadius` | number/object | `0` | Border radius (in pixels) |
| `inflateAmount` | number/'auto' | `'auto'` | Inflation amount when drawing |
| `pointStyle` | string | `'circle'` | Legend point style |

### borderSkipped Values
- `'start'` — skip first border
- `'end'` — skip last border
- `'middle'` — skip middle (for floating bars)
- `'bottom'`, `'left'`, `'top'`, `'right'` — specific sides
- `false` — don't skip any border

## Arc Configuration

Used in polar area, doughnut, and pie charts.

Namespace: `options.elements.arc`, global: `Chart.defaults.elements.arc`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `angle` | number | `circumference / count` | Arc angle (polar only) |
| `backgroundColor` | Color | default bg | Fill color |
| `borderAlign` | string | `'center'` | Stroke alignment: `'center'`, `'inner'` |
| `borderColor` | Color | `'#fff'` | Stroke color |
| `borderDash` | number[] | `[]` | Dash pattern |
| `borderDashOffset` | number | `0` | Dash offset |
| `borderJoinStyle` | string | `'round'` (inner) / `'bevel'` | Join style |
| `borderWidth` | number | `2` | Stroke width |
| `circular` | boolean | `true` | Curved arc; `false` = flat |

## Global Element Defaults

```javascript
// Set border width for all bars globally
Chart.defaults.elements.bar.borderWidth = 2;

// Set point radius for all charts
Chart.defaults.elements.point.radius = 5;
```

## Element Options Resolution

Element options resolve through these scopes (highest to lowest priority):
1. `dataset` level
2. `options.datasets[type]`
3. `options.datasets[type].elements[elementType]`
4. `options.elements[elementType]`
5. `options` chart level
6. `overrides[type].datasets[type].elements[elementType]`
7. `defaults.datasets[type].elements[elementType]`
8. `defaults.elements[elementType]`
9. `defaults`

## Colors Reference

Colors can be specified as:
- Named colors: `'red'`, `'blue'`, `'green'`
- RGB: `'rgb(255, 99, 132)'`
- RGBA: `'rgba(255, 99, 132, 0.5)'`
- HEX: `'#ff6384'`
- HSL: `'hsl(340, 80%, 60%)'`

For dynamic colors, use scriptable options with `Chart.helpers.color()`:
```javascript
backgroundColor: function(context) {
  const color = 'rgba(255, 99, 132, 0.5)';
  return Chart.helpers.color(color).alpha(0.5).rgbString();
}
```

## Padding

Padding can be specified as:
- Number: applies to all sides
- Object: `{ top: 10, right: 20, bottom: 5, left: 15 }`
- Array `[topRight, bottomRight, bottomLeft, topLeft]` (CSS-style)

## Fonts

Font objects:
```javascript
font: {
  family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
  size: 14,
  style: 'normal' | 'italic' | 'bold',
  weight: 'normal' | 'bold' | '600' | '700',
  lineHeight: 1.2
}
```
