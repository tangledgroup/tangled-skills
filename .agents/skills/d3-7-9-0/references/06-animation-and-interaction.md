# D3 Animation and Interaction

## Transitions

### Creating Transitions

```javascript
// Basic transition
selection.transition()
    .duration(750)
    .ease(d3.easeCubicInOut)
    .attr("fill", "steelblue")
    .attr("opacity", 1);

// With delay
selection.transition()
    .delay((d, i) => i * 10)
    .duration(750)
    .attr("y", d => y(d.value));

// Named transition
selection.transition("myTransition")
    .attr("x", 100);

// Active selection
d3.active(node);                    // Get current transition
d3.active(node, "transitionName");
```

### Transition Methods

```javascript
// Timing
transition.duration(ms);
transition.delay(ms);
transition.ease(easeFunction);
transition.easeVarying(fitn(d) => ease);

// Attribute tweening
transition.attrTween("transform", (d) => {
    const i = d3.interpolateString(oldValue, newValue);
    return t => attr.setAttribute("transform", i(t));
});

// Style tweening
transition.styleTween("fill", () => interpolateColor(c1, c2));

// Text tweening
transition.textTween(targetText);

// Custom tween
transition.tween("myTween", () => {
    const node = this;
    return t => { /* update node */ };
});

// Removal
transition.remove();
```

### Transition Control Flow

```javascript
// End promise
transition.end.then(() => console.log("done"));

// Interrupt transitions
selection.interrupt();
selection.interrupt("transitionName");

// Filter transitions
transition.filter(predicate);

// Selection methods on transitions
transition.each(fn);
transition.empty();
transition.node();
transition.nodes();
transition.size();

// Event handling
transition.on("start", function(d, i, nodes) {});
transition.on("end", function(d, i, nodes) {});
transition.on("interrupt", fn);

// Merge transitions
transition.merge(otherTransition);

// Select within transition
transition.select("selector");
transition.selectAll("selector");
```

## Easing Functions

```javascript
// Quadratic
d3.easeQuad;           d3.easeQuadIn;   d3.easeQuadOut;   d3.easeQuadInOut;

// Cubic
d3.easeCubic;          d3.easeCubicIn;  d3.easeCubicOut;  d3.easeCubicInOut;

// Sinusoidal
d3.easeSin;            d3.easeSinIn;    d3.easeSinOut;    d3.easeSinInOut;

// Exponential
d3.easeExp;            d3.easeExpIn;    d3.easeExpOut;    d3.easeExpInOut;

// Circular
d3.easeCircle;         d3.easeCircleIn; d3.easeCircleOut; d3.easeCircleInOut;

// Polynomial
d3.easePoly;           d3.easePolyIn;   d3.easePolyOut;   d3.easePolyInOut;
d3.easePoly.exponent(2);

// Elastic
d3.easeElastic;        d3.easeElasticIn;
d3.easeElastic.amplitude(1);
d3.easeElastic.period(0.4);

// Back (overshoot)
d3.easeBack;           d3.easeBackIn;
d3.easeBack.overshoot(1.70158);

// Bounce
d3.easeBounce;         d3.easeBounceIn; d3.easeBounceOut; d3.easeBounceInOut;
```

## Timers

```javascript
// One-time timeout
d3.timeout(callback, delay = 0, time = Date.now());
// → {restart(), stop()}

// Repeating interval
d3.interval(callback, delay = 1000, time = Date.now());
// → {restart(), stop()}

// Timer with custom clock
d3.timer(callback, delay = 0, time = Date.now());
// → {restart(), stop(), started: bool}

// Flush pending timers
d3.timerFlush();

// Current time
d3.now();
```

## Zoom (d3-zoom)

```javascript
const zoom = d3.zoom()
    .scaleExtent([1, 10])
    .translateExtent([[-100, -100], [width + 100, height + 100]])
    .interpolate(d3.interpolateZoom)
    .filter(event => !event.ctrlKey)
    .on("zoom", onZoom);

svg.call(zoom);

// Zoom events
function onZoom(event) {
    const transform = event.transform;
    circles.attr("transform", transform);
}

// Zoom methods
svg.transition().call(zoom.scaleBy, 2);        // Scale by factor
svg.transition().call(zoom.scaleTo, 3);        // Scale to factor
svg.transition().call(zoom.translateBy, 100, 50);

// Get current transform
d3.zoomTransform(svg.node());
// → {x, y, k}

// Transform methods
transform.apply([x, y]);           // Apply to point
transform.applyX(x);
transform.applyY(y);
transform.invert([x, y]);          // Inverse
transform.rescaleX(scale);         // Rescale axis
transform.toString();              // Serialize
```

