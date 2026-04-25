# Axes & Scales

## Overview

Axes determine how data maps to pixel values. Two categories:
- **Cartesian** — x/y axes for bar, line, scatter, bubble charts
- **Radial** — r axis for radar, polar area, doughnut, pie charts

### Default Scale IDs
- Cartesian: `'x'` (index), `'y'` (value)
- Radial: `'r'`

Datasets map to scales via `xAxisID`, `yAxisID`, or `rAxisID`. If not specified, the first scale of that axis is used.

## Common Scale Options

Namespace: `options.scales[scaleId]`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `type` | string | — | Scale type (e.g., `'linear'`, `'category'`, `'time'`) |
| `alignToPixels` | boolean | `false` | Align pixels to device pixels |
| `backgroundColor` | Color | — | Background color of scale area |
| `border` | object | — | Border configuration |
| `display` | boolean/string | `true` | `true`=visible, `false`=hidden, `'auto'`=only if dataset visible |
| `grid` | object | — | Grid line config (see below) |
| `min` | number | — | User-defined minimum, overrides data |
| `max` | number | — | User-defined maximum, overrides data |
| `reverse` | boolean | `false` | Reverse axis direction |
| `stacked` | boolean/string | `false` | Stack values. `'single'` stacks positive+negative together |
| `suggestedMax` | number | — | Suggested max (extends range without overriding auto-fit) |
| `suggestedMin` | number | — | Suggested min |
| `ticks` | object | — | Tick config (see below) |
| `weight` | number | `0` | Sort order; higher = further from chart area |

## Common Tick Options

Namespace: `options.scales[scaleId].ticks`

| Name | Type | Scriptable | Default | Description |
|------|------|:----------:|---------|-------------|
| `backdropColor` | Color | Yes | `'rgba(255,255,255,0.75)'` | Label background |
| `backdropPadding` | Padding | — | `2` | Backdrop padding |
| `callback` | function | — | — | Format tick value as string |
| `display` | boolean | — | `true` | Show labels |
| `color` | Color | Yes | default | Tick color |
| `font` | Font | Yes | default | Tick font |
| `major` | object | — | `{}` | Major tick config |
| `padding` | number | — | `3` | Label offset from axis |
| `showLabelBackdrop` | boolean | Yes | varies | Draw background behind labels |
| `textStrokeColor` | Color | Yes | — | Text stroke color |
| `textStrokeWidth` | number | Yes | `0` | Text stroke width |
| `z` | number | — | `0` | Z-index of tick layer |

### Custom Tick Callback
```javascript
ticks: {
  callback: (value) => value + ' kg',
  // or format numbers
  callback: (value) => value.toLocaleString()
}
```

## Axis Range Settings

`suggestedMin`/`suggestedMax` extend range without overriding auto-fit:
```javascript
// If data max is 50, but suggestedMax is 100, scale goes to 100
y: { suggestedMin: 0, suggestedMax: 100 }
```

`min`/`max` set explicit ends — some data may be clipped:
```javascript
y: { min: 0, max: 100 }
```

## Axis Callbacks

Namespace: `options.scales[scaleId]`

| Callback | Description |
|----------|-------------|
| `beforeUpdate` | Before update process starts |
| `beforeSetDimensions` | Before dimensions are set |
| `afterSetDimensions` | After dimensions are set |
| `beforeDataLimits` | Before data limits calculated |
| `afterDataLimits` | After data limits calculated |
| `beforeBuildTicks` | Before ticks created |
| `afterBuildTicks` | After ticks created (useful for filtering) |
| `beforeTickToLabelConversion` | Before ticks → strings |
| `afterTickToLabelConversion` | After ticks → strings |
| `beforeCalculateLabelRotation` | Before label rotation |
| `afterCalculateLabelRotation` | After label rotation |
| `beforeFit` | Before scale fits to canvas |
| `afterFit` | After scale fits to canvas |
| `afterUpdate` | End of update process |

## Updating Scale Defaults

```javascript
Chart.defaults.scales.linear.min = 0;
Chart.defaults.scales.category.autoSkip = true;
```

## Creating New Axes

