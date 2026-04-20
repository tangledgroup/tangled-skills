# Migration Guide

## v4 → v3 Breaking Changes

Chart.js 4.x is an **ESM-only package**. Your project must use ES modules (`"type": "module"` in `package.json`).

### Package Format

| v3 | v4 |
|----|----|
| `dist/chart.esm.js` | `dist/chart.js` |
| `dist/chart.umd.js` (before 4.5.0) | `dist/chart.umd.min.js` |
| N/A | `chart.js/auto` — auto-register all components |
| N/A | `chart.js/helpers` — separate helpers package |

### Configuration Changes

#### Scale Border Options

```javascript
// v3
scales: {
  y: {
    grid: {
      drawBorder: true,
      borderWidth: 1,
      borderColor: 'rgba(0,0,0,0.1)',
      borderDash: [],
      borderDashOffset: 0
    }
  }
}

// v4
scales: {
  y: {
    grid: { drawBorder: true },  // keep for grid lines
    border: {
      display: true,              // was drawBorder
      width: 1,                   // was borderWidth
      color: 'rgba(0,0,0,0.1)',   // was borderColor
      dash: [],                   // was borderDash
      dashOffset: 0               // was borderDashOffset
    }
  }
}
```

#### Plugin Hooks

| v3 | v4 |
|----|----|
| `destroy(chart)` | `afterDestroy(chart)` |

#### Time Scale

- Tick callbacks now receive **timestamps** (not formatted labels)
- `time.stepSize` → `ticks.stepSize`
- Default property for object data: `x` or `y` (was `t`)

#### Doughnut/Pie

| v3 | v4 |
|----|----|
| `cutoutPercentage: 50` | `cutout: '50%'` or `cutout: 50` (pixels) |
| `rotation: -Math.PI/2` | `rotation: 0` (0 is at top) |
| `circumference: 2*Math.PI` | `circumference: 360` (degrees) |
| Polar area `angle` in radians | Polar area `angle` in degrees |

#### Chart Defaults

| v3 | v4 |
|----|----|
| `Chart.defaults.global` | `Chart.defaults` |
| `Chart.defaults.line` | `Chart.defaults.overrides.line` |
| `Chart.defaults.global.defaultColor` | `Chart.defaults.color` |
| `defaultFontColor` | `color` |
| `defaultFontFamily` | `font.family` |
| `defaultFontSize` | `font.size` |
| `legend/title/tooltip` in root scope | Moved to `plugins.legend/title/tooltip` |

#### Other Changes

- `maintainAspectRatio` now respects container height
- Linear scales add/subtract 5% of max when min === max
- `maxTicksLimit` behavior changed with `autoSkip`
- Dataset controller defaults moved to `overrides`
- `ChartMeta` parameters reordered: `<Type, Element, DatasetElement>` (was `<Element, DatasetElement, Type>`)

### ESM-Only Package

```bash
# Add to package.json
{
  "type": "module"
}
```

#### CommonJS Workaround

If using CommonJS, use dynamic import:
```javascript
const { Chart } = await import('chart.js');
```

#### Jest Testing

Jest requires ESM configuration. Consider migrating to Vitest:
```bash
npm install -D vitest
```
Vitest has ESM support out of the box.

## v3 → v2 Breaking Changes (Reference)

These changes are relevant for understanding the current architecture:

### Axis Configuration

```javascript
// v2
options: {
  scales: {
    xAxes: [{
      id: 'x',
      type: 'time',
      title: { display: true, text: 'Date' }
    }],
    yAxes: [{
      id: 'y',
      title: { display: true, text: 'value' }
    }]
  }
}

// v3+
options: {
  scales: {
    x: {
      type: 'time',
      title: { display: true, text: 'Date' }
    },
    y: {
      title: { display: true, text: 'value' }
    }
  }
}
```

### Key Option Renames (v2 → v3)

