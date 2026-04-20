# Axes and Scales Reference

## Scale Types

Chart.js provides several built-in scale types:

| Type | Description | Use Case |
|------|-------------|----------|
| `'category'` | Categorical (text labels) | Bar charts, time series with labels |
| `'linear'` | Linear numeric scale | Numeric data on any axis |
| `'logarithmic'` | Logarithmic scale | Data spanning multiple orders of magnitude |
| `'time'` | Time-based linear scale | Temporal data (requires date adapter) |
| `'timeseries'` | Time scale optimized for many points | High-frequency time series |
| `'radialLinear'` | Polar coordinate scale | Radar charts, polar area charts |

## Cartesian Scales (X and Y)

### Linear Scale Options

```javascript
scales: {
  y: {
    type: 'linear',
    // Position
    position: 'left',           // 'left', 'right', 'top', 'bottom'
    
    // Range
    min: 0,                     // Minimum value (overrides auto-calculation)
    max: 100,                   // Maximum value
    beginAtZero: true,          // Force axis to start at 0
    
    // Title
    title: {
      display: true,
      text: 'Sales ($)',
      color: '#000',
      font: { size: 14, weight: 'bold' },
      padding: { top: 10, bottom: 10 }
    },
    
    // Grid lines
    grid: {
      display: true,
      color: 'rgba(0, 0, 0, 0.1)',
      lineWidth: 1,
      drawOnChartArea: true,    // Draw grid in chart area
      drawTicks: true,          // Draw ticks on grid lines
      tickLength: 8,
      tickWidth: 1,
      tickColor: 'rgba(0,0,0,0.1)',
      border: {
        dash: [],
        dashOffset: 0,
        width: 1
      }
    },
    
    // Ticks
    ticks: {
      color: '#333',
      font: { size: 11, family: 'Helvetica' },
      padding: 5,
      maxTicksLimit: 10,
      maxRotation: 0,            // Prevent text rotation
      minRotation: 0,
      autoSkip: true,            // Auto-skip labels if crowded
      autoSkipPadding: 35,
      callback: function(value) {
        return '$' + value;      // Format tick labels
      }
    },
    
    // Border
    border: {
      display: true,
      color: 'rgba(0,0,0,0.1)',
      dash: [],
      dashOffset: 0,
      width: 1
    }
  }
}
```

### Category Scale Options

```javascript
scales: {
  x: {
    type: 'category',
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],  // Alternative data source
    
    // Position
    position: 'bottom',
    
    // Offset
    offset: false,           // Add space at edges
    // (when true, first and last ticks are at edges)
    
    // Ticks
    ticks: {
      maxRotation: 45,       // Allow rotated labels
      autoSkip: true,
      autoSkipPadding: 20
    }
  }
}
```

### Logarithmic Scale Options

```javascript
scales: {
  y: {
    type: 'logarithmic',
    min: 1,                  // Must be > 0 for log scale
    // min and max are used as the range boundaries
  }
}
```

### Time Scale Options

```javascript
scales: {
  x: {
    type: 'time',
    time: {
      unit: 'day',                    // 'millisecond', 'second', 'minute', 'hour', 'day', 'week', 'month', 'quarter', 'year'
      displayFormats: {
        day: 'MMM d',
        week: 'MMM d',
        month: 'MMM yyyy'
      },
      tooltipFormat: 'PPP',           // ISO date format for tooltips
      round: false,                   // Round to unit boundary
      step: 1,                        // Interval between ticks
      min: '2024-01-01',              // Minimum date
      max: '2024-12-31'               // Maximum date
    },
    adapters: {
      date: {
        locale: 'en'                  // Date adapter locale
      }
    }
  }
}
```

**Note:** Time scales require a date adapter (e.g., `chartjs-adapter-date-fns`, `chartjs-adapter-moment`, or `chartjs-adapter-luxon`).

## Radial Linear Scale (Polar/Radar)

```javascript
scales: {
  r: {
    type: 'radialLinear',
    position: 'left',
    
    // Ticks
    ticks: {
      color: '#333',
      backdropColor: 'transparent',
      backdropPadding: 2,
      callback: function(value) {
        return value + '%';
      }
    },
    
    // Grid
    grid: {
      color: 'rgba(0,0,0,0.1)'
    },
    
    // Angle lines
    angleLines: {
      display: true,
      color: 'rgba(0,0,0,0.1)',
      lineWidth: 1
    },
    
    // Point labels
    pointLabels: {
      display: true,
      color: '#333',
      font: { size: 12 },
      padding: 10
    }
  }
}
```

