---
name: d3-7-9-0
description: Complete toolkit for D3.js 7.9.0, the JavaScript library for bespoke data-driven documents providing SVG and Canvas-based visualizations with scales, axes, shapes, transitions, geo-projections, force simulations, hierarchy layouts, array utilities, and color interpolation. Use when building custom interactive charts, geographic maps, network diagrams, animated data visualizations, or implementing low-level graphics with direct DOM control instead of charting-library abstractions.
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
  - https://observablehq.com/@d3/gallery
---

# D3.js 7.9.0

## Overview

D3 (Data-Driven Documents) is a free, open-source JavaScript library for **bespoke data visualization** using web standards. Unlike charting libraries with built-in "chart" abstractions, D3 provides low-level primitives — scales, axes, shapes, transitions, and selections — that you compose into custom visualizations. It works directly with SVG, Canvas, and HTML elements, giving complete control over every pixel.

D3 is a suite of 30+ discrete modules bundled for convenience. Each module can be used independently (e.g., `d3-array` for data manipulation without any rendering). Modules are organized into five categories:

| Category | Modules |
|----------|--------|
| **Selection** | d3-selection, d3-transition, d3-dispatch |
| **Visualization** | d3-axis, d3-chord, d3-color, d3-contour, d3-delaunay, d3-force, d3-geo, d3-hierarchy, d3-interpolate, d3-path, d3-polygon, d3-quadtree, d3-scale, d3-scale-chromatic, d3-shape |
| **Animation** | d3-ease, d3-timer, d3-transition |
| **Interaction** | d3-brush, d3-dispatch, d3-drag, d3-zoom |
| **Data** | d3-array, d3-dsv, d3-fetch, d3-format, d3-random, d3-time, d3-time-format |

**Key philosophy:** D3 makes things *possible*, not necessarily *easy*. It trades convenience for flexibility — you write more code but have total control over the output.

### D3 vs. Observable Plot

D3's high-level sister library is **[Observable Plot](https://observablehq.com/plot/)**. Whereas a histogram in D3 might require 50 lines of code, Plot can do it in one! Plot's concise yet expressive API lets you focus more on analyzing and visualizing data instead of web development. You can even **combine Plot and D3** for the best of both — use Plot for common charts and D3 for bespoke customizations.

| When to Use | Recommendation |
|-------------|---------------|
| Private dashboard, one-off analysis | Observable Plot |
| Media-quality bespoke visualization (NYT, The Pudding) | D3 |
| Time-constrained project | Observable Plot |
| Need full control over every visual detail | D3 |
| Combining standard + custom charts | Plot + D3 together |

### D3 Works with the Web

D3 doesn't introduce a new graphical representation — it works directly with web standards (SVG, Canvas, DOM). This brings many benefits:
- **External stylesheets** can alter chart appearance, including media queries for responsive design or dark mode
- **Browser debugger and element inspector** work natively to review what your code is doing
- **Synchronous, imperative evaluation** — calling `selection.attr()` immediately mutates the DOM — makes debugging easier than frameworks with complex async runtimes
- **Framework compatible** — D3 can be paired with React, Vue, Svelte, and other web frameworks

### D3 for Bespoke Visualization

D3 is the tool of choice for media organizations like The New York Times or The Pudding, where a single graphic may be seen by millions and teams collaborate to advance visual communication. D3 is **overkill for throwing together a private dashboard** — many whizbang examples took immense effort to implement.

### D3 for Dynamic Visualization

D3's most novel concept is the **data join**: given a set of data and a set of DOM elements, the data join allows you to apply separate operations for entering, updating, and exiting elements. The data join exists so that you can control exactly what happens when your data changes and update the display in response. This direct control allows extremely performant updates — only touching the elements and attributes that need changing, without diffing the DOM — and smooth animated transitions between states.

## When to Use

