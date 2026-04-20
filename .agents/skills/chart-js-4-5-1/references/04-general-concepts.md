# General Concepts Reference

## Data Structures

### Supported Data Formats

Chart.js accepts data in multiple formats depending on chart type:

```javascript
// 1. Array of values (with labels array)
{
  labels: ['Jan', 'Feb', 'Mar'],
  datasets: [{
    data: [10, 20, 30]
  }]
}

// 2. Object with key-value pairs
{
  datasets: [{
    data: { 'Jan': 10, 'Feb': 20, 'Mar': 30 }
  }]
}

// 3. Scatter/Bubble format (array of objects)
{
  datasets: [{
    data: [
      { x: 1, y: 2 },
      { x: 3, y: 4 }
    ]
  }]
}

// 4. Internal format (skip parsing for performance)
{
  datasets: [{
    data: [0, 1, 2, 3, 4]  // Auto-indexed from 0
  }]
}

// 5. Mixed data types
{
  datasets: [{
    data: [10, null, 30, undefined, 50]  // null/undefined = skip
  }]
}
```

### Data Parsing

Chart.js automatically parses data based on the scale type:
- **Category scale**: values matched by label index
- **Linear/Logarithmic**: values parsed as numbers
- **Time scale**: values parsed as dates (requires adapter)
- **Internal format**: no parsing, data used directly (fastest)

To skip parsing entirely:
```javascript
{
  parsing: false,  // Disable all parsing
  data: [0, 1, 2, 3, 4]  // Must already be in internal format
}
```

#### Custom Parsing Configuration

When data uses non-standard property names, configure `parsing`:

```javascript
{
  // Each row has custom field names
  data: [
    { id: 'Sales', net: 100, cogs: 50 },
    { id: 'Purchases', net: 120, cogs: 55 }
  ],
  options: {
    parsing: {
      xAxisKey: 'id',     // Maps to x-axis
      yAxisKey: 'net'     // Maps to y-axis
    },
    datasets: [
      { label: 'Net sales', data: data, parsing: { yAxisKey: 'net' } },
      { label: 'COGS', data: data, parsing: { yAxisKey: 'cogs' } }
    ]
  }
}
```

For doughnut/pie/radar/polarArea charts, use `key` instead:
```javascript
{
  options: {
    parsing: { key: 'nested.value' }  // Reads data[0].nested.value = 1500
  }
}
```

Nested keys with dots must be escaped: `xAxisKey: 'data\\.key'`.

#### Data Normalization

For logarithmic scales, negative values are ignored. Use `isNumber()` helper for validation:
```javascript
import { isNumber } from 'chart.js/helpers';
if (isNumber(value)) { /* valid number */ }
```

### Fonts

Font configuration applies globally or per-element:

```javascript
// Global defaults
Chart.defaults.font.family = "'Helvetica Neue', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.font.weight = 'normal';
Chart.defaults.font.lineHeight = 1.2;

// Per-element
{
  plugins: {
    title: { font: { size: 16, weight: 'bold' } },
    legend: { labels: { font: { size: 11 } } },
    tooltip: {
      titleFont: { size: 13, weight: 'bold' },
      bodyFont: { size: 12 }
    }
  }
}
```

## Options Resolution (Detailed)

Options cascade through scopes. When a property is not found in one scope, it falls back to the next:

### Chart-Level Options Cascade
1. `config.options` (instance options)
2. `Chart.defaults.overrides[config.type]`
3. `Chart.defaults` (global defaults)

### Dataset-Level Options Cascade
1. `dataset.*` (per-dataset config)
2. `config.options.datasets[dataset.type]`
3. `config.options`
4. `Chart.defaults.overrides[config.type].datasets[dataset.type]`
5. `Chart.defaults.datasets[dataset.type]`
6. `Chart.defaults`

### Element-Level Options Cascade
1. `dataset.*`
2. `config.options.datasets[dataset.type].elements[elementType]`
3. `config.options.elements[elementType]`
4. `Chart.defaults.overrides[config.type].datasets[dataset.type].elements[elementType]`
5. `Chart.defaults.datasets[dataset.type].elements[elementType]`
6. `Chart.defaults.elements[elementType]`
7. `Chart.defaults`

### Scale Options Cascade
1. `config.options.scales[scaleId]`
2. `Chart.defaults.overrides[config.type].scales[scaleId]`
3. `Chart.defaults.scales[scaleId]`
4. `Chart.defaults.scale` (universal fallback)

## Scriptable Options

Scriptable options accept a function instead of a static value. The function is called for each data element:

```javascript
{
  backgroundColor: function(context) {
    // context.dataIndex: index within the dataset
    // context.datasetIndex: index of the dataset
    // context.dataset: the full dataset object
    // context.parsed: parsed data value {x, y, ...}
    // context.raw: raw data value
    // context.element: the rendered element
    
    const value = context.dataset.data[context.dataIndex];
    return value > 0 ? 'green' : 'red';
  }
}
```

### Resolving Other Scriptable Options

A resolver is passed as the second argument:
```javascript
{
  color: function(context, options) {
    // Resolve another scriptable option's value
    return Chart.helpers.color(options.backgroundColor()).lighten(0.2);
  }
}
```

### Validating Context

Always validate the context type:
```javascript
{
  backgroundColor: function(context) {
    if (context.type !== 'data') return;
    // Safe to use context.dataIndex, etc.
  }
}
```

## Indexable Options

Indexable options accept an array where each element applies to the corresponding data point:

