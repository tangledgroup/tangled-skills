# Facet and Trellis

Faceting partitions data into subsets and creates a view for each subset. Two approaches: the `facet` operator (flexible, composable) and encoding channels (`row`, `column`, `facet` as shortcuts).

## Facet Operator

Full control with explicit facet + spec:

```json
{
  "facet": {"row": {"field": "Origin", "type": "nominal"}},
  "spec": {
    "data": {"url": "data/cars.json"},
    "mark": "bar",
    "encoding": {
      "x": {"bin": true, "field": "Horsepower"},
      "y": {"aggregate": "count"}
    }
  }
}
```

### Facet Field Definition

| Property | Type | Description |
|----------|------|-------------|
| `field` | string | Data field to facet by |
| `type` | string | `"nominal"` or `"ordinal"` (not quantitative unless binned) |
| `timeUnit` | string | Temporal unit for temporal fields |
| `bin` | boolean \| object | Bin the facet field |
| `header` | object | Header label/title customization |

### Facet Mapping

| Property | Description |
|----------|-------------|
| `row` | Vertical faceting (stacked rows) |
| `column` | Horizontal faceting (side-by-side columns) |
| Both | Grid of small multiples |

### Wrapped Facet

Use `facet` with `columns` for wrapped layout:

```json
{
  "facet": {"field": "site", "type": "ordinal", "columns": 2, "sort": {"op": "median", "field": "yield"}},
  "spec": {
    "data": {"url": "data/barley.json"},
    "mark": "point",
    "encoding": {
      "x": {"aggregate": "median", "field": "yield"},
      "y": {"field": "variety", "type": "ordinal", "sort": "-x"},
      "color": {"field": "year", "type": "nominal"}
    }
  }
}
```

## Encoding Channel Shortcuts

### Row Facet (Encoding)

```json
{
  "data": {"url": "data/cars.json"},
  "mark": "bar",
  "encoding": {
    "x": {"bin": true, "field": "Horsepower"},
    "y": {"aggregate": "count"},
    "row": {"field": "Origin"}
  }
}
```

### Column Facet (Encoding)

```json
{
  "encoding": {
    "column": {"field": "gender", "header": {"titleFontSize": 20, "labelFontSize": 15}},
    "x": {"field": "age", "type": "ordinal"},
    "y": {"aggregate": "sum", "field": "people"}
  }
}
```

### Grid Facet (Row + Column)

```json
{
  "encoding": {
    "row": {"field": "category1"},
    "column": {"field": "category2"},
    "x": {"field": "value"}
  }
}
```

### Wrapped Facet (Encoding)

```json
{
  "encoding": {
    "facet": {"field": "MPAA Rating", "type": "ordinal", "columns": 2},
    "x": {"field": "Worldwide Gross"},
    "y": {"field": "US DVD Sales"}
  }
}
```

### Row/Column Channel Properties

| Property | Type | Description |
|----------|------|-------------|
| `align` | string \| [string] | Axis alignment (`"center"`, `"none"`) |
| `center` | boolean \| [boolean] | Center axes within facets |
| `spacing` | number | Spacing between facets |
| `columns` | number | Max columns for wrapped facet |

## Resolve (Scale Independence)

**Default**: Shared scales, axes, and legends across facets.

**Independent**: Override with `resolve`:

```json
{
  "facet": {"row": {"field": "category"}},
  "spec": {...},
  "resolve": {"scale": {"y": "independent"}}
}
```

## Facet Configuration

```json
{
  "config": {
    "facet": {
      "spacing": 20,
      "columns": 3
    }
  }
}
```

## Trellis Patterns

### Scatter Small Multiples

```json
{
  "encoding": {
    "facet": {"field": "category", "columns": 2},
    "x": {"field": "x_val"},
    "y": {"field": "y_val"}
  }
}
```

### Binned Row Trellis

```json
{
  "encoding": {
    "row": {"field": "Origin"},
    "x": {"bin": {"maxbins": 15}, "field": "Horsepower"},
    "y": {"aggregate": "count"}
  }
}
```

### Line Quarter Trellis

```json
{
  "mark": "point",
  "encoding": {
    "x": {"timeUnit": "quarter", "field": "date"},
    "y": {"aggregate": "mean", "field": "price"},
    "color": {"field": "symbol"},
    "column": {"field": "date", "timeUnit": "year"}
  }
}
```

### Area Trellis

```json
{
  "mark": "area",
  "encoding": {
    "row": {"field": "category"},
    "x": {"field": "date"},
    "y": {"field": "value"}
  }
}
```

### Stacked Bar Trellis

```json
{
  "mark": "bar",
  "encoding": {
    "row": {"field": "group"},
    "x": {"field": "category"},
    "y": {"aggregate": "count"},
    "color": {"field": "subcategory"}
  }
}
```

## Bullet Charts (Facet + Layer)

Complex faceted charts with layered specs:

```json
{
  "facet": {"row": {"field": "title", "type": "ordinal"}},
  "spec": {
    "encoding": {"x": {"type": "quantitative", "scale": {"nice": false}}},
    "layer": [
      {"mark": {"type": "bar", "color": "#eee"}, "encoding": {"x": {"field": "ranges[2]"}}},
      {"mark": {"type": "bar", "color": "#ddd"}, "encoding": {"x": {"field": "ranges[1]"}}},
      {"mark": {"type": "bar", "color": "#ccc"}, "encoding": {"x": {"field": "ranges[0]"}}},
      {"mark": {"type": "bar", "color": "steelblue", "size": 10}, "encoding": {"x": {"field": "measures[0]"}}},
      {"mark": {"type": "tick", "color": "black"}, "encoding": {"x": {"field": "markers[0]"}}}
    ]
  },
  "resolve": {"scale": {"x": "independent"}}
}
```

## Facet vs Repeat Comparison

| Feature | `facet` | `repeat` |
|---------|---------|----------|
| Data | Partitioned by facet field | Full dataset in each view |
| Composition | Composable with other operators | Cannot be layered |
| Shortcut | `row`/`column` encoding channels | `repeat` array/object |
| Use when | Compare subsets of same data | Same chart, different fields |
