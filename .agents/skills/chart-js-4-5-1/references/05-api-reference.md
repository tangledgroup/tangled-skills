# API Reference

## Chart Class

The main `Chart` class is the entry point for all rendered charts.

### Constructor

```typescript
new Chart(context: CanvasRenderingContext2D | HTMLCanvasElement, config: ChartConfiguration): Chart
```

**Parameters:**
- `context`: 2D canvas rendering context or the canvas element itself
- `config`: Chart configuration object

### Chart Configuration Type

```typescript
interface ChartConfiguration {
  type: string;                                    // Chart type
  data: ChartData;                                 // Data
  options?: ChartOptions;                          // Options
  plugins?: Plugin[];                              // Plugins
}
```

### Chart Instance Methods

| Method | Description |
|--------|-------------|
| `chart.destroy()` | Remove the chart instance |
| `chart.update(mode?: string, defaultUpdateMode?: string)` | Update chart with optional animation mode |
| `chart.render()` | Render the chart (no animation) |
| `chart.stop()` | Stop any current animation |
| `chart.resize(newWidth?, newHeight?)` | Resize chart dimensions |
| `chart.canvas.width` / `.height` | Access canvas dimensions |
| `chart.currentDevicePixelRatio` | Get device pixel ratio |
| `chart.notifyPlugins(hook, args)` | Notify plugins of an event |
| `chart.getDatasetMeta(datasetIndex)` | Get metadata for a dataset |
| `chart.getElementAtEvent(event)` | Get elements at event position |
| `chart.getElementsAtEventForMode(event, mode, options, intersect?)` | Get elements by interaction mode |
| `chart.getElementsAtXAxis(event)` | Get elements at X-axis position |
| `chart.getSortedVisibleDatasetMetas()` | Get all visible datasets sorted by draw order |
| `chart.isDatasetVisible(datasetIndex)` | Check if dataset is visible |
| `chart.showTooltip(items, forceUpdate?)` | Show tooltip programmatically |
| `chart.hideTooltip(index?, animate?, callback?)` | Hide tooltip |
| `chart.tooltip.draw(Chart, args, options?)` | Draw tooltip on canvas |
| `chart.tooltip.getPixelForValue(value)` | Get pixel position for a data value |
| `chart.getDatasetAtIndex(datasetIndex)` | Get dataset info at index |
| `chart.toggleDataVisibility(datasetIndex)` | Toggle dataset visibility |
| `chart.setDataVisibility(datasetIndex, visible)` | Set dataset visibility |
| `chart.hide(index?, datasetIndex?)` | Hide element or dataset |
| `chart.show(index?, datasetIndex?)` | Show element or dataset |
| `chart.scales` | Object containing all scale instances |
| `chart.plugins` | Array of registered plugins |
| `chart.options` | Resolved chart options |
| `chart.canvas` | The canvas HTML element |
| `chart.ctx` | The canvas 2D rendering context |
| `chart.chartArea` | Object with `{left, top, right, bottom}` |
| `chart.width` | Chart width in pixels |
| `chart.height` | Chart height in pixels |
| `chart.aspectRatio` | Width/height ratio |
| `chart.scale` | The scale used for this chart (radial charts) |
| `chart.config` | The chart configuration object |
| `chart.id` | Unique chart identifier |

### Update Modes

| Mode | Description |
|------|-------------|
| `'default'` | Animate non-data property changes |
| `'none'` | No animation, immediate update |
| `'active'` | Active transition (hover) |
| `'reset'` | Reset transition |
| `'show'` / `'hide'` | Show/hide transitions |
| `'resize'` | Resize transition |

### Chart Events

Chart.js exposes events through the canvas element:
- `'click'`, `'mousemove'`, `'mouseout'`, `'mouseover'`, `'mouseenter'`, `'mouseleave'`
- Custom events via `chart.canvas.addEventListener('chartjsEvent', handler)`

Use `getElementsAtEventForMode()` to interpret events.

## Registry

The registry stores all registered components (controllers, elements, scales, plugins).