- Building **bespoke interactive visualizations** that don't fit standard chart templates (media-quality graphics)
- Creating **geographic maps** with projections, graticules, GeoJSON/TopoJSON, vector tiles, raster tiles
- Implementing **force-directed graphs** for network visualization with physics simulations
- Building **animated transitions** between data views with object constancy
- Working with **hierarchical data** (treemaps, sunbursts, circle packing, trees, cluster dendrograms)
- Needing **scales** for mapping data domains to visual ranges (linear, time, ordinal, log, pow, symlog, sequential, diverging)
- Creating **axes** for standard chart reference lines with grid-line styling
- Performing **data transformations** (grouping, binning, sorting, summarizing, bisecting)
- Building **SVG/Canvas graphics** with direct DOM control and CSS integration
- Implementing **drag, brush, and zoom** interactions with touch support
- Generating **contour plots** (marching squares, kernel density estimation)
- Creating **Delaunay triangulations** and **Voronoi diagrams**
- Computing **color interpolations** in Lab, HCL, RGB, Cubehelix color spaces
- Working with **chord diagrams** and **ribbon/arrow rendering**
- Formatting **numbers, dates, and CSV/TSV data** for display
- **Combine with Observable Plot** for common charts, then D3 for custom touches

## Core Concepts

### The Data Join Pattern

The fundamental D3 pattern for binding data to DOM elements:

```javascript
// Select all <rect> elements, bind data, enter+update+exit
const rects = svg.selectAll("rect")
    .data(data)
    .join(
        enter => enter.append("rect"),       // New elements
        update => update,                    // Existing elements
        exit => exit.remove()                // Removed elements
    )
    .attr("x", (d, i) => x(i))
    .attr("y", d => y(d.value))
    .attr("width", bandScale.bandwidth())
    .attr("height", d => height - y(d.value));
```

### Scales

Scales map input domains to output ranges. Key types:

| Scale | Use Case | Import |
|-------|----------|--------|
| `scaleLinear` | Continuous numeric data | `d3.scaleLinear()` |
| `scaleTime` / `scaleUtc` | Date/time data | `d3.scaleTime()` |
| `scaleOrdinal` | Categorical/discrete data | `d3.scaleOrdinal()` |
| `scaleBand` | Bar charts with spacing | `d3.scaleBand()` |
| `scalePoint` | Points within band range | `d3.scalePoint()` |
| `scalePow` / `scaleSqrt` | Power/square root transforms | `d3.scalePow().exponent(2)` |
| `scaleLog` | Logarithmic data | `d3.scaleLog().base(10)` |
| `scaleSequential` | Color scales for heatmaps | `d3.scaleSequential(d3.interpolateViridis)` |
| `scaleDiverging` | Diverging color scales | `d3.scaleDiverging(d3.interpolateRdBu)` |
| `scaleQuantize` / `scaleQuantile` | Quantized/quantile scales | `d3.scaleQuantize()` |
| `scaleThreshold` | Threshold-based mapping | `d3.scaleThreshold([0, 50, 100], ["low", "med", "high"])` |

**Example — Bar chart scales:**
```javascript
const x = d3.scaleBand()
    .domain(data.map(d => d.category))
    .range([marginLeft, width - marginRight])
    .padding(0.1);

const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.value)])
    .range([height - marginBottom, marginTop]);

const color = d3.scaleOrdinal()
    .domain(categories)
    .range(d3.schemeTableau10);
```

### Axes

Axes generate standard reference lines and labels for scales:

```javascript
const xAxis = d3.axisBottom(x)
    .tickSize(-height + marginTop + marginBottom)  // Grid lines
    .tickPadding(8);

svg.append("g")
    .attr("transform", `translate(0,${height - marginBottom})`)
    .call(xAxis);

// Style the axis
svg.select(".domain").remove();  // Hide axis line
svg.selectAll(".tick line")
    .attr("stroke-opacity", 0.1);
```

### Shapes (d3-shape)

D3 provides path generators for common shapes:

