# Migration

## v4 to v5 Migration

### Breaking Changes
- `chart.js` and `helpers` are now ESM-only (no UMD)
- Use `import Chart from 'chart.js/auto'` or tree-shaken imports
- Date adapters must be loaded before creating charts with time scales

### New Features
- Improved TypeScript support
- Better tree-shaking
- Enhanced animation system

## v3 to v4 Migration

### Breaking Changes

#### Configuration Changes
- `animation.charts[type]` → `transitions[type]`
- `dataset.backgroundColor` array fallback removed — use scriptable options instead
- `scaleLabel` renamed to `title` in scale configuration
- `ticks.userCallback` / `onChange` / `major.userCallback` renamed in tick config

#### Scale Options
- `position` → `axis` for determining axis direction
- `labels` (for category scale) is now under `categoryScale` defaults

#### Plugin Changes
- Plugin hooks updated for v3 API
- `afterDraw` → `afterRender`
- `beforeDatasetDraw` / `afterDatasetDraw` → `beforeDatasetsDraw` / `afterDatasetsDraw`

#### Data Structure
- Object data parsing: dot notation keys now use double backslash escaping
  - `'data.key'` → parsing key `'data\\.key'`

#### Chart Type Changes
- `scatter` chart: x-axis is linear by default (was category in v2)
- `bubble` chart: requires `{x, y, r}` data format
- Polar area: new `spacingMode` option (`'angular'`, `'proportional'`, `'parallel'`)

#### Options Resolution
- Scriptable options now receive a resolver as second parameter
- Option context objects preserved across calls

### Migration Code Examples

#### Old v3 → New v4
```javascript
// OLD (v3)
animation: {
  charts: {
    line: { duration: 1500 }
  }
}

// NEW (v4)
transitions: {
  active: { animation: { duration: 1500 } },
  normal: { animation: { duration: 1000 } }
}
```

#### Scale Title
```javascript
// OLD (v3)
scales: {
  x: {
    scaleLabel: { display: true, text: 'Month' }
  }
}

// NEW (v4)
scales: {
  x: {
    title: { display: true, text: 'Month' }
  }
}
```

#### Tick Callback
```javascript
// OLD (v3)
ticks: {
  userCallback: (value) => value + ' units'
}

// NEW (v4)
ticks: {
  callback: (value) => value + ' units'
}
```

## v2 to v3 Migration

### Major Changes
- Chart.js v3 is tree-shakeable — must explicitly register components
- `chart.js` → `import Chart from 'chart.js/auto'` loads everything
- Bundle optimization: import and register only needed components

#### Registration Required
```javascript
// OLD (v2) — all components auto-registered
import Chart from 'chart.js';

// NEW (v3+) — must register
import { Chart, BarController, CategoryScale, LinearScale, BarElement } from 'chart.js';
Chart.register(BarController, CategoryScale, LinearScale, BarElement);
```

#### Options Restructuring
- `scaleLabel` → `title`
- `ticks.userCallback` → `ticks.callback`
- `ticks.onChange` removed
- `pointLabels` → `angleLines` / `pointLabels` restructuring
- `legend.position` accepts `'chartArea'`
- `tooltip.callbacks.label` signature changed

#### Scale Options
```javascript
// OLD (v2)
scales: {
  xAxes: [{ type: 'category', ... }],
  yAxes: [{ type: 'linear', ... }]
}

// NEW (v3+)
scales: {
  x: { type: 'category', ... },
  y: { type: 'linear', ... }
}
```

#### Dataset Options
- `xAxisID` / `yAxisID` instead of `xScaleID` / `yScaleID`
- `pointStyle` accepts image/canvas elements
- `borderSkipped` for bar charts

#### Plugin Hooks
- `afterDraw` → `afterRender`
- Dataset hooks renamed to plural: `beforeDatasetsDraw`, `afterDatasetsDraw`
- New hooks: `beforeLayout`, `afterLayout`, `beforeDraw`, `draw`, `afterClip`, `beforeClip`

## Key Differences Summary

| v2 | v3/v4 |
|----|-------|
| `xAxes` / `yAxes` arrays | `x` / `y` objects |
| `scaleLabel` | `title` |
| `ticks.userCallback` | `ticks.callback` |
| `xScaleID` / `yScaleID` | `xAxisID` / `yAxisID` |
| Auto-registered components | Manual registration required |
| `chart.js` | `chart.js/auto` or tree-shaken imports |
| UMD builds for all loaders | ESM-first, helpers separate |
| `afterDraw` | `afterRender` |