```javascript
{
  backgroundColor: [
    'rgba(255, 99, 132, 0.5)',  // For data index 0
    'rgba(54, 162, 235, 0.5)',  // For data index 1
    'rgba(255, 206, 86, 0.5)'   // For data index 2
    // If fewer items than data points, the array loops
  ],
  pointRadius: [5, 10, 15, 20, 25]
}
```

**Note:** When both scriptable and indexable options are supported, prefer scriptable for dynamic values.

## Option Context Levels

The option context object has hierarchical levels:

### Chart Context
- `chart`: the Chart instance
- `type`: `'chart'`

### Dataset Context (extends chart)
- `dataset`: the dataset object
- `datasetIndex`: index of the dataset
- `mode`: update mode
- `active`: whether an element is active (hovered)
- `type`: `'dataset'`

### Data Context (extends dataset)
- `dataIndex`: index of the data point
- `parsed`: parsed values `{x, y, ...}`
- `raw`: raw data value
- `element`: the rendered element
- `active`: whether this element is active
- `type`: `'data'`

### Scale Context (extends chart)
- `scale`: the Scale instance
- `type`: `'scale'`

### Tick Context (extends scale)
- `tick`: the tick object
- `index`: tick index
- `type`: `'tick'`

## Colors and Styling

### Supported Color Formats

Chart.js accepts any CSS color format:
```javascript
// Named colors
backgroundColor: 'red'

// RGB/RGBA
backgroundColor: 'rgb(255, 99, 132)'
backgroundColor: 'rgba(255, 99, 132, 0.5)'

// Hex
backgroundColor: '#ff6384'
backgroundColor: '#f64'

// HSL/HSLA
backgroundColor: 'hsl(12, 100%, 60%)'
backgroundColor: 'hsla(12, 100%, 60%, 0.5)'

// CanvasGradient (for fills)
const gradient = ctx.createLinearGradient(0, 0, 0, 400);
gradient.addColorStop(0, 'rgba(75, 192, 192, 1)');
gradient.addColorStop(1, 'rgba(75, 192, 192, 0)');
backgroundColor: gradient;

// CanvasPattern
const pattern = ctx.createPattern(image, 'repeat');
backgroundColor: pattern;
```

### Color Manipulation Helper

Chart.js provides a color helper:
```javascript
import { color } from 'chart.js/helpers';

const baseColor = color('rgb(75, 192, 192)');
const lighter = baseColor.lighten(0.2);   // Lighter by 20%
const darker = baseColor.darken(0.3);     // Darker by 30%
const alpha = baseColor.alpha(0.5);       // Set alpha to 0.5
const rgbString = baseColor.rgbString();  // 'rgb(75, 192, 192)'
const hexString = baseColor.hexString();  // '#4bc0c0'
const hslString = baseColor.hslString();  // 'hsl(180, 50%, 52%)'
```

## Performance Optimization

### Parsing and Internal Format

Skip parsing for maximum performance:
```javascript
{
  parsing: false,
  data: [0, 1, 2, 3, 4]  // Already in internal numeric format
}
```

### Data Decimation

Reduce points before rendering:
```javascript
{
  plugins: {
    decimation: {
      enabled: true,
      algorithm: 'lttb',
      threshold: 1000  // Only when > 1000 points
    }
  }
}
```

### Tree Shaking (ESM Bundles)

Import only what you need:
```javascript
import {
  Chart,
  CategoryScale,
  LinearScale,
  LineController,
  LineElement,
  PointElement,
  Title,
  Legend
} from 'chart.js';

Chart.register(
  CategoryScale, LinearScale, LineController,
  LineElement, PointElement, Title, Legend
);
```

### Disabling Unnecessary Features

```javascript
{
  options: {
    animation: false,           // Disable animations
    responsive: false,          // Disable responsive resizing
    interaction: { mode: 'none' }, // Disable hover interactions
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false }
    }
  }
}
```

### Canvas Device Pixel Ratio

```javascript
{
  options: {
    responsive: true,
    maintainAspectRatio: true,  // Keep aspect ratio
    // Or set fixed size:
    // width: 400,
    // height: 200
  }
}
```

## Responsive Design

### Basic Responsive Chart

```javascript
new Chart(ctx, {
  options: {
    responsive: true,           // Enable responsiveness
    maintainAspectRatio: true,  // Preserve aspect ratio
    // Set explicit dimensions for better control:
    // width: undefined,       // Use container width
    // height: undefined,      // Use container height
  }
});
```

### Responsive with Fixed Aspect Ratio

```javascript
// Set canvas CSS
<canvas id="chart" style="width: 100%; max-height: 400px;"></canvas>

new Chart(ctx, {
  options: {
    responsive: true,
    maintainAspectRatio: false  // Allow height to vary
  }
});
```

### Resize Handling

Chart.js automatically handles window resize events. For custom resize behavior:
```javascript
{
  options: {
    onResize: function(chart, size) {
      // Called on every resize
      console.log(`Size: ${size.width}x${size.height}`);
    }
  }
}
```

### HiDPI / Retina Display

Chart.js automatically handles device pixel ratio. For manual control:
```javascript
// Set canvas width/height attributes (not CSS) for proper DPI
<canvas id="chart" width="800" height="400"></canvas>

new Chart(ctx, {
  options: {
    responsive: false,  // Use exact dimensions
    maintainAspectRatio: false
  }
});
```

## Fonts

Font configuration applies globally or per-element:

```javascript
// Global defaults
Chart.defaults.font.family = "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.font.weight = 'normal';

// Per-element
{
  plugins: {
    title: { font: { size: 16, weight: 'bold' } },
    legend: { labels: { font: { size: 11 } } },
    tooltip: {
      titleFont: { size: 13, weight: 'bold' },
      bodyFont: { size: 12 }
    }
  }
}
```