```javascript
// Line chart
const line = d3.line()
    .x(d => x(d.date))
    .y(d => y(d.value))
    .curve(d3.curveMonotoneY);

svg.append("path")
    .datum(data)
    .attr("d", line)
    .attr("fill", "none")
    .attr("stroke", "steelblue");

// Area chart
const area = d3.area()
    .x(d => x(d.date))
    .y0(height - marginBottom)
    .y1(d => y(d.value))
    .curve(d3.curveMonotoneY);

svg.append("path").datum(data).attr("d", area);

// Pie chart
const pie = d3.pie().value(d => d.value);
const arc = d3.arc().innerRadius(50).outerRadius(150);
const arcs = pie(data);

// Stack chart
const stack = d3.stack().keys(keys).order(d3.stackOrderAscending);
const stacked = stack(data);
```

### Color Schemes (d3-scale-chromatic)

| Category | Interpolators |
|----------|--------------|
| Categorical | `schemeCategory10`, `schemeTableau10`, `schemeObservable10`, `schemeAccent`, `schemePaired` |
| Sequential | `interpolateViridis`, `interpolatePlasma`, `interpolateInferno`, `interpolateMagma`, `interpolateCividis`, `interpolateBlues`, `interpolateGreens`, `interpolateOranges` |
| Diverging | `interpolateRdBu`, `interpolateRdYlBu`, `interpolateBrBG`, `interpolatePiYG`, `interpolateSpectral` |
| Cyclical | `interpolateRainbow`, `interpolateSinebow` |

```javascript
const color = d3.scaleSequential(d3.interpolateViridis)
    .domain([0, d3.max(data, d => d.value)]);

// Or for categorical:
const color = d3.scaleOrdinal(d3.schemeTableau10);
```

## Installation / Setup

### CDN (ES Module — Recommended)
```html
<script type="module">
  import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7.9.0/+esm";
</script>
```

### CDN (UMD Bundle)
```html
<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
```

### npm / yarn / pnpm
```bash
npm install d3
# or specific modules:
npm install d3-array d3-scale d3-selection d3-shape d3-axis
```

```javascript
import * as d3 from "d3";
// Or individual modules:
import { scaleLinear, axisBottom } from "d3";
import { mean, median } from "d3-array";
```

## Usage Examples

### Basic Bar Chart
```html
<div id="chart"></div>
<script type="module">
  import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7.9.0/+esm";

  const data = [
    {category: "A", value: 30},
    {category: "B", value: 45},
    {category: "C", value: 20}
  ];

  const width = 640, height = 400;
  const marginTop = 20, marginRight = 20, marginBottom = 30, marginLeft = 40;

  const x = d3.scaleBand()
      .domain(data.map(d => d.category))
      .range([marginLeft, width - marginRight])
      .padding(0.1);

  const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.value)])
      .range([height - marginBottom, marginTop]);

  const svg = d3.create("svg")
      .attr("width", width)
      .attr("height", height);

  svg.append("g")
      .attr("transform", `translate(0,${height - marginBottom})`)
      .call(d3.axisBottom(x));

  svg.append("g")
      .attr("transform", `translate(${marginLeft},0)`)
      .call(d3.axisLeft(y));

  svg.selectAll("rect")
      .data(data)
      .join("rect")
      .attr("x", d => x(d.category))
      .attr("y", d => y(d.value))
      .attr("width", x.bandwidth())
      .attr("height", d => height - marginBottom - y(d.value))
      .attr("fill", "steelblue");

  document.getElementById("chart").appendChild(svg.node());
</script>
```

### Line Chart with Missing Data
```javascript
const line = d3.line()
    .defined(d => d.value !== null)  // Skip nulls
    .x(d => x(d.date))
    .y(d => y(d.value))
    .curve(d3.curveMonotoneY);

svg.append("path")
    .datum(data)
    .attr("d", line)
    .attr("fill", "none")
    .attr("stroke", "steelblue")
    .attr("stroke-width", 1.5);
```

### Force-Directed Graph
```javascript
const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).distance(100))
    .force("charge", d3.forceManyBody().strength(-30))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .on("tick", () => {
      links.attr("x2", d => d.target.x).attr("y2", d => d.target.y);
      nodes.attr("cx", d => d.x).attr("cy", d => d.y);
    });
```

