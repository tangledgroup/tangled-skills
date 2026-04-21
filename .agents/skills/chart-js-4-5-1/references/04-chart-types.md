# Chart Types

## Line Chart

Plots data points connected by lines. Often used for trend data or comparing datasets.

### Required Components
`LineController`, `PointElement`, `LineElement`, `CategoryScale`, `LinearScale`

### Dataset Properties
| Name | Type | Scriptable | Indexable | Default |
|------|------|:----------:|:---------:|---------|
| `backgroundColor` | Color | Yes | - | `'rgba(0,0,0,0.1)'` |
| `borderColor` | Color | Yes | - | `'rgba(0,0,0,0.1)'` |
| `borderWidth` | number | Yes | - | `3` |
| `borderCapStyle` | string | Yes | - | `'butt'` |
| `borderDash` | number[] | Yes | - | `[]` |
| `borderDashOffset` | number | Yes | - | `0` |
| `borderJoinStyle` | string | Yes | - | `'miter'` |
| `tension` | number | Yes | - | `0` |
| `pointRadius` | number | Yes | Yes | `3` |
| `pointStyle` | string | Yes | Yes | `'circle'` |
| `pointBackgroundColor` | Color | Yes | Yes | `'rgba(0,0,0,0.1)'` |
| `pointBorderColor` | Color | Yes | Yes | `'rgba(0,0,0,0.1)'` |
| `pointHoverRadius` | number | Yes | Yes | `4` |
| `fill` | boolean/string | Yes | - | `false` |
| `showLine` | boolean | - | - | `true` |
| `stepped` | boolean/string | - | - | `false` |
| `spanGaps` | boolean/number | - | - | — |
| `cubicInterpolationMode` | string | Yes | - | `'default'` |
| `xAxisID` | string | - | - | first x axis |
| `yAxisID` | string | - | - | first y axis |

### cubicInterpolationMode
- `'default'` — monotonic cubic interpolation
- `'monotone'` — same as default
- `'straight'` — straight lines (no curves)

### Stepped Lines
```javascript
stepped: true,           // stepped-before
stepped: 'before',       // step before point
stepped: 'after',        // step after point
stepped: 'middle',       // step in middle
stepped: false           // smooth line (default)
```

### Fill Modes
```javascript
fill: true,              // fill to axis
fill: '-1',              // fill to previous dataset
fill: '^index',          // fill to Nth dataset up
fill: 'origin',          // fill to origin
fill: 'start',           // fill to start
fill: 'end',             // fill to end
```

### Segment Styling
```javascript
segments: {
  0: { borderColor: 'red' },        // first segment
  1: { backgroundColor: 'blue' },   // second segment
  from: 3, to: 5, props: { ... }   // range of segments
}
```

## Bar Chart

Data values as vertical bars. Shows trend data or compares multiple datasets side by side.

### Required Components
`BarController`, `BarElement`, `CategoryScale`, `LinearScale`

### Dataset Properties
| Name | Type | Scriptable | Indexable | Default |
|------|------|:----------:|:---------:|---------|
| `backgroundColor` | Color | Yes | Yes | `'rgba(0,0,0,0.1)'` |
| `borderColor` | Color | Yes | Yes | `'rgba(0,0,0,0.1)'` |
| `borderWidth` | number/object | Yes | Yes | `0` |
| `borderSkipped` | string/boolean | Yes | Yes | `'start'` |
| `borderRadius` | number/object | Yes | Yes | `0` |
| `base` | number | Yes | Yes | — |
| `barThickness` | number/string | - | - | auto |
| `maxBarThickness` | number | - | - | — |
| `barPercentage` | number | - | - | `0.9` |
| `categoryPercentage` | number | - | - | `0.8` |
| `inflateAmount` | number/'auto' | Yes | Yes | `'auto'` |
| `minBarLength` | number | - | - | — |
| `skipNull` | boolean | - | - | — |
| `grouped` | boolean | - | - | `true` |
| `pointStyle` | string | Yes | - | `'circle'` |

### borderSkipped
Values: `'start'`, `'end'`, `'middle'`, `'bottom'`, `'left'`, `'top'`, `'right'`, `false`

### Horizontal Bar
Set `indexAxis: 'y'` on the dataset or chart options.

## Bubble Chart

Three dimensions: x position, y position, and bubble radius (r).

### Required Components
`BubbleController`, `PointElement`, `LinearScale` (x/y)

### Data Format
```javascript
data: [{x: 20, y: 30, r: 15}, {x: 40, y: 10, r: 10}]
```

### Dataset Properties
| Name | Type | Scriptable | Indexable | Default |
|------|------|:----------:|:---------:|---------|
| `backgroundColor` | Color | Yes | Yes | `'rgba(0,0,0,0.1)'` |
| `borderColor` | Color | Yes | Yes | `'rgba(0,0,0,0.1)'` |
| `borderWidth` | number | Yes | Yes | `3` |
| `radius` | number | Yes | Yes | `3` |
| `hoverRadius` | number | Yes | Yes | `4` |
| `hitRadius` | number | Yes | Yes | `1` |
| `pointStyle` | string | Yes | Yes | `'circle'` |
| `rotation` | number | Yes | Yes | `0` |

