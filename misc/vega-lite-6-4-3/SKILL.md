---
name: vega-lite-6-4-3
description: 'Vega-Lite 6.4.3 — high-level grammar of interactive graphics. Generate, author, and debug Vega-Lite specifications for bar charts, line charts, scatterplots, area charts, maps, heatmaps, boxplots, faceted/layered/concatenated multi-view visualizations, and interactive selections. Compiles to Vega (lower-level visualization grammar). Use when generating interactive data visualizations or authoring Vega-Lite JSON specs.

  '
---

# Vega-Lite 6.4.3

## Overview

Vega-Lite is a high-level grammar for interactive graphics. It provides a concise JSON syntax for rapidly generating interactive multi-view visualizations. A Vega-Lite specification declares the data, mark type, and encoding channels; the compiler then produces a full [Vega](https://vega.github.io/vega) specification that renders the chart.

## Spec Structure

Every Vega-Lite spec is a JSON object. The simplest form is a **single-view** specification:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A simple bar chart",
  "data": { "url": "data/cars.json" },
  "mark": "bar",
  "encoding": {
    "x": { "field": "Origin", "type": "nominal" },
    "y": { "aggregate": "count", "type": "quantitative" }
  }
}
```

### Top-Level Properties

| Property | Description |
|----------|-------------|
| `$schema` | Schema URL (e.g., `https://vega.github.io/schema/vega-lite/v6.json`) |
| `background` | Canvas background color |
| `padding` | View padding in pixels or object `{top, right, bottom, left}` |
| `autosize` | Auto-sizing behavior: `"pad"`, `"fit"`, or `"none"` |
| `config` | Global configuration overrides (marks, axes, legends, etc.) |
| `usermeta` | Arbitrary metadata passed through to Vega |

### Common Properties (all spec types)

| Property | Description |
|----------|-------------|
| `name` | Unique name for the view (used in composition) |
| `description` | Human-readable description of the visualization |
| `title` | Title text, or object with `text`, `anchor`, `orient`, etc. |
| `data` | Data source(s) — inline values, URL, named, or generators |
| `transform` | Array of data transformation operations |
| `params` | Named parameters for interactivity (selections, expressions) |

### Single-View Properties

| Property | Description |
|----------|-------------|
| `mark` | Mark type string (`"bar"`, `"line"`, etc.) or mark definition object |
| `encoding` | Mapping of data fields to visual channels |
| `width` / `height` | View dimensions in pixels, `"container"`, or step-based |
| `view` | View background styling (fill, stroke, cornerRadius, cursor) |
| `projection` | Geographic projection settings for map views |

### Composition Types

Beyond single-view specs, Vega-Lite supports four composition operators:

- **`layer`** — overlay multiple marks on the same view
- **`facet`** — split a chart into a grid of small multiples
- **`concat`** (`hconcat`, `vconcat`, `concat`) — arrange views side-by-side or stacked
- **`repeat`** — repeat a spec across fields, rows, or columns

Composition specs add layout properties (`align`, `bounds`, `center`, `spacing`) and a `resolve` property for independent scales/axes/legends.

## Data Sources

Vega-Lite supports four ways to provide data:

### Inline Values

Embed data directly in the spec as an array of objects:

```json
{
  "data": {
    "values": [
      {"category": "A", "value": 28},
      {"category": "B", "value": 55}
    ]
  }
}
```

Primitive arrays (`[5, 3, 8]`) are auto-mapped to `{"data": value}` objects.

### URL

Load external data (JSON by default, CSV/TSV with format):

```json
{
  "data": {
    "url": "data/cars.json",
    "format": { "type": "json" }
  }
}
```

Format types: `json`, `csv`, `tsv`, `dsv` (custom delimiter), `topojson`.

### Named

Declare a named data source to be populated at runtime via Vega's View API:

```json
{ "data": { "name": "myData" } }
```

### Datasets

Top-level `datasets` mapping for shared inline data across multiple references:

```json
{
  "datasets": { "shared": [1, 2, 3] },
  "data": { "name": "shared" }
}
```

### Data Generators

