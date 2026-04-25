---
name: d3-7-9-0
description: Complete toolkit for D3.js 7.9.0, the JavaScript library for bespoke data-driven documents providing SVG and Canvas-based visualizations with scales, axes, shapes, transitions, geo-projections, force simulations, hierarchy layouts, array utilities, color interpolation, formatting, and selection/joining APIs. Use when building custom interactive charts, geographic maps, network diagrams, animated data visualizations, or implementing low-level graphics with direct DOM control instead of charting-library abstractions.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.1"
tags:
  - JavaScript
  - visualization
  - SVG
  - Canvas
  - data-visualization
category: frontend
external_references:
  - https://d3js.org/what-is-d3
  - https://d3js.org/
  - https://d3js.org/api
  - https://d3js.org/getting-started
  - https://github.com/d3
  - https://observablehq.com/@d3/gallery
---
## Overview
**D3** (or **D3.js**) is a free, open-source JavaScript library for visualizing data. Its low-level approach built on web standards offers unparalleled flexibility in authoring dynamic, data-driven graphics. For over a decade D3 has powered groundbreaking and award-winning visualizations.

D3 was created by Mike Bostock in 2011. It was co-authored with Jeff Heer and Vadim Ogievetsky at Stanford. The name "D3" stands for *data-driven documents*, where *documents* refers to the Document Object Model (DOM).

D3 is not a charting library. It has no concept of "charts". Instead, it provides 30 discrete modules that you compose together: CSV parsers, time scales, linear scales, ordinal scales, color schemes, stack layouts, area shapes, axes, selections, transitions, force simulations, geo-projections, hierarchy layouts, and more. Each module works independently or together.

**D3 is for bespoke visualization.** It makes things possible, not necessarily easy. Use D3 when you need maximal expressiveness for custom interactive visualizations. For simpler needs, consider Observable Plot.

## When to Use
- Building custom, bespoke data visualizations that no charting library can produce
- Creating interactive charts with dynamic data updates (enter/update/exit pattern)
- Implementing geographic maps with D3 geo-projections
- Building force-directed network graphs
- Rendering hierarchical data as treemaps, sunburst diagrams, or tree layouts
- Performing low-level SVG/Canvas manipulation driven by data
- Working with React, Vue, Svelte, or vanilla HTML — D3 modules like scales and shapes don't touch the DOM at all
- Needing fine-grained control over every visual encoding (position, color, size, shape)

## Core Concepts
### The Data Join

D3's most novel concept. Given a set of data and a set of DOM elements, the data join applies separate operations for *entering*, *updating*, and *exiting* elements. This allows extremely performant updates — only touch elements that need changing.

```js
const circles = svg.selectAll("circle")
  .data(data)
  .join(
    enter => enter.append("circle").attr("r", 0),
    update => update,
    exit => exit.transition().attr("r", 0).remove()
  )
  .attr("cx", d => x(d.x))
  .attr("cy", d => y(d.y))
  .attr("fill", d => color(d.category));
```

### Selections

A selection is a set of DOM elements. Use `d3.select()` for the first match, `d3.selectAll()` for all matches. Chain methods to modify attributes, styles, classes, properties, text content, and more.

```js
const svg = d3.select("#chart")
  .attr("width", 640)
  .attr("height", 400);
```

### Scales

Scales map a dimension of abstract data to a visual representation. D3 provides linear, time, pow, log, symlog, ordinal, band, point, sequential, diverging, quantile, quantize, and threshold scales.

```js
const x = d3.scaleLinear()
  .domain([0, 10])
  .range([0, width]);
x(5); // 320 (if range is [0, 640])
```

### Shapes

Shape generators produce SVG path `d` attributes from data: lines, areas, arcs, pies, stacks, symbols. Each exposes accessors to control how input data maps to visual representation.

```js
const line = d3.line()
  .x(d => x(d.date))
  .y(d => y(d.value));
path.attr("d", line(data));
```

### Transitions

Transitions animate changes to the DOM. Instead of applying changes instantaneously, they smoothly interpolate from current state to target state over a given duration.

```js
circle.transition()
  .duration(750)
  .attr("r", 10);
```

### Axes

Axes document position encodings. Use `d3.axisBottom`, `d3.axisTop`, `d3.axisLeft`, `d3.axisRight` with a scale. Append as a `<g>` and transform to position.

```js
svg.append("g")
  .attr("transform", `translate(0,${height})`)
  .call(d3.axisBottom(x));
```

### Color

D3 provides color space representations (RGB, HSL, CIELAB, CIELUV, OKLCH, OKLab), named colors, and scale-chromatic schemes (categorical, cyclical, diverging, sequential).

```js
const color = d3.scaleSequential(d3.interpolateViridis)
  .domain([0, 100]);
color(50); // interpolated color
```

