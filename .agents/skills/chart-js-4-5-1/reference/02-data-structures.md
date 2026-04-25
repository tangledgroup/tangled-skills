# Data Structures & Options

## Data Formats

### Primitive Array
```javascript
data: [20, 10],
// labels at same index used for index axis
labels: ['a', 'b']
```

### Tuple Array
```javascript
data: [[10, 20], [15, null], [20, 10]]
// first element = index axis, second = value axis
// null skips the point
```

### Object Array (most flexible)
```javascript
data: [{x: 10, y: 20}, {x: 15, y: null}, {x: 20, y: 10}]
// parsing can be disabled for performance
// data must already be sorted
```

### Object Array with Custom Keys
```javascript
data: [{id: 'Sales', nested: {value: 1500}}, {id: 'Purchases', nested: {value: 500}}],
options: {
  parsing: { xAxisKey: 'id', yAxisKey: 'nested.value' }
}
```

For pie/doughnut/radar/polarArea with custom keys:
```javascript
options: { parsing: { key: 'nested.value' } }
```

### Object (property names as index)
```javascript
data: { January: 10, February: 20 }
// property name = index, value = value
```

## Dataset Configuration

| Name | Type | Description |
|------|------|-------------|
| `label` | `string` | Label for legend and tooltips |
| `clip` | `number\|object` | Clip relative to chartArea. Positive = overflow, negative = pixels inside, 0 = at chartArea. Per side: `{left: 5, top: false, right: -2, bottom: 0}` |
| `order` | `number` | Drawing order (affects stacking, tooltip, legend) |
| `stack` | `string` | Stack group ID. Defaults to dataset type |
| `parsing` | `boolean\|object` | How to parse data. `false` disables parsing |
| `hidden` | `boolean` | Hide dataset from rendering |

### Custom Parsing Example
```javascript
const data = [{x: 'Jan', net: 100, cogs: 50, gm: 50}];
datasets: [{
  label: 'Net sales', data: data, parsing: { yAxisKey: 'net' }
}, {
  label: 'COGS', data: data, parsing: { yAxisKey: 'cogs' }
}]
```

## TypeScript Data Types
```typescript
import { ChartData } from 'chart.js';

const datasets: ChartData<'bar', {key: string, value: number}[]> = {
  datasets: [{
    data: [{key: 'Sales', value: 20}],
    parsing: { xAxisKey: 'key', yAxisKey: 'value' }
  }]
};
```

## Option Resolution

Options resolve from top to bottom. Higher priority overrides lower.

### Chart Level
`options` → `overrides[type]` → `defaults`

### Dataset Level
`dataset` → `options.datasets[type]` → `options` → `overrides[type].datasets[type]` → `defaults.datasets[type]` → `defaults`

### Element Level
`dataset` → `options.datasets[type]` → `options.datasets[type].elements[elementType]` → `options.elements[elementType]` → `options` → ...

### Scale Options
`options.scales` → `overrides[type].scales` → `defaults.scales` → `defaults.scale`

## Scriptable Options
Options accept functions called per data point:
```javascript
color: function(context) {
  const value = context.dataset.data[context.dataIndex];
  return value < 0 ? 'red' : 'green';
},
borderColor: function(context, options) {
  // resolve another option's value
  return Chart.helpers.color(options.color).lighten(0.2);
}
```

## Indexable Options
Options accept arrays matching data indices:
```javascript
color: ['red', 'blue', 'green', 'black']
// loops if fewer items than data points
```

## Option Context Objects

Context objects provide data for scriptable options:

### chart context
- `chart`: the chart instance
- `type`: `'chart'`

### dataset context (inherits chart)
- `dataset`: current dataset
- `datasetIndex`: index of dataset
- `active`: whether element is hovered
- `mode`: update mode
- `type`: `'dataset'`

### data context (inherits dataset)
- `dataIndex`: index of data point
- `parsed`: parsed data values
- `raw`: raw data value
- `element`: the element (point, bar, arc)
- `type`: `'data'`

### scale context
- `scale`: the scale object
- `type`: `'scale'`

### tick context (inherits scale)
- `tick`: the tick object
- `index`: tick index
- `type`: `'tick'`
