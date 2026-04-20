---
name: chart-js-4-5-1
description: Complete toolkit for Chart.js 4.5.1, the most popular open-source JavaScript charting library using HTML5 Canvas rendering. Use when creating interactive charts (line, bar, pie, doughnut, radar, polar area, scatter, bubble, area), configuring axes and scales, customizing animations, tooltips, legends, elements, implementing responsive design, handling data structures, performance optimization, or building data visualizations with TypeScript support across all major JavaScript frameworks.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "4.5.1"
tags:
  - charts
  - canvas
  - data-visualization
  - javascript
  - html5
  - responsive
category: frontend
external_references:
  - https://www.chartjs.org/docs/latest/
  - https://github.com/chartjs/Chart.js
---

# Chart.js 4.5.1

## Overview

Chart.js is the most popular open-source JavaScript charting library (~60,000 GitHub stars, ~2.4M weekly npm downloads). It renders charts on HTML5 Canvas for high performance with large datasets and provides a simple yet flexible API for creating interactive data visualizations.

**Key features:**
- 8 built-in chart types: Line, Bar, Doughnut/Pie, Radar, Polar Area, Scatter, Bubble, and Mixed charts
- Fully responsive with device pixel ratio support
- Animated transitions with configurable easing functions
- Built-in TypeScript typings
- Canvas-based rendering (performant for large datasets)
- Plugin architecture for extensions (zoom, annotation, etc.)
- Tree-shaking support for minimal bundle sizes

## When to Use

Use this skill when:
- Creating charts (line, bar, pie, doughnut, radar, polar area, scatter, bubble) in JavaScript/TypeScript projects
- Configuring chart options: axes, scales, legends, tooltips, animations, elements
- Implementing responsive charts that adapt to container size changes
- Customizing chart appearance: colors, fonts, borders, shadows, gradients
- Building data dashboards or reporting interfaces
- Integrating Chart.js with React, Vue, Svelte, Angular, or vanilla JS
- Optimizing chart performance for large datasets
- Migrating from Chart.js v2 or v3 to v4

## Core Concepts

### Chart Configuration

Every chart is created from a configuration object passed to the `Chart` constructor:

```javascript
const config = {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{
      label: 'Sales',
      data: [12, 19, 3],
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  },
  options: {
    responsive: true,
    plugins: { title: { display: true, text: 'Monthly Sales' } }
  }
};

const myChart = new Chart(context, config);
```

### Chart Types

| Type | Description | Key Properties |
|------|-------------|----------------|
| `line` | Data points connected by lines | `tension`, `fill`, `stepped`, `showLine` |
| `bar` | Vertical/horizontal bars | `borderSkipped`, `borderRadius`, `base` |
| `doughnut` / `pie` | Circular charts with segments | `cutout`, `offset`, `hoverOffset` |
| `radar` | Polar coordinate polygon | `pointBackgroundColor`, `fill` |
| `polarArea` | Radial segments by angle | Same as arc element options |
| `scatter` | X/Y point cloud (line-type) | `data: [{x, y}]` format |
| `bubble` | Circles sized by value | `data: [{x, y, r}]` format |
| `mixed` | Combination of types in one chart | Different `type` per dataset |

### Data Structure

Data formats (see [General Concepts](references/04-general-concepts.md) for full details):

```javascript
// Array format (with labels)
{ labels: ['Jan', 'Feb'], datasets: [{ data: [12, 19] }] }

// Object format (key-value pairs)
{ datasets: [{ data: { Jan: 12, Feb: 19 } }] }

// Scatter/Bubble format (x,y points)
{ datasets: [{ data: [{ x: -5, y: 3 }, { x: 2, y: 6 }] }] }

// Bubble format (x, y, radius)
{ datasets: [{ data: [{ x: 10, y: 5, r: 10 }] }] }

// Internal format (skip parsing for performance)
{ parsing: false, datasets: [{ data: [0, 1, 2, 3, 4] }] }

// Custom parsing (arbitrary property names)
{
  data: [{ id: 'Sales', net: 100 }],
  options: { parsing: { xAxisKey: 'id', yAxisKey: 'net' } }
}
```

### Option Resolution

Options cascade through scopes (see [General Concepts](references/04-general-concepts.md) for full details):

1. **Chart level**: `options` → `overrides[type]` → `defaults`
2. **Dataset level**: `dataset` → `options.datasets[type]` → `defaults.datasets[type]` → `defaults`
3. **Element level**: `dataset` → `options.datasets[type].elements[elementType]` → `defaults.elements[elementType]` → `defaults`
4. **Scale options**: `options.scales` → `overrides[type].scales` → `defaults.scales`

