# Specification & Data

## Contents
- Top-Level Specification Properties
- Autosize
- Data Sources
- Data Formats

## Top-Level Specification Properties

Every Vega specification is a JSON object with these top-level properties:

| Property | Type | Description |
|----------|------|-------------|
| `$schema` | URL | The schema URL, e.g., `https://vega.github.io/schema/vega/v6.json` |
| `description` | String | Text description; ≥5.10 sets `aria-label` on the container element |
| `background` | Color / Signal | Background color of the view (default: transparent) |
| `width` | Number / Signal | Width in pixels of the data rectangle |
| `height` | Number / Signal | Height in pixels of the data rectangle |
| `padding` | Number / Object / Signal | Padding in pixels around the visualization. Object format: `{"left": 5, "top": 5, "right": 5, "bottom": 5}`. Applied after autosize layout |
| `autosize` | String / Object / Signal | Sizing behavior. See Autosize section below |
| `config` | Config | Default visual settings for marks, axes, legends |
| `signals` | Signal[] | Dynamic variables that parameterize the visualization |
| `data` | Data[] | Dataset definitions and transforms |
| `scales` | Scale[] | Scales mapping data values to visual values |
| `projections` | Projection[] | Cartographic projections for geographic data |
| `axes` | Axis[] | Coordinate axes visualizing scale mappings |
| `legends` | Legend[] | Legends visualizing scale mappings for color, shape, size |
| `title` | Title | Title text describing the visualization |
| `marks` | Mark[] | Graphical marks (rectangles, lines, symbols, etc.) |
| `encode` | Encode | Encoding directives for the top-level group mark's data rectangle |
| `usermeta` | Object | Optional metadata ignored by the Vega parser |

## Autosize

Controls how the visualization size is determined:

### String Values
- `"pad"` (default) — Expand view to fit all content including axes/legends/titles
- `"fit"` — Shrink plot area so everything fits within specified width/height
- `"none"` — Fixed size from width/height/padding only; content outside is clipped
- `"fit-x"` — Adjust only width; height auto-sizes as `pad`
- `"fit-y"` — Adjust only height; width auto-sizes as `pad`

### Object Format
```json
{
  "type": "pad",
  "resize": true,
  "contains": "content"
}
```

| Property | Type | Description |
|----------|------|-------------|
| `type` | String | One of `"pad"`, `"fit"`, `"fit-x"`, `"fit-y"`, `"none"` |
| `resize` | Boolean | Re-calculate layout on every view update (default: `false`) |
| `contains` | String | `"content"` (default: width/height = plot dimensions) or `"padding"` (width/height = total view size) |

## Data Sources

Each data definition requires a unique `name`. At most one of `source`, `url`, or `values` should be defined.

| Property | Type | Description |
|----------|------|-------------|
| `name` | String | **Required.** Unique name for the dataset |
| `url` | String | URL to load data from. Default format is row-oriented JSON |
| `values` | Any[] | Inline data array. Can also be CSV strings with appropriate format |
| `source` | String / String[] | Name(s) of source datasets. Array form merges/union multiple sources |
| `format` | Object | Data format and parsing options |
| `transform` | Transform[] | Array of transforms applied to the data |
| `async` | Boolean | ≥5.9 Load data asynchronously; dataflow completes while loading in background (default: `false`) |
| `on` | Trigger[] | Updates to insert, remove, toggle, or clear data values on trigger conditions |

### Dynamic Data Loading (≥4.2)
The `url` and `format` parameters may include signal references, enabling runtime data source changes. When using signals in URLs, downstream transforms and encodings may initially evaluate with empty datasets — ensure signal expressions handle empty data gracefully.

## Data Formats

The `format` object specifies parsing instructions:

| Property | Type | Description |
|----------|------|-------------|
| `type` | String | Format type: `"json"` (default), `"csv"`, `"tsv"`, `"dsv"`, `"topojson"` |
| `parse` | String / Object | `"auto"` for type inference, or `{"field": "date"}` for explicit types (`"boolean"`, `"date"`, `"number"`, `"string"`) |

### JSON Format
| Property | Type | Description |
|----------|------|-------------|
| `property` | String | JSON property path to extract data from (e.g., `"values.features"`) |
| `copy` | Boolean | Copy input data before use (useful for pre-parsed JSON that shouldn't be modified) |

### CSV Format
| Property | Type | Description |
|----------|------|-------------|
| `parse` | String / Object | Same as top-level format parse |
| `delimiter` | String | Character delimiter (default: `,`) |

### TopoJSON Format
| Property | Type | Description |
|----------|------|-------------|
| `property` | String | TopoJSON object property name (e.g., `"countries"`) |

## Example: Complete Minimal Spec

```json
{
  "$schema": "https://vega.github.io/schema/vega/v6.json",
  "width": 400,
  "height": 200,
  "padding": 5,
  "data": [
    {
      "name": "table",
      "values": [
        {"category": "A", "value": 28},
        {"category": "B", "value": 55},
        {"category": "C", "value": 43}
      ]
    }
  ],
  "scales": [
    {
      "name": "xscale",
      "type": "band",
      "domain": {"data": "table", "field": "category"},
      "range": "width"
    },
    {
      "name": "yscale",
      "type": "linear",
      "domain": {"data": "table", "field": "value"},
      "range": "height"
    }
  ],
  "marks": [
    {
      "type": "rect",
      "from": {"data": "table"},
      "encode": {
        "enter": {
          "x": {"scale": "xscale", "field": "category"},
          "width": {"scale": "xscale"},
          "y": {"scale": "yscale", "field": "value"},
          "y2": {"scale": "yscale", "value": 0},
          "fill": {"value": "steelblue"}
        }
      }
    }
  ]
}
```