## Doughnut & Pie Charts

Pie charts show proportions. Doughnut charts are the same with a cutout in the center. Default `cutout: 0` for pie, `'50%'` for doughnut.

### Required Components
`DoughnutController` / `PieController`, `ArcElement` (no scales)

### Data Format
```javascript
data: {
  labels: ['Red', 'Blue', 'Yellow'],
  datasets: [{ data: [300, 50, 100] }]
}
```

### Dataset Properties
| Name | Type | Scriptable | Indexable | Default |
|------|------|:----------:|:---------:|---------|
| `backgroundColor` | Color | Yes | Yes | `'rgba(0,0,0,0.1)'` |
| `borderColor` | Color | Yes | Yes | `'#fff'` |
| `borderWidth` | number | Yes | Yes | `1` |
| `borderAlign` | string | Yes | Yes | `'center'` |
| `hoverOffset` | number | - | - | `0` |
| `offset` | number | - | - | `0` |
| `spacing` | number | - | - | `0` |

### Doughnut-specific Options
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `cutout` | number/string | `'50%'` | Inner cutout (pixels or percentage) |
| `offset` | number | — | Offset all arcs equally |
| `spacing` | number | — | Gap between arcs |

## Polar Area Chart

Like pie charts but each segment has equal angle; radius varies by value.

### Required Components
`PolarAreaController`, `ArcElement`, `RadialLinearScale` (r)

### Data Format
```javascript
data: {
  labels: ['Red', 'Green', 'Yellow'],
  datasets: [{ data: [11, 16, 7] }]
}
```

### Dataset Properties
Same as doughnut plus:
| Name | Type | Scriptable | Indexable | Default |
|------|------|:----------:|:---------:|---------|
| `circular` | boolean | Yes | Yes | `true` |
| `spacing` | number | - | - | `0` |
| `spacingMode` | string | - | - | `'proportional'` (`'angular'`, `'proportional'`, `'parallel'`) |

## Radar Chart

Shows multiple data points and variation between them. Good for comparing 2+ datasets.

### Required Components
`RadarController`, `LineElement`, `PointElement`, `RadialLinearScale` (r)

### Data Format
```javascript
data: {
  labels: ['Eating', 'Drinking', 'Sleeping'],
  datasets: [
    { label: 'A', data: [65, 59, 90] },
    { label: 'B', data: [28, 48, 40] }
  ]
}
```

### Dataset Properties
Same as line chart. Key additions:
| Name | Type | Scriptable | Indexable | Default |
|------|------|:----------:|:---------:|---------|
| `fill` | boolean/string | Yes | - | `false` |
| `xAxisID` | string | - | - | first r axis |
| `yAxisID` | string | - | - | — |

## Scatter Chart

XY point clouds. Based on line chart but with linear x-axis.

### Required Components
`ScatterController`, `PointElement`, `LinearScale` (x/y)

### Data Format
```javascript
data: [{x: -10, y: 0}, {x: 0, y: 10}, {x: 10, y: 5}]
```

### Dataset Properties
Same as line chart. Default `showLine: false`.

## Area Charts

Area charts are line charts with `fill` enabled. Use the `Filler` plugin (included by default).

### Filling Modes
```javascript
fill: { target: 'origin' }    // fill to origin
fill: { target: '-1' }       // fill to previous dataset
fill: { target: chartArea }  // fill to chart area boundary
```

### Line Boundaries (Advanced)
Define boundaries for multi-line fills:
```javascript
data: [{
  data: [{y: 10, top: 20}, {y: 15, top: 25}],
  fill: { target: 'top' }
}]
```

### Line Datasets (Advanced)
Multiple datasets with different boundary references:
```javascript
datasets: [
  { data: [...], fill: '-1' },   // fills to previous
  { data: [...], fill: '^1' },   // fills upward N
]
```

### Line Drawtime (Advanced)
Control which animation frame the line draws on:
```javascript
data: [{ drawTime: 'beforeDraw', data: [...] }]
```

## Mixed Charts

Combine multiple chart types in one chart. Specify `type` per dataset.

```javascript
const config = {
  type: 'line',                              // default type
  data: {
    datasets: [
      { type: 'bar', label: 'Bar', data: [1,2,3] },
      { type: 'line', label: 'Line', data: [3,2,1] }
    ]
  }
};
```

### Drawing Order
Control with `order` property on datasets:
```javascript
datasets: [
  { order: 1, ... },   // drawn first
  { order: 2, ... },   // drawn second
]
```

## Combo Bar-Line Chart

Combine bar and line on same chart:
```javascript
const config = {
  type: 'bar',
  data: {
    datasets: [
      { type: 'bar', label: 'Revenue', data: [...] },
      { type: 'line', label: 'Growth', data: [...] }
    ]
  },
  options: {
    scales: {
      y: { position: 'left' },
      y1: { position: 'right', grid: { drawOnChartArea: false } }
    }
  }
};
```