### Zoomable Area Chart
```javascript
const zoom = d3.zoom()
    .scaleExtent([1, 10])
    .translateExtent([[-marginLeft, -marginTop], [width, height]])
    .on("zoom", (event) => {
      const transformedX = event.transform.rescaleX(x);
      svg.select(".x-axis").call(d3.axisBottom(transformedX));
      path.attr("d", area.x(d => transformedX(d.date)));
    });

svg.call(zoom);
```

### Choropleth Map
```javascript
const projection = d3.geoAlbersUsa()
    .fitSize([width, height], geojson);

const path = d3.geoPath(projection);

const color = d3.scaleSequential(d3.interpolateYlOrRd)
    .domain([0, d3.max(data, d => d.value)]);

svg.selectAll("path")
    .data(geojson.features)
    .join("path")
    .attr("d", path)
    .attr("fill", d => color(getValue(d)))
    .attr("stroke", "#fff");
```

## Advanced Topics

### Transitions and Animation
D3 provides powerful transition system with object constancy — elements maintain identity across data changes:
- `selection.transition()` — create a transition
- `.duration()`, `.delay()`, `.ease()` — control timing
- `d3.easeBack`, `d3.easeBounce`, `d3.easeElastic` — easing functions
- `transition.attrTween()`, `styleTween()`, `textTween()` — custom tweened attributes

### Geographic Projections
D3 supports dozens of map projections:
- **Cylindrical**: Mercator, Equirectangular, TransverseMercator, EqualEarth, NaturalEarth1
- **Conic**: Albers (usa), ConicConformal, ConicEqualArea, ConicEquidistant
- **Azimuthal**: AzimuthalEqualArea, AzimuthalEquidistant, Gnomonic, Orthographic, Stereographic

### Hierarchy Layouts
- `d3.hierarchy()` — create hierarchy from nested/flat data
- `d3.tree()` — tidy tree layout
- `d3.cluster()` — cluster dendrogram
- `d3.partition()` — partition diagram
- `d3.pack()` / `d3.packSiblings()` / `d3.packEnclose()` — circle packing
- `d3.treemap()` — treemap with squarify, binary, dice, slice-dice layouts
- `d3.stratify()` — convert flat table to hierarchy

### Data Manipulation (d3-array)
- **Summarizing**: `d3.sum`, `d3.mean`, `d3.median`, `d3.min`, `d3.max`, `d3.extent`, `d3.quantile`, `d3.variance`, `d3.deviation`, `d3.mode`, `d3.count`
- **Floating-point precision**: `d3.fsum()`, `d3.fcumsum()`
- **Grouping**: `d3.group()`, `d3.groups()`, `d3.rollup()`, `d3.rollups()`, `d3.index()`, `d3.indexes()`, `d3.flatGroup()`, `d3.flatRollup()`, `d3.groupSort()`
- **Sorting**: `d3.sort()`, `d3.shuffle()`, `d3.shuffler()`, `d3.permute()`, `d3.quickselect()`
- **Binning**: `d3.bin()` with `thresholdFreedmanDiaconis`, `thresholdScott`, `thresholdSturges`
- **Bisecting**: `d3.bisect()`, `d3.bisectLeft/Right/Center()`, `bisector()` for object arrays
- **Sets**: `d3.union()`, `d3.intersection()`, `d3.difference()`, `d3.subset()`, `d3.superset()`, `d3.disjoint()`
- **Transforming**: `d3.cross()`, `d3.merge()`, `d3.pairs()`, `d3.transpose()`, `d3.zip()`
- **Ticks/Range**: `d3.ticks()`, `d3.tickIncrement/Step()`, `d3.nice()`, `d3.range()`
- **Interning**: `d3.InternMap`, `d3.InternSet`
- **Blurring**: `d3.blur()`, `d3.blur2()`, `d3.blurImage()`

