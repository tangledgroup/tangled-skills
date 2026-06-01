---
name: vega-lite-6-4-3
description: >-
  Complete toolkit for Vega-Lite 6.4.3 providing a declarative JSON grammar
  for creating interactive data visualizations including bar charts, line
  charts, scatter plots, area charts, heatmaps, geographic maps, and
  multi-view dashboards with faceting, layering, concatenation, and
  repeat operators. Use when building Vega-Lite specifications, encoding
  data to visual marks, composing layered or faceted views, adding
  interactivity via selections and parameters, or embedding
  visualizations in web applications.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - vega-lite
  - visualization
  - grammar-of-graphics
  - json-spec
  - charts
  - data-viz
  - interactive
category: library
external_references:
  - https://vega.github.io/vega-lite/
  - https://github.com/vega/vega-lite/tree/main/examples/specs
  - https://github.com/vega/vega-lite/tree/main/examples/specs/normalized
---

# Vega-Lite 6.4.3

## Overview

Vega-Lite is a high-level grammar of interactive graphics. It provides a
concise, declarative JSON syntax to create visualizations by mapping data
fields to properties of graphical marks (bars, lines, points, etc.). The
Vega-Lite compiler automatically produces axes, legends, and scales based
on carefully designed default rules. Specifications compile to lower-level
[Vega](https://vega.github.io/vega/) specifications for rendering.

A Vega-Lite spec follows this core pattern:

```
data → transform → mark → encoding
```

## When to Use

- Creating bar, line, scatter, area, pie, or heatmap charts from JSON specs
- Building dashboards with faceting, layering, or concatenation
- Adding interactivity via selections (brush, hover, click) and parameters
- Creating geographic maps with projections (choropleth, dot maps)
- Embedding visualizations in web applications using `vega-embed`
- Designing statistical charts: box plots, error bars, density plots
- Transforming data inline: aggregate, bin, filter, fold, pivot, window

## Core Concepts

**Grammar of Graphics**: Visualizations are built from data transformed into
marks with encoding mappings. The compiler infers scales, axes, and legends.

**Spec Types**: Single-view (one mark), layered (`layer`), faceted
(`facet`/`row`/`column`), concatenated (`hconcat`/`vconcat`/`concat`),
and repeated (`repeat`).

**Data Types**: `quantitative` (numbers), `temporal` (dates),
`ordinal` (ordered categories), `nominal` (un-ordered categories),
`geojson` (geographic features).

**Encoding Channels**: Position (`x`, `y`, `theta`, `radius`), mark
properties (`color`, `size`, `shape`, `opacity`), text/tooltip,
facet channels (`row`, `column`, `facet`).

## Usage Examples

### Minimal Bar Chart

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": {
    "values": [
      {"category": "A", "value": 28},
      {"category": "B", "value": 55},
      {"category": "C", "value": 43}
    ]
  },
  "mark": "bar",
  "encoding": {
    "x": {"field": "category", "type": "nominal"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

### Line Chart with Time Series

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": {"url": "data/stocks.csv"},
  "transform": [{"filter": "datum.symbol==='GOOG'"}],
  "mark": "line",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "price", "type": "quantitative"}
  }
}
```

### Scatter Plot

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": {"url": "data/cars.json"},
  "mark": "point",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

### Stacked Bar Chart

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": {"url": "data/seattle-weather.csv"},
  "mark": "bar",
  "encoding": {
    "x": {"timeUnit": "month", "field": "date", "type": "ordinal"},
    "y": {"aggregate": "count", "type": "quantitative"},
    "color": {"field": "weather", "type": "nominal"}
  }
}
```

### Pie Chart

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": {
    "values": [
      {"category": "A", "value": 4},
      {"category": "B", "value": 6},
      {"category": "C", "value": 10}
    ]
  },
  "mark": "arc",
  "encoding": {
    "theta": {"field": "value", "type": "quantitative"},
    "color": {"field": "category", "type": "nominal"}
  }
}
```

### Layered Chart (Bars with Labels)

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": {
    "values": [
      {"a": "A", "b": 28},
      {"a": "B", "b": 55},
      {"a": "C", "b": 43}
    ]
  },
  "encoding": {
    "y": {"field": "a", "type": "nominal"},
    "x": {"field": "b", "type": "quantitative", "scale": {"domain": [0, 60]}}
  },
  "layer": [
    {"mark": "bar"},
    {
      "mark": {"type": "text", "align": "left", "baseline": "middle", "dx": 3},
      "encoding": {"text": {"field": "b", "type": "quantitative"}}
    }
  ]
}
```

### Faceted (Trellis) Chart

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": {"url": "data/movies.json"},
  "mark": "point",
  "encoding": {
    "facet": {"field": "MPAA Rating", "type": "ordinal", "columns": 2},
    "x": {"field": "Worldwide Gross", "type": "quantitative"},
    "y": {"field": "US DVD Sales", "type": "quantitative"}
  }
}
```

### Interactive Brush Highlight

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "data": {"url": "data/cars.json"},
  "params": [
    {"name": "brush", "select": "interval",
     "value": {"x": [55, 160], "y": [13, 37]}}
  ],
  "mark": "point",
  "encoding": {
    "x": {"field": "Horsepower", "type": "quantitative"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"},
    "color": {
      "condition": {"param": "brush", "field": "Cylinders", "type": "ordinal"},
      "value": "grey"
    }
  }
}
```

### Embedding in a Web Page

```html
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
<div id="vis"></div>
<script>
  var spec = { /* Vega-Lite spec object */ };
  vegaEmbed("#vis", spec);
</script>
```

## Advanced Topics

**Spec and Data Sources**: Inline values, URLs, named sources, data generators, formats → [Spec and Data](reference/01-spec-and-data.md)

**Mark Types**: All 18 marks including composite marks (boxplot, errorbar, errorband) with properties → [Marks](reference/02-marks.md)

**Encoding Channels**: Position, polar, geographic, mark property, text, tooltip, facet channels and channel definitions → [Encoding Channels](reference/03-encoding-channels.md)

**Data Types and Scales**: Quantitative/temporal/ordinal/nominal types, scale types, domain/range, band position → [Data Types and Scales](reference/04-data-types-and-scales.md)

**Transforms**: All 20 transforms — aggregate, bin, calculate, density, filter, fold, impute, joinaggregate, loess, lookup, pivot, quantile, regression, sample, stack, timeunit, window → [Transforms](reference/05-transforms.md)

**View Composition**: Layer, facet, concat (hconcat/vconcat), repeat, resolve for independent/shared scales → [View Composition](reference/06-view-composition.md)

**Parameters and Interactivity**: Value/expr parameters, point/interval selections, bind, conditional encodings → [Parameters and Interactivity](reference/07-parameters-and-interactivity.md)

**Styling and Configuration**: Axis, legend, header, title, format, config, style, gradient, invalid data handling → [Styling and Config](reference/08-styling-and-config.md)

**Chart Recipes by Type**: Complete example specs organized by chart category — bar, histogram, scatter, line, area, circular, heatmap, composite marks, layered, multi-view, maps, interactive, advanced calculations → [Charts by Type](reference/09-charts-by-type.md)
