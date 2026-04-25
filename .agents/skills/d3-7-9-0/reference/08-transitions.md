# Transitions and Animation

> **Source:** https://d3js.org/d3-transition
> **Loaded from:** SKILL.md (via progressive disclosure)

A transition is a selection-like interface for animating changes to the DOM. Instead of applying changes instantaneously, transitions smoothly interpolate from current state to target state over a given duration.

## Creating Transitions

### selection.transition()

Creates a transition on the current selection. Inherits timing from parent or uses defaults.

```js
d3.select("body")
  .transition()
  .style("background-color", "red");
```

### d3.transition([name])

Creates a named transition at the root level. Names allow selecting specific transitions.

```js
const fade = d3.transition("fade").duration(500);
selection.transition(fade).style("opacity", 0);
```

## Transition Methods

Transitions support most selection methods: `attr`, `style`, `classed`, `text`, `html`, `raise`, `lower`.

### transition.attr(name, value)

Animates attribute changes.

```js
circle.transition()
  .duration(750)
  .attr("r", 10);
```

### transition.style(name, value[, priority])

Animates style changes.

```js
rect.transition()
  .duration(500)
  .style("fill", "orange");
```

### transition.tween(name, factory)

Custom interpolation between values. Factory returns an interpolate function `(t) => value`.

```js
circle.transition()
  .duration(750)
  .attrTween("r", function() {
    const i = d3.interpolateNumber(0, 10);
    return t => this.setAttribute("r", i(t));
  });
```

## Timing Control

### transition.duration([value])

Set transition duration in milliseconds. Can be a function for per-element timing.

```js
transition.duration(750);
transition.duration((d, i) => 100 * i); // staggered
```

### transition.delay([value])

Set delay before transition starts in milliseconds.

```js
transition.delay(100);
transition.delay((d, i) => 30 * i); // staggered start
```

### transition.ease([ease])

Set the easing function. Default is `d3.easeCubic`.

```js
transition.ease(d3.easeLinear);
transition.ease(d3.easeElastic);
transition.ease(d3.easeBack);
transition.ease(d3.easeBounce);
```

**Available easings:**
- `d3.easeLinear` — constant speed
- `d3.easePoly` — polynomial (`.exponent(n)`)
- `d3.easeQuad` — quadratic
- `d3.easeCubic` — cubic (default)
- `d3.easeSin` — sinusoidal
- `d3.easeExp` — exponential
- `d3.easeCircle` — circular
- `d3.easeElastic` — elastic oscillation
- `d3.easeBack` — overshoot
- `d3.easeBounce` — bounce

## Chaining Transitions

Chain multiple transitions by calling `.transition()` again on a transition. Each subsequent call creates a child transition that starts when the parent ends.

```js
selection
  .transition()
  .duration(500)
  .attr("x", 100)
  .transition()
  .delay(200)
  .duration(500)
  .attr("y", 200);
```

## Control Flow

### transition.end

Promise that resolves when all transitions on the selection end.

```js
await selection.transition().duration(1000).end();
```

### transition.remove()

Removes elements after transition completes.

```js
selection.exit()
  .transition()
  .duration(300)
  .style("opacity", 0)
  .remove();
```

### selection.interrupt([name])

Interrupts any active transition and renders current state immediately.

```js
selection.interrupt(); // interrupt all
selection.interrupt("fade"); // interrupt specific named transition
```

## Selection Methods on Transitions

| Supported | Not supported |
|-----------|---------------|
| `attr()` | `append()` |
| `style()` | `insert()` |
| `classed()` | `remove()` |
| `text()` | `datum()` |
| `html()` | `each()` (use transition.each) |
| `raise()` | |
| `lower()` | |
| `attrTween()` | |
| `styleTween()` | |

## Complete Animation Example

```js
// Staggered bar chart animation
svg.selectAll(".bar")
  .data(data)
  .join(
    enter => enter.append("rect")
      .attr("x", d => x(d.name))
      .attr("width", x.bandwidth())
      .attr("y", height)
      .attr("height", 0)
      .attr("fill", "steelblue"),
    update => update,
    exit => exit.transition().duration(300).attr("height", 0).remove()
  )
  .transition()
  .delay((d, i) => i * 50)
  .duration(750)
  .ease(d3.easeElastic.out)
  .attr("y", d => y(d.value))
  .attr("height", d => height - y(d.value));
```