### Data I/O (d3-fetch, d3-dsv, d3-format)
- **Fetching**: `d3.csv()`, `d3.json()`, `d3.text()`, `d3.xml()`, `d3.svg()`, `d3.html()`, `d3.image()`, `d3.buffer()`
- **CSV/TSV**: `d3.csvParse()`, `d3.tsvParse()`, `d3.dsvFormat()`, `d3.autoType()`
- **Number formatting**: `d3.format()`, `d3.formatPrefix()`, locale-aware formatting
- **Random distributions**: `d3.randomUniform/Normal/Exponential/Beta/Gamma/Poisson/Int/Lcg()`

### Time (d3-time, d3-time-format)
- **Intervals**: `d3.timeMillisecond` through `d3.timeYear`, `d3.timeWeek` (Sunday-based)
- **Formatting**: `d3.timeFormat()`, `d3.timeParse()`, `d3.utcFormat()`, `d3.utcParse()`
- **Tick generation**: `d3.timeTicks()`, `d3.utcTicks()`
- **Custom intervals**: `d3.timeInterval`, interval filtering and range

### Color (d3-color, d3-interpolate)
- **Color spaces**: `d3.rgb()`, `d3.hsl()`, `d3.lab()`, `d3.hcl()`, `d3.cubehelix()`
- **Color operations**: `.brighter()`, `.darker()`, `.opacity()`, `.displayable()`
- **Interpolation**: `d3.interpolate()`, `d3.interpolateRgb/Hcl/Lab/Hsl/Cubehelix()`
- **Color space long-form**: `interpolateHclLong()`, `interpolateHslLong()`, `interpolateCubehelixLong()`
- **Transform interpolation**: `d3.interpolateTransformSvg()`, `d3.interpolateTransformCss()`
- **Zoom interpolation**: `d3.interpolateZoom()`
- **Piecewise**: `d3.piecewise(interpolator, values)`

### Force Simulation (d3-force)
- **Simulation**: `d3.forceSimulation(nodes)` with `.alpha()`, `.tick()`, `.stop()`, `.restart()`
- **Link force**: `d3.forceLink(links).distance().strength().id()`
- **Many-body force**: `d3.forceManyBody().strength().distanceMin().distanceMax().theta()`
- **Position forces**: `d3.forceX()`, `d3.forceY()`, `d3.forceRadial()`
- **Center force**: `d3.forceCenter(x, y).strength()`
- **Collide force**: `d3.forceCollide().radius().strength().iterations()`
- **Alpha control**: `.alpha()`, `.alphaDecay()`, `.alphaMin()`, `.alphaTarget()`

### Contour Plots (d3-contour)
- **Contour polygons**: `d3.contourDensity().size().bandwidth().thresholds().contours()`
- **Marching squares**: Renders contour lines from raster/grid data
- **Density estimation**: Kernel density with Gaussian kernel

### Chord Diagrams (d3-chord)
- **Chords**: `d3.chord().padAngle().sortChords()`. Computes layout for matrix data
- **Ribbons**: `d3.ribbon()` with `source`, `target`, `radius`, `padAngle` for SVG path generation
- **Directed chords**: `d3.chordDirected()` for asymmetric relationships
- **Transpose**: `d3.chordTranspose(matrix)`

### Delaunay & Voronoi (d3-delaunay)
- **Delaunay triangulation**: `d3.Delaunay.from(data, x, y)` or `d3.delaunay(points)`
- **Methods**: `.hull()`, `.triangles()`, `.neighbors()`, `.find(x, y)`, `.render()`
- **Voronoi diagrams**: `delaunay.voronoi(extent)` with `.cellPolygon()`, `.contains()`, `.renderCell()`
- **Use cases**: Nearest-neighbor search, spatial partitioning, mesh generation

### Interaction
- **Zoom** (`d3-zoom`): Pan and zoom with wheel, touch, and mouse events. `zoomTransform()`, `transform.rescaleX()`, `scaleBy/scaleTo/translateBy`
- **Drag** (`d3-drag`): Drag behavior with subject customization, `dragEnable/dragDisable`, touch support
- **Brush** (`d3-brush`): 2D, X, and Y brush rectangles. `brushSelection()`, `brush.move()`
- **Events** (`d3-selection/events`): `selection.on()`, `d3.pointer()`, `d3.pointers()`, event delegation
- **Dispatch** (`d3-dispatch`): Event emitter pattern for custom events

