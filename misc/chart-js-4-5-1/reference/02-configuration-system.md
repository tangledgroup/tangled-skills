# Configuration System

## Configuration Object Structure

Every chart is created with a configuration object:

```js
const config = {
  type: 'line',           // Chart type (can be overridden per dataset for mixed charts)
  data: {                 // Data structures
    labels: ['Jan', 'Feb'],
    datasets: [{
      label: 'Dataset 1',
      data: [10, 20]
    }]
  },
  options: {              // Chart options (scales, plugins, interactions, etc.)
    responsive: true,
    scales: { ... },
    plugins: { ... }
  },
  plugins: [              // Inline plugins (alternative to global registration)
    /* plugin objects */
  ]
};

const chart = new Chart(ctx, config);
```

## Global Configuration

Chart.js merges options from multiple levels. Global defaults are set on `Chart.defaults`:

```js
// Set interaction mode globally for all charts
Chart.defaults.interaction.mode = 'nearest';

// Set default colors
Chart.defaults.backgroundColor = '#9BD0F5';
Chart.defaults.borderColor = '#36A2EB';
Chart.defaults.color = '#000';

// Set default fonts
Chart.defaults.font = {
  family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
  size: 14,
  style: 'normal',
  weight: undefined
};

// Dataset-level defaults
Chart.defaults.datasets.line.showLine = false;

// Per-chart-type overrides
Chart.overrides.line.plugins.legend.display = false;
```

## Options Resolution

Options resolve from top to bottom using context-dependent routes. The resolution order for chart-level options:

1. `options` (passed to this chart)
2. `overrides[config.type]` (chart-type-specific defaults)
3. `defaults` (global defaults)

For dataset-level options, the resolution includes:

1. `dataset` object properties
2. `options.datasets[dataset.type]`
3. `overrides[config.type].datasets[dataset.type]`
4. `defaults.datasets[dataset.type]`
5. `defaults`

For element-level options (e.g., point radius), lookup uses the element type prefix first (`pointRadius`), then falls back to unprefixed (`radius`).

## Scriptable Options

Many options accept functions that are called for each data value, receiving a `context` argument:

```js
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['A', 'B', 'C'],
    datasets: [{
      data: [10, 20, 30],
      backgroundColor: (context) => {
        const value = context.dataset.data[context.dataIndex];
        return value > 25 ? 'rgb(75, 192, 192)' : 'rgb(255, 99, 132)';
      }
    }]
  }
});
```

The context object includes: `chart`, `dataIndex`, `datasetIndex`, `dataset`, `type`, `mode`, `active`, and scale-specific properties.

## Indexable Options

Options can also be arrays, where each element applies to the corresponding data point:

```js
datasets: [{
  data: [10, 20, 30],
  backgroundColor: ['red', 'green', 'blue']
}]
```

## Responsive Charts

Charts adapt to container size when `responsive: true` (the default):

```js
options: {
  responsive: true,
  maintainAspectRatio: true,   // Keep original width/height ratio
  aspectRatio: 2,              // Width / height ratio (ignored if height is explicitly set)
  onResize: (chart, size) => { /* custom resize logic */ },
  resizeDelay: 100             // Debounce resize updates (ms)
}
```

**Important:** For responsive charts, the canvas must be in a relatively positioned container:

```html
<div style="position: relative; height: 40vh; width: 80vw;">
  <canvas id="myChart"></canvas>
</div>
```

Do not set relative dimensions (`vw`, `vh`, `%`) directly on the `<canvas>` element — this produces invalid or blurry results. Set them on the container instead.

## Device Pixel Ratio

By default, Chart.js detects and uses the device pixel ratio for crisp rendering on high-DPI displays:

```js
options: {
  devicePixelRatio: 2  // Override auto-detection
}
```

## Interactions

Configure how the chart responds to user events:

```js
options: {
  interaction: {
    mode: 'nearest',     // 'nearest', 'index', 'point', 'dataset', 'x', 'y'
    intersect: true,      // Only trigger when mouse intersects an element
    axis: 'xy',          // Directions used for distance calculation
    includeInvisible: false  // Include points outside chart area
  },
  events: ['mousemove', 'mouseout', 'click', 'touchstart', 'touchmove'],
  onHover: (event, activeElements, chart) => { /* custom hover */ },
  onClick: (event, activeElements, chart) => { /* custom click */ }
}
```

Interaction modes:

- **`nearest`** — nearest data element under point
- **`index`** — all data items in the nearest index
- **`point`** — nearest point only
- **`dataset`** — all points in the nearest dataset
- **`x`** / **`y`** — items in the same x/y coordinate
- **`xy`** — items in the same x and y coordinates

## Layout

Control chart area layout with padding:

```js
options: {
  layout: {
    padding: {
      top: 10,
      right: 15,
      bottom: 10,
      left: 10
    }
  }
}
```

## Locale

Set the locale for number and date formatting:

```js
options: {
  locale: 'de-DE'
}
```

## Canvas Background

Set a background color behind the entire chart using the built-in canvas background plugin:

```js
options: {
  plugins: {
    canvasBackground: {
      color: 'rgb(240, 240, 240)'
    }
  }
}
```

## Elements Configuration

Style all instances of an element type globally:

```js
// Global point styling
Chart.defaults.elements.point.radius = 5;
Chart.defaults.elements.point.hitRadius = 10;

// Per-chart element styling
options: {
  elements: {
    point: {
      radius: 4,
      pointStyle: 'circle',   // 'circle', 'cross', 'crossRot', 'dash', 'line', 'rect', 'rectRounded', 'rectRot', 'star', 'triangle', false
      rotation: 0
    },
    line: {
      tension: 0.1,
      borderWidth: 2
    },
    bar: {
      borderWidth: 1,
      borderRadius: 4
    }
  }
}
```

## Title Configuration

```js
options: {
  plugins: {
    title: {
      display: true,
      text: 'My Chart Title',
      font: { size: 18, weight: 'bold' },
      color: '#333',
      padding: { top: 10, bottom: 10 },
      align: 'center'  // 'start', 'center', 'end'
    }
  }
}
```

## Subtitle Configuration

```js
options: {
  plugins: {
    subtitle: {
      display: true,
      text: 'Subtitle text',
      font: { size: 14 },
      color: '#666'
    }
  }
}
```