| v2 | v3+ |
|----|-----|
| `scales.[x/y]Axes.ticks.beginAtZero` | `scales[id].beginAtZero` |
| `scales.[x/y]Axes.ticks.min` | `scales[id].min` |
| `scales.[x/y]Axes.ticks.max` | `scales[id].max` |
| `scales.[x/y]Axes.ticks.userCallback` | `scales[id].ticks.callback` |
| `scales.[x/y]Axes.scaleLabel` | `scales[id].title` |
| `tooltips` namespace | `tooltip` |
| `legend/title/tooltip` in root | Moved to `plugins.*` |
| `elements.rectangle` | `elements.bar` |
| `steppedLine` (dataset) | `stepped` |
| `showLines` (chart) | `showLine` |
| `hover.animationDuration` | `animation.active.duration` |
| `responsiveAnimationDuration` | `animation.resize.duration` |
| `polarArea.elements.arc.angle` (radians) | Degrees |

### Dataset Options Moved to Chart Level

| v2 | v3+ |
|----|-----|
| `barPercentage` (in scale config) | Dataset option |
| `barThickness` (in scale config) | Dataset option |
| `categoryPercentage` (in scale config) | Dataset option |
| `maxBarThickness` (in scale config) | Dataset option |
| `minBarLength` (in scale config) | Dataset option |

### Defaults Restructured

| v2 | v3+ |
|----|-----|
| `Chart.defaults.global` | `Chart.defaults` |
| `Chart.defaults.global.defaultColor` | `Chart.defaults.color` |
| `Chart.defaults.global.fontFamily` | `Chart.defaults.font.family` |
| `Chart.defaults.global.fontSize` | `Chart.defaults.font.size` |
| `legend/title/tooltip` in root scope | `Chart.defaults.plugins.legend/title/tooltip` |
| Dataset controller defaults | Moved to `overrides.*` |

### Removed Features

- `horizontalBar` chart type (use `indexAxis: 'y'`)
- `Chart.bundle.js` / `Chart.bundle.min.js`
- CSS injection
- `time.stepSize` in scale config (use `ticks.stepSize`)
- `suggestedMax` / `suggestedMin` removed (use `max`/`min` with `beginAtZero`)

## v4 Tree-Shaking Components

### Required Components Per Chart Type

| Chart | Controller | Elements | Scales | Plugins |
|-------|-----------|----------|--------|---------|
| Bar | `BarController` | `BarElement` | `CategoryScale`, `LinearScale` | `Tooltip`, `Legend`, `Title` |
| Bubble | `BubbleController` | `PointElement` | `LinearScale` (x/y) | `Tooltip`, `Legend` |
| Doughnut | `DoughnutController` | `ArcElement` | *(none)* | `Tooltip`, `Legend` |
| Pie | `PieController` | `ArcElement` | *(none)* | `Tooltip`, `Legend` |
| Line | `LineController` | `LineElement`, `PointElement` | `CategoryScale`, `LinearScale` | `Tooltip`, `Legend` |
| Polar Area | `PolarAreaController` | `ArcElement` | `RadialLinearScale` | `Tooltip`, `Legend` |
| Radar | `RadarController` | `LineElement`, `PointElement` | `RadialLinearScale` | `Tooltip`, `Legend` |
| Scatter | `ScatterController` | `PointElement` | `LinearScale` (x/y) | `Tooltip`, `Legend` |

### Complete Import Example (Line Chart)

```javascript
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  Title
} from 'chart.js';

Chart.register(
  LineController, LineElement, PointElement,
  CategoryScale, LinearScale,
  Tooltip, Legend, Title
);
```

### Available Plugins

| Plugin | ID | Purpose |
|--------|----|---------|
| Decimation | `decimation` | Reduce data points for performance |
| Filler | `filler` | Fill area under line/radar charts |
| Legend | `legend` | Display legend |
| SubTitle | `subTitle` | Additional subtitle |
| Title | `title` | Chart title |
| Tooltip | `tooltip` | Hover tooltips |

### Available Scales

**Cartesian (x/y):**
- `CategoryScale` — Text labels
- `LinearScale` — Linear numeric
- `LogarithmicScale` — Logarithmic
- `TimeScale` — Time-based
- `TimeSeriesScale` — High-frequency time series

**Radial (r):**
- `RadialLinearScale` — Polar coordinates (radar, polar area)
