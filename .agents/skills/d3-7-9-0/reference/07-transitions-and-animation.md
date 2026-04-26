# Transitions and Animation

## Transition Basics

Transitions interpolate attribute and style values over time. They are created by calling `.transition()` on a selection:

```js
selection.transition()
    .duration(750)           // milliseconds
    .delay((d, i) => i * 100) // staggered start
    .attr("fill", "red")
    .attr("r", 20);
```

The transition creates a new state that D3 animates toward. Attributes not specified in the transition are unchanged.

## Selecting Elements for Transitions

```js
// Transition on current selection
selection.transition().attr("opacity", 0);

// Named transitions (synchronize multiple selections)
selection.transition().name("fade").attr("opacity", 0);
selection.transition("fade").attr("fill", "red");

// Select during transition
selection.transition()
    .selectAll("circle")
    .transition()
    .attr("r", 10);

// Interrupt ongoing transitions
selection.interrupt();
selection.interrupt("fade");  // specific named transition
```

## Modifying Elements

Transitions support the same modification methods as selections:

```js
// Attributes
selection.transition().attr("cx", d => x(d.value));

// Styles
selection.transition().style("font-size", "24px").style("fill", "red");

// DOM properties
selection.transition().property("checked", true);

// Text content
selection.transition().tween("text", function() {
    const interpolator = d3.interpolateNumber(0, d.value);
    return t => this.textContent = Math.round(interpolator(t));
});

// Transform
selection.transition()
    .attrTween("transform", function() {
        const i = d3.interpolateString("rotate(0)", "rotate(360)");
        return t => i(t);
    });
```

**Interpolators** are functions `f(number) → value` that map [0, 1] to intermediate values:

```js
d3.interpolateNumber(a, b);   // numeric interpolation
d3.interpolateString(a, b);   // string with embedded numbers
d3.interpolateRgb(a, b);      // color interpolation
d3.interpolateRound(a, b);    // integer interpolation
d3.interpolateTransformCss(a, b); // CSS transform
d3.interpolateZoom(a, b);     // zoom (translate + scale)
d3.interpolateHcl(a, b);      // HCL color space
d3.interpolateLab(a, b);      // LAB color space
```

**Custom tweens** for complex animations:

```js
selection.transition()
    .attrTween("d", function(d) {
        const that = this;
        const i = d3.interpolate(this._current || d, d);
        this._current = i(0);
        return t => { that.setAttribute("d", line(i(t))); };
    });
```

## Timing

Control the speed and rhythm of transitions:

```js
// Duration (milliseconds)
selection.transition().duration(1000);

// Delay before starting
selection.transition().delay(500);
selection.transition().delay((d, i, nodes) => i * 50); // staggered

// Ease function (timing curve)
selection.transition().ease(d3.easeCubicInOut);
```

**Ease functions:**

- `easeLinear` — constant speed (default for transitions)
- `easePolyIn(k)`, `easePolyOut(k)`, `easePolyInOut(k)` — polynomial
- `easeQuadIn`, `easeQuadOut`, `easeQuadInOut`
- `easeCubicIn`, `easeCubicOut`, `easeCubicInOut`
- `easeSinIn`, `easeSinOut`, `easeSinInOut`
- `easeExpIn`, `easeExpOut`, `easeExpInOut`
- `easeCircleIn`, `easeCircleOut`, `easeCircleInOut`
- `easeElasticIn(amplitude, period)`, `easeElasticOut`, `easeElasticInOut`
- `easeBackIn(overshoot)`, `easeBackOut`, `easeBackInOut`
- `easeBounceIn`, `easeBounceOut`, `easeBounceInOut`

## Control Flow

```js
// Callback when transition ends
selection.transition()
    .attr("opacity", 0)
    .end()
    .then(() => {
        selection.remove();
    });

// Multiple callbacks
selection.transition()
    .on("start", function() { console.log("started"); })
    .on("end", function() { console.log("ended"); })
    .on("interrupt", function() { console.log("interrupted"); });

// Filter during transition
selection.filter(d => d.value > 50)
    .transition()
    .attr("fill", "red");

// Merge transitions
selection1.transition().attr("fill", "red")
    .merge(selection2.transition())
    .attr("opacity", 0.5);
```

## Timers

Low-level timer API for custom animations:

```js
// One-shot timer
d3.timer(callback, delay);  // delay in ms, default 0

function callback(elapsed) {
    // elapsed: time since timer started (ms)
    if (elapsed > 1000) return true; // return true to stop
    // update animation frame
}

// Repeating interval
const interval = d3.timer(callback);
interval.restart(newCallback, delay);  // restart with new callback
interval.stop();                       // stop timer
```

## Complete Example: Animated Bar Chart

```js
// Initial render with transition
svg.selectAll("rect")
    .data(data)
    .join("rect")
    .attr("x", (d, i) => x(i))
    .attr("y", height)
    .attr("width", x.bandwidth())
    .attr("height", 0)
    .transition()
    .duration(500)
    .delay((d, i) => i * 50)
    .ease(d3.easeBackOut.overshoot(1.5))
    .attr("y", d => y(d))
    .attr("height", d => height - y(d));

// Update on data change
function update(newData) {
    svg.selectAll("rect")
        .data(newData)
        .join("rect")
        .transition()
        .duration(300)
        .attr("y", d => y(d))
        .attr("height", d => height - y(d));
}
```
