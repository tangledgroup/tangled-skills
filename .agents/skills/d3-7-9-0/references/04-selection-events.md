# Selections — Events

> **Source:** https://d3js.org/d3-selection/events
> **Loaded from:** SKILL.md (via progressive disclosure)

D3 event handling wraps native DOM events with consistent behavior and additional utilities.

## Listening to Events

### selection.on(type[, listener[, options]])

Attaches or removes an event listener. The `this` context inside the listener is the current DOM element. The first argument is the event, followed by datum `d`, index `i`.

```js
// Basic click handler
d3.selectAll("p").on("click", (event) => console.log(event));

// With data access
circle.on("click", (event, d) => {
  console.log(d.name);
});

// Remove listener
selection.on("click", null);

// Named namespace for selective removal
selection.on("click.foo", listener1);
selection.on("click.bar", listener2);
selection.on("click.foo", null); // removes only foo
```

## Event Dispatching

### selection.dispatch(type[, options])

Synthesizes and dispatches an event on each selected element. Useful for programmatic event triggering.

```js
d3.select("p").dispatch("click");
```

## Pointer Events

### d3.pointer(event[, target])

Returns the mouse/touch position relative to the target element (default: `event.currentTarget`). Returns `[x, y]` array.

```js
const [x, y] = d3.pointer(event);
```

### d3.pointers(event[, target])

Returns pointer positions for all active pointers (supports multi-touch).

```js
const points = d3.pointers(event);
```

## Event Modifiers

D3 provides modifiers for controlling event propagation and default behavior:

- `event.preventDefault()` — prevent browser default
- `event.stopPropagation()` — stop bubbling
- `event.stopImmediatePropagation()` — stop all listeners
- `event.preventMousemove` — suppress mousemove until mouseup (for click consistency)

## Common Event Patterns

### Click with data

```js
svg.selectAll("rect")
  .data(data)
  .on("click", (event, d) => {
    highlight(d);
  });
```

### Mouse tracking

```js
svg.on("mousemove", (event) => {
  const [x, y] = d3.pointer(event);
  tooltip.attr("transform", `translate(${x}, ${y})`);
});
```

### Drag detection (without d3-drag)

```js
selection
  .on("mousedown", (event) => {
    event.stopPropagation();
    event.preventDefault();
  })
  .on("click", (event, d) => {
    // Click without drag
  });
```

## Important Notes

- `this` inside listener is the current DOM element — use `d3.select(this)` to create a selection
- Use `event.currentTarget` for the element the listener is attached to
- Use `event.target` for the actual element that received the event
- Named namespaces (`.foo`) allow selective removal of listeners
- For complex interactions, prefer d3-drag, d3-zoom, or d3-brush modules
