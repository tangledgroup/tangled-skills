# Spec Structure & Data Sources

## Specification Types

Vega-Lite specifications are JSON objects. There are three tiers:

### Top-Level Properties

Present on all spec types (single view, layered, multi-view):

| Property | Type | Description |
|----------|------|-------------|
| `$schema` | string | Schema URL, e.g., `"https://vega.github.io/schema/vega-lite/v6.json"` |
| `background` | string | Canvas background color (CSS color) |
| `padding` | number \| object | View padding; `{top, right, bottom, left}` or single number |
| `autosize` | string \| object | Auto-sizing: `"pad"`, `"fit"`, `"none"`, `"fit-x"`, `"fit-y"` |
| `config` | object | Global configuration overrides |
| `usermeta` | object | Arbitrary metadata passed through to Vega |

### Common Properties

Present on all view specifications (single, layered, multi-view):

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Unique view name (for composition referencing) |
| `description` | string | Human-readable description |
| `title` | string \| object | Chart title with formatting options |
| `data` | object \| array | Data source definition(s) |
| `transform` | array | Data transformation operations |
| `params` | array | Named parameters for interactivity |

### Single-View Specification

The simplest spec — one mark type, one encoding:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "A simple bar chart",
  "data": {"url": "data/cars.json"},
  "mark": "bar",
  "encoding": {
    "x": {"field": "Origin", "type": "nominal"},
    "y": {"aggregate": "count", "type": "quantitative"}
  }
}
```

Additional single-view properties:

| Property | Type | Description |
|----------|------|-------------|
| `mark` | string \| object | Mark type or mark definition |
| `encoding` | object | Data-to-visual-channel mappings |
| `width` / `height` | number \| string \| object | View dimensions |
| `view` | object | View background styling |
| `projection` | object | Geographic projection settings |

### Layered Specification

Overlays multiple mark types on the same view:

```json
{
  "data": {"url": "data/seattle-temps.csv"},
  "layer": [
    {
      "mark": "line",
      "encoding": {
        "x": {"field": "date", "type": "temporal"},
        "y": {"field": "temperature", "type": "quantitative"}
      }
    },
    {
      "mark": "point",
      "encoding": {
        "x": {"field": "date", "type": "temporal"},
        "y": {"field": "temperature", "type": "quantitative"},
        "color": {"value": "red"}
      }
    }
  ]
}
```

### Multi-View Specifications

| Type | Description |
|------|-------------|
| `facet` | Split into grid of small multiples (row/column) |
| `hconcat` | Horizontal concatenation |
| `vconcat` | Vertical concatenation |
| `concat` | General 2D grid concatenation |
| `repeat` | Repeat spec across fields |

Composition specs add:

- **Layout**: `align`, `bounds`, `center`, `spacing`
- **Resolve**: `resolve.scale`, `resolve.axis`, `resolve.legend` for independent scales/guides

## Title Configuration

Title can be a string or object with formatting properties:

```json
{
  "title": {
    "text": "Monthly Precipitation",
    "subtitle": "1948-2012",
    "anchor": "start",
    "orient": "top",
    "fontSize": 16,
    "fontWeight": "bold"
  }
}
```

Key title properties: `text`, `subtitle`, `align`, `anchor`, `angle`, `baseline`, `color`, `dx`, `dy`, `font`, `fontSize`, `fontStyle`, `fontWeight`, `orient`, `style`.

Set global defaults via `config.title`.

## View Sizing

### Width and Height

`width` and `height` set the data rectangle (plotting area), not total visualization size.

| Approach | Example | Behavior |
|----------|---------|----------|
| Fixed pixels | `"width": 400` | Exact pixel width of plot area |
| Responsive | `"width": "container"` | Matches parent container |
| Per-step | `{"step": 20}` | Width per discrete band/point |
| Default | _(omit)_ | From config: `continuousWidth` (200) or `discreteWidth` (step-based, default step 20) |

### Autosize Types

The `autosize` property controls total visualization size vs. plot area:

| Type | Behavior |
|------|----------|
| `"pad"` (default) | Grow view to fit all content (axes, legends, titles may extend beyond width/height) |
| `"fit"` | Shrink plot area to fit within width + padding; axes/legends included |
| `"none"` | No auto-sizing; content outside width/height is clipped |
| `"fit-x"` | Fit only horizontally |
| `"fit-y"` | Fit only vertically |

Autosize object: `{type: "pad", resize: true, contains: "view"}`. `contains` can be `"view"` or `"padding"`.

**Limitations**: `fit` only works on single-view and layered specs (not facet/concat/repeat). Explicit step sizes override fit in that dimension.

### Default Size Rules

- **Continuous x-field**: width = `config.view.continuousWidth` (200 default)
- **Discrete x-field**: width = cardinality × `config.view.step` (20 default)
- **Continuous y-field**: height = `config.view.continuousHeight` (200 default)
- **Discrete y-field**: height = cardinality × `config.view.step`

### Multi-View Sizing

Width/height of facet/concat/repeat is determined by the composed unit views. Set `width`/`height` on inner specs to control overall size.

## Data Sources

### Inline Values

Embed data directly as an array of objects:

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

Properties: `values`, `name` (for referencing), `format`.

Primitive arrays (`[5, 3, 8]`) are auto-mapped to `{"data": value}`.

### URL

Load external data:

```json
{
  "data": {
    "url": "data/cars.json",
    "format": {"type": "json"}
  }
}
```

Format types:

| Type | Description | Extra Properties |
|------|-------------|------------------|
| `json` (default) | Row-oriented JSON objects | `property` (nested path) |
| `csv` | Comma-separated values | — |
| `tsv` | Tab-separated values | — |
| `dsv` | Custom delimiter | `delimiter` |
| `topojson` | TopoJSON → GeoJSON | `feature`, `mesh` |

### Named Data Sources

Declare empty named sources for runtime population via Vega View API:

```json
{"data": {"name": "myData"}}
```

Populate at runtime:

```js
vegaEmbed('#vis', spec).then((res) =>
  res.view.insert('myData', [{/* data */}]).run()
);
```

### Datasets

Top-level `datasets` for shared inline data:

```json
{
  "datasets": {
    "shared": [1, 2, 3]
  },
  "data": {"name": "shared"}
}
```

### Data Generators

| Generator | Purpose | Properties |
|-----------|---------|------------|
| `sequence` | Numeric sequences | `start`, `stop`, `step`, `as` |
| `graticule` | GeoJSON lat/lon grid | `extent`, `step`, `precision` |
| `sphere` | GeoJSON sphere (globe) | `true` or `{}` |

```json
// Sequence example
{"data": {"sequence": {"start": 0, "stop": 10, "step": 0.1, "as": "x"}}}

// Graticule example
{"data": {"graticule": true}}

// Sphere example
{"data": {"sphere": true}}
```
