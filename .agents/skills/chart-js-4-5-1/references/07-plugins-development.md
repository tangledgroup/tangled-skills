# Plugins & Development

## Using Plugins

### Inline Plugins
Defined directly in chart config:
```javascript
const chart = new Chart(ctx, {
  plugins: [{
    beforeInit(chart, args, options) { /* ... */ }
  }]
});
```

### Per-Chart Plugins
Shared between specific charts:
```javascript
const myPlugin = { id: 'myPlugin', /* hooks */ };

const chart1 = new Chart(ctx, { plugins: [myPlugin] });
const chart2 = new Chart(ctx, { plugins: [myPlugin] });
```

### Global Plugins
Applied to all charts:
```javascript
Chart.register({
  id: 'myPlugin',
  // hooks...
});
```

:::warning Inline plugins cannot be registered globally.:::

## Plugin ID Convention

- No dots or underscores at start
- URL-safe characters only (lowercase, hyphens)
- Short but descriptive
- Public packages should prefix with `chartjs-plugin-`

## Plugin Options

Options scoped by plugin ID under `options.plugins`:
```javascript
options: {
  plugins: {
    myPlugin: { foo: 'bar', baz: 42 }
  }
}
```

### Disabling Plugins
```javascript
// Disable specific global plugin for one chart
options: { plugins: { myPlugin: false } }

// Disable all plugins for one chart
options: { plugins: false }
```

### Plugin Defaults
```javascript
const plugin = {
  id: 'myPlugin',
  defaults: { optionA: 'defaultA', optionB: 10 },
  beforeDraw: (chart, args, options) => {
    // options.optionA is 'defaultA' if not overridden
  }
};
```

## Plugin Core API — Extension Hooks

### Chart Initialization
| Hook | Arguments | Description |
|------|-----------|-------------|
| `beforeInit` | `(chart, args, options)` | Before initialization |
| `afterInit` | `(chart, args, options)` | After initialization |

### Chart Update
| Hook | Arguments | Description |
|------|-----------|-------------|
| `beforeReset` | `(chart, args, options)` | Before reset |
| `reset` | `(chart, args, options)` | Reset chart state |
| `beforeUpdate` | `(chart, args, options)` | Before update starts |
| `beforeDatasetsUpdate` | `(chart, args, options)` | Before dataset update |
| `afterDatasetsUpdate` | `(chart, args, options)` | After dataset update |
| `afterUpdate` | `(chart, args, options)` | After update completes |
| `afterLayout` | `(chart, args, options)` | After layout pass |

### Scale Update
| Hook | Arguments | Description |
|------|-----------|-------------|
| `beforeScaleDestroy` | `(chart, args, options)` | Before scale destroyed |
| `scaleDestroy` | `(chart, args, options)` | Scale being destroyed |
| `afterScaleDestroy` | `(chart, args, options)` | After scale destroyed |
| `beforeScaleSetDimensions` | `(chart, args, options)` | Before scale dimensions |
| `afterScaleSetDimensions` | `(chart, args, options)` | After scale dimensions |
| `beforeDataLimits` | `(chart, args, options)` | Before data limits |
| `afterDataLimits` | `(chart, args, options)` | After data limits |
| `beforeBuildTicks` | `(chart, args, options)` | Before ticks built |
| `afterBuildTicks` | `(chart, args, options)` | After ticks built |
| `beforeTickToLabelConversion` | `(chart, args, options)` | Before tick→label |
| `afterTickToLabelConversion` | `(chart, args, options)` | After tick→label |

### Rendering
| Hook | Arguments | Cancelable | Description |
|------|-----------|:----------:|-------------|
| `beforeDraw` | `(chart, args, options)` | Yes | Before chart draw |
| `draw` | `(chart, args, options)` | — | During chart draw |
| `afterDraw` | `(chart, args, options)` | Yes | After chart draw |
| `beforeDatasetsDraw` | `(chart, args, options)` | Yes | Before datasets |
| `datasetsDraw` | `(chart, args, options)` | — | During dataset draw |
| `afterDatasetsDraw` | `(chart, args, options)` | Yes | After datasets |
| `beforeClip` | `(chart, args, options)` | Yes | Before clipping |
| `afterClip` | `(chart, args, options)` | Yes | After clipping |
| `afterRender` | `(chart, args, options)` | Yes | After render complete |

### Event Handling
| Hook | Arguments | Description |
|------|-----------|-------------|
| `beforeEvent` | `(chart, args, options)` | Before event processing. Set `args.changed = true` to trigger re-render |
| `afterEvent` | `(chart, args, options)` | After event processing |

### Chart Destroy
| Hook | Arguments | Description |
|------|-----------|-------------|
| `beforeDestroy` | `(chart, args, options)` | Before destroy starts |
| `destroy` | `(chart, args, options)` | During destroy |
| `afterDestroy` | `(chart, args, options)` | After destroy completes |