### Zoom Constrained

```javascript
d3.zoom()
    .constrain((transform, extent) => {
        // Custom constraint function
        return transform;
    });
```

## Drag (d3-drag)

```javascript
const drag = d3.drag()
    .filter(event => !event.ctrlKey)     // Ignore ctrl+click
    .on("start", onDragStart)
    .on("drag", onDrag)
    .on("end", onDragEnd);

svg.call(drag);

// Drag configuration
drag.filter(() => true);                // Custom filter
drag.container(node);                   // Coordinate space
drag.subject(event);                    // Return drag subject
drag.touchable(touchSupportObject);     // Touch support
drag.clickDistance(5);                  // Max distance for click

// Enable/disable
d3.dragEnable(svg.node());
d3.dragDisable(svg.node());
d3.dragEnable(document.body, true);   // Force enable
```

### Drag Event Properties

```javascript
function onDrag(event) {
    event.sourceEvent;       // Original mouse/touch event
    event.subject;           // Drag subject (set by .subject())
    event.x, event.y;        // Current position
    event.dx, event.dy;      // Delta since last move
    event.pressure;          // Touch pressure
}
```

## Brush (d3-brush)

```javascript
const brush = d3.brush()
    .extent([[marginLeft, marginTop], [width - marginRight, height - marginBottom]])
    .filter(event => !event.ctrlKey)
    .on("start", onBrushStart)
    .on("brush", onBrush)
    .on("end", onBrushEnd);

svg.append("g").call(brush);

// Brush selection
function onBrushEnd(event) {
    const selection = d3.brushSelection(svg.node());
    // → [[x0, y0], [x1, y1]] or null
}

// Brush variants
d3.brushX();    // Horizontal brush
d3.brushY();    // Vertical brush
d3.brush();     // 2D brush

// Configuration
brush.extent(extent);
brush.filter(() => true);
brush.handleSize(6);
brush.keyModifiers(true/false);
brush.touchable(touchSupport);

// Programmatic control
svg.select(".brush").call(brush.move, [[10, 10], [50, 50]]);
svg.select(".brush").call(brush.move, null);   // Clear
```

## Events (d3-selection)

```javascript
// Basic event listener
selection.on("click", handler);
selection.on("mousedown mouseup", handler);
selection.on("mouseover", onEnter);
selection.on("mouseout", onLeave);

// With data
selection.on("click", function(event, d) {
    // this = DOM element
    // d = bound data
    event.preventDefault();
});

// Multiple handlers
selection.on("click.handler1", handler1)
         .on("click.handler2", handler2);

// Remove specific handler
selection.on("click.handler1", null);

// Event delegation
d3.select("body").on("click.foo", ".button", handler);

// Pointer events
d3.pointer(event, container);     // → [x, y] in container coords
d3.pointers(event, target);       // → [[x,y], ...] for multi-touch
```

## Dispatch (d3-dispatch)

```javascript
const dispatch = d3.dispatch("start", "end", "change");

// Subscribe
dispatch.on("start", onStart)
        .on("end", onEnd);

// Call handlers
dispatch.call("start", context, arg1, arg2);

// Copy dispatch
const copy = dispatch.copy();

// Check if listener exists
dispatch.on("start");
```

## Interpolation (d3-interpolate)

```javascript
// Value interpolation
d3.interpolate(0, 100)(0.5);        // → 50
d3.interpolate("steelblue", "red")(0.5);
d3.interpolateDate(date1, date2)(0.5);
d3.interpolateString("M0,0 L10,10", "M0,10 L10,0")(0.5);
d3.interpolateArray([1, 2], [3, 4])(0.5);
d3.interpolateObject({x: 0}, {x: 100})(0.5);

// Color interpolation
d3.interpolateRgb("steelblue", "red")(0.5);
d3.interpolateHcl("steelblue", "red")(0.5);
d3.interpolateLab("steelblue", "red")(0.5);
d3.interpolateHsl("steelblue", "red")(0.5);
d3.interpolateCubehelix("steelblue", "red")(0.5);

// Zoom interpolation
d3.interpolateZoom([x0, y0, r0], [x1, y1, r1])(t);

// Piecewise interpolation
d3.piecewise(d3.interpolateRgb, ["#f00", "#0f0", "#00f"]);

// Quantize
d3.quantile(interpolator, n);

// Basis
d3.interpolateBasis([c1, c2, c3]);
d3.interpolateBasisClosed([c1, c2, c3, c1]);
```

## Transform Interpolation

```javascript
d3.interpolateTransformSvg(t1, t2)(t);
d3.interpolateTransformCss(t1, t2)(t);
```
