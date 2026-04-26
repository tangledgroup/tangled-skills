# Performance and Integration

## Data Structures

Dataset `data` accepts multiple formats. Choose the right format for your use case:

### Primitive Array (numbers)

```js
{
  labels: ['A', 'B', 'C'],
  datasets: [{
    data: [10, 20, 30]
  }]
}
```

Labels array provides the index axis values. Most common for bar and line charts.

### Tuple Array `[x, y]`

```js
{
  datasets: [{
    data: [[0, 10], [1, 20], [2, 30]]
  }]
}
```

First element is the index, second is the value. Useful when labels are numeric.

### Object Array (internal format)

```js
{
  datasets: [{
    data: [{ x: 'A', y: 10 }, { x: 'B', y: 20 }, { x: 'C', y: 30 }]
  }]
}
```

This is the internal parsed format. When using this format, set `parsing: false` to skip parsing overhead. Data must be sorted.

### Object Array with Custom Properties

```js
{
  datasets: [{
    data: [
      { id: 'Sales', nested: { value: 1500 } },
      { id: 'Purchases', nested: { value: 500 } }
    ]
  }]
},
options: {
  parsing: {
    xAxisKey: 'id',
    yAxisKey: 'nested.value'
  }
}
```

For pie/doughnut/radar/polarArea, use `parsing.item` instead:

```js
{
  type: 'doughnut',
  data: {
    datasets: [{
      data: [
        { label: 'Sales', nested: { value: 1500 } },
        { label: 'Purchases', nested: { value: 500 } }
      ]
    }]
  },
  options: {
    parsing: { item: 'nested.value' }
  }
}
```

Use `null` for skipped values in any format. Keys with dots must be escaped: `'data\\.key'`.

## Parsing

By default, Chart.js parses data into internal format. Disable parsing when data is already prepared:

```js
options: {
  parsing: false  // Global
}
```

Or per-dataset:

```js
datasets: [{
  parsing: false,
  data: [{ x: 0, y: 10 }, { x: 1, y: 20 }]
}]
```

## Data Normalization

When providing sorted, unique-indexed data consistent across datasets, set `normalized: true` to skip normalization checks:

```js
datasets: [{
  normalized: true,
  data: [{ x: 0, y: 10 }, { x: 1, y: 20 }]
}]
```

## Data Decimation

The decimation plugin automatically samples large datasets for line charts. Reduces memory and improves rendering speed.

```js
import { Chart, Decimation } from 'chart.js';
Chart.register(Decimation);

options: {
  plugins: {
    decimation: {
      enabled: true,
      algorithm: 'lttb',   // 'lttb' or 'min-max'
      samples: undefined,  // Number of output samples (defaults to canvas width for lttb)
      threshold: undefined // Trigger decimation when data points exceed this (defaults to 4x canvas width)
    }
  }
}
```

Algorithms:

- **`lttb`** (Largest Triangle Three Buckets) — Significantly reduces points, best for showing trends
- **`min-max`** — Preserves peaks, may use up to 4 points per pixel, good for noisy signals

Requirements: dataset must have `indexAxis: 'x'`, must be a line type, x-axis must be `'linear'` or `'time'`.

Line charts also support automatic decimation during draw when certain conditions are met, but explicit decimation is more efficient.

## Tick Optimization

Reduce tick calculation overhead:

```js
ticks: {
  // Set fixed rotation to avoid auto-calculation
  minRotation: 45,
  maxRotation: 45,
  // Sample a subset of labels for sizing
  sampleSize: 5,
  // Limit maximum ticks
  maxTicksLimit: 10
}
```

## Specifying Min/Max

When you know the data range, specify it to avoid computation:

```js
scales: {
  x: {
    type: 'time',
    min: new Date('2019-01-01').valueOf(),
    max: new Date('2019-12-31').valueOf()
  },
  y: {
    type: 'linear',
    min: 0,
    max: 100
  }
}
```

## Disabling Animations

For best performance with large datasets, disable animations:

```js
options: {
  animation: false
}
```

This renders the chart once instead of multiple times during updates. Line charts use Path2D caching when animations are disabled.

## Web Worker Rendering

Offload Chart.js rendering to a web worker using OffscreenCanvas:

**Main thread:**

