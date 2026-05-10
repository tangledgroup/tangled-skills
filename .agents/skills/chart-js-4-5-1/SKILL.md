---
name: chart-js-4-5-1
description: Complete toolkit for Chart.js 4.5.1, the most popular open-source JavaScript charting library using HTML5 Canvas rendering. Use when creating interactive charts (line, bar, pie, doughnut, radar, polar area, scatter, bubble, area), configuring axes and scales, customizing animations, tooltips, legends, elements, implementing responsive design, handling data structures, performance optimization, or building data visualizations with TypeScript support across all major JavaScript frameworks.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
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
  - https://discord.gg/HxEguTK6av
  - https://github.com/chartjs/awesome
  - https://stackoverflow.com/questions/tagged/chart.js
  - https://github.com/chartjs/Chart.js
---

# Chart.js 4.5.1

## Overview

Chart.js is the most popular open-source JavaScript charting library, with ~60,000 GitHub stars and ~2,400,000 weekly npm downloads. It renders charts on HTML5 `<canvas>` elements, making it performant for large datasets and complex visualizations. The library is MIT-licensed, tree-shakeable, includes built-in TypeScript typings, and comes with sound defaults that produce production-ready charts with minimal configuration.

Chart.js supports nine built-in chart types: line, bar, doughnut, pie, radar, polar area, bubble, scatter, and area (via the filler plugin). Multiple chart types can be combined into mixed charts by specifying `type` per dataset. The library is compatible with all major JavaScript frameworks through community-maintained wrappers: React (`react-chartjs-2`), Vue (`vue-chartjs`), Svelte (`svelte-chartjs`), and Angular (`ng2-charts`).

## When to Use

- Creating interactive charts from JavaScript data (line, bar, pie, doughnut, radar, polar area, scatter, bubble, area)
- Building responsive data visualizations that adapt to container size
- Configuring axes, scales, tooltips, legends, and animations for custom chart behavior
- Optimizing chart performance for large datasets using decimation, parsing control, and normalized data
- Integrating Chart.js with bundlers (Webpack, Rollup, Vite) or framework wrappers
- Customizing chart appearance through plugins, elements, colors, fonts, and scriptable options
- Building mixed charts that combine multiple chart types on the same canvas

## Core Concepts

**Canvas rendering** — Chart.js renders on HTML5 `<canvas>`, not SVG. This makes it fast for large datasets but means styling is done through configuration options, not CSS.

**Configuration-driven** — Charts are created by passing a configuration object with `type`, `data`, and `options`. Options cascade from global defaults (`Chart.defaults`) through chart-type overrides to per-chart settings.

**Data structures** — Dataset `data` can be arrays of numbers, tuples `[x, y]`, or objects with named properties. Labels are provided in `data.labels`. The internal format uses objects, and setting `parsing: false` skips parsing for performance when data is already in internal format.

**Plugins system** — Chart.js has a plugin architecture with built-in plugins (Legend, Tooltip, Title, SubTitle, Filler, Decimation) and supports custom plugins with lifecycle hooks (`beforeInit`, `beforeDraw`, `afterUpdate`, etc.). Plugins are registered globally via `Chart.register()` or passed inline per chart.

**Tree-shakeable** — When using bundlers, import only the controllers, elements, scales, and plugins you need to minimize bundle size. Use `'chart.js/auto'` for quick start with all features included.

## Installation / Setup

Install from npm:

```bash
npm install chart.js
```

Or use a CDN:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

With bundlers (Webpack, Rollup, Vite), import and register components:

```js
import { Chart, BarController, BarElement, CategoryScale, LinearScale } from 'chart.js';

Chart.register(BarController, BarElement, CategoryScale, LinearScale);
```

For quick start with all features:

```js
import Chart from 'chart.js/auto';
```

## Usage Examples

**Basic bar chart:**

```html
<div style="position: relative; height: 40vh; width: 80vw;">
  <canvas id="myChart"></canvas>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx = document.getElementById('myChart');
const chart = new Chart(ctx, {
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
    scales: {
      y: { beginAtZero: true }
    }
  }
});
</script>
```

**Line chart with multiple datasets:**

```js
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
    datasets: [
      {
        label: 'Dataset 1',
        data: [65, 59, 80, 81, 56, 55, 40],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      },
      {
        label: 'Dataset 2',
        data: [28, 48, 40, 19, 86, 27, 90],
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1
      }
    ]
  }
});
```

**Doughnut chart:**

```js
new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ['Red', 'Blue', 'Yellow'],
    datasets: [{
      data: [300, 50, 100],
      backgroundColor: ['rgb(255, 99, 132)', 'rgb(54, 162, 235)', 'rgb(255, 205, 86)'],
      hoverOffset: 4
    }]
  }
});
```

**Mixed chart (bar + line):**

```js
new Chart(ctx, {
  data: {
    labels: ['January', 'February', 'March', 'April'],
    datasets: [
      {
        type: 'bar',
        label: 'Bar Dataset',
        data: [10, 20, 30, 40]
      },
      {
        type: 'line',
        label: 'Line Dataset',
        data: [15, 25, 35, 45]
      }
    ]
  }
});
```

## Advanced Topics

**Chart Types**: Line, bar, doughnut, pie, radar, polar area, bubble, scatter, and area charts with dataset-specific options → [Chart Types](reference/01-chart-types.md)

**Configuration System**: Options resolution, global defaults, scriptable/indexable options, per-dataset overrides, and element-level configuration → [Configuration System](reference/02-configuration-system.md)

**Axes and Scales**: Cartesian axes (category, linear, logarithmic, time, time series), radial axes, tick configuration, grid lines, and scale customization → [Axes and Scales](reference/03-axes-and-scales.md)

**Plugins and Customization**: Built-in plugins (Legend, Tooltip, Title, SubTitle, Filler, Decimation), custom plugin lifecycle hooks, external tooltips, and HTML legends → [Plugins and Customization](reference/04-plugins-and-customization.md)

**Performance and Integration**: Data parsing control, decimation algorithms, normalized data, web worker rendering, bundler tree-shaking, framework integrations, and responsive design patterns → [Performance and Integration](reference/05-performance-and-integration.md)
