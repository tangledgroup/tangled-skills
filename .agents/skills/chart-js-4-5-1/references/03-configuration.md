# Configuration Deep Dive Reference

## Animations

Chart.js animates charts out of the box. Animation configuration has 3 keys:

### Animation Configuration Structure

```javascript
{
  animation: {
    duration: 1000,           // ms per animation
    easing: 'easeOutQuart',   // easing function
    delay: 0,                 // ms before starting
    loop: false,              // repeat animation
    onProgress: null,         // callback during animation
    onComplete: null          // callback when done
  },
  animations: {
    numbers: {                // Animate numeric properties
      properties: ['x', 'y', 'borderWidth', 'radius', 'tension'],
      type: 'number'
    },
    colors: {                 // Animate color properties
      properties: ['color', 'borderColor', 'backgroundColor'],
      type: 'color'
    }
  },
  transitions: {
    active: { animation: { duration: 400 } },
    resize: { animation: { duration: 0 } },
    show: { /* appear from transparent */ },
    hide: { /* fade to transparent */ }
  }
}
```

### Easing Functions

Available easing functions (Robert Penner's equations):
- `'linear'`
- `'easeInQuad'`, `'easeOutQuad'`, `'easeInOutQuad'`
- `'easeInCubic'`, `'easeOutCubic'`, `'easeInOutCubic'`
- `'easeInQuart'`, `'easeOutQuart'`, `'easeInOutQuart'`
- `'easeInQuint'`, `'easeOutQuint'`, `'easeInOutQuint'`
- `'easeInSine'`, `'easeOutSine'`, `'easeInOutSine'`
- `'easeInExpo'`, `'easeOutExpo'`, `'easeInOutExpo'`
- `'easeInCirc'`, `'easeOutCirc'`, `'easeInOutCirc'`
- `'easeInElastic'`, `'easeOutElastic'`, `'easeInOutElastic'`
- `'easeInBack'`, `'easeOutBack'`, `'easeInOutBack'`
- `'easeInBounce'`, `'easeOutBounce'`, `'easeInOutBounce'`

### Transitions

Transitions define animation behavior for different update modes:

| Transition | Default Duration | Purpose |
|------------|-----------------|---------|
| `active` | 400ms | Hover state changes |
| `resize` | 0ms (none) | Window resize |
| `show` | — | Dataset visibility shown |
| `hide` | — | Dataset visibility hidden |
| `reset` | — | Reset to initial state |

### Custom Transitions

```javascript
{
  transitions: {
    show: {
      animations: {
        x: { from: 0 },
        y: { from: 0 }
      }
    },
    hide: {
      animations: {
        x: { to: 0 },
        y: { to: 0 }
      }
    }
  }
}
```

### Animation Callbacks

```javascript
{
  animation: {
    onProgress: function(animation) {
      // Called each frame of animation
      // animation.currentStep, animation.numSteps
      progressBar.value = animation.currentStep / animation.numSteps;
    },
    onComplete: function() {
      console.log('Animation complete!');
    }
  }
}
```

### Disabling Animations

```javascript
// Disable all animations
chart.options.animation = false;

// Disable specific property animations
chart.options.animations.colors = false;
chart.options.animations.x = false;

// Disable a transition by setting duration to 0
chart.options.transitions.active.animation.duration = 0;
```

## Elements Configuration

Elements are rendered shapes: points, lines, bars, arcs.

### Point Element Options

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `radius` | `number` | `3` | Point radius |
| `pointStyle` | `string\|Image\|HTMLCanvasElement` | `'circle'` | Point shape |
| `rotation` | `number` | `0` | Rotation in degrees |
| `backgroundColor` | `Color` | default | Fill color |
| `borderWidth` | `number` | `1` | Stroke width |
| `borderColor` | `Color` | default | Stroke color |
| `hitRadius` | `number` | `1` | Extra hit detection radius |
| `hoverRadius` | `number` | `4` | Radius when hovered |
| `hoverBorderWidth` | `number` | `1` | Border width when hovered |

### Line Element Options

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `tension` | `number` | `0` | Bézier curve tension (0 = straight) |
| `backgroundColor` | `Color` | default | Fill color |
| `borderWidth` | `number` | `3` | Stroke width |
| `borderColor` | `Color` | default | Stroke color |
| `borderCapStyle` | `string` | `'butt'` | Line cap: `'butt'`, `'round'`, `'square'` |
| `borderDash` | `number[]` | `[]` | Dash pattern |
| `borderDashOffset` | `number` | `0.0` | Dash offset |
| `borderJoinStyle` | `string` | `'miter'` | Join style: `'round'`, `'bevel'`, `'miter'` |
| `capBezierPoints` | `boolean` | `true` | Keep Bézier control points inside chart |
| `cubicInterpolationMode` | `string` | `'default'` | Interpolation: `'default'`, `'monotone'` |
| `fill` | `boolean\|string` | `false` | Fill area under line |
| `stepped` | `boolean\|string` | `false` | Show as stepped line |

### Bar Element Options

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `backgroundColor` | `Color` | default | Fill color |
| `borderWidth` | `number` | `0` | Stroke width |
| `borderColor` | `Color` | default | Stroke color |
| `borderSkipped` | `string` | `'start'` | Skipped border edge |
| `borderRadius` | `number\|object` | `0` | Corner radius |
| `inflateAmount` | `number\|'auto'` | `'auto'` | Inflate amount when drawing |

### Arc Element Options (Doughnut/Pie/Polar)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `backgroundColor` | `Color` | default | Fill color |
| `borderColor` | `Color` | `'#fff'` | Stroke color |
| `borderWidth` | `number` | `2` | Stroke width |
| `borderAlign` | `'center'\|'inner'` | `'center'` | Stroke alignment |
| `borderDash` | `number[]` | `[]` | Dash pattern |
| `borderDashOffset` | `number` | `0.0` | Dash offset |
| `borderJoinStyle` | `string` | — | Join style |
| `circular` | `boolean` | `true` | Curved arc vs flat arc |

### Setting Element Defaults

```javascript
// Global defaults for all charts
Chart.defaults.elements.point.radius = 5;
Chart.defaults.elements.line.tension = 0.4;
Chart.defaults.elements.bar.borderRadius = 4;
Chart.defaults.elements.arc.borderWidth = 3;
```

## Legend and Title

### Legend Configuration

```javascript
{
  plugins: {
    legend: {
      display: true,
      position: 'top',            // 'top', 'left', 'bottom', 'right'
      align: 'center',            // Alignment within the container
      fullSize: true,             // Expand legend width to chart width
      reverse: false,             // Reverse legend order
      rotate: 0,                  // Rotate items (in degrees)
      
      // Labels
      labels: {
        color: '#333',            // Label text color
        boxWidth: 40,             // Width of colored box
        boxHeight: 20,            // Height of colored box
        padding: 10,              // Padding around each item
        font: {
          size: 12,
          family: 'Helvetica',
          weight: 'normal'
        },
        usePointStyle: false,     // Use point style instead of rectangle
        pointStyle: 'circle',     // Point style for legend items
        
        // Callbacks
        generateLabels: function(chart) {
          // Return custom legend items
          return chart.data.datasets.map((dataset, i) => ({
            text: dataset.label,
            fillStyle: dataset.backgroundColor,
            strokeStyle: dataset.borderColor,
            lineWidth: 1,
            hidden: !chart.isDatasetVisible(i),
            index: i
          }));
        },
        onClick: function(e, legendItem, legend) {
          // Custom click handler
          chart.toggleDataVisibility(legendItem.index);
          chart.update();
        },
        onHover: function(e, legendItem, legend) {
          // Custom hover handler
        }
      }
    }
  }
}
```

### Title Configuration

```javascript
{
  plugins: {
    title: {
      display: true,
      text: 'Chart Title',
      color: '#000',
      font: {
        size: 16,
        weight: 'bold',
        family: 'Helvetica'
      },
      padding: {
        top: 10,
        bottom: 30
      },
      align: 'center'            // 'start', 'center', 'end'
    }
  }
}
```

## Tooltips

### Tooltip Configuration

```javascript
{
  plugins: {
    tooltip: {
      enabled: true,              // Enable mouse tooltips
      mode: 'nearest',            // Interaction mode: 'nearest', 'index', 'dataset', 'x', 'y'
      intersect: true,            // Require intersection for selection
      
      // Positioning
      position: 'average',        // 'average', 'nearest', 'next', 'axis', 'x', 'y'
      xAlign: 'center',           // Horizontal alignment on screen
      yAlign: 'center',           // Vertical alignment on screen
      
      // Styling
      backgroundColor: 'rgba(0,0,0,0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: 'rgba(255,255,255,0.1)',
      borderWidth: 1,
      cornerRadius: 6,
      padding: 12,
      
      // Fonts
      titleFont: { size: 13, weight: 'bold' },
      bodyFont: { size: 12 },
      footerFont: { size: 12 },
      
      // Callbacks for custom content
      callbacks: {
        title: function(tooltipItems) {
          return tooltipItems[0].label;
        },
        label: function(context) {
          return context.dataset.label + ': ' + context.parsed.y;
        },
        afterLabel: function(context) {
          return '(in thousands)';
        }
      },
      
      // External tooltip handler (for custom HTML tooltips)
      external: function(context) {
        const tooltipModel = context.tooltip;
        // Render custom tooltip element
      }
    }
  }
}
```

### Interaction Modes

| Mode | Behavior |
|------|----------|
| `'nearest'` | Returns the nearest item(s) to cursor |
| `'index'` | Returns all items at the same index |
| `'dataset'` | Returns all items in the same dataset |
| `'x'` | Returns all items with matching X value |
| `'y'` | Returns all items with matching Y value |

### Custom Tooltip Content

```javascript
{
  plugins: {
    tooltip: {
      callbacks: {
        // Format numbers with locale
        label: function(context) {
          return context.dataset.label + ': ' +
            new Intl.NumberFormat('en-US', {
              style: 'currency',
              currency: 'USD'
            }).format(context.parsed.y);
        },
        // Multi-line labels
        afterLabel: function(context) {
          const total = context.chart.data.datasets[context.datasetIndex].data.reduce((a, b) => a + b, 0);
          return `Total: ${total}`;
        }
      }
    }
  }
}
```

### Disabling Tooltips

```javascript
{
  plugins: {
    tooltip: { enabled: false }
  }
}
```

## Data Decimation

Reduce dataset size before rendering for performance with large datasets:

```javascript
{
  plugins: {
    decimation: {
      enabled: true,
      algorithm: 'min-max',     // 'lttb' or 'min-max'
      threshold: 500            // Only decimate when points > this value
    }
  }
}
```

### Decimation Algorithms

| Algorithm | Description | Best For |
|-----------|-------------|----------|
| `'lttb'` | Largest Triangle Three Buckets | Preserving visual shape |
| `'min-max'` | Keep min/max in each bucket | Preserving range |

## Canvas Background

```javascript
{
  options: {
    backgroundColor: 'rgba(0,0,0,0.05)',
    // or set on the canvas element directly
    // <canvas style="background-color: #f5f5f5;"></canvas>
  }
}
```

## Device Pixel Ratio

Force a specific device pixel ratio for higher resolution rendering (useful for printing or bitmap conversion):

```javascript
{
  options: {
    devicePixelRatio: 2  // Override window.devicePixelRatio
    // Default is window.devicePixelRatio (usually 1 on non-Retina, 2-3 on Retina)
  }
}
```

Setting `devicePixelRatio` to a value other than 1 scales the canvas resolution relative to container size. No visible difference on screen; the difference appears when zooming or printing.

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
    // Or shorthand:
    // padding: 10,           // All sides
    // padding: { top: 10, bottom: 10 }  // Top/bottom only
  }
}
```

Padding affects the chartArea where data is rendered. It does not affect the legend or title areas.

### Element Positioning

Scales can be positioned at different edges:

```javascript
{
  scales: {
    x: { position: 'bottom' },     // 'bottom', 'top'
    y: { position: 'left' }        // 'left', 'right'
  }
}
```

For polar/radar charts, the radial scale position:
```javascript
{
  scales: {
    r: {
      position: 'left'  // 'left', 'right'
    }
  }
}
```
