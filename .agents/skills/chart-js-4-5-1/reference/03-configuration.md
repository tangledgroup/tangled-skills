# Configuration

## Animations

Chart.js animates charts out of the box. Animation config has 3 keys:

| Key | Type | Description |
|-----|------|-------------|
| `animation` | `object` | Single animation config |
| `animations` | `object` | Per-element animations |
| `transitions` | `object` | Mode-specific overrides |

### animation (single)
Namespace: `options.animation`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `duration` | `number` | `1000` | Milliseconds per animation |
| `easing` | `string` | `'easeOutQuart'` | Easing function |
| `delay` | `number` | — | Delay before starting |
| `loop` | `boolean` | — | Loop endlessly |
| `onProgress` | `function` | — | Called each animation step |
| `onComplete` | `function` | — | Called when done |

### easing functions
`linear`, `easeInQuad`, `easeOutQuad`, `easeInOutQuad`, `easeInCubic`, `easeOutCubic`, `easeInOutCubic`, `easeInQuart`, `easeOutQuart`, `easeInOutQuart`, `easeInQuint`, `easeOutQuint`, `easeInOutQuint`, `easeInSine`, `easeOutSine`, `easeInOutSine`, `easeInExpo`, `easeOutExpo`, `easeInOutExpo`, `easeInCirc`, `easeOutCirc`, `easeInOutCirc`, `easeInElastic`, `easeOutElastic`, `easeInOutElastic`, `easeInBack`, `easeOutBack`, `easeInOutBack`, `easeInBounce`, `easeOutBounce`, `easeInOutBounce`

### animations (per-element)
Namespace: `options.animations[name]`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `properties` | `string[]` | key name | Property names this applies to |
| `type` | `string` | typeof property | `'number'`, `'color'`, or `'boolean'` |
| `from` | varies | current value | Start value |
| `to` | varies | updated value | End value |
| `fn` | `function` | — | Custom interpolator |

Default animations:
- `numbers`: properties `['x', 'y', 'borderWidth', 'radius', 'tension']`, type `'number'`
- `colors`: properties `['color', 'borderColor', 'backgroundColor']`, type `'color'`

### transitions (mode-specific)
Namespace: `options.transitions[mode]`

Default transitions:
- `active`: duration 400ms (hover)
- `resize`: duration 0 (no animation)
- `show`: colors fade in from transparent
- `hide`: colors fade to transparent

### Disabling Animation
```javascript
chart.options.animation = false;          // all animations
chart.options.animations.colors = false;  // color animations only
chart.options.animations.x = false;       // x property only
```

## Tooltip

Namespace: `options.plugins.tooltip`, global: `Chart.defaults.plugins.tooltip`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `enabled` | `boolean` | `true` | Enable tooltips |
| `mode` | `string` | `interaction.mode` | Which elements appear |
| `intersect` | `boolean` | `interaction.intersect` | Require mouse intersection |
| `position` | `string` | `'average'` | `'average'` or `'nearest'` |
| `callbacks` | `object` | — | Custom label/formatter functions |
| `itemSort` | `function` | — | Sort tooltip items |
| `filter` | `function` | — | Filter tooltip items |
| `backgroundColor` | `Color` | `'rgba(0,0,0,0.8)'` | Background color |
| `titleColor` | `Color` | `'#fff'` | Title text color |
| `titleFont` | `Font` | `{weight: 'bold'}` | Title font |
| `bodyColor` | `Color` | `'#fff'` | Body text color |
| `bodyFont` | `Font` | `{}` | Body font |
| `footerColor` | `Color` | `'#fff'` | Footer text color |
| `footerFont` | `Font` | `{weight: 'bold'}` | Footer font |
| `padding` | `Padding` | `6` | Internal padding |
| `cornerRadius` | `number\|object` | `6` | Corner radius |
| `caretSize` | `number` | `5` | Arrow size |
| `displayColors` | `boolean` | `true` | Show color boxes |
| `usePointStyle` | `boolean` | `false` | Use point style instead of color boxes |
| `xAlign` | `string` | auto | `'left'`, `'center'`, `'right'` |
| `yAlign` | `string` | auto | `'top'` (plus computed offset) |

### Tooltip Callbacks
```javascript
callbacks: {
  title: (items) => items[0].label,
  label: (context) => `${context.dataset.label}: ${context.parsed.y}`,
  after: (items) => 'Total: ' + items.reduce((sum, i) => sum + i.parsed.y, 0)
}
```

## Legend

