# Plugins and Customization

## Plugin Architecture

Plugins are the primary way to customize or change Chart.js default behavior. They have lifecycle hooks that fire at various stages of chart initialization, update, rendering, and event handling.

### Built-in Plugins

- **Legend** — Displays dataset information (always registered by default)
- **Tooltip** — Shows data values on hover/click (always registered by default)
- **Title** — Chart title display
- **SubTitle** — Subtitle display
- **Filler** — Area filling between datasets or boundaries
- **Decimation** — Data sampling for large line chart datasets

### Using Plugins

Pass plugins inline in the chart config:

```js
const chart = new Chart(ctx, {
  type: 'line',
  data: data,
  plugins: [
    {
      id: 'myPlugin',
      beforeDraw: (chart, args, options) => {
        // custom logic
      }
    }
  ]
});
```

Register globally to apply to all charts:

```js
Chart.register({
  id: 'myGlobalPlugin',
  beforeDraw: (chart) => {
    // applies to every chart
  }
});
```

### Plugin ID

Plugins must define a unique `id` following npm package name conventions (lowercase, URL-safe, no leading dot/underscore). Public plugins should be prefixed with `chartjs-plugin-`.

### Plugin Options

Plugin options live under `options.plugins.{plugin-id}`:

```js
options: {
  plugins: {
    myPlugin: {
      foo: 'bar'
    }
  }
}
```

Disable a specific plugin for one chart:

```js
options: {
  plugins: {
    myPlugin: false
  }
}
```

Disable all plugins:

```js
options: {
  plugins: false
}
```

### Plugin Defaults

Set default values for plugin options in the plugin's `defaults`:

```js
const plugin = {
  id: 'customBackground',
  beforeDraw(chart, args, options) {
    const { ctx, chartArea } = chart;
    if (chartArea) {
      ctx.save();
      ctx.fillStyle = options.color;
      ctx.fillRect(chartArea.left, chartArea.top, chartArea.width, chartArea.height);
      ctx.restore();
    }
  },
  defaults: {
    color: 'lightGreen'
  }
};
```

### Plugin Lifecycle Hooks

**Chart Initialization:**
- `beforeInit(chart, args, options)` — Chart is being initialized

**Chart Update:**
- `beforeUpdate(chart, args, options)` — Before update begins
- `afterUpdate(chart, args, options)` — After chart is updated
- `afterDraw(chart, args, options)` — After chart is drawn

**Rendering (cancelable with `false` return):**
- `beforeLayout(chart, args, options)` — Before layout calculation
- `afterLayout(chart, args, options)` — After layout
- `beforeDatasetsUpdate(chart, args, options)` — Before datasets update
- `afterDatasetsUpdate(chart, args, options)` — After datasets update
- `beforeDatasetUpdate(chart, args, options)` — Before individual dataset update
- `afterDatasetUpdate(chart, args, options)` — After individual dataset update
- `beforeDatasetsDraw(chart, args, options)` — Before drawing datasets
- `afterDatasetsDraw(chart, args, options)` — After drawing datasets
- `beforeDatasetDraw(chart, args, options)` — Before drawing individual dataset
- `afterDatasetDraw(chart, args, options)` — After drawing individual dataset

**Event Handling:**
- `resize(chart, args, options)` — Chart is being resized
- `destroy(chart, args, options)` — Chart is being destroyed

If a plugin makes changes requiring re-render, set `args.changed = true`.

## Legend Plugin

Namespace: `options.plugins.legend`

```js
plugins: {
  legend: {
    display: true,
    position: 'top',       // 'top', 'left', 'bottom', 'right', 'chartArea'
    align: 'center',       // 'start', 'center', 'end'
    reverse: false,
    onClick: (event, legendItem, legend) => { /* toggle dataset visibility */ },
    onHover: (event, legendItem, legend) => { /* hover handler */ },
    labels: {
      color: '#666',
      font: { size: 12 },
      padding: 10,
      usePointStyle: false,
      pointStyle: 'circle',
      boxWidth: 20,
      boxHeight: 20,
      generateLabels: (chart) => { /* custom label generation */ }
    },
    title: {
      display: true,
      text: 'Legend Title',
      color: '#333',
      font: { size: 14, weight: 'bold' }
    }
  }
}
```

For HTML legends (more visual customization), use the `generateLabels` callback to build DOM elements.

## Tooltip Plugin

Namespace: `options.plugins.tooltip`