### Data Loading

D3 provides convenient parsing on top of Fetch: `d3.csv()`, `d3.tsv()`, `d3.json()`, `d3.text()`, `d3.xml()`, `d3.html()`. Auto-detects delimiters and parses types.

```js
const data = await d3.csv("data.csv");
// [{date: "2024-01-01", value: 42}, …]
```

## Installation / Setup
### CDN (Vanilla HTML)

ESM + CDN — recommended:
```html
<script type="module">
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
</script>
```

UMD bundle:
```html
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script>
// d3 is a global
</script>
```

### npm / yarn / pnpm

```bash
npm install d3
```

```js
import * as d3 from "d3";
// Or import specific modules:
import {select, selectAll} from "d3";
import {mean, median} from "d3-array";
```

### Framework Integration

- **React**: Use D3 modules that don't touch DOM (scales, shapes, arrays) declaratively. For DOM-manipulating modules (selections, transitions, axes), use `useRef` + `useEffect`.
- **Svelte**: Reactive statements (`$:`) pair nicely with D3 data joins for efficient updates.
- **Vue**: Similar pattern — compute D3 shapes/scales in computed properties, apply DOM changes in lifecycle hooks.

## Usage Examples
### Basic Line Chart

```js
const width = 640;
const height = 400;
const marginTop = 20, marginRight = 20, marginBottom = 30, marginLeft = 40;

const x = d3.scaleUtc()
  .domain([new Date("2023-01-01"), new Date("2024-01-01")])
  .range([marginLeft, width - marginRight]);

const y = d3.scaleLinear()
  .domain([0, 100])
  .range([height - marginBottom, marginTop]);

const svg = d3.create("svg")
  .attr("width", width)
  .attr("height", height);

// Axes
svg.append("g").attr("transform", `translate(0,${height - marginBottom})`)
  .call(d3.axisBottom(x));
svg.append("g").attr("transform", `translate(${marginLeft},0)`)
  .call(d3.axisLeft(y));

// Line
const line = d3.line()
  .x(d => x(d.date))
  .y(d => y(d.value));

svg.append("path")
  .datum(data)
  .attr("fill", "none")
  .attr("stroke", "steelblue")
  .attr("stroke-width", 1.5)
  .attr("d", line);
```

### Bar Chart with Data Join

```js
const bars = svg.selectAll(".bar")
  .data(data)
  .join(
    enter => enter.append("rect")
      .attr("class", "bar")
      .attr("x", d => x(d.name))
      .attr("width", x.bandwidth())
      .attr("y", height)
      .attr("height", 0),
    update => update,
    exit => exit.remove()
  )
  .transition().duration(750)
  .attr("y", d => y(d.value))
  .attr("height", d => height - y(d.value));
```

### Scatter Plot with Zoom

```js
const zoom = d3.zoom()
  .scaleExtent([1, 10])
  .translateExtent([[-10, -10], [width + 10, height + 10]])
  .on("zoom", ({transform}) => {
    g.attr("transform", transform);
  });

svg.call(zoom);
```

### Force-Directed Graph

```js
const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id))
  .force("charge", d3.forceManyBody())
  .force("center", d3.forceCenter(width / 2, height / 2));

simulation.on("tick", () => {
  link.attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  node.attr("cx", d => d.x).attr("cy", d => d.y);
});
```

### Treemap

```js
const root = d3.hierarchy(data)
  .sum(d => d.value)
  .sort((a, b) => b.value - a.value);

const treemap = d3.treemap()
  .size([width, height])
  .padding(3);

treemap(root);

svg.selectAll("rect")
  .data(root.leaves())
  .join("rect")
  .attr("x", d => d.x0)
  .attr("y", d => d.y0)
  .attr("width", d => d.x1 - d.x0)
  .attr("height", d => d.y1 - d.y0)
  .attr("fill", d => color(d.data.category));
```

## Advanced Topics
## Advanced Topics

- [Selection Selecting](reference/01-selection-selecting.md)
- [Selection Modifying](reference/02-selection-modifying.md)
- [Selection Joining](reference/03-selection-joining.md)
- [Selection Events](reference/04-selection-events.md)
- [Scales](reference/05-scales.md)
- [Axes](reference/06-axes.md)
- [Shapes](reference/07-shapes.md)
- [Transitions](reference/08-transitions.md)
- [Interaction](reference/09-interaction.md)
- [Data Processing](reference/10-data-processing.md)
- [Color](reference/11-color.md)
- [Force](reference/12-force.md)
- [Geo](reference/13-geo.md)
- [Hierarchy](reference/14-hierarchy.md)
- [Array Utilities](reference/15-array-utilities.md)
- [Additional Modules](reference/16-additional-modules.md)

