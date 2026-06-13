# Chart Types

## Line Chart

Plots data points connected by lines. Used for trend data and comparing datasets.

```js
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
    datasets: [{
      label: 'My Dataset',
      data: [65, 59, 80, 81, 56, 55, 40],
      fill: false,
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.1
    }]
  }
});
```

Key dataset properties: `fill`, `borderColor`, `borderWidth`, `tension` (Bézier curve tension, 0 for straight lines), `pointRadius`, `pointBackgroundColor`, `pointBorderColor`, `showLine` (hide the line, show only points), `spanGaps` (connect across null values).

Default scales: CategoryScale (x), LinearScale (y).

## Bar Chart

Displays data as vertical bars. Used for comparing discrete categories or showing trends.

```js
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
    datasets: [{
      label: 'My Dataset',
      data: [65, 59, 80, 81, 56, 55, 40],
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      borderColor: 'rgb(75, 192, 192)',
      borderWidth: 1
    }]
  },
  options: {
    scales: {
      y: { beginAtZero: true }
    }
  }
});
```

Key dataset properties: `backgroundColor`, `borderColor`, `borderWidth`, `borderSkipped` (which edge to skip border on), `barPercentage`, `categoryPercentage`, `roundedCorners`. Set `indexAxis: 'y'` for horizontal bars.

Default scales: CategoryScale (x), LinearScale (y).

## Doughnut and Pie Charts

Show proportional data as segments of a circle. Doughnut has a cutout; pie does not.

```js
new Chart(ctx, {
  type: 'doughnut',   // or 'pie'
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

Key dataset properties: `backgroundColor`, `borderColor`, `borderWidth`, `hoverOffset` (how much segments expand on hover), `weight` (relative weight of the dataset), `spacing` (gap between arcs).

The only difference between pie and doughnut is the default `cutout`: `'0%'` for pie, `'50%'` for doughnut.

Neither uses scales — data is rendered proportionally.

## Radar Chart

Shows multiple data points and variation between them on a radial axis. Useful for comparing two or more datasets across shared dimensions.

```js
new Chart(ctx, {
  type: 'radar',
  data: {
    labels: ['Eating', 'Drinking', 'Sleeping', 'Designing', 'Coding', 'Cycling', 'Running'],
    datasets: [{
      label: 'My Dataset',
      data: [65, 59, 90, 81, 56, 55, 40],
      backgroundColor: 'rgba(75, 192, 192, 0.2)',
      borderColor: 'rgb(75, 192, 192)'
    }]
  },
  options: {
    elements: {
      line: { borderWidth: 3 }
    }
  }
});
```

Default scale: RadialLinearScale.

## Polar Area Chart

Similar to doughnut but each segment has the same angle, with radius determined by data value. Shows magnitude across categories.

```js
new Chart(ctx, {
  type: 'polarArea',
  data: {
    labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple'],
    datasets: [{
      data: [11, 16, 7, 3, 14],
      backgroundColor: [
        'rgba(255, 99, 132, 0.5)',
        'rgba(54, 162, 235, 0.5)',
        'rgba(255, 205, 86, 0.5)',
        'rgba(75, 192, 192, 0.5)',
        'rgba(153, 102, 255, 0.5)'
      ]
    }]
  }
});
```

Key dataset properties: `backgroundColor`, `borderColor`, `borderWidth`, `angleStart` (rotation offset).

Default scale: RadialLinearScale.

## Scatter Chart

Based on line charts but with a linear x-axis. Data must be objects with `x` and `y` properties. Shows correlation between two variables.

```js
new Chart(ctx, {
  type: 'scatter',
  data: {
    datasets: [{
      label: 'Scatter Dataset',
      data: [
        { x: -10, y: 0 },
        { x: 0, y: 10 },
        { x: 10, y: 5 }
      ],
      backgroundColor: 'rgb(75, 192, 192)'
    }]
  },
  options: {
    scales: {
      x: { type: 'linear', position: 'bottom' }
    }
  }
});
```

Default scales: LinearScale (x), LinearScale (y).

## Bubble Chart

Displays three dimensions: x position, y position, and bubble radius (`r`). Used for showing relationships between three variables.

```js
new Chart(ctx, {
  type: 'bubble',
  data: {
    datasets: [{
      label: 'Dataset',
      data: [
        { x: 20, y: 30, r: 15 },
        { x: 40, y: 10, r: 10 }
      ],
      backgroundColor: 'rgb(255, 99, 132)'
    }]
  }
});
```

Default scales: LinearScale (x), LinearScale (y).

## Area Chart

Both `line` and `radar` charts support the `fill` option on datasets to create filled areas. This is implemented by the Filler plugin.

Fill modes:

- **Absolute dataset index** — `fill: 1` fills to dataset at index 1
- **Relative dataset index** — `fill: '-1'` fills to the previous dataset
- **Boundary** — `fill: 'start'`, `'end'`, or `'origin'`
- **Disabled** — `fill: false`

```js
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Feb', 'Mar'],
    datasets: [
      {
        label: 'Dataset 1',
        data: [10, 20, 30],
        fill: 'origin'
      },
      {
        label: 'Dataset 2',
        data: [5, 15, 25],
        fill: '-1'  // fills to previous dataset
      }
    ]
  }
});
```

## Mixed Chart Types

Create mixed charts by specifying `type` on each dataset instead of at the chart level:

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
  },
  options: { /* shared options */ }
});
```

Note: When using mixed charts, default options are only considered at the dataset level and are not merged at the chart level.

## Component Requirements by Chart Type

When using bundlers with tree-shaking, each chart type requires specific components:

- **Bar**: BarController, BarElement, CategoryScale (x), LinearScale (y)
- **Bubble**: BubbleController, PointElement, LinearScale (x/y)
- **Doughnut**: DoughnutController, ArcElement (no scales)
- **Line**: LineController, LineElement, PointElement, CategoryScale (x), LinearScale (y)
- **Pie**: PieController, ArcElement (no scales)
- **PolarArea**: PolarAreaController, ArcElement, RadialLinearScale
- **Radar**: RadarController, LineElement, PointElement, RadialLinearScale
- **Scatter**: ScatterController, PointElement, LinearScale (x/y)
