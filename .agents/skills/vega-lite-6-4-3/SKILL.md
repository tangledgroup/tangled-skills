---
name: vega-lite-6-4-3
description: Declarative visualization with Vega-Lite 6.4.3 — JSON specs for charts, graphs, and statistical visualizations. Use when creating data visualizations, charts (bar, line, scatter, pie, area, heatmap, boxplot), maps, or any Vega-Lite spec. Covers mark types, encoding channels, transforms, composition, scales, axes, legends, interactivity, and data sources.
---

# vega-lite 6.4.3

## Overview

Vega-Lite is a high-level grammar of interactive graphics. It provides a concise JSON syntax for rapidly creating visualizations to support data analysis. A Vega-Lite spec compiles to Vega (the lower-level visualization language), making it easier to produce publication-quality charts without wrestling with low-level details.

**Version 6.4.3** is the latest stable release in the v6 line. Key features include:
- 14 primitive marks (arc, area, bar, circle, geoshape, image, line, point, rect, rule, square, text, tick, trail)
- 3 composite marks (boxplot, errorbar, errorband)
- Declarative encoding channels (x, y, x2, y2, color, size, shape, opacity, theta, radius, text, tooltip, order, detail, key)
- Data transforms (filter, aggregate, bin, timeUnit, window, joinaggregate, flatten, fold, pivot, sequence, sample, lookup)
- Composition patterns (layer, hconcat, vconcat, concat, repeat, facet)
- Interactive selections and parameters

### Installation

```bash
npm install vega-lite@6.4.3 vega@5.27.0
```

Vega-Lite depends on Vega. The schema URL for specs is `https://vega.github.io/schema/vega-lite/v6.json`.

## Usage

A Vega-Lite spec is a JSON object with these top-level properties:

```jsonc
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Chart description",
  "data": { "url": "data.csv" },       // or {"values": [...]}
  "transform": [...],                   // optional data transforms
  "mark": "bar",                        // mark type (string or object)
  "encoding": {                         // channel encodings
    "x":   {"field": "category", "type": "nominal"},
    "y":   {"aggregate": "sum", "field": "value", "type": "quantitative"},
    "color": {"field": "group", "type": "nominal"}
  }
}
```

### Spec Structure

Every spec has:
- **`$schema`** — schema version (use `v6.json` for v6.x)
- **`data`** — data source (URL, inline values, or named datasets)
- **`mark`** — the visual mark type (`"bar"`, `"line"`, `"circle"`, etc.)
- **`encoding`** — mapping of data fields to visual channels

Optional top-level properties:
- **`transform`** — array of data transformation operations
- **`layer`** — array of layered specs (for composite visualizations)
- **`hconcat` / `vconcat` / `concat`** — layout compositions
- **`facet` / `column`** — faceted views
- **`repeat`** — repeated encodings
- **`config`** — default configuration overrides
- **`width` / `height`** — viewport dimensions (`"container"` for responsive)

### Mark Types

| Category | Marks |
|---|---|
| **Primitive** | arc, area, bar, circle, geoshape, image, line, point, rect, rule, square, text, tick, trail |
| **Composite** | boxplot, errorbar, errorband |

See reference files below for mark-specific details.

### Data Types

Vega-Lite recognizes four data types:
- **`quantitative`** — continuous numeric values (scales: linear, log, sqrt, pow)
- **`ordinal`** — ordered categories (scales: point, band, ordinal, quantile)
- **`nominal`** — unordered categories (scales: point, band, ordinal)
- **`temporal`** — dates/times (scales: temporal, utc)

### Encoding Channels

