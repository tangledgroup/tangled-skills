# Interaction — Zoom, Drag, Brush

> **Source:** https://d3js.org/d3-zoom, d3-drag, d3-brush
> **Loaded from:** SKILL.md (via progressive disclosure)

D3 provides behavior modules for user interaction: zooming/panning, dragging, and brushing.

## Zoom Behavior — d3-zoom

Handles panning and zooming via mouse wheel, pinch, or direct manipulation. Works with SVG, HTML, and Canvas.

### Creating a Zoom Behavior

```js
const zoom = d3.zoom()
  .scaleExtent([1, 10])        // min/max zoom levels
  .translateExtent([[-100, -100], [width + 100, height + 100]]) // pan bounds
  .extent([[0, 0], [width, height]]) // zoomable area
  .filter(event => !event.ctrlKey) // ctrl+scroll = browser zoom
  .on("zoom", onZoom);
```

### Applying Zoom

Attach to a selection with `.call(zoom)`. The zoom transform is available in the event.

```js
svg.call(zoom);

function onZoom(event) {
  const transform = event.transform;
  g.attr("transform", transform);
}
```

### Zoom Transform

The transform object has methods for applying transformations:

```js
// Methods
transform.scale(k)       // return new scaled transform
transform.translate(x, y) // return new translated transform
transform.apply([x, y])  // apply to point
transform.invert([x, y]) // reverse apply

// Properties
transform.k      // scale factor
transform.x      // translation x
transform.y      // translation y
```

### Zooming Scales

Combine with d3-scale to zoom axes automatically:

```js
const zoom = d3.zoom().on("zoom", ({transform}) => {
  const newX = transform.rescaleX(x);
  g.select(".x-axis").call(d3.axisBottom(newX));
  line.x(d => newX(d.date));
  path.attr("d", line(data));
});
```

### Programmatic Zoom

```js
svg.transition().duration(750).call(zoom.transform, d3.zoomIdentity.scale(2).translate(-width/4, -height/4));
```

## Drag Behavior — d3-drag

Handles mouse and touch drag events.

### Creating a Drag Behavior

```js
const drag = d3.drag()
  .subject(event => {
    const [sx, sy] = d3.pointer(event, svg.node());
    return {x: sx, y: sy}; // drag from pointer position
  })
  .on("start", onDragStart)
  .on("drag", onDrag)
  .on("end", onDragEnd);

circle.call(drag);
```

### Drag Events

- `start` — drag begins
- `drag` — pointer moves while dragging
- `end` — drag ends

The event includes:
- `event.sourceEvent` — the underlying mouse/touch event
- `event.subject` — the subject being dragged (if set via `.subject()`)
- `event.x`, `event.y` — current position
- `event.dx`, `event.dy` — change since last event
- `event.active` — number of concurrent drags

### Drag Configuration

```js
d3.drag()
  .container(element)    // coordinate space (default: svg)
  .subject(event => ({x: sx, y: sy}))
  .filter(event => !event.ctrlKey)  // ignore ctrl+drag
  .clickThreshold(10)    // pixels before considered drag
  .touchAllowed(false)   // disable touch dragging
  .on("start", fn)
  .on("drag", fn)
  .on("end", fn);
```

## Brush Behavior — d3-brush

Provides rectangular selection for focus+context, data region selection.

### Creating a Brush

```js
const brush = d3.brush()
  .extent([[marginLeft, marginTop], [width - marginRight, height - marginBottom]])
  .on("start", onBrushStart)
  .on("brush", onBrush)
  .on("end", onBrushEnd);

svg.append("g")
  .attr("class", "brush")
  .call(brush);
```

### Brush Types

```js
// X-axis brush (select horizontal range)
const brush = d3.brushX()
  .extent([[0, 0], [width, height]])
  .on("brush end", onBrush);

// Y-axis brush (select vertical range)
const brush = d3.brushY()
  .extent([[0, 0], [width, height]])
  .on("brush end", onBrush);

// 2D brush
const brush = d3.brush()
  .extent([[0, 0], [width, height]])
  .on("brush end", onBrush);
```

### Brush Selection

Get/set the current selection:

```js
// Get selection: [[x0, y0], [x1, y1]]
const selection = g.call(brush).selection();

// Set selection programmatically
g.call(brush.move, [[100, 50], [300, 200]]);

// Clear selection
g.call(brush.move, null);
```

### Brush Selection Events

- `start` — brush begins
- `brush` — brush is being drawn (continuous)
- `end` — brush ends (may have empty selection if clicked without dragging)

```js
function onBrush(event) {
  if (!event.selection) return;
  const [[x0, y0], [x1, y1]] = event.selection;
  // Filter data within brush region
  filteredData = data.filter(d => d.x >= x0 && d.x <= x1);
}
```

### Combining Brush with Zoom

```js
const zoom = d3.zoom().on("zoom", ({transform}) => {
  g.attr("transform", transform);
  brush.move(g.call(brush).selection(), null); // reset brush
});

const brush = d3.brush()
  .extent([[0, 0], [width, height]])
  .on("brush end", function(event) {
    if (event.selection) {
      const [[x0], [x1]] = event.selection;
      svg.transition().call(
        zoom.transform,
        d3.zoomIdentity.scale(width / (x1 - x0)).translate(-x0, 0)
      );
    }
  });
```
