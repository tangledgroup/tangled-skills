# Interactions

## Zoom Behavior

Zoom enables panning and scaling via mouse wheel, drag, or touch gestures:

```js
const zoom = d3.zoom()
    .scaleExtent([0.5, 8])       // min/max zoom levels
    .translateExtent([[-1000, -1000], [width + 1000, height + 1000]])
    .on("zoom", (event) => {
        // event.transform has: k (scale), x (translateX), y (translateY)
        svg.selectAll("g").attr("transform", event.transform);

        // Update axis after zoom
        xAxis.scale(event.transform.rescaleX(xScale));
        svg.select(".x-axis").call(xAxis);
    });

// Apply to container
svg.call(zoom);

// Programmatically set zoom level
svg.call(zoom.transform, d3.zoomIdentity.translate(50, 30).scale(2));

// Reset zoom
svg.call(zoom.transform, d3.zoomIdentity);
```

**Zoom identity and transforms:**

```js
d3.zoomIdentity;  // { k: 1, x: 0, y: 0 }

const t = d3.zoomIdentity
    .translate(100, 50)
    .scale(2)
    .translate(-50, -25);

// Apply transform to scale (rescale for zoomed axes)
const newXScale = event.transform.rescaleX(xScale);
```

## Drag Behavior

Drag enables click-and-drag interaction on elements:

```js
const drag = d3.drag()
    .on("start", function(event) {
        d3.select(this).attr("cursor", "grabbing");
    })
    .on("drag", function(event) {
        // event.x, event.y — current pointer position in container coordinates
        // event.dx, event.dy — displacement since last event
        d3.select(this)
            .attr("cx", event.x)
            .attr("cy", event.y);
    })
    .on("end", function(event) {
        d3.select(this).attr("cursor", "pointer");
    });

// Apply to selection
selection.call(drag);

// Configure drag
drag.container(svgNode);     // set coordinate container element
drag.filter(function() { return !event.button; }); // only left click
drag.subject(function(d) { return { x: d.x, y: d.y }; }); // initial position
drag.touchable(false);       // disable touch events
```

## Brush Behavior

Brush allows selecting a region of the visualization:

```js
const brush = d3.brush()
    .extent([[0, 0], [width, height]])
    .on("brush", function(event) {
        // event.selection — [[x0, y0], [x1, y1]] or null
        if (!event.selection) return;
        const [[x0, y0], [x1, y1]] = event.selection;
        // Filter or highlight elements within selection
    })
    .on("end", function(event) {
        if (!event.selection) return;
        console.log("brush ended with:", event.selection);
    });

// Apply brush to SVG group
svg.append("g")
    .attr("class", "brush")
    .call(brush);

// One-dimensional brushes
const brushX = d3.brushX().extent([[marginLeft, 0], [width - marginRight, height]]);
const brushY = d3.brushY().extent([[0, marginTop], [width, height - marginBottom]]);

// Get current brush selection
d3.brushSelection(brushNode);

// Programmatically set/clear selection
svg.select(".brush").call(brush.move, [[50, 50], [200, 200]]);
svg.select(".brush").call(brush.move, null); // clear
```

**Brush with zoom (linked views):**

```js
// Brush on overview chart drives zoom on detail chart
const brush = d3.brushX()
    .extent([[0, 0], [width, height]])
    .on("end", function(event) {
        if (!event.selection) return;
        const [x0, x1] = event.selection.map(xScale.invert);
        // Zoom main chart to brushed range
        mainSvg.call(zoom.transform,
            d3.zoomIdentity.scale(width / (x1 - x0)).translate(-x0 * width / (x1 - x0), 0));
    });
```

## Dispatch (Custom Events)

Create custom event emitters for component communication:

```js
// Create dispatcher with named events
const dispatch = d3.dispatch("selection", "filter");

// Register listeners
dispatch.on("selection", function(selectedItems) {
    console.log("selected:", selectedItems);
});

dispatch.on("filter", function(predicate) {
    // update filtered view
});

// Emit events
dispatch.call("selection", null, [{ id: 1 }, { id: 2 }]);
dispatch.call("filter", null, d => d.value > 50);

// Remove listener
dispatch.on("selection", null);
```

Events can carry arbitrary arguments after the `null` (which represents `this`).

## Touch Support

D3 interaction behaviors support touch events automatically. Configure with:

```js
drag.touchable(() => true);       // enable touch for drag
brush.touchable(() => true);      // enable touch for brush
zoom.filter(function(event) {     // control which events trigger zoom
    return !event.ctrlKey && !event.button;
});
```

The `filter` method on all behaviors controls which input events initiate the interaction. By default, D3 ignores events with modifier keys (except for specific key interactions).
