# Axes and Scales

## Overview

Axes map data values to pixel positions on the chart. Chart.js supports two axis categories:

- **Cartesian axes** — x and y axes for 2D charts (line, bar, scatter, bubble)
- **Radial axes** — single angular/radial axis for radar and polar area charts

Default scale IDs: `x` and `y` for cartesian charts, `r` for radial charts.

Each dataset maps to scales via `xAxisID`, `yAxisID`, or `rAxisID`. If not specified, the first scale of that axis is used. If no scale exists, a new one is auto-created.

## Defining Scales

```js
options: {
  scales: {
    x: {
      type: 'category',
      title: {
        display: true,
        text: 'Month'
      }
    },
    y: {
      type: 'linear',
      beginAtZero: true,
      title: {
        display: true,
        text: 'Value'
      }
    },
    // Custom-named scale for a second axis
    y2: {
      type: 'logarithmic',
      position: 'right'
    }
  }
}
```

Map a dataset to the custom scale:

```js
datasets: [{
  yAxisID: 'y2',
  data: [100, 1000, 10000]
}]
```

## Common Axis Options

All axes support these options (`options.scales[scaleId]`):

- **`type`** — Scale type string (e.g., `'category'`, `'linear'`, `'time'`)
- **`display`** — `true`, `false`, or `'auto'` (visible only if at least one dataset uses it)
- **`position`** — `'left'`, `'right'`, `'top'`, `'bottom'`
- **`min`** / **`max`** — Override data-derived range
- **`suggestedMin`** / **`suggestedMax`** — Adjust range without overriding data extremes
- **`reverse`** — Reverse the scale direction
- **`stacked`** — Stack data values (`true`, `false`, `'sign'`)
- **`grid`** — Grid line configuration
- **`ticks`** — Tick configuration
- **`title`** — Scale title configuration
- **`border`** — Border configuration
- **`weight`** — Sort order (higher weights are further from chart area)
- **`alignToPixels`** — Align pixel values to device pixels

## Grid Line Configuration

Namespace: `options.scales[scaleId].grid`

```js
grid: {
  display: true,
  color: 'rgba(0, 0, 0, 0.1)',
  borderColor: 'rgba(0, 0, 0, 0.1)',
  borderWidth: 1,
  drawOnChartArea: true,
  drawTicks: true,
  tickColor: 'rgba(0, 0, 0, 0.1)',
  tickLength: 6,
  tickWidth: 1,
  offset: false
}
```

## Tick Configuration

Namespace: `options.scales[scaleId].ticks`

```js
ticks: {
  display: true,
  color: '#666',
  font: { size: 12 },
  padding: 5,
  maxRotation: 50,
  minRotation: 0,
  autoSkip: true,           // Auto-skip overlapping labels
  autoSkipPadding: 3,
  maxTicksLimit: 11,        // Maximum number of ticks
  maxTicksLimit: 'auto',    // Auto-calculate based on scale size
  callback: (value, index, ticks) => value.toFixed(2),  // Custom formatting
  mirror: false,            // Place ticks inside the chart area
  crossAlign: 'near',       // 'near', 'center', 'far'
  showLabelBackdrop: false,
  backdropColor: 'rgba(255, 255, 255, 0.75)',
  backdropPadding: 2
}
```

## Scale Title Configuration

```js
title: {
  display: true,
  text: 'My Axis',
  color: '#333',
  font: { size: 14, weight: 'bold' },
  padding: { top: 4, bottom: 4 },
  align: 'end'  // 'start', 'center', 'end'
}
```

## Cartesian Scale Types

### Category Scale

Maps string labels to integer indices. Used by default on the index axis (x for vertical charts, y for horizontal).

```js
scales: {
  x: {
    type: 'category',
    labels: ['Jan', 'Feb', 'Mar']  // Can also use data.labels
  }
}
```

### Linear Scale

Maps numbers to pixel positions with even spacing. Used by default on the value axis.

```js
scales: {
  y: {
    type: 'linear',
    beginAtZero: true,
    min: 0,
    max: 100
  }
}
```

### Logarithmic Scale

Maps numbers using logarithmic spacing. Useful for data spanning several orders of magnitude.

```js
scales: {
  y: {
    type: 'logarithmic',
    beginAtZero: false  // log scale cannot start at zero
  }
}
```

### Time Scale

Displays dates and times. Data is spread according to actual time intervals. **Requires a date adapter** (e.g., `chartjs-adapter-date-fns`, `chartjs-adapter-luxon`, or `chartjs-adapter-moment`).

```js
import 'chartjs-adapter-date-fns';

scales: {
  x: {
    type: 'time',
    time: {
      unit: 'month',           // 'millisecond', 'second', 'minute', 'hour', 'day', 'week', 'month', 'quarter', 'year'
      displayFormats: {
        month: 'MMM yyyy'
      },
      tooltipFormat: 'PP'
    },
    bounds: 'data',            // 'data' or 'ticks'
    ticks: {
      source: 'auto',          // 'auto' or 'labels'
      autoSkip: true,
      maxTicksLimit: 12
    }
  }
}
```

Input formats: timestamps (ms since epoch), date strings parseable by the adapter, or Date objects. Use timestamps with `parsing: false` for best performance.

### Time Series Scale

Same as time scale but data is not automatically sorted. Use when data order matters and should be preserved.

```js
scales: {
  x: { type: 'timeseries' }
}
```

## Radial Scale

Used by radar and polar area charts. Maps values along the radial direction.

```js
scales: {
  r: {
    type: 'radialLinear',
    beginAtZero: true,
    angleLines: {
      display: true,
      color: 'rgba(0, 0, 0, 0.1)'
    },
    pointLabels: {
      display: true,
      color: '#666',
      font: { size: 12 }
    },
    grid: {
      circular: true  // Use circular grid lines instead of polygonal
    }
  }
}
```

## Multiple Axes

Create multiple axes by defining additional scale entries and mapping datasets to them:

```js
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['A', 'B', 'C'],
    datasets: [
      {
        label: 'Dataset 1',
        data: [10, 20, 30],
        yAxisID: 'y1'
      },
      {
        label: 'Dataset 2',
        data: [100, 200, 300],
        yAxisID: 'y2'
      }
    ]
  },
  options: {
    scales: {
      y1: {
        type: 'linear',
        position: 'left',
        beginAtZero: true
      },
      y2: {
        type: 'logarithmic',
        position: 'right'
      }
    }
  }
});
```