```javascript
import { registry } from 'chart.js';

// Get a component by type
const controller = registry.getController('line');
const scale = registry.getScale('category');
const element = registry.getElement('point');
const plugin = registry.getPlugin('legend');

// Get all registered components
const controllers = registry.getControllers();   // Map
const scales = registry.getScales();             // Map
const elements = registry.getElements();         // Map
const plugins = registry.getPlugins();           // Map
```

## DatasetController

Base class for chart type controllers. Each chart type has a controller:

| Controller | Chart Types |
|------------|-------------|
| `LineController` | `'line'`, `'scatter'` |
| `BarController` | `'bar'`, `'barHorizontal'` |
| `DoughnutController` | `'doughnut'`, `'pie'` |
| `PolarAreaController` | `'polarArea'` |
| `RadarController` | `'radar'` |
| `BubbleChartController` | `'bubble'` |

### Controller Properties

```javascript
controller.chart;           // Chart instance
controller.getMeta();       // Get dataset metadata
controller.getParsedData(); // Parse data for this dataset
controller.getContext();    // Get option context
controller.updateElement(element, index, properties, mode); // Update element
controller.resolveDataElementOptions(mode); // Resolve data element options
```

### Controller Methods

| Method | Description |
|--------|-------------|
| `attach()` | Called when chart is attached |
| `detached()` | Called when chart is detached |
| `update(index)` | Update dataset at index |
| `draw()` | Draw the dataset |
| `getLabelAndValue(index)` | Get label and value for data point |
| `getXScale()` | Get the X scale |
| `getYScale()` | Get the Y scale |
| `getScaleForId(scaleID)` | Get a specific scale by ID |
| `resolveElementOptions(index, mode)` | Resolve options for an element |
| `syncFromDatasets()` | Sync metadata with datasets |

## Scale Class

Base class for all scales.

### Scale Properties

```javascript
scale.chart;              // Chart instance
scale.options;            // Scale options
scale.ctx;                // Canvas context
scale.canvas;             // Canvas element
scale.width;              // Scale width
scale.height;             // Scale height
scale.xOffset;            // X offset
scale.yOffset;          Y offset
scale.getPixelForValue(value);     // Value → pixel
scale.getValueForPixel(pixel);     // Pixel → value
scale.getTicks();               // Get all ticks
scale.getLabelAndValue(i);      // Get label and value at index
```

### Scale Methods

| Method | Description |
|--------|-------------|
| `parse(raw, from?, to?)` | Parse raw data values |
| `buildTicks()` | Build tick objects |
| `generateTickLabels(ticks)` | Generate tick label strings |
| `getPixelForDecimal(decimal)` | Get pixel for decimal position (0-1) |
| `getPixelForValue(value)` | Get pixel for a value |
| `getValueForPixel(pixel)` | Get value for a pixel |
| `getBasePixel()` | Get the base axis pixel |
| `getReversePixels()` | Get reverse pixel position |
| `getRatio()` | Get the ratio of this scale |
| `update(width, height, padding?)` | Update scale dimensions |
| `fit()` | Adjust scale to fit |
| `isPointInArea(point)` | Check if point is in scale area |

## Element Classes

### PointElement

```javascript
// Properties
element.x;
element.y;
element.base;
element.options;    // Resolved options (pointStyle, radius, etc.)

// Methods
element.tooltipPosition();  // Get tooltip position
element.getRange?(axis);    // Get range for hit detection
```

### LineElement

```javascript
// Properties
element.points;           // Array of PointElement
element.options;
element.spanGaps;         // Whether to span gaps
element.cubicInterpolationMode;

// Methods
element.updateControlPoints(curveSlope, maxHeight, maxWidth);  // Update Bézier control points
element.getPointCoordinates(index);  // Get point coordinates
```

### BarElement

```javascript
// Properties
element.x;
element.y;
element.base;
element.width;
element.height;
element.options;
element.optionsOptions;     // Options for each side (top, right, bottom, left)

// Methods
area();                     // Get the bar's area rectangle
tooltipPosition();          // Get tooltip position
```

### ArcElement

```javascript
// Properties
element.x;
element.y;
element.startAngle;
element.endAngle;
element.innerRadius;
element.outerRadius;
element.options;
element.optionsOptions;     // Options for each side

// Methods
tooltipPosition();          // Get tooltip position
centerPoint();              // Get center point of arc
```

