---
name: chart-js-4-5-1
description: Complete toolkit for Chart.js 4.5.1, the most popular open-source JavaScript charting library using HTML5 Canvas rendering. Use when creating interactive charts (line, bar, pie, doughnut, radar, polar area, scatter, bubble, area), configuring axes and scales, customizing animations, tooltips, legends, elements, implementing responsive design, handling data structures, performance optimization, or building data visualizations with TypeScript support across all major JavaScript frameworks.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.2.0"
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

Chart.js is the most popular JavaScript charting library (~60,000 GitHub stars, ~2.4M weekly npm downloads). It renders charts on HTML5 Canvas for high performance with large datasets. Built-in TypeScript support, tree-shaking, and framework-agnostic design.

## When to Use

- Creating interactive charts (line, bar, pie, doughnut, radar, polar area, scatter, bubble, area)
- Configuring axes, scales, tooltips, legends, and animations
- Building responsive data visualizations for web applications
- Implementing custom chart types, plugins, or axis types
- Optimizing bundle size with tree-shaking
- Working with TypeScript-typed chart configurations

## Quick Start

Create a minimal chart:

```html
<div style="width: 600px;">
  <canvas id="myChart"></canvas>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
  const ctx = document.getElementById('myChart');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
      datasets: [{
        label: '# of Votes',
        data: [12, 19, 3, 5, 2, 3],
        borderWidth: 1
      }]
    },
    options: {
      scales: { y: { beginAtZero: true } }
    }
  });
</script>
```

## Installation

**npm:** `npm install chart.js`

**CDN (jsDelivr):** `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`

**CDN (CDNJS):** `<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.5.1/chart.umd.min.js"></script>`

## Core Concepts

### Chart Configuration Structure

```javascript
const config = {
  type: 'line',       // chart type
  data: {},           // data object (labels + datasets)
  options: {},        // chart options
  plugins: []         // inline plugins for this chart
};
```

### Data Structure

Data consists of `labels` (index axis labels) and `datasets` array. Each dataset has a `label`, `data`, and styling options:

```javascript
data: {
  labels: ['Jan', 'Feb', 'Mar'],
  datasets: [{
    label: 'Sales',
    data: [10, 20, 15],       // primitive array
    backgroundColor: 'rgba(255,99,132,0.5)'
  }]
}
```

Data formats:
- `number[]` — values paired with `labels` at same index
- `{x, y}[]` — explicit coordinate pairs (scatter, line)
- `[{x, y, r}]` — bubble data (r = radius)
- `[[x, y], ...]` — tuple arrays
- `{ key: value }` — object with property names as index

For object data with custom keys, use `parsing`:
```javascript
data: myArray,
parsing: { xAxisKey: 'name', yAxisKey: 'value' }
```

### Scriptable and Indexable Options

Options can be functions (scriptable) or arrays (indexable):

```javascript
backgroundColor: function(context) {
  return context.dataset.data[context.dataIndex] > 0 ? 'green' : 'red';
},
borderColor: ['red', 'blue', 'green']  // per-data-point
```

### Global Configuration

Set defaults globally via `Chart.defaults`:
```javascript
Chart.defaults.interaction.mode = 'nearest';
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0,0,0,0.9)';
```

## Chart Types Overview

| Type | Description | Required Components |
|------|-------------|---------------------|
| `line` | Line plots, trends | LineController, PointElement, LineElement, CategoryScale, LinearScale |
| `bar` | Vertical bars | BarController, BarElement, CategoryScale, LinearScale |
| `horizontalBar` | Horizontal bars (bar + indexAxis: 'y') | Same as bar |
| `bubble` | 3D dots (x, y, r) | BubbleController, PointElement, LinearScale (x/y) |
| `doughnut` | Ring charts | DoughnutController, ArcElement |
| `pie` | Circle charts (cutout: 0) | PieController, ArcElement |
| `polarArea` | Radial segments | PolarAreaController, ArcElement, RadialLinearScale |
| `radar` | Polygon comparisons | RadarController, PointElement, LineElement, RadialLinearScale |
| `scatter` | XY point clouds | ScatterController, PointElement, LinearScale (x/y) |

## Built-in Plugins

Chart.js ships with these plugins:
- **Legend** — dataset visibility toggle
- **Title** — chart title text
- **Tooltip** — hover data display
- **Filler** — area fill under lines (for area charts)
- **Decimation** — data sampling for large datasets
- **Canvas Background** — custom canvas backgrounds

## Tree-Shaking (Bundle Optimization)

Import only what you need:

```javascript
import { Chart, BarController, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
Chart.register(BarController, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);
```

Or use `chart.js/auto` for all features (no tree-shaking):
```javascript
import Chart from 'chart.js/auto';
```

## Advanced Topics

- [Reference: Getting Started](references/01-getting-started.md) — installation, step-by-step guide, integration
- [Reference: Data Structures & Options](references/02-data-structures.md) — data formats, options resolution, scriptable/indexable
- [Reference: Configuration](references/03-configuration.md) — animations, tooltips, legend, title, interactions, responsive
- [Reference: Chart Types](references/04-chart-types.md) — detailed chart type properties
- [Reference: Axes & Scales](references/05-axes-scales.md) — cartesian, radial, scale configuration
- [Reference: Elements](references/06-elements.md) — point, line, bar, arc element styling
- [Reference: Plugins & Development](references/07-plugins-development.md) — custom plugins, API, extending
- [Reference: Migration](references/08-migration.md) — v3 and v4 migration guides

## References

- Official documentation: https://www.chartjs.org/docs/latest/
- GitHub repository: https://github.com/chartjs/Chart.js
- Ecosystem (plugins, integrations): https://github.com/chartjs/awesome
- Discord: https://discord.gg/HxEguTK6av
- Stack Overflow: https://stackoverflow.com/questions/tagged/chart.js
