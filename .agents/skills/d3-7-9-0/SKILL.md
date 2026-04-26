---
name: d3-7-9-0
description: Complete toolkit for D3.js 7.9.0, the JavaScript library for bespoke data-driven documents providing SVG and Canvas-based visualizations with scales, axes, shapes, transitions, geo-projections, force simulations, hierarchy layouts, array utilities, color interpolation, formatting, and selection/joining APIs. Use when building custom interactive charts, geographic maps, network diagrams, animated data visualizations, or implementing low-level graphics with direct DOM control instead of charting-library abstractions.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "7.9.0"
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

# D3.js 7.9.0

## Overview

D3 (Data-Driven Documents) is a JavaScript library for producing dynamic, interactive data visualizations in the browser. Rather than providing high-level chart abstractions, D3 gives you low-level primitives to manipulate the DOM, SVG, and Canvas based on data. It works by binding arbitrary data to the Document Object Model, then applying data-driven transformations to create, update, and remove elements.

D3 is built as a collection of 26+ independent modules that work together but can be used separately. The library supports ES modules, UMD bundles, and CDN delivery. It requires no build tools — you can load it directly from a `<script>` tag or import individual modules with native ES module syntax.

D3 is developed by Observable, Inc., created by Mike Bostock, and released under the ISC license. The current version is 7.9.0 with over 111,000 GitHub stars.

## When to Use

- Building custom charts (line, bar, area, scatter, histogram, pie, donut) from scratch
- Creating geographic maps with spherical projections and GeoJSON data
- Implementing force-directed graph layouts and network diagrams
- Building interactive dashboards with zoom, pan, brush, and drag behaviors
- Generating SVG or Canvas visualizations with direct DOM control
- Creating animated transitions between visual states
- Working with hierarchical data (treemaps, pack layouts, dendrograms, sunburst)
- When you need more control than charting libraries like Chart.js or D3-based wrappers provide
- Building bespoke visual encodings that don't fit standard chart types

## Core Concepts

**Data Join**: The central pattern in D3. Data is bound to DOM elements using the `selection.data()` method, producing three groups: `enter` (new data with no element), `update` (existing data with existing element), and `exit` (existing element with no data). This pattern drives efficient DOM updates.

**Scales**: Functions that map input domains to output ranges. Scales translate abstract data values into visual properties — pixel positions, colors, sizes, opacities. D3 provides linear, logarithmic, power, ordinal, band, point, time, sequential, diverging, quantile, quantize, and threshold scales.

**Selections**: D3's DOM manipulation API, similar to jQuery but designed for data binding. Select elements with `d3.select()` or `d3.selectAll()`, then chain methods to modify attributes, styles, properties, and classes.

**Shapes**: Generators that produce SVG path data or Canvas drawing commands from data. Includes lines, areas, arcs, pies, stacks, links, and symbols. Shapes work with scales to position data visually.

**Transitions**: D3's animation system interpolates between current and target attribute values over time, with configurable duration, delay, and easing functions. Transitions can be chained and synchronized across multiple selections.

## Installation / Setup

D3 works in any JavaScript environment — browser, Node.js, Observable notebooks, or any framework.

**ES Module via CDN (recommended):**

```html
<script type="module">
  import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";
</script>
```

**UMD via CDN (global `d3` variable):**

```html
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
```

**npm installation:**

```bash
npm install d3
```

Then import in JavaScript:

```js
import * as d3 from "d3";
// Or import individual modules:
import { scaleLinear, line, select } from "d3";
```

**Observable notebooks**: D3 is available by default — no import needed. Just return the generated DOM element from a cell.

## Usage Examples

**Basic line chart with axes:**

```js
const width = 640, height = 400;
const marginTop = 20, marginRight = 20, marginBottom = 30, marginLeft = 40;

// Scales map data to pixel space
const x = d3.scaleUtc()
    .domain([new Date("2023-01-01"), new Date("2024-01-01")])
    .range([marginLeft, width - marginRight]);

const y = d3.scaleLinear()
    .domain([0, 100])
    .range([height - marginBottom, marginTop]);

// Create SVG container
const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height);

// Add axes
svg.append("g")
    .attr("transform", `translate(0,${height - marginBottom})`)
    .call(d3.axisBottom(x));

svg.append("g")
    .attr("transform", `translate(${marginLeft},0)`)
    .call(d3.axisLeft(y));
```

**Bar chart with data join pattern:**

```js
const data = [30, 80, 45, 60, 25];
const x = d3.scaleBand().domain(data.map((_, i) => i)).range([0, width]).padding(0.1);
const y = d3.scaleLinear().domain([0, d3.max(data)]).range([height, 0]);

svg.selectAll("rect")
    .data(data)
    .join("rect")
    .attr("x", (d, i) => x(i))
    .attr("y", d => y(d))
    .attr("width", x.bandwidth())
    .attr("height", d => height - y(d));
```

**Line chart with path generator:**

```js
const line = d3.line()
    .x((d, i) => x(i))
    .y(d => y(d))
    .curve(d3.curveMonotoneX);

svg.append("path")
    .datum(data)
    .attr("fill", "none")
    .attr("stroke", "steelblue")
    .attr("stroke-width", 1.5)
    .attr("d", line);
```

**Animated transitions:**

```js
svg.selectAll("circle")
    .data(data)
    .join("circle")
    .attr("cx", (d, i) => x(i))
    .attr("cy", d => y(d))
    .attr("r", 0)
    .transition()
    .duration(750)
    .delay((d, i) => i * 100)
    .attr("r", 5);
```

## Advanced Topics

**Selections and Data Joins**: The enter/update/exit pattern, joining data to elements, local variables, event handling → See [Selections and Data Joins](reference/01-selections-and-data-joins.md)

**Scales and Axes**: Linear, time, ordinal, band, point, log, pow, sequential, diverging, quantile, quantize, threshold scales and axis generation → See [Scales and Axes](reference/02-scales-and-axes.md)

**Shapes and Paths**: Line, area, arc, pie, stack, link, symbol generators, curves, radial variants, and the path API → See [Shapes and Paths](reference/03-shapes-and-paths.md)

**Geographic Maps**: Projections (azimuthal, conic, cylindrical), GeoJSON paths, spherical shapes, streams, and geographic math → See [Geographic Maps](reference/04-geographic-maps.md)

**Force Simulations**: Force-directed layouts with center, collide, link, many-body, and position forces → See [Force Simulations](reference/05-force-simulations.md)

**Hierarchy Layouts**: Tree, cluster, partition, pack, treemap layouts and the stratify operator → See [Hierarchy Layouts](reference/06-hierarchy-layouts.md)

**Transitions and Animation**: Transition selection, modification, timing, control flow, easing functions, and timers → See [Transitions and Animation](reference/07-transitions-and-animation.md)

**Interactions**: Zoom, drag, brush behaviors, and custom event dispatch → See [Interactions](reference/08-interactions.md)

**Data Utilities**: Array operations, grouping, statistics, sorting, CSV/TSV parsing, fetch, formatting, random, time, and color → See [Data Utilities](reference/09-data-utilities.md)