```js
const canvas = document.getElementById('myChart');
const offscreen = canvas.transferControlToOffscreen();
const worker = new Worker('worker.js');
worker.postMessage({ canvas: offscreen, config: chartConfig }, [offscreen]);
```

**Worker (worker.js):**

```js
importScripts('https://cdn.jsdelivr.net/npm/chart.js');

onmessage = function(event) {
  const { canvas, config } = event.data;
  const chart = new Chart(canvas, config);

  // Handle resize manually
  onmessage = function(resizeEvent) {
    if (resizeEvent.data.type === 'resize') {
      chart.resize(resizeEvent.data.width, resizeEvent.data.height);
    }
  };
};
```

Considerations:

- Transferring data between threads is expensive — generate config/data on the worker side when possible
- Use ArrayBuffers for fast data transfer
- Functions cannot be transferred between threads — strip them before transfer and re-add after
- DOM-dependent plugins (including mouse interactions) won't work in workers
- Chart resizing must be handled manually

## Bundler Integration

### Quick Start (all features)

```js
import Chart from 'chart.js/auto';
```

### Tree-Shaken (optimized bundle)

Import only what you need:

```js
import {
  Chart,
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

Chart.register(
  BarController,
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend
);
```

### Available Components

**Controllers:** BarController, BubbleController, DoughnutController, LineController, PieController, PolarAreaController, RadarController, ScatterController

**Elements:** ArcElement, BarElement, LineElement, PointElement

**Plugins:** Decimation, Filler, Legend, SubTitle, Title, Tooltip

**Scales:** CategoryScale, LinearScale, LogarithmicScale, TimeScale, TimeSeriesScale, RadialLinearScale

### Helper Functions

Import helpers separately:

```js
import { getHoverColor, getRtlAdapter, isNullOrUndef } from 'chart.js/helpers';
```

## Framework Integrations

Community-maintained wrappers provide native integration:

- **React**: `react-chartjs-2` (https://github.com/reactchartjs/react-chartjs-2)
- **Vue**: `vue-chartjs` (https://github.com/apertureless/vue-chartjs)
- **Svelte**: `svelte-chartjs` (https://github.com/SauravKanchan/svelte-chartjs)
- **Angular**: `ng2-charts` (https://github.com/valor-software/ng2-charts)

## Script Tag Integration

For simple HTML pages without bundlers:

```html
<div style="position: relative; height: 40vh; width: 80vw;">
  <canvas id="myChart"></canvas>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
const ctx = document.getElementById('myChart');
const chart = new Chart(ctx, {
  type: 'bar',
  data: { /* ... */ },
  options: { /* ... */ }
});
</script>
```

## Node.js Usage

Chart.js can render charts on the server side using a canvas backend like `node-canvas` or `canvas`:

```js
import { createCanvas, registerFont } from 'canvas';
import { Chart } from 'chart.js';

const canvas = createCanvas(400, 400);
const chart = new Chart(canvas.getContext('2d'), {
  type: 'bar',
  data: { /* ... */ },
  options: { /* ... */ }
});

// Export as buffer
const buffer = canvas.toBuffer('image/png');
```

## TypeScript Support

Chart.js includes built-in TypeScript typings. Use the `ChartConfiguration` interface for type-safe configuration:

```ts
import type { ChartConfiguration } from 'chart.js';

const config: ChartConfiguration<'bar'> = {
  type: 'bar',
  data: {
    labels: ['A', 'B', 'C'],
    datasets: [{
      label: 'Dataset',
      data: [10, 20, 30]
    }]
  },
  options: {
    scales: {
      y: { beginAtZero: true }
    }
  }
};
```

Type-safe chart type registration:

```ts
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

// Access typed chart instance
const chart = new Chart<'bar', { label: string; data: number[] }>('myChart', config);
```

## Migration Notes

### From v3 to v4

- Node.js ESM support improved
- Default `interaction.mode` changed from `'index'` to `'nearest'`
- Default `interaction.intersect` changed from `false` to `true`
- Scale `position` is now determined by the axis (`axis` property) rather than position string
- `scales[xAxisID]` and `scales[yAxisID]` replaced with `xAxisID`/`yAxisID` on datasets
- Plugin hooks receive an `args` object as second parameter
- Removed: `Chart.helpers` namespace (import helpers separately)

### From v2 to v3/v4

Major breaking changes include configuration restructuring, scale system overhaul, and removal of legacy APIs. See the official migration guides for detailed steps.
