# Getting Started

## Installation

### npm
```bash
npm install chart.js
```

### CDN
**jsDelivr:** `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`
**CDNJS:** `<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.5.1/chart.umd.min.js"></script>`

### GitHub
Download from https://github.com/chartjs/Chart.js/releases/latest. Note: you must build Chart.js from source — prebuilt releases are no longer provided.

## Integration

### Script Tag
```html
<script src="path/to/chartjs/dist/chart.umd.min.js"></script>
<script>
  const myChart = new Chart(ctx, {...});
</script>
```

### Bundlers (Webpack, Rollup, Vite)
```javascript
// Quick start — all features (no tree-shaking)
import Chart from 'chart.js/auto';

// Bundle optimized — import only what you need
import { Chart, BarController, CategoryScale, LinearScale, BarElement } from 'chart.js';
Chart.register(BarController, CategoryScale, LinearScale, BarElement);
```

### CommonJS
```javascript
const { Chart } = await import('chart.js');
```

### RequireJS
Use UMD builds only:
```javascript
require(['path/to/chart.js/dist/chart.umd.min.js'], function(Chart){
  const myChart = new Chart(ctx, {...});
});
```

## Tree-Shaking Component Reference

| Chart Type | Required Controllers | Required Elements | Required Scales |
|------------|---------------------|-------------------|-----------------|
| Bar | `BarController` | `BarElement` | `CategoryScale`, `LinearScale` |
| Bubble | `BubbleController` | `PointElement` | `LinearScale` (x/y) |
| Doughnut/Pie | `DoughnutController` / `PieController` | `ArcElement` | None |
| Line | `LineController` | `LineElement`, `PointElement` | `CategoryScale`, `LinearScale` |
| Polar Area | `PolarAreaController` | `ArcElement` | `RadialLinearScale` (r) |
| Radar | `RadarController` | `LineElement`, `PointElement` | `RadialLinearScale` (r) |
| Scatter | `ScatterController` | `PointElement` | `LinearScale` (x/y) |

### Available Plugins for Tree-Shaking
- `Decimation` — data decimation
- `Filler` — line area fill
- `Legend` — legend display
- `SubTitle` — subtitle support
- `Title` — title display
- `Tooltip` — tooltip display

### Available Scales for Tree-Shaking
**Cartesian:** `CategoryScale`, `LinearScale`, `LogarithmicScale`, `TimeScale`, `TimeSeriesScale`
**Radial:** `RadialLinearScale`

### Helper Functions
Import separately from helpers package:
```javascript
import { getRelativePosition } from 'chart.js/helpers';

const canvasPosition = getRelativePosition(event, chart);
const dataX = chart.scales.x.getValueForPixel(canvasPosition.x);
```

## Step-by-Step Example

```javascript
import Chart from 'chart.js/auto';

const ctx = document.getElementById('myChart');
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
    datasets: [{
      label: 'Acquisitions by year',
      data: [10, 20, 15, 25, 22, 30, 28],
      backgroundColor: 'rgba(54, 162, 235, 0.5)',
      borderColor: 'rgb(54, 162, 235)',
      borderWidth: 1
    }]
  },
  options: {
    responsive: true,
    animation: false,
    plugins: {
      legend: { display: true },
      tooltip: { enabled: true }
    },
    scales: {
      y: { beginAtZero: true }
    }
  }
});
```

## Framework Integrations

Chart.js works with all major frameworks via community wrappers:
- **React:** react-chartjs-2 (https://github.com/reactchartjs/react-chartjs-2)
- **Vue:** vue-chartjs (https://github.com/apertureless/vue-chartjs/)
- **Svelte:** svelte-chartjs (https://github.com/SauravKanchan/svelte-chartjs)
- **Angular:** ng2-charts (https://github.com/valor-software/ng2-charts)
