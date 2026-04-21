# Selections — Modifying Elements

> **Source:** https://d3js.org/d3-selection/modifying
> **Loaded from:** SKILL.md (via progressive disclosure)

Selection methods for modifying element attributes, styles, classes, properties, and text content.

## Attribute Methods

### selection.attr(name[, value])

Gets or sets an attribute. If value is a function, it is evaluated with `(d, i, nodes)` signature.

```js
// Set single attribute
selection.attr("color", "red");

// Get current attribute
selection.attr("color"); // "red"

// Function-based setting
selection.attr("cx", (d, i) => x(d.value));
```

### selection.property(name[, value])

Gets or sets a DOM property (as opposed to an attribute). Properties like `value`, `checked`, `disabled` are often better set as properties.

```js
selection.property("disabled", true);
selection.property("value", d => d.name);
```

## Style Methods

### selection.style(name[, value[, priority]])

Gets or sets a CSS style. Optional third argument: `"important"` for `!important` priority.

```js
selection.style("color", "red");
selection.style("font-size", "14px", "important");

// Remove style
selection.style("color", null);
```

### selection.classed(name[, value])

Gets or sets CSS classes. Can add multiple classes at once with space-separated names. If value is a function, evaluated per element.

```js
selection.classed("foo", true);
selection.classed("foo bar", true);
selection.classed("active", d => d.active);

// Toggle
selection.classed("highlight", !selection.classed("highlight"));
```

### selection.style() / classed() — Getting

When called with one argument (no value), returns the computed style/class of the first non-null element.

```js
selection.style("color"); // "red", perhaps
selection.classed("foo"); // true, perhaps
```

## Text and HTML Content

### selection.text([value])

Gets or sets text content (escaping HTML).

```js
selection.text("Hello, world!");
const t = selection.text(); // get current text
```

### selection.html([value])

Gets or sets inner HTML (parses as HTML, not escaped).

```js
selection.html("<strong>Bold</strong>");
```

## Data-Driven Modification

All modification methods accept functions with signature `(d, i, nodes)` where `d` is the datum, `i` is the index within the group, and `nodes` is the array of DOM elements.

```js
selection
  .attr("x", (d, i) => xScale(d.x))
  .attr("y", (d, i) => yScale(d.y))
  .style("fill", (d) => colorScale(d.category))
  .text((d) => d.label);
```

## Removing Elements

### selection.remove()

Removes each selected element from the DOM.

```js
selection.remove();
```

## Inserting and Appending

### selection.append(type)

Creates a new element as the last child of each selected element. The type can be a string tag name or a function returning a node.

```js
svg.append("g").attr("class", "axis");
circle.append("title").text(d => d.name);
```

### selection.insert(type[, before])

Creates a new element as the previous sibling. `before` can be a selector string or function that returns the reference element.

```js
svg.insert("rect", ".label")
  .attr("class", "background");
```

## Setting Data and Index

### selection.datum([value])

Gets or sets the bound data without entering/exiting. When setting, replaces data for all selected elements.

```js
selection.datum({name: "test"}); // single element
selection.datum(); // get bound datum
```
