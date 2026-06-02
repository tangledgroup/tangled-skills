# API & Embedding

## Contents
- Parser API
- View Construction
- View Configuration
- Dataflow & Rendering
- Signals API
- Event Handling
- Image Export
- Data & Scales API
- Embedding Examples

## Parser API

The Vega parser accepts a JSON specification and generates a reactive dataflow graph.

```javascript
const runtime = vega.parse(spec, config);
const view = new vega.View(runtime).initialize('#container');
view.runAsync();
```

### vega.parse(specification[, config, options])

| Parameter | Type | Description |
|-----------|------|-------------|
| `specification` | Object | Vega JSON specification |
| `config` | Object / null | Config overrides (merged with defaults; spec-level config takes precedence) |
| `options.ast` | Boolean | ≥5.12 Include ASTs for expressions instead of JS code fragments |

## View Construction

### new vega.View(runtime[, options])

```javascript
// Method chain style
const view = new vega.View(runtime)
  .logLevel(vega.Warn)
  .renderer('svg')
  .initialize('#view')
  .hover();
view.runAsync();

// Options object style
const view = new vega.View(runtime, {
  logLevel: vega.Warn,
  renderer: 'svg',
  container: '#view',
  hover: true
});
view.runAsync();

// Async/await style
const view = await new vega.View(runtime, {
  logLevel: vega.Warn,
  renderer: 'svg',
  container: '#view',
  hover: true
}).runAsync();
```

### Constructor Options

| Option | Type | Description |
|--------|------|-------------|
| `background` | Color | View background color |
| `bind` | String / Element | DOM element for signal-bound inputs |
| `container` | String / Element | Parent DOM container |
| `hover` | Boolean | Enable hover processing |
| `loader` | Object | Data file/image loader instance |
| `logLevel` | Number | Log level: `vega.None`, `vega.Warn`, `vega.Info`, `vega.Debug` |
| `logger` | Object | Custom logger instance |
| `renderer` | String | `'canvas'` (default) or `'svg'` |
| `tooltip` | Function | Custom tooltip handler |
| `locale` | Object | ≥5.12 Number/date locale definitions |
| `expr` | Function | ≥5.13 Alternate expression evaluator |
| `watchPixelRatio` | Boolean | Re-render on pixel ratio changes (zoom/monitor change) |

### view.finalize()

Call when the view is no longer needed to unregister timers, remove event listeners, and prevent memory leaks.

## View Configuration

| Method | Description |
|--------|-------------|
| `initialize([container, bindContainer])` | Initialize rendering; adds Canvas/SVG to DOM if container provided |
| `loader([loader])` | Get/set data loader instance |
| `logLevel(level)` | Set log level |
| `logger([logger])` | Get/set logger instance |
| `renderer(type)` | Set `'canvas'` or `'svg'`; reset + re-render |
| `tooltip(handler)` | Set tooltip handler `(handler, event, item, value)` |
| `hover([hoverSet, updateSet])` | Enable hover (call **once** at init; not idempotent) |
| `description([text])` | ≥5.10 Set/get aria-label text |
| `background([color])` | Set background color (equivalent to `signal('background', color)`) |
| `width([pixels])` | Set width (equivalent to `signal('width', pixels)`) |
| `height([pixels])` | Set height (equivalent to `signal('height', pixels)`) |
| `padding([obj])` | Set padding: number or `{left, top, right, bottom}` |
| `resize()` | Flag for autosize recalculation on next runAsync |

## Dataflow & Rendering

| Method | Description |
|--------|-------------|
| `runAsync([encode, prerun, postrun])` | Evaluate dataflow + render. Returns Promise. Await before re-invoking |
| `run([encode, prerun, postrun])` | Async evaluation; returns immediately (not awaited) |
| `runAfter(callback)` | Schedule callback after current dataflow completes |
| `dirty(item)` | Mark scenegraph item for redraw |
| `container()` | Return DOM container element |
| `scenegraph()` | Return Vega scenegraph instance |
| `origin()` | Return `[x, y]` origin coordinates |

## Signals API