- **`sequence`** — generate numeric sequences (`start`, `stop`, `step`)
- **`graticule`** — GeoJSON latitude/longitude grid for maps
- **`sphere`** — GeoJSON sphere object for globe backgrounds

## Encoding Channels

The `encoding` object maps data to visual properties. Each channel definition is one of:

- **Field definition** — `{field, type}` with optional scale/axis/sort settings
- **Value definition** — `{value: ...}` for constant visual values
- **Datum definition** — `{datum: ...}` for constant data values through a scale

### Channel Groups

| Group | Channels | Purpose |
|-------|----------|---------|
| Position | `x`, `y`, `x2`, `y2` | Mark position or bar/area width/height |
| Polar Position | `theta`, `radius`, `theta2`, `radius2` | Arc mark angles and radii |
| Geo Position | `longitude`, `latitude`, `longitude2`, `latitude2` | Geographic coordinates |
| Mark Property | `color`, `opacity`, `size`, `shape`, `angle`, `strokeWidth`, `strokeDash`, `fillOpacity`, `strokeOpacity` | Visual properties of marks |
| Text/Tooltip | `text`, `tooltip` | Labels and hover tooltips |
| Hyperlink | `href` | Clickable links |
| Description | `description` | ARIA accessibility text |
| Level of Detail | `detail` | Grouping without visual encoding |
| Key | `key` | Object constancy for transitions |
| Order | `order` | Stacking/drawing order |
| Facet | `facet`, `row`, `column` | Small multiples |

### Data Types

Every field definition requires a `type`:

| Type | Description | Example |
|------|-------------|---------|
| `quantitative` | Continuous numeric data (ratio/interval) | `42.0`, `7.3` |
| `temporal` | Date/time values | `"2015-03-07"`, timestamps |
| `ordinal` | Ranked order without magnitude | `"small"`, `"medium"`, `"large"` |
| `nominal` | Categorical names with no order | `"USA"`, `"Japan"`, `"Germany"` |
| `geojson` | GeoJSON geographic shapes | Feature collections |

### Channel Definition Properties

Beyond `field` and `type`, field definitions support:

- **Inline transforms**: `aggregate`, `bin`, `timeUnit`
- **Scale config**: `scale` object with `type`, `domain`, `range`, `zero`, `nice`, `clamp`
- **Axis config**: `axis` object with `title`, `format`, `labelAngle`, `orient`, etc.
- **Legend config**: `legend` object with `title`, `orient`, `symbolType`, etc.
- **Sort order**: `sort` — `"ascending"`, `"descending"`, `"x"`, array, or field
- **Conditional encoding**: `condition` for parameter-driven visual changes
- **Format**: `format` string for text/tooltip display

## Mark Types

The `mark` property declares the visual primitive. It can be a simple string (`"bar"`) or a mark definition object (`{type: "bar", filled: true}`).

### Primitive Marks (11)

| Mark | Visual Role | Key Encodings |
|------|-------------|---------------|
| `area` | Filled region under a line | `x`, `y`, `y2` (ranged) |
| `bar` | Rectangular bars | `x`, `y`, stacking |
| `circle` | Circular points | `x`, `y`, `size`, `color` |
| `line` | Connected segments | `x`, `y`, interpolation |
| `point` | Point markers (various shapes) | `x`, `y`, `shape`, `filled` |
| `rect` | Rectangles/heatmaps | `x`, `y`, `x2`, `y2` |
| `rule` | Lines at a single position | `x` or `y`, `x2`/`y2` (ranged) |
| `square` | Square points | `x`, `y`, `size` |
| `text` | Text labels/annotations | `x`, `y`, `text`, `align` |
| `tick` | Tick marks/dot plots | `x` or `y`, `thickness` |
| `geoshape` | GeoJSON polygons/lines | `longitude`, `latitude` or geoshape data |

### Composite Marks (3)

| Mark | Composed Of | Purpose |
|------|-------------|---------|
| `boxplot` | rule + rect + point | Statistical box-and-whisker display |
| `errorbar` | rule + tick | Error range visualization |
| `errorband` | area | Confidence/shaded error region |

### Mark Definition Object

```json
{
  "mark": {
    "type": "point",
    "filled": true,
    "size": 100,
    "strokeWidth": 1.5
  }
}
```