| Channel | Description |
|---|---|
| `x`, `y` | Position on horizontal/vertical axis |
| `x2`, `y2` | Secondary position (for ranged marks: bar, area, rect, rule) |
| `color` | Fill or stroke color |
| `fill`, `stroke` | Explicit fill/stroke (overrides `color`) |
| `size` | Area of points, width of bars, font size of text |
| `shape` | Symbol shape for point marks |
| `opacity` | Transparency (0–1) |
| `theta`, `radius` | Polar coordinates for arc/text marks |
| `text` | Text content for text marks |
| `tooltip` | Hover tooltip content |
| `order` | Drawing/stacking order |
| `detail` | Splits data without visual encoding (creates separate mark groups) |
| `key` | Data key for interaction binding |

## Gotchas

- **Vega-Lite is JSON, not JavaScript** — specs are pure JSON objects. No variables, no functions, no template literals. Use transforms for computed fields.
- **`aggregate` vs `bin`** — `aggregate` reduces data (sum, mean, count), `bin` groups continuous values into ranges. They serve different purposes and can be combined.
- **Stacking is automatic** — bar, area, and tick marks stack by default when a third encoding channel (like `color`) creates groups. Use `"stack": null` to disable.
- **`point` vs `circle` vs `square`** — `point` has stroke only by default, `circle` and `square` are filled. Use `{"filled": true}` on point marks to fill them.
- **`line` sorts by x, `trail` preserves data order** — use `trail` when the natural order of your data matters (e.g., GPS traces).
- **`mark` as string vs object** — `"bar"` is shorthand for `{"type": "bar"}`. Use object form when you need mark properties like `{"type": "area", "interpolate": "monotone"}`.
- **Scale zero behavior** — quantitative axes include zero by default. Use `"scale": {"zero": false}` for charts where zero baseline is misleading (e.g., stock prices).
- **Composite marks are convenience wrappers** — `boxplot`, `errorbar`, and `errorband` compile to layered primitive marks. You can replicate them manually with `layer`.
- **Data URL resolution** — relative URLs in `"url"` resolve against the embedding page's origin, not the spec file location.
- **`timeUnit` truncates dates** — `{"timeUnit": "yearmonth"}` drops day/hour info. Combine with `"format"` on axes for display control.
- **`facet` vs `repeat`** — `facet` shares a single encoding across panels; `repeat` iterates over different fields for the same channel.
- **Selections require Vega 5.x** — interactive selections (`"type": "point"`, `"interval"`) depend on Vega's signal system. Ensure compatible versions.
- **Config precedence** — `config.style.<mark>` applies defaults, but explicit encoding always wins. Style configs are additive, not exclusive.

## References

Detailed reference for each mark type and cross-cutting topics:

### Mark Types
- [Arc — pie charts, donut charts](references/01-mark-arc.md)
- [Area — area charts](references/02-mark-area.md)
- [Bar — bar charts](references/03-mark-bar.md)
- [Circle — scatter plot circles](references/04-mark-circle.md)
- [Geoshape — maps, choropleth](references/05-mark-geoshape.md)
- [Image — image marks](references/06-mark-image.md)
- [Line — line charts](references/07-mark-line.md)
- [Point — scatter plot points](references/08-mark-point.md)
- [Rect — heatmaps, mosaic plots](references/09-mark-rect.md)
- [Rule — reference lines](references/10-mark-rule.md)
- [Square — scatter plot squares](references/11-mark-square.md)
- [Text — labels, annotations](references/12-mark-text.md)
- [Tick — strip plots](references/13-mark-tick.md)
- [Trail — trail lines](references/14-mark-trail.md)
- [Boxplot — box-and-whisker](references/15-mark-boxplot.md)
- [Errorbar — error bars](references/16-mark-errorbar.md)
- [Errorband — confidence bands](references/17-mark-errorband.md)

### Cross-Cutting Topics
- [Encoding Channels](references/18-encoding-channels.md)
- [Data Sources](references/19-data-sources.md)
- [Transforms](references/20-transforms.md)
- [Composition (layer, concat, repeat, facet)](references/21-composition.md)
- [Scales, Axes, Legends, Config](references/22-scales-axes-legends.md)
- [Interactivity (selections, parameters)](references/23-interactivity.md)