### Scriptable Options

Options accept functions called for each data point:

```javascript
{
  backgroundColor: function(context) {
    const value = context.dataset.data[context.dataIndex];
    return value < 0 ? 'red' : (index % 2 ? 'blue' : 'green');
  }
}
```

The `context` provides: `chart`, `dataset`, `datasetIndex`, `dataIndex`, `parsed`, `raw`, `element`. A resolver is passed as the second argument.

### Indexable Options

Options accept arrays where each element corresponds to a data point:

```javascript
{
  backgroundColor: ['red', 'blue', 'green', 'yellow'],
  pointRadius: [5, 10, 15, 20]
}
```

### Axes and Scales

Chart.js v4+ uses a unified scale system. Built-in types: `'category'`, `'linear'`, `'logarithmic'`, `'time'`, `'timeseries'`, `'radialLinear'`.

```javascript
options: {
  scales: {
    x: { type: 'category', title: { display: true, text: 'Month' } },
    y: { type: 'linear', beginAtZero: true, title: { display: true, text: 'Sales ($)' } }
  }
}
```

### Events and Interactions

```javascript
{
  events: ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove'],
  onHover: (event, elements, chart) => {},
  onClick: (event, elements, chart) => {},
  interaction: {
    mode: 'nearest',        // 'point', 'nearest', 'index', 'dataset', 'x', 'y'
    intersect: true,
    axis: 'x',              // 'x', 'y', 'xy', 'r'
    includeInvisible: false
  }
}
```

**Converting events to data values:**
```javascript
import { getRelativePosition } from 'chart.js/helpers';
// const pos = getRelativePosition(event, chart);
// const dataX = chart.scales.x.getValueForPixel(pos.x);
```

### Plugin System

```javascript
const myPlugin = {
  id: 'myPlugin',
  beforeDraw: (chart) => {},
  afterDraw: (chart) => {},
  beforeDatasetsDraw: (chart) => {},
  afterDatasetsDraw: (chart) => {},
  beforeEvent: (chart, args) => {},
  afterEvent: (chart, args) => {},
  resize: (chart, size) => {},
  afterDestroy: (chart) => {}  // replaces 'destroy' in v4
};

Chart.register(myPlugin);
const chart = new Chart(ctx, { plugins: [myPlugin] });
```

### Global Defaults

```javascript
Chart.defaults.font.family = "'Helvetica Neue', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#666';
Chart.defaults.plugins.title.align = 'center';
```

## Installation

**Note:** Chart.js v4+ is an **ESM-only package**. Add `"type": "module"` to `package.json`.

### npm (Recommended)

```bash
npm install chart.js
```

```javascript
import { Chart } from 'chart.js';
// Tree-shake: import only what you need
import { Chart, LineController, LineElement, PointElement, CategoryScale, LinearScale } from 'chart.js';
Chart.register(LineController, LineElement, PointElement, CategoryScale, LinearScale);

// Or auto-register everything (no tree-shaking):
import Chart from 'chart.js/auto';
```

### CDN

```html
<!-- CDNJS -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.5.1/chart.umd.min.js"></script>
<!-- jsDelivr -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js"></script>
```

### ES Modules (Browser)

```html
<script type="module">
  import { Chart, ArcElement, CategoryScale, LineController, LinearScale, LineElement, PointElement } from 'https://cdn.jsdelivr.net/npm/chart.js@4.5.1/+esm';
  Chart.register(ArcElement, CategoryScale, LineController, LinearScale, LineElement, PointElement);
</script>
```

### CommonJS (Dynamic Import)

```javascript
const { Chart } = await import('chart.js');
```

### Framework Integrations

- **React**: `npm install react-chartjs-2 chart.js`
- **Vue**: `npm install vue-chartjs chart.js`
- **Svelte**: `npm install svelte-chartjs chart.js`
- **Angular**: `npm install ng2-charts chart.js`

### Helper Functions

```javascript
import { getRelativePosition, color as getColor, isNumber } from 'chart.js/helpers';
const pos = getRelativePosition(event, chart);
const lighterColor = getColor('rgb(75, 192, 192)').lighten(0.2);
```

## Usage Examples

### Basic Line Chart

```javascript
const ctx = document.getElementById('myChart').getContext('2d');
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
    datasets: [{
      label: 'My First Dataset',
      data: [65, 59, 80, 81, 56, 55, 40],
      fill: false,
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  },
  options: { responsive: true, plugins: { title: { display: true, text: 'Chart.js Line Chart' } } }
});
```

