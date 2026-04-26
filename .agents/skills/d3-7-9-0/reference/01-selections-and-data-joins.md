# Selections and Data Joins

## Selecting Elements

D3 selections are arrays of DOM elements wrapped with data-binding methods. They form the foundation of all D3 operations.

**Basic selection:**

```js
// Select a single element by CSS selector
const p = d3.select("p");

// Select all matching elements
const items = d3.selectAll("li");

// Select from an existing selection (scoped)
const firstLi = p.select("li");
const allLi = p.selectAll("li");
```

**Creating elements:**

```js
// Create a new element without appending to DOM
const svg = d3.create("svg")
    .attr("width", 640)
    .attr("height", 400);

// Append to existing selection
const circle = svg.append("circle")
    .attr("cx", 50)
    .attr("cy", 50)
    .attr("r", 20);

// Insert before a reference element
svg.insert("circle", "rect");
```

**Modifying elements:**

```js
// Set attributes
selection.attr("fill", "steelblue");

// Conditional attribute (null removes the attribute)
selection.attr("opacity", d => d.value > 0.5 ? 1 : null);

// Set styles
selection.style("font-size", "12px")
    .style("color", d => d.color);

// Set DOM properties
selection.property("checked", true);

// Set text or HTML content
selection.text("Hello");
selection.html("<strong>Bold</strong>");

// Add/remove/ toggle classes
selection.classed("active", true);
selection.classed("inactive", false);
selection.classed("highlight", (d, i) => i % 2 === 0);
```

**Removing elements:**

```js
selection.remove();
```

## Joining Data

The data join is D3's core pattern. It binds data to DOM elements and produces three groups: enter, update, and exit.

**The modern `.join()` shorthand:**

```js
// .join("rect") handles enter, update, and exit in one call
svg.selectAll("rect")
    .data(data)
    .join("rect")
    .attr("x", (d, i) => x(i))
    .attr("y", d => y(d))
    .attr("width", 20)
    .attr("height", d => h(d));
```

**The explicit enter/update/exit pattern:**

```js
const circles = svg.selectAll("circle")
    .data(data, (d, i) => i); // key function for identity

// EXIT: remove elements no longer in data
circles.exit()
    .transition()
    .duration(300)
    .attr("r", 0)
    .remove();

// UPDATE: modify existing elements
circles
    .attr("cx", (d, i) => x(i))
    .attr("cy", d => y(d));

// ENTER: create new elements for new data
circles.enter()
    .append("circle")
    .attr("cx", (d, i) => x(i))
    .attr("cy", d => y(d))
    .attr("r", 0)
    .transition()
    .duration(500)
    .attr("r", 5);
```

**Key function for data identity:**

```js
// Without key: elements matched by index
selection.data(data);

// With key: elements matched by unique identifier
selection.data(data, d => d.id);
```

The key function is essential when data can be reordered, inserted, or removed — it ensures the correct element is updated rather than all elements being destroyed and recreated.

## Handling Events

D3 provides a unified event API for DOM events:

```js
// Add event listener
selection.on("click", function(event, d) {
    console.log("clicked", d);
    // event is the native DOM event
    // d is the bound data
});

// Multiple events
selection.on("mouseover mouseout", function(event, d) {
    if (event.type === "mouseover") {
        d3.select(this).attr("fill", "red");
    } else {
        d3.select(this).attr("fill", "steelblue");
    }
});

// Remove event listener
selection.on("click", null);

// Access the current selection from within an event
selection.on("click", function(event) {
    d3.select(this).attr("stroke", "red");
});
```

**Custom events with d3-dispatch:**

```js
const dispatch = d3.dispatch("brush", "end");

// Listen
dispatch.on("brush", function(selection) {
    console.log("brushed", selection);
});

// Emit
dispatch.call("brush", null, [[0, 0], [100, 100]]);
```

## Control Flow

D3 selections support iteration and conditional operations:

```js
// Iterate over selected elements
selection.each(function(d, i, nodes) {
    // this is the current DOM node
    // d is bound data
    // i is index
    // nodes is the full HTMLCollection
});

// Filter selection
const large = selection.filter(d => d.value > 50);

// Sort selection by data value
selection.sort((a, b) => a.value - b.value);

// Call a function on the selection
function drawAxis(g) {
    g.append("line").attr("class", "axis");
}
svg.append("g").call(drawAxis);
```

## Local Variables

D3 locals provide per-selection storage, avoiding data pollution:

```js
const highlight = d3.local();

// Set local value
selection.call(highlight.set, true);

// Get local value
selection.each(function() {
    console.log(highlight.get(this));
});

// Remove local value
selection.call(highlight.remove);
```

Locals are useful for storing state that should not be part of the bound data, such as hover states or animation flags.

## Namespaces

For SVG elements in HTML context or cross-document operations:

```js
// Create element with namespace
const svg = d3.create("svg:svg", "http://www.w3.org/2000/svg");

// Namespace-aware selection
selection.select("svg:title");
```

D3 7 uses `d3.create()` for namespaced element creation and handles SVG namespaces automatically when creating SVG content.