See [Reference: Developers → Axes](./07-plugins-development.md#creating-new-axes) for extending axis types.

---

## Cartesian Scales

### Category Scale

Used for text labels (x-axis in bar/line charts). Maps string labels to integer indices.

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `labels` | string[]/number[] | — | Labels array (alternative to data labels) |
| `offset` | boolean | — | Space items within the axis |

### Linear Scale

For continuous numeric data.

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `beginAtZero` | boolean | `false` | Start axis at zero |

### Logarithmic Scale

For data spanning multiple orders of magnitude.

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `beginAtZero` | boolean | `false` | Start axis at zero |

### Time Scale

For temporal data. Uses date adapters (moment.js, luxon, or date-fns).

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `source` | string | `'auto'` | `'labels'`, `'auto'`, `'data'` |
| `isoWeekday` | boolean | — | Use ISO weekday for category scale |
| `min` | string/number/date | — | Minimum time value |
| `max` | string/number/date | — | Maximum time value |
| `tooltipFormat` | string | — | Moment/luxon date format for tooltips |
| `unit` | string | — | `'year'`, `'month'`, `'week'`, `'day'`, `'hour'`, `'minute'`, `'second'`, `'millisecond'` |
| `round` | string | — | Round ticks to this unit |
| `displayFormats` | object | — | Format overrides per unit |
| `time` | object | — | Time-specific options |
| `ticks.source` | string | `'auto'` | `'labels'`, `'data'`, `'auto'` |
| `ticks.stepSize` | number | — | Fixed tick step size |
| `ticks.maxTicksLimit` | number | — | Max ticks to display |
| `limits` | object | — | `{ max, min, stepSize }` per unit |

#### Time Source
- `'labels'` — use data labels as time values
- `'data'` — use x values of data points
- `'auto'` — automatic based on chart type

#### Unit Sizes (in milliseconds)
| Unit | ms |
|------|-----|
| `year` | 31536000000 |
| `month` | 2629746000 |
| `week` | 604800000 |
| `day` | 86400000 |
| `hour` | 3600000 |
| `minute` | 60000 |
| `second` | 1000 |
| `millisecond` | 1 |

### Time Series Scale

Same as time scale but auto-calculates step size based on data range.

---

## Radial Scales

### Radial Linear Scale

Used for radar, polar area, doughnut, and pie charts.

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `beginAtZero` | boolean | `false` | Start at zero |
| `angleLines` | object | — | Line config between center and labels |
| `pointLabels` | object | — | Label display/config |
| `ticks` | object | — | Tick config (see common ticks) |

#### Angle Lines
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `display` | boolean | `true` | Show angle lines |
| `color` | Color | — | Line color |
| `borderWidth` | number | `1` | Line width |
| `circle` | boolean | `false` | Draw circle instead of lines |

#### Point Labels
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `display` | boolean | `true` | Show point labels |
| `color` | Color | — | Label color |
| `font` | Font | — | Label font |
| `padding` | number | `5` | Padding |
| `callback` | function | — | Format label text: `(value) => value` |

## Grid Line Configuration

Namespace: `options.scales[scaleId].grid`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `display` | boolean | `true` | Show grid lines |
| `color` | Color | — | Grid line color (supports arrays for per-tick) |
| `borderColor` | Color | — | Border color |
| `borderWidth` | number | — | Line width |
| `borderDash` | number[] | — | Dashed line pattern |
| `borderDashOffset` | number | — | Dash offset |
| `drawBorder` | boolean | — | Draw axis border |
| `drawOnChartArea` | boolean | `true` | Draw grid on chart area |
| `drawTicks` | boolean | — | Draw tick marks |
| `tickColor` | Color | — | Tick mark color |
| `tickBorderDash` | number[] | — | Tick dash pattern |
| `tickBorderDashOffset` | number | — | Tick dash offset |
| `tickLength` | number | — | Tick mark length |
| `tickWidth` | number | — | Tick mark width |
| `offset` | boolean | — | Offset grid lines from center |
| `zeroLineWeight` | number | — | Weight of zero line |

## Styling Axes

### Border Configuration
Namespace: `options.scales[scaleId].border`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `display` | boolean | — | Show border |
| `color` | Color | — | Border color |
| `width` | number | — | Border width |
| `dash` | number[] | — | Dash pattern |

### Major Tick Configuration
Namespace: `options.scales[scaleId].ticks.major`

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `enabled` | boolean | — | Enable major tick styling |
| `font` | Font | — | Major tick font |
| `color` | Color | — | Major tick color |

### Tick Auto-Skip
```javascript
ticks: {
  autoSkip: true,
  maxTicksLimit: 10
}
```

### Creating Custom Tick Formats
```javascript
ticks: {
  callback: (value, index) => {
    if (index % 5 === 0) return value + ' units';
    return '';
  }
}
```