### Animation Gallery Examples
D3's gallery includes 100+ examples across categories. Each example is forkable on Observable:

| Category | Key Examples (Observable) |
|----------|-------------|
| **Bars** | Bar chart, horizontal bar, stacked/normalized/diverging bars, grouped bar, Marimekko chart, calendar, timeline, electricity usage, revenue by music format |
| **Lines** | Line chart (with missing data), multi-line, change line, slope chart (2 examples), Marey's trains, candlestick, variable-color line, gradient encoding, threshold encoding, parallel coordinates |
| **Areas** | Area chart (with missing data), stacked area, normalized stacked area, streamgraph, difference chart, band chart, ridgeline (joy) plot, horizon chart (standard + realtime) |
| **Dots** | Scatterplot, scatterplot with shapes, SPLOM, dot plot, global temperature trends, bubble map, spike map, bubble chart, beeswarm (+ mirrored), Hertzsprung–Russell diagram |
| **Radial** | Pie chart (+ update), donut chart, radial area chart, radial stacked bar chart (2 layouts) |
| **Hierarchies** | Treemap (+ cascaded + nested), circle packing (+ zoomable), indented tree, tidy tree (+ radial), cluster dendrogram (+ radial), sunburst (+ zoomable), icicle (+ zoomable), tangled tree, phylogenetic tree, force-directed tree |
| **Networks** | Force-directed graph (+ disjoint), mobile patent suits, arc diagram, Sankey diagram (+ 2 variants), hierarchical edge bundling (2 variants), chord diagram (3 variants) |
| **Maps** | Choropleth (+ US state + world + bivariate), world map, projection transitions/comparison, antimeridian cutting, Tissot's indicatrix, web mercator/raster/vector tiles, raster-vector, vector field, GeoTIFF contours, Voronoi airport maps, solar terminator/path, star map, cartogram |
| **Animation** | Animated treemap, temporal force-directed graph, connected scatterplot, wealth/health of nations, scatterplot tour, bar chart race, stacked-to-grouped bars, streamgraph transitions, smooth zooming, zoom to bounding box, orthographic-to-equirectangular, world tour, Walmart's growth, hierarchical bar chart, collapsible tree, sortable bar chart, pie chart update, arc tween |
| **Interaction** | Versor dragging, index chart, brushable scatterplot (+ matrix), pannable chart, zoomable area/bar charts, seamless zoomable map tiles |
| **Analysis** | Moving average, Bollinger bands, box plot, histogram, kernel density estimation, density contours, volcano contours, contours, hexbin (+ area + map), Q-Q plot, normal quantile plot, parallel sets |
| **Annotation** | Inline labels, directly labelling lines, line chart with tooltip, Voronoi labels, occlusion, graticule labels, styled axes, color legend |
| **Essays** | Explorable explanations: packEnclose, centerline labeling, methods of comparison, predator and prey |
| **Fun** | Polar clock, Stern–Brocot tree, Voronoi stippling, watercolor, PSR B1919+21, epicyclic gearing, owls to the max, tadpoles, word cloud, Spilhaus shoreline map, phases of the moon, color schemes |

## References

### Documentation
- Official documentation: https://d3js.org
- API index (all modules): https://d3js.org/api
- What is D3? (philosophy & guide): https://d3js.org/what-is-d3
- Getting started: https://d3js.org/getting-started
- Gallery of examples: https://observablehq.com/@d3/gallery
- Community: https://d3js.org/community

### Code & Resources
- GitHub repository: https://github.com/d3/d3
- Releases: https://github.com/d3/d3/releases
- Observable Plot (high-level alternative): https://observablehq.com/plot/
- License: ISC · Copyright 2010–2025 Mike Bostock and Observable, Inc.