## Plugin Interface

All plugins implement the Plugin interface:

```typescript
interface Plugin {
  id: string;
  
  // Lifecycle hooks
  beforeDraw?(chart: Chart, args: object, options: any): boolean | void;
  afterDraw?(chart: Chart, args: object, options: any): void;
  beforeDatasetsDraw?(chart: Chart, args: object, options: any): void;
  afterDatasetsDraw?(chart: Chart, args: object, options: any): void;
  beforeEvent?(chart: Chart, args: BeforeEventArgs, options: any): ChartEvent[] | void;
  afterEvent?(chart: Chart, args: AfterEventArgs, options: any): void;
  
  // Resize
  resize?(chart: Chart, size: { width: number; height: number }): void;
  
  // Data
  beforeUpdate?(chart: Chart, args: object, options: any): void;
  afterUpdate?(chart: Chart, args: object, options: any): void;
  
  // Destroy
  destroy?(chart: Chart): void;
  
  // Options
  additionalOptionScopes?: string[];
}
```

### Plugin Hook Arguments

| Hook | Args Properties |
|------|-----------------|
| `beforeDraw` / `afterDraw` | `cancelAnimation`, `originalOptions` |
| `beforeEvent` / `afterEvent` | `event`, `replayed`, `cancel` |
| `resize` | `width`, `height` |
| `beforeUpdate` / `afterUpdate` | `mode`, `cancelAnimation` |

## Enums

### DecimationAlgorithm

```javascript
import { DecimationAlgorithm } from 'chart.js';
// 'lttb' | 'min-max'
```

### UpdateModeEnum

```javascript
import { UpdateModeEnum } from 'chart.js';
// 'default' | 'none' | 'reset' | 'resize' | 'show' | 'hide' | 'active'
```

## TypeScript Types

Key types for TypeScript users:

```typescript
// Chart data
interface ChartData<DataType = number[], LabelType = string> {
  labels?: LabelType[];
  datasets: ChartDataset<DataType, LabelType>[];
}

// Chart dataset
interface ChartDataset<DataType = number[], LabelType = string> {
  type?: string;
  label?: string;
  data: DataType;
  // ... chart-type-specific properties
}

// Chart configuration
interface ChartConfiguration<DataType = number[], LabelType = string> {
  type: string;
  data: ChartData<DataType, LabelType>;
  options?: ChartOptions<DataType, LabelType>;
  plugins?: Plugin[];
}

// Chart options
interface ChartOptions {
  responsive?: boolean;
  maintainAspectRatio?: boolean;
  animation?: AnimationConfiguration;
  transitions?: Record<string, AnimationConfiguration>;
  color?: Color;
  backgroundColor?: Color;
  title?: TitleOptions;
  legend?: LegendOptions;
  tooltip?: TooltipOptions;
  plugins?: Record<string, any>;
  scales?: Record<string, ScaleOptions>;
  // ...
}

// Interaction options
interface InteractionOptions {
  mode?: InteractionMode;
  intersect?: boolean;
  axis?: 'x' | 'y' | 'xy';
  includeInvisible?: boolean;
}

// Animation configuration
interface AnimationConfiguration {
  duration?: number;
  easing?: string;
  onProgress?: (animation: AnimationEvent) => void;
  onComplete?: (animation: AnimationEvent) => void;
}

// Active element
interface ActiveElement {
  element: Element;
  datasetIndex: number;
  dataIndex: number;
}

// Chart event
interface ChartEvent {
  // Standard canvas event properties
  native: Event;
  x: number;
  y: number;
}
```

## Helpers Namespace

Chart.js provides utility helpers (tree-shakeable):

```javascript
import {
  isNumber, isObject, isArray, isFinite,
  addRoundedRectPath,
  niceNum,
  toPercentage, toDimension,
  readAxisProperties,
  color as getColor,
  throttle
} from 'chart.js/helpers';

// Type checking
isNumber(123);        // true
isObject({a: 1});     // true
isArray([1,2]);       // true
isFinite(Infinity);   // false

// Math
niceNum(0.3, false);  // Round to "nice" number
toPercentage(50, 100); // '50%'
```