:::warning The `destroy` hook is deprecated since v3.7.0. Use `afterDestroy` instead.:::

## Chart API

### Creating a Chart
```javascript
const chart = new Chart(ctx, config);
// or
const chart = new Chart(ctx, { type, data, options });
```

### Methods
| Method | Description |
|--------|-------------|
| `chart.destroy()` | Destroy the chart instance |
| `chart.stop()` | Stop ongoing animations |
| `chart.resize(newWidth, newHeight)` | Resize the chart |
| `chart.render([mode])` | Start animation/render |
| `chart.update([mode])` | Update chart with new data/options |
| `chart.reset()` | Reset animated values to starting point |
| `chart.animate()` | Start the animation |
| `chart.isPaused()` | Check if chart is paused |
| `chart.clear()` | Clear the canvas |
| `chart.stop()` / `chart.start()` | Pause/resume animations |

### Update Modes
| Mode | Description |
|------|-------------|
| `'default'` | Normal update with animations |
| `'none'` | Update without animations |
| `'show'` | Show transition (fade in) |
| `'hide'` | Hide transition (fade out) |
| `'resize'` | Resize transition |
| `'active'` | Active/hover transition |

### Data Methods
| Method | Description |
|--------|-------------|
| `chart.getData()` | Get chart data |
| `chart.setData(data)` | Set new data |
| `chart.addData(datasets, labels)` | Add data at end |
| `chart.removeData(count)` | Remove data from start |
| `chart.showDataset(datasetIndex)` | Show specific dataset |
| `chart.hideDataset(datasetIndex)` | Hide specific dataset |
| `chart.getDatasetMeta(datasetIndex)` | Get metadata for a dataset |

### Element Methods
| Method | Description |
|--------|-------------|
| `chart.getElementsAtEventForMode(event, mode, options, retroactive)` | Get elements by event |
| `chart.getSortedVisibleDatasetMetas()` | Get visible datasets sorted by order |
| `chart.getVisibleDatasetCount()` | Count visible datasets |

## Creating Custom Chart Types

### Basic Structure
```javascript
const MyChart = Chart.controllers.line.extend({
  draw() {
    // custom draw logic
    Chart.controllers.line.prototype.draw.call(this);
  }
});

Chart.register(MyChart);
```

### Registering a New Type
```javascript
Chart.register({
  type: 'myChart',
  controller: MyController,
  defaults: { /* default options */ }
});
```

## Creating Custom Axes

### Basic Structure
```javascript
const myScale = new Scale();
myScale.id = 'myScale';
myScale.legendLabel = 'My Scale';

Chart.register(myScale);
```

### Required Methods
| Method | Arguments | Description |
|--------|-----------|-------------|
| `parse` | `(raw, index)` | Parse raw data value |
| `buildTicks` | `()` | Build tick objects |
| `getLabelForValue` | `(value)` | Return label for value |
| `getPixelForValue` | `(value)` | Convert value to pixel |
| `getValueForPixel` | `(pixel)` | Convert pixel to value |
| `calculateLabelRotation` | `()` | Calculate tick rotation |
| `getPixelForTick` | `(index)` | Get pixel for tick index |
| `getTicks` | `()` | Return all ticks |

### Optional Methods
| Method | Arguments | Description |
|--------|-----------|-------------|
| `beforeUpdate` | — | Before update process |
| `afterUpdate` | — | After update process |
| `setPadding` | `(padding)` | Set extra padding |
| `draw` | `(clip)` | Draw the axis |

## TypeScript Plugin Typings

```typescript
import { ChartType, Plugin } from 'chart.js';

declare module 'chart.js' {
  interface PluginOptionsByType<TType extends ChartType> {
    myPlugin?: {
      optionA: string;
      optionB: number;
    };
  }
}
```

## Performance Tips

### Parsing Optimization
Disable parsing when data is already in internal format:
```javascript
options: { parsing: false }
// or per dataset
datasets: [{ data: [...], parsing: false }]
```

### Data Normalization
Normalize data to `{x, y}` format to skip parsing:
```javascript
data: normalizedData  // already sorted, internal format
```

### Decimation
Enable for large datasets:
```javascript
plugins: {
  decimation: {
    enabled: true,
    algorithm: 'lttb',  // or 'minmax'
    threshold: 1000
  }
}
```

### Tree-Shaking
Import only needed components to reduce bundle size. See [Getting Started → Tree-Shaking](./01-getting-started.md#tree-shaking-component-reference).

## Accessibility

- Charts are rendered on `<canvas>` — add `alt` text via the `alt` option
- Tooltips provide hover-based data access
- Use semantic HTML around the chart for context
