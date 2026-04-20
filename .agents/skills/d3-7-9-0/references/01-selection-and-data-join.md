# D3 Selection and Data Join

## Selection Basics

### Selecting Elements

```javascript
// Single element
const container = d3.select("#container");

// All matching elements
const rects = d3.selectAll("rect.bar");

// From a selection
const nested = svg.select(".chart").selectAll("circle");

// Child/children selection
selection.selectChild();                    // First matching child
selection.selectChildren(selector);         // All matching children
```

### Selecting from Window/Document

```javascript
// Select from window
d3.window(svg.node());          // Get the window containing an element

// Select from document
d3.select(document.body);
d3.selectAll("script[type='application/json']");
```

## The Data Join Pattern

The data join is D3's core pattern for binding data to DOM elements.

### Three-argument join() (Recommended)

```javascript
const circles = svg.selectAll("circle")
    .data(data, d => d.id)          // Optional key function
    .join(
        enter => enter.append("circle").attr("r", 0),
        update => update.attr("fill", "steelblue"),
        exit => exit.transition().duration(500).attr("r", 0).remove()
    )
    .transition().duration(750)
    .attr("cx", d => x(d.x))
    .attr("cy", d => y(d.y));
```

### Two-argument join (Legacy)

```javascript
const circles = svg.selectAll("circle")
    .data(data);

// Enter selection
const enter = circles.enter()
    .append("circle");

// Update (existing + new)
circles.attr("cx", d => x(d.x));

// Exit
circles.exit().remove();
```

### Key Function

Use a key function for stable identity across data changes:

```javascript
svg.selectAll("rect")
    .data(data, d => d.id)   // Use unique id for stability
    .join("rect");
```

## Control Flow

```javascript
// Check if selection is empty
if (selection.empty()) { ... }

// Get first node
const node = selection.node();

// Get all nodes as array
const nodes = selection.nodes();

// Iterate over selections
selection.each(function(d, i, nodes) {
    // this refers to the DOM element
});

// Apply a function to each selection
selection.call(someFunction);

// Check size
const count = selection.size();

// Filter selection
selection.filter(predicate);
```

## Modifying Elements

### Attributes
```javascript
selection.attr("class", "bar");
selection.attr("x", d => xScale(d.value));
selection.attr("cx cy r", d => `${d.x} ${d.y} 5`);
```

### Styles
```javascript
selection.style("fill", "steelblue");
selection.style("stroke-width", 1.5);
selection.style("opacity", 0.8);
```

### Properties
```javascript
// For properties that differ from attributes (e.g., checked, value)
selection.property("checked", true);
```

### Text and HTML
```javascript
selection.text(d => d.label);
selection.html("<strong>Bold</strong>");
```

### Class Manipulation
```javascript
selection.classed("active", d => d.active);
selection.classed({"highlight": true, "dimmed": false});
```

### Insert and Append
```javascript
// Insert before existing elements
svg.insert("circle", ":last-child")
    .attr("cx", 50).attr("cy", 50).attr("r", 10);

// Append at end
svg.append("g").attr("class", "axis");
```

### Sort and Order
```javascript
selection.sort(comparator);           // Sort DOM elements
selection.order();                     // Reorder to match data
selection.raise();                     // Move to front
selection.lower();                     // Move to back
```

## Namespaces

```javascript
// SVG namespace
d3.namespace("http://www.w3.org/2000/svg");

// Create with namespace
svg.append("svg:g")
    .attr("xmlns", "http://www.w3.org/2000/svg");

// Custom namespace
const ns = d3.namespace("http://purl.org/dc/elements/1.1/");
svg.append(ns.prefix + ":title")
    .text("Chart Title");
```

## Local Variables

For passing data between selection methods:

```javascript
const local = d3.local();

selection.each(function(d) {
    local.set(this, computeSomething(d));
});

selection.attr("x", function() {
    return local.get(this);
});
```
