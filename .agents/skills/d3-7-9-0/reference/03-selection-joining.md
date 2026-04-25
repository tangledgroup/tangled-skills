# Selections — Data Joining

> **Source:** https://d3js.org/d3-selection/joining
> **Loaded from:** SKILL.md (via progressive disclosure)

The data join is D3's most novel concept. Given a set of data and a set of DOM elements, it applies separate operations for entering, updating, and exiting elements.

## The Update Pattern

### selection.data([data[, key]])

Binds array `data` to selected elements. Returns an update selection with bound data. If `key` is provided, it determines element-to-data matching.

```js
const p = d3.selectAll("p").data(data);
```

### selection.join([enter[, update][, exit]])

Convenience method for the full enter-update-exit pattern. Each argument is a function receiving its respective selection.

```js
svg.selectAll("circle")
  .data(data)
  .join(
    enter => enter.append("circle").attr("r", 0),
    update => update.attr("r", d => radius(d.value)),
    exit => exit.transition().duration(500).attr("r", 0).remove()
  )
  .attr("fill", d => color(d.category));
```

### selection.enter()

Returns the enter selection — placeholders for data elements that have no corresponding DOM element. Append new elements here.

```js
const enter = svg.selectAll("circle")
  .data(data)
  .enter();

enter.append("circle")
  .attr("r", 0)
  .attr("cx", d => x(d.x))
  .attr("cy", d => y(d.y));
```

### selection.exit()

Returns the exit selection — DOM elements without corresponding data. Remove or transition them here.

```js
svg.selectAll("circle")
  .data(data)
  .exit()
  .transition().duration(300)
  .attr("r", 0)
  .remove();
```

## Key Functions

The key function determines how data maps to DOM elements. By default, data index matches element index. A key function enables stable identity:

```js
svg.selectAll("div")
  .data(data, d => d.id)
  .join(
    enter => enter.append("div").text(d => d.name),
    update => update,
    exit => exit.remove()
  );
```

## Enter Selection Methods

Enter selections support most selection methods. Common pattern: append elements, set initial state, then transition to final state.

```js
enter.append("rect")
  .attr("x", d => x(d.name))
  .attr("width", x.bandwidth())
  .attr("y", height)
  .attr("height", 0)
  .transition().duration(750)
  .attr("y", d => y(d.value))
  .attr("height", d => height - y(d.value));
```

## Join Variations

### Simple append (no exit needed)

When data only grows:

```js
svg.selectAll("circle")
  .data(data)
  .enter()
  .append("circle")
  .attr("cx", d => x(d.x))
  .attr("cy", d => y(d.y));
```

### Full three-function join

When data can grow, shrink, or change:

```js
const circles = svg.selectAll("circle")
  .data(data, d => d.id)
  .join(
    enter => enter.append("circle").attr("r", 0),
    update => update,
    exit => exit.remove()
  );

circles
  .attr("cx", d => x(d.x))
  .attr("cy", d => y(d.y))
  .attr("fill", d => color(d.category));
```

## Important Notes

- Enter selection does not include existing elements — only placeholders
- Exit selection does not include enter elements — only orphaned DOM nodes
- The update selection includes both existing and enter elements by default
- Use key functions when data items have stable identities (IDs, keys)
- Transition on enter elements to animate from initial state