Namespace: `options.plugins.legend`, global: `Chart.defaults.plugins.legend`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `display` | `boolean` | `true` | Show legend |
| `position` | `string` | `'top'` | `'top'`, `'left'`, `'bottom'`, `'right'`, `'chartArea'` |
| `align` | `string` | `'center'` | `'start'`, `'center'`, `'end'` |
| `reverse` | `boolean` | `false` | Reverse order |
| `onClick` | `function` | — | Click handler for legend items |
| `onHover` | `function` | — | Mouse move handler |
| `labels.boxWidth` | `number` | `40` | Legend box width |
| `labels.padding` | `number` | `10` | Padding between rows |
| `labels.usePointStyle` | `boolean` | `false` | Use point style for legend |
| `title.display` | `boolean` | — | Show title |
| `title.text` | `string` | — | Title text |

### Disable Legend
```javascript
options: { plugins: { legend: { display: false } } }
```

## Title

Namespace: `options.plugins.title`, global: `Chart.defaults.plugins.title`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `display` | `boolean` | `false` | Show title |
| `text` | `string\|string[]` | `''` | Title text (array = multiline) |
| `position` | `string` | `'top'` | `'top'`, `'left'`, `'bottom'`, `'right'` |
| `align` | `string` | `'center'` | `'start'`, `'center'`, `'end'` |
| `font` | `Font` | `{weight: 'bold'}` | Font config |
| `padding` | `Padding` | `10` | Padding (top/bottom) |
| `fullSize` | `boolean` | `true` | Take full canvas width/height |

```javascript
options: {
  plugins: {
    title: { display: true, text: 'Monthly Sales', font: { size: 18 } }
  }
}
```

## Interactions

Namespace: `options.interaction`, global: `Chart.defaults.interaction`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `mode` | `string` | `'nearest'` | Interaction mode (see below) |
| `intersect` | `boolean` | `true` | Require intersection |
| `axis` | `string` | `'x'` | `'x'`, `'y'`, `'xy'`, `'r'` |
| `includeInvisible` | `boolean` | `false` | Include invisible points |

### Interaction Modes
- `'nearest'` — show nearest element(s)
- `'index'` — show all at same index
- `'dataset'` — show entire dataset
- `'x'` / `'y'` — project on axis
- `'none'` — no interaction

### Events
Namespace: `options`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `events` | `string[]` | `['mousemove','mouseout','click','touchstart','touchmove']` | Browser events to listen to |
| `onHover` | `function` | — | Called on any event over chartArea |
| `onClick` | `function` | — | Called on click/contextmenu over chartArea |

### Converting Events to Data
```javascript
onClick: (e) => {
  const pos = Chart.helpers.getRelativePosition(e, chart);
  const x = chart.scales.x.getValueForPixel(pos.x);
  const y = chart.scales.y.getValueForPixel(pos.y);
}
```

## Responsive

Namespace: `options.responsive`, global: `Chart.defaults.responsive`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `responsive` | `boolean` | `true` | Resize with container |
| `maintainAspectRatio` | `boolean` | `false` | Keep aspect ratio |
| `aspectRatio` | `number` | varies | Default: 1 for radial, 2 for others |
| `onResize` | `function` | — | Called on resize |

```javascript
options: {
  responsive: true,
  maintainAspectRatio: false,
  aspectRatio: 2
}
```

## Decimation

Namespace: `options.plugins.decimation`, global: `Chart.defaults.plugins.decimation`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `algorithm` | `string` | `'minmax'` | `'lttb'` or `'minmax'` |
| `enabled` | `boolean` | `false` | Enable decimation |
| `threshold` | `number` | — | Point threshold for enabling |

## Canvas Background

```javascript
const plugin = {
  id: 'customBackground',
  beforeDraw: (chart, args, options) => {
    const { ctx } = chart;
    ctx.save();
    ctx.globalCompositeOperation = 'destination-over';
    ctx.fillStyle = options.color;
    ctx.fillRect(0, 0, chart.width, chart.height);
    ctx.restore();
  },
  defaults: { color: '#ffffff' }
};
```

## Device Pixel Ratio

Namespace: `options.devicePixelRatio`, global: `Chart.defaults.devicePixelRatio`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `devicePixelRatio` | `number\|function` | auto | Override DPI. Use function for responsive: `(chart) => chart.canvas.offsetWidth / 2` |

## Layout

Namespace: `options.layout`, global: `Chart.defaults.layout`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `padding` | `Padding` | `{top:0,right:0,bottom:0,left:0}` | Padding around chart area |

## Locale & Number Formatting

Namespace: `options.plugins.tooltip`, global settings

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `locale` | `string` | — | Set locale for number formatting (e.g., `'de-DE'`) |