### Bar Chart with Multiple Datasets

```javascript
new Chart(document.getElementById('barChart'), {
  type: 'bar',
  data: {
    labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
    datasets: [{
      label: 'Dataset 1',
      data: [12, 19, 3, 5, 2, 3],
      backgroundColor: 'rgba(255, 99, 132, 0.5)'
    }, {
      label: 'Dataset 2',
      data: [15, 8, 12, 7, 9, 11],
      backgroundColor: 'rgba(54, 162, 235, 0.5)'
    }]
  },
  options: { scales: { y: { beginAtZero: true } } }
});
```

### Doughnut/Pie Chart

```javascript
new Chart(document.getElementById('doughnutChart'), {
  type: 'doughnut',
  data: {
    labels: ['Red', 'Blue', 'Yellow'],
    datasets: [{
      label: 'My Dataset',
      data: [300, 50, 100],
      backgroundColor: ['rgba(255,99,132,0.8)', 'rgba(54,162,235,0.8)', 'rgba(255,206,86,0.8)'],
      borderWidth: 1
    }]
  },
  options: { cutout: '50%', plugins: { legend: { position: 'bottom' } } }
});
```

### Mixed Chart Type

```javascript
new Chart(document.getElementById('mixedChart'), {
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
    datasets: [{
      type: 'bar', label: 'Revenue', data: [10, 20, 30, 45, 50]
    }, {
      type: 'line', label: 'Target', data: [15, 25, 35, 50, 60],
      borderColor: 'rgb(255, 99, 132)', tension: 0.3
    }]
  }
});
```

### Radar Chart

```javascript
new Chart(document.getElementById('radarChart'), {
  type: 'radar',
  data: {
    labels: ['Speed', 'Strength', 'Defense', 'Magic', 'Stamina'],
    datasets: [{
      label: 'Player 1', data: [85, 70, 90, 60, 75],
      backgroundColor: 'rgba(255, 99, 132, 0.2)', borderColor: 'rgb(255, 99, 132)'
    }, {
      label: 'Player 2', data: [70, 85, 60, 80, 70],
      backgroundColor: 'rgba(54, 162, 235, 0.2)', borderColor: 'rgb(54, 162, 235)'
    }]
  }
});
```

### Chart Update and API Usage

```javascript
const chart = new Chart(ctx, config);

// Update data and re-render
chart.data.datasets[0].data = [newData];
chart.update();          // animate changes
chart.update('none');    // no animation

// Show/hide datasets
chart.setDatasetVisibility(0, true);
chart.toggleDataVisibility(2);

// Get elements at event position
const points = chart.getElementsAtEventForMode(e, 'nearest', { intersect: true }, false);
```

### TypeScript Usage

```typescript
import { Chart, ChartConfiguration, ChartData, ChartOptions } from 'chart.js';

const config: ChartConfiguration = {
  type: 'line' as const,
  data: {
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [{ label: 'Sales', data: [12, 19, 3], borderColor: 'rgb(75, 192, 192)' }]
  },
  options: { responsive: true, scales: { y: { beginAtZero: true } } }
};

const myChart = new Chart(ctx, config);
```

## Advanced Topics

For detailed reference material, see the reference files:

- [**Chart Types**](references/01-chart-types.md) — Detailed configuration for all 8 chart types, filling modes, filler plugin, drawing order
- [**Axes and Scales**](references/02-axes-and-scales.md) — Cartesian, category, mathematical scales, axis labeling, styling, zoom control, positioning
- [**Configuration Deep Dive**](references/03-configuration.md) — Animations, elements, legend/title, tooltips, decimation, device pixel ratio, layout/padding
- [**General Concepts**](references/04-general-concepts.md) — Data structures, custom parsing, options resolution, scriptable/indexable options, colors, fonts, performance, responsive design
- [**API Reference**](references/05-api-reference.md) — Chart class, DatasetController, Scale, Element classes, Plugin interface, TypeScript types
- [**Migration Guide**](references/06-migration.md) — v4→v3 breaking changes, ESM migration, tree-shaking component list, v2→v3 reference

## References

- Official documentation: https://www.chartjs.org/docs/latest/
- GitHub repository: https://github.com/chartjs/Chart.js
- Ecosystem/plugins: https://github.com/chartjs/awesome
- Community: https://discord.gg/HxEguTK6av
- Stack Overflow: https://stackoverflow.com/questions/tagged/chart.js
- CDNJS: https://cdnjs.com/libraries/Chart.js
- jsDelivr: https://www.jsdelivr.com/package/npm/chart.js?path=dist
