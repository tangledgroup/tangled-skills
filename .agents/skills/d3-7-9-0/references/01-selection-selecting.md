# Selections — Selecting Elements

> **Source:** https://d3js.org/d3-selection/selecting
> **Loaded from:** SKILL.md (via progressive disclosure)

A selection is a set of elements from the DOM. Typically identified by CSS selectors like `.fancy` or `div`.

## Top-Level Selection

### d3.select(selector)

Selects the first element matching the selector string. If no match, returns empty selection. If selector is not a string, selects the specified node directly.

```js
const svg = d3.select("#chart");
d3.select(document.body).style("background", "red");
```

### d3.selectAll(selector)

Selects all matching elements in document order. If selector is not a string, selects the specified array of nodes or iterable.

```js
const p = d3.selectAll("p");
d3.selectAll(document.links).style("color", "red");
```

### d3.selection()

Returns the root selection (`document.documentElement`). Can be used to test for selections (`instanceof d3.selection`) or extend the prototype.

```js
const root = d3.selection();

// Extend prototype
d3.selection.prototype.checked = function(value) {
  return arguments.length < 1
      ? this.property("checked")
      : this.property("checked", !!value);
};
d3.selectAll("input[type=checkbox]").checked(true);
```

## Subselection Methods

### selection.select(selector)

For each selected element, selects the first descendant matching the selector. If selector is a function, it is evaluated for each element with `(d, i, nodes)` signature.

```js
const b = d3.selectAll("p").select("b"); // first <b> in every <p>

// Function-based selection
const previous = d3.selectAll("p").select(function() {
  return this.previousElementSibling;
});
```

### selection.selectAll(selector)

For each selected element, selects all descendants matching the selector.

```js
const b = d3.selectAll("p").selectAll("b"); // all <b> in every <p>
```

### selection.selectChild([selector]) / selectChildren([selector])

Selects direct children only. If selector is omitted, selects all children.

```js
selection.selectChild("rect.active");
selection.selectChildren();
```

## Selection Chaining Convention

Methods that return the current selection (like `attr`, `style`) use 4-space indent. Methods that return a new selection (like `append`, `select`) use 2-space indent. This reveals changes of context:

```js
d3.select("body")
  .append("svg")
    .attr("width", 960)
    .attr("height", 500)
  .append("g")
    .attr("transform", "translate(20,20)")
  .append("rect")
    .attr("width", 920)
    .attr("height", 460);
```

## Namespace Support

D3 selections support SVG and HTML namespaces. Use `d3.namespace()` for prefixed names:

```js
const ns = d3.namespace("http://www.w3.org/1999/xhtml");
```