| Method | Description |
|--------|-------------|
| `signal(name[, value])` | Get signal value or set new value + return view |
| `getState([options])` | Export all signal values and modified data sets |
| `setState(state)` | Restore state from getState output; calls run() |
| `addSignalListener(name, handler)` | Register listener `(name, newValue)` on signal change |
| `removeSignalListener(name, handler)` | Remove a registered listener |

**Important:** Signal listeners fire during dataflow evaluation. Do not call `run()` or `runAsync()` from within a listener — use `prerun` callbacks instead.

## Event Handling

| Method | Description |
|--------|-------------|
| `events(source, type[, filter])` | Create EventStream for view/window/CSS selector source |
| `addEventListener(type, handler[, options])` | Register DOM event listener `(event, item)`; idempotent |
| `removeEventListener(type, handler)` | Remove registered listener |
| `addResizeListener(handler)` | Register size change listener `(width, height)`; idempotent |
| `removeResizeListener(handler)` | Remove resize listener |
| `globalCursor(flag)` | ≥5.13 Set cursor on entire document body (true) or view only (false) |
| `preventDefault(flag)` | Call preventDefault() on input events by default |

## Image Export

All export methods return Promises. Can be used client-side or server-side.

| Method | Description |
|--------|-------------|
| `toCanvas([scaleFactor, options])` | Promise resolving to canvas element; scaleFactor (default 1) |
| `toSVG([scaleFactor])` | Promise resolving to SVG string |
| `toImageURL(type[, scaleFactor])` | Promise resolving to image URL (`'svg'`, `'png'`, or `'canvas'`) |

### Canvas Options
| Option | Type | Description |
|--------|------|-------------|
| `type` | String | Canvas type (e.g., `'pdf'` for node-canvas) |
| `context` | Object | Key-value pairs for Canvas 2D context |
| `externalContext` | Context2D | ≥5.12 External canvas to render into (resolves to null) |

## Data & Scales API

| Method | Description |
|--------|-------------|
| `scale(name)` | Return live scale/projection instance (do not modify!) |
| `data(name[, values])` | Get data array (live), or ≥5.5 set new values |
| `addDataListener(name, handler)` | Register listener `(name, newValue)` on data change |
| `removeDataListener(name, handler)` | Remove data listener |
| `change(name, changeset)` | Apply changeset to dataset; await runAsync before next change |
| `insert(name, tuples)` | Insert data tuples (cannot combine with remove on same pulse) |
| `remove(name, tuples)` | Remove tuples or use predicate function `(d) => d.count < 5` |

### Data Updates
```javascript
// Insert
view.insert('data', [{x: 1, y: 2}]).run();

// Remove with predicate
view.remove('table', d => d.count < 5).run();

// Complex changes
view.change('data', vega.changeset().insert([...]).remove([...])).run();
```

**Important:** Inserted tuples must be pre-parsed JavaScript objects. Format directives from the spec are NOT applied to View API data. Await `runAsync` between sequential changes.

## Embedding Examples

### Basic Web Page
```html
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
</head>
<body>
  <div id="vis"></div>
  <script>
    fetch('spec.json').then(r => r.json()).then(spec => {
      vega.parse(spec).then(runtime => {
        const view = new vega.View(runtime, {
          container: '#vis',
          renderer: 'svg',
          hover: true
        });
        view.runAsync();
      });
    });
  </script>
</body>
</html>
```

### Node.js (Server-Side Rendering)
```javascript
const vega = require('vega');
const fs = require('fs');

const spec = JSON.parse(fs.readFileSync('spec.json', 'utf8'));
const runtime = vega.parse(spec);
const view = new vega.View(runtime);

view.initialize().runAsync().then(() => {
  return view.toSVG();
}).then(svg => {
  fs.writeFileSync('output.svg', svg);
});
```

### Export PNG
```javascript
view.runAsync().then(() => {
  return view.toImageURL('png', 2); // 2x resolution
}).then(url => {
  const link = document.createElement('a');
  link.href = url;
  link.download = 'chart.png';
  link.click();
});
```
