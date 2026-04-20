# Chart Types Reference

## Line Chart

A line chart plots data points on a line, often used to show trends or compare datasets.

### Dataset Properties

Key properties for each dataset:

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `data` | `object\|object[]\|number[]\|string[]` | **required** | Data points |
| `label` | `string` | `''` | Label for legend/tooltips |
| `fill` | `boolean\|string` | `false` | How to fill area under line |
| `tension` | `number` | `0` | Bézier curve tension (0 = straight lines) |
| `borderWidth` | `number` | `3` | Line stroke width in pixels |
| `borderColor` | `Color` | `rgba(0,0,0,0.1)` | Line color |
| `backgroundColor` | `Color` | `rgba(0,0,0,0.1)` | Fill color |
| `pointRadius` | `number` | `3` | Point radius (0 = hidden) |
| `pointStyle` | `string\|Image\|HTMLCanvasElement` | `'circle'` | Point shape |
| `stepped` | `boolean\|string` | `false` | Show as stepped line |
| `showLine` | `boolean` | `true` | Whether to draw the line |
| `spanGaps` | `boolean\|number` | `undefined` | Draw across null data points |
| `order` | `number` | `0` | Drawing order |
| `stack` | `string` | `'line'` | Stack group ID |

### Point Styles

Supported `pointStyle` values:
- `'circle'`, `'cross'`, `'crossRot'`, `'dash'`, `'line'`, `'rect'`, `'rectRounded'`, `'rectRot'`, `'star'`, `'triangle'`, `false`

### Area Filling Modes

For the `fill` property on line/radar datasets:
- `false` — No fill (default)
- `'origin'` — Fill to origin (0)
- `'start'` — Fill to start of scale
- `'end'` — Fill to end of scale
- `'-1'` or `'1'` — Fill to adjacent dataset
- `'#ID'` — Fill to element with specified ID
- `{ target: 'origin', above: 'red', below: 'blue' }` — Multi-color fill
- `'shape'` — Fill inside line shape
- `'stack'` — Stacked value below
- Absolute dataset index: `1`, `2`, `3` — Fill to specific dataset
- Relative: `'+1'`, `'-2'` — Fill relative to current dataset

**Multi-color fill example:**
```javascript
{
  fill: {
    target: 'origin',
    above: 'rgb(255, 0, 0)',   // Area above origin
    below: 'rgb(0, 0, 255)'    // Area below origin
  }
}
```

### Filler Plugin Configuration

Area filling is implemented by the `Filler` plugin:

```javascript
{
  plugins: {
    filler: {
      drawTime: 'beforeDatasetDraw',  // 'beforeDraw' | 'beforeDatasetDraw' | 'beforeDatasetsDraw'
      propagate: true                  // Recursively extend fill to visible targets
    }
  }
}
```

When `propagate: true`, hidden dataset targets are followed to find the final fill boundary.

## Bar Chart

Shows data values as vertical bars. Can be horizontal by swapping axes.

### Dataset Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `data` | `object[]\|number[]\|string[]` | **required** | Data values |
| `backgroundColor` | `Color\|Color[]` | `rgba(0,0,0,0.1)` | Bar fill color(s) |
| `borderColor` | `Color\|Color[]` | `rgba(0,0,0,0.1)` | Bar border color(s) |
| `borderWidth` | `number\|number[]` | `1` | Border width in pixels |
| `borderSkipped` | `string` | `'start'` | Skipped border: `'start'`, `'end'`, `'middle'`, `'bottom'`, `'left'`, `'top'`, `'right'`, or `false` |
| `borderRadius` | `number\|object` | `0` | Bar corner radius in pixels |
| `base` | `number` | `0` | Base value for the bar |
| `barPercentage` | `number` | `1` | Percentage of available width used |
| `barThickness` | `number\|'flex'` | — | Specific bar thickness in pixels, or `'flex'` to distribute |
| `maxBarThickness` | `number` | `Number.MAX_VALUE` | Maximum bar thickness |
| `minBarLength` | `number` | `0` | Minimum bar length in pixels |

### Horizontal Bar Chart

Set `indexAxis: 'y'` on the dataset or use `'barHorizontal'` type (v4+).