```js
plugins: {
  tooltip: {
    enabled: true,
    mode: 'nearest',       // 'nearest', 'index', 'point', 'dataset', 'x', 'y'
    intersect: true,
    position: 'average',   // 'average' or 'nearest'
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    titleColor: '#fff',
    bodyColor: '#fff',
    footerColor: '#fff',
    titleFont: { weight: 'bold' },
    bodyFont: {},
    padding: 10,
    caretPadding: 10,
    caretSize: 5,
    cornerRadius: 6,
    displayColors: true,
    boxWidth: 20,
    boxHeight: 20,
    boxPadding: 6,
    usePointStyle: false,
    borderColor: 'rgba(0, 0, 0, 0)',
    borderWidth: 0,
    callbacks: {
      title: (items) => items[0]?.label || '',
      label: (context) => `${context.dataset.label}: ${context.parsed.y}`,
      labelColor: (context) => ({
        borderColor: context.dataset.borderColor,
        backgroundColor: context.dataset.backgroundColor
      }),
      afterBody: (items) => 'Custom footer text',
      footer: (items) => `Total: ${items.reduce((s, i) => s + i.parsed.y, 0)}`
    },
    filter: (item, index) => item.parsed.y > 0,
    itemSort: (a, b) => a.dataIndex - b.dataIndex
  }
}
```

### External Tooltips

Render tooltips as HTML elements outside the canvas:

```js
plugins: {
  tooltip: {
    enabled: false,  // Disable built-in tooltip
    external: function(context) {
      const tooltipEl = document.getElementById('chartjs-tooltip');
      if (!tooltipEl) return;

      const model = context.tooltip;
      if (model.opacity === 0) {
        tooltipEl.style.opacity = 0;
        return;
      }

      if (model.body) {
        const title = model.title?.join('<br>') || '';
        const body = model.body.map(b => b.lines).join('<br>');
        tooltipEl.innerHTML = `<div>${title}</div><div>${body}</div>`;
      }

      const { offsetLeft: left, offsetTop: top } = context.chart.canvas;
      tooltipEl.style.opacity = 1;
      tooltipEl.style.left = (left + model.caretX) + 'px';
      tooltipEl.style.top = (top + model.caretY) + 'px';
      tooltipEl.style.backgroundColor = model.backgroundColor;
      tooltipEl.style.color = model.bodyColor;
    }
  }
}
```

## Animation Configuration

Namespace: `options.animation`

```js
options: {
  animation: {
    duration: 1000,        // Duration in milliseconds
    easing: 'easeOutQuart', // Easing function name
    delay: (context) => context.dataIndex * 100,  // Staggered animation
    onComplete: (animation) => { /* callback */ },
    onProgress: (event) => { /* progress callback */ }
  },
  animations: {
    // Per-property animation config
    numbers: {
      type: 'number',
      property: 'y',
      duration: 500
    },
    tension: {
      type: 'number',
      duration: 1000,
      easing: 'linear',
      from: 1,
      to: 0,
      loop: true
    }
  },
  transitions: {
    // Transition-specific animation (e.g., active state)
    active: {
      animation: {
        duration: 0
      }
    }
  }
}
```

Disable animations entirely:

```js
options: {
  animation: false
}
```

## Custom Elements

Create custom chart elements by extending built-in element classes:

```js
import { ArcElement, Registry } from 'chart.js';

class CustomArc extends ArcElement {
  draw(ctx) {
    // Custom drawing logic
    super.draw(ctx);
  }
}

CustomArc.id = 'customArc';
CustomArc.defaults = ArcElement.defaults;

Registry.addElements(CustomArc);
```

## Colors

Chart.js supports three color categories:

- **`backgroundColor`** — Fill color for geometric elements (default: `rgba(0, 0, 0, 0.1)`)
- **`borderColor`** — Stroke/border color (default: `rgba(0, 0, 0, 0.1)`)
- **`color`** — Text/font color (default: `#666`)

Colors can be specified as CSS color strings, RGB arrays `[r, g, b]`, RGBA arrays `[r, g, b, a]`, or hex strings. Canvas gradients and patterns are also supported.

## Fonts

Global font settings in `Chart.defaults.font`:

```js
Chart.defaults.font = {
  family: "'Helvetica Neue', 'Helvetica', 'Arial', sans-serif",
  size: 14,
  style: 'normal',      // 'normal', 'italic', 'oblique'
  weight: undefined,    // 'normal', 'bold', 'lighter', 'bolder', or number
  lineHeight: undefined
};
```

Per-element font overrides:

```js
plugins: {
  legend: {
    labels: {
      font: { size: 16, weight: 'bold' }
    }
  }
}
```