Mark properties are organized into groups:

- **General**: `cursor`, `style`, `tooltip`, `clip`, `invalid`, `order`, `aria`
- **Position/Offset**: `x`, `y`, `width`, `height`, `xOffset`, `yOffset`
- **Color**: `filled`, `color`, `fill`, `stroke`, `opacity`, `fillOpacity`, `strokeOpacity`, `blend`
- **Stroke Style**: `strokeCap`, `strokeDash`, `strokeJoin`, `strokeWidth`
- **Hyperlink**: `href`

Mark properties in the definition are overridden by encoding channels. Global defaults can be set via `config.mark` or mark-specific configs like `config.bar`.

## When to Use

Use this skill when you need to:

- **Generate a Vega-Lite spec** from a description of the desired chart (bar, line, scatterplot, heatmap, map, etc.)
- **Build interactive visualizations** with selection parameters, brushes, crossfiltering, or hover effects
- **Compose multi-view layouts** using layer, facet, concat, or repeat operators
- **Transform data within the spec** using aggregate, bin, calculate, filter, window, joinaggregate, or other transforms
- **Embed Vega-Lite in web applications** — compile to Vega, use the embed API, configure TypeScript usage
- **Debug or optimize existing specs** — fix encoding errors, adjust scales/axes/legends, handle invalid data
- **Explore data visually** — generate histograms, QQ plots, parallel coordinates, ternary diagrams, and other analytical chart types

## Advanced Topics

### Foundation

- [Spec Structure & Data Sources](reference/01-spec-and-data.md) — full spec patterns, all data source types, view sizing
- [Encoding Channels](reference/02-encoding-channels.md) — complete channel reference, scales, axes, legends, conditionals
- [Mark Basics](reference/03-mark-basics.md) — mark definition properties, config, styles

### Mark Types

- [Bar Charts](reference/04-bar-charts.md) — simple, grouped, stacked, binned, temporal, labeled, Gantt, bullet
- [Line Charts](reference/05-line-charts.md) — time series, multi-line, imputed, slope, bump, interpolation
- [Trail Charts](reference/06-trail-charts.md) — connected trails, comet charts
- [Area Charts](reference/07-area-charts.md) — stacked, density, gradient, horizon
- [Scatterplots (Circle)](reference/08-scatterplots.md) — 2D scatter, bubble, binned, dot plots
- [Point Marks](reference/09-point-marks.md) — 1D/2D points, shapes, color/opacity encodings
- [Rect Charts](reference/10-rect-charts.md) — heatmaps, mosaics, lasagna
- [Arc Charts](reference/11-arc-charts.md) — pie, donut, radial histograms
- [Rule Marks](reference/12-rule-marks.md) — color mean, extent rules
- [Tick Marks](reference/13-tick-marks.md) — dot plots, strips, histogram ticks
- [Text Marks](reference/14-text-marks.md) — labels, annotations, format strings
- [Square & Image](reference/15-square-and-image.md) — square points, embedded images

### Composite Marks

- [Boxplots](reference/16-boxplots.md) — 1D/2D, grouped, pre-aggregated, custom marks
- [Error Marks](reference/17-error-marks.md) — errorbars and errorbands

### Geographic

- [Geographic Charts](reference/18-geographic-charts.md) — choropleths, geo points/lines, projections

### Composition

- [Histograms](reference/19-histograms.md) — bin patterns, log/nonlinear bins
- [Layer Composition](reference/20-layer-composition.md) — overlaying marks, dual-axis, annotations
- [Facet & Trellis](reference/21-facet-and-trellis.md) — row/column faceting, small multiples
- [Concat & Repeat](reference/22-concat-and-repeat.md) — hconcat/vconcat, repeat operators, resolve

### Cross-Cutting

- [Transforms](reference/23-transforms.md) — all 19 data transforms as reference catalog
- [Parameters & Selection](reference/24-params-and-selection.md) — interactivity, selections, bindings
- [Advanced Patterns](reference/25-advanced-patterns.md) — waterfall, parallel coordinates, ternary, isotype
- [Usage & Embedding](reference/26-usage-and-embedding.md) — web embedding, compilation, TypeScript, debugging