```javascript
{
  type: 'bar',
  options: {
    indexAxis: 'y',  // horizontal bars
    scales: {
      x: { beginAtZero: true }
    }
  }
}
```

## Doughnut / Pie Chart

Circular charts divided into segments. Pie has no hole; doughnut has a configurable `cutout`.

### Dataset Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `data` | `number[]` | **required** | Segment values |
| `backgroundColor` | `Color\|Color[]` | — | Arc fill colors |
| `borderColor` | `Color\|Color[]` | `'#fff'` | Arc border colors |
| `borderWidth` | `number\|number[]` | `2` | Border width in pixels |
| `borderAlign` | `'center'\|'inner'` | `'center'` | Stroke alignment |
| `hoverOffset` | `number` | `0` | Offset when hovered |
| `offset` | `number\|object` | `0` | Distance to offset the arc |

### Chart Options

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `cutout` | `string\|number` | `'50%'` | Inner cutout (percentage or pixels) — 0 = pie |
| `radius` | `string\|number` | `'80%'` | Chart radius |
| `animation.animateRotate` | `boolean` | `true` | Animate the arc angle |
| `animation.animateScale` | `boolean` | `false` | Animate from center scale |

## Radar Chart

Polar coordinate chart showing values on multiple axes radiating from center.

### Dataset Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `data` | `number[]` | **required** | Data values per axis |
| `fill` | `boolean` | `true` | Fill area under line |
| `backgroundColor` | `Color` | `rgba(0,0,0,0.1)` | Fill color |
| `borderColor` | `Color` | `rgba(0,0,0,0.1)` | Border color |
| `pointBackgroundColor` | `Color` | `rgba(0,0,0,0.1)` | Point fill color |
| `pointBorderColor` | `Color` | `rgba(0,0,0,0.1)` | Point border color |
| `pointRadius` | `number` | `3` | Point radius |

## Polar Area Chart

Similar to doughnut but each segment has equal angle and radius varies by value.

### Chart Options

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `angleLines.display` | `boolean` | `false` | Show angle lines |
| `scales.r` | `object` | — | Radial scale configuration |

### Dataset Properties

Uses arc element options: `backgroundColor`, `borderColor`, `borderWidth`, `borderAlign`, `borderDash`.

## Scatter Chart

Plots individual data points on X/Y axes (uses line chart infrastructure).

### Data Format

```javascript
{
  datasets: [{
    label: 'Scatter',
    data: [
      { x: -10, y: 0 },
      { x: 0, y: 10 },
      { x: 10, y: 5 }
    ]
  }]
}
```

### Key Properties

Same as line chart. The primary difference is the data format uses `{x, y}` objects.

## Bubble Chart

Similar to scatter but each point has a third dimension (radius).

### Data Format

```javascript
{
  datasets: [{
    label: 'Bubble Dataset',
    data: [
      { x: 10, y: 20, r: 5 },   // radius = 5px
      { x: 15, y: -2, r: 10 },
      { x: -5, y: 3, r: 15 }
    ]
  }]
}
```

### Key Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `data` | `object[]` | **required** | Array of `{x, y, r}` objects |
| `r` | `number` | — | Radius for each data point |
| `barPercentage` | `number` | `1` | Controls bubble size |

## Mixed Chart

Combine multiple chart types in a single chart by setting different `type` per dataset:

```javascript
{
  type: 'line',
  data: {
    labels: ['A', 'B', 'C'],
    datasets: [
      {
        type: 'bar',
        label: 'Bar Dataset',
        data: [10, 20, 30]
      },
      {
        type: 'line',
        label: 'Line Dataset',
        data: [15, 25, 35],
        borderColor: 'rgb(75, 192, 192)'
      }
    ]
  }
}
```

### Drawing Order

Control which chart type renders on top with the `order` property:
- Lower `order` values render on top
- Default order: `'line'` and `'bar'` are separate groups
- Set `order: 1` for bar, `order: 2` for line to put bars on top

## Chart Type Registry

Access available chart types programmatically:

```javascript
import { Chart, registry } from 'chart.js';

// Get all registered chart types
const types = registry.getControllers();  // Map of type -> controller

// Register a custom chart type
class MyChart extends Chart {
  static id = 'myChart';
  // ... implementation
}
Chart.register(MyChart);
```