## Axis Labeling and Styling

### Tick Formatting

Use the `callback` function for custom tick labels:

```javascript
ticks: {
  // Currency format
  callback: (value) => '$' + value.toLocaleString(),
  
  // Percentage format
  callback: (value) => (value * 100).toFixed(1) + '%',
  
  // Scientific notation
  callback: (value) => value.toExponential(2),
  
  // Custom formatting with context
  callback: function(context) {
    const tick = context.tick;
    return tick.value % 1000 === 0 ? tick.value.toLocaleString() : '';
  }
}
```

### Tick Color Per Value

Scriptable tick options:

```javascript
ticks: {
  color: function(context) {
    return context.tick.value < 0 ? 'red' : 'blue';
  },
  font: function(context) {
    return { size: 14, weight: 'bold' };
  }
}
```

### Grid Line Styling

```javascript
grid: {
  // Conditional styling
  color: function(context) {
    return context.index === 0 ? 'black' : 'rgba(0,0,0,0.1)';
  },
  lineWidth: function(context) {
    return context.index === 0 ? 2 : 1;
  },
  // Draw only before ticks
  drawTicks: false,
  // Tick size
  tickLength: 5,
  // Tick color
  tickColor: 'rgba(0,0,0,0.1)'
}
```

## Controlling Axis Zoom

### Pan and Zoom (via Plugin)

Chart.js core does not include pan/zoom. Use community plugins:
- `chartjs-plugin-zoom` — Mouse wheel zoom, click-drag pan
- `chartjs-plugin-pannable` — Touch/mouse panning

```bash
npm install chartjs-plugin-zoom hammerjs
```

```javascript
import { ZoomPlugin } from 'chartjs-plugin-zoom';
import Hammer from 'hammerjs';

new Chart(ctx, {
  plugins: [ZoomPlugin],
  options: {
    plugins: {
      zoom: {
        pan: {
          enabled: true,
          mode: 'x'       // 'x', 'y', or 'xy'
        },
        zoom: {
          enabled: true,
          mode: 'x',      // Zoom direction
          speed: 0.05     // Zoom speed factor
        }
      }
    }
  }
});
```

### Programmatic Axis Range Control

```javascript
// Set axis range programmatically
chart.scales.y.setMinValue(0);
chart.scales.y.setMaxValue(200);
chart.update();

// Or update via config and re-render
chart.options.scales.y.min = 0;
chart.options.scales.y.max = 200;
chart.update();
```

### Clip Configuration

Control how datasets clip relative to chart area:

```javascript
datasets: [{
  clip: {
    left: 5,    // Allow 5px overflow to the left
    right: -10, // Clip 10px inside on the right
    top: false, // No clipping on top (default)
    bottom: 0   // Clip at chart area boundary
  }
}]
```

## Scale Options Resolution

Scale options follow this resolution order:
1. `options.scales[scaleId]`
2. `overrides[config.type].scales[scaleId]`
3. `defaults.scales[scaleId]`
4. `defaults.scale` (fallback for all scales)

```javascript
// Global fallback for all unnamed scales
Chart.defaults.scale.display = true;

// Per-type scale override
Chart.defaults.line.scales.y.min = 0;
```

## Multiple Axes

```javascript
{
  options: {
    scales: {
      x: {
        position: 'bottom'
      },
      y: {
        position: 'left',
        title: { display: true, text: 'Revenue ($)' }
      },
      y1: {
        position: 'right',
        title: { display: true, text: 'Units Sold' },
        grid: { drawOnChartArea: false }  // Avoid overlapping grid lines
      }
    }
  },
  data: {
    datasets: [
      { yAxisID: 'y', data: [100, 200, 300] },   // Uses left axis
      { yAxisID: 'y1', data: [10, 20, 30] }       // Uses right axis
    ]
  }
}
```

## Axis Positioning

### Cartesian Axes

```javascript
{
  scales: {
    x: { position: 'bottom' },   // 'bottom', 'top'
    y: { position: 'left' }      // 'left', 'right'
  }
}
```

### Radial Scale Positioning

```javascript
{
  scales: {
    r: {
      position: 'left'  // 'left', 'right' (for radar/polar charts)
    }
  }
}
```

## Layout and Padding

### Chart Area Padding

```javascript
{
  options: {
    padding: {
      top: 10,
      right: 20,
      bottom: 10,
      left: 30
    }
    // Shorthand:
    // padding: 10           // All sides equal
    // padding: { top: 10 }  // Top only
  }
}
```

Padding affects the chartArea (where data is rendered) but not legend/title areas.
