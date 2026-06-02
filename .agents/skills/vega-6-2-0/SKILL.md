---
name: vega-6-2-0
description: >
  Vega 6.2.0 — declarative visualization grammar for creating interactive charts
  in JSON. Define data, scales, marks, axes, legends, signals, and interactions
  to render HTML5 Canvas or SVG visualizations. Use when authoring Vega
  specifications, building interactive data visualizations, or working with
  Vega's JSON-based visualization grammar.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - vega
  - visualization
  - charts
  - grammar-of-graphics
  - data-viz
  - interactive-graphics
  - json-spec
category: library
external_references:
  - https://www.npmjs.com/package/vega/v/6.2.0
  - https://github.com/vega/vega/tree/v6.2.0
---

# Vega 6.2.0

## Overview

**Vega** is a *visualization grammar* — a declarative, JSON-based format for creating, saving, and sharing interactive visualization designs. With Vega you describe data visualizations as structured JSON objects and render them using either HTML5 Canvas or SVG.

Vega specifications define data sources, scales, marks (visual encodings), axes, legends, signals (dynamic variables), event streams (user interactions), and transforms (data processing). The Vega runtime compiles the specification into a dataflow graph, evaluates it, and renders the result.

Key capabilities:
- **Declarative JSON specs** — describe visualizations without imperative drawing code
- **Canvas and SVG rendering** — choose renderer at runtime
- **Rich interactivity** — signals, event streams, triggers for dynamic behavior
- **Data transforms** — filter, aggregate, bin, stack, project, and more
- **12 mark types** — rect, line, area, symbol, arc, text, group, path, rule, shape, image, trail
- **10+ scale types** — linear, log, pow, sqrt, time, ordinal, band, point, quantile, threshold
- **50+ transforms** — aggregate, bin, filter, stack, force-directed layout, treemap, Voronoi, word cloud
- **d3-scale integration** — leverages D3's scale library internally

For documentation, tutorials, and examples, see the [Vega website](https://vega.github.io/vega). Try Vega in the online [Vega Editor](https://vega.github.io/editor/#/examples/vega/bar-chart).

## When to Use

- Authoring interactive data visualizations using a declarative JSON specification
- Creating charts that need rich interactivity (tooltips, brushing, selection)
- Working with Vega-Lite's output and needing to hand-edit the compiled Vega spec
- Building custom visualization components in web applications or Node.js
- Generating reports with Canvas or SVG output from data
- Creating geographic visualizations with cartographic projections

## Core Concepts

### Specification Structure

Every Vega specification is a JSON object. The minimal outline:

```json
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "description": "A simple bar chart",
  "width": 500,
  "height": 200,
  "padding": 5,
  "autosize": "pad",

  "signals": [],
  "data": [],
  "scales": [],
  "projections": [],
  "axes": [],
  "legends": [],
  "marks": []
}
```

Top-level properties: `$schema`, `description`, `background`, `width`, `height`, `padding`, `autosize`, `config`, `signals`, `data`, `scales`, `projections`, `axes`, `legends`, `title`, `marks`, `encode`, `usermeta`.

### Data Model

Vega uses a **tabular data model** — arrays of JavaScript objects (records/rows with named fields). Data can be specified inline (`values`), loaded from a URL, or derived from other datasets (`source`). Vega supports JSON, CSV, TSV, DSV, and TopoJSON formats.

### Visualization Grammar Layers

1. **Data** — source definitions and transforms that process raw data
2. **Scales** — map data values to visual values (pixels, colors, sizes)
3. **Marks** — graphical primitives (rectangles, lines, symbols, text) with visual encodings
4. **Axes & Legends** — coordinate axes and scale legends for interpretation
5. **Signals** — dynamic variables that parameterize the visualization
6. **Event Streams & Triggers** — user interaction handlers that update signals

### Rendering

Vega supports two renderers:
- **Canvas** (default) — faster for large datasets
- **SVG** — better for accessibility, interactivity, and DOM integration

### Autosize Modes

| Mode | Behavior |
|------|----------|
| `pad` (default) | Expand view to fit all content including axes/legends |
| `fit` | Shrink plot area to fit within specified dimensions |
| `none` | Fixed size from width/height/padding only |
| `fit-x` / `fit-y` | Adjust only one dimension |

## Advanced Topics

**Specification & Data**: Top-level properties, autosize, data sources and formats → [Specification & Data](reference/01-specification-and-data.md)
**Scales & Projections**: All scale types (linear, log, time, ordinal, etc.), domains, ranges, cartographic projections → [Scales & Projections](reference/02-scales-and-projections.md)
**Marks & Encoding**: 12 mark types, encode sets (enter/update/exit/hover), visual encoding channels → [Marks & Encoding](reference/03-marks-and-encoding.md)
**Transforms**: 50+ transforms — basic, geographic, layout, hierarchy, cross-filter → [Transforms](reference/04-transforms.md)
**Signals & Events**: Signal definitions, event streams, handlers, triggers for interactivity → [Signals & Events](reference/05-signals-and-events.md)
**Expressions**: Expression language, bound variables, math/string/date/color functions → [Expressions](reference/06-expressions.md)
**Axes, Legends & Title**: Axis configuration, legend properties, title options → [Axes, Legends & Title](reference/07-axes-legends-title.md)
**Configuration & Theming**: Config object for global defaults, styles, locale → [Configuration & Theming](reference/08-configuration-and-theming.md)
**API & Embedding**: View API, parse/render methods, embedding in web pages and Node.js → [API & Embedding](reference/09-api-and-embedding.md)
**Usage Examples**: Bar chart, line chart, scatterplot, interactive tooltip examples → [Usage Examples](reference/10-usage-examples.md)
