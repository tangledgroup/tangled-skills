# Concat and Repeat

Concatenation places views side-by-side. Repeat creates multiple views from a template by varying fields.

## Concatenation Operators

### hconcat (Horizontal)

Place views in a column:

```json
{
  "data": {"url": "data/weather.csv"},
  "hconcat": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"timeUnit": "month", "field": "date"},
        "y": {"aggregate": "mean", "field": "precipitation"}
      }
    },
    {
      "mark": "point",
      "encoding": {
        "x": {"field": "temp_min", "bin": true},
        "y": {"field": "temp_max", "bin": true},
        "size": {"aggregate": "count"}
      }
    }
  ]
}
```

### vconcat (Vertical)

Place views in a row:

```json
{
  "vconcat": [
    {"mark": "bar", "encoding": {...}},
    {"mark": "point", "encoding": {...}}
  ]
}
```

### concat (General/Wrappable)

Flexible flow layout with `columns`:

```json
{
  "concat": [
    {"mark": "bar", "encoding": {...}},
    {"mark": "point", "encoding": {...}},
    {"mark": "line", "encoding": {...}}
  ],
  "columns": 2
}
```

### Nested Concat

Combine hconcat and vconcat for grid layouts:

```json
{
  "vconcat": [
    {"mark": "bar", "height": 60, "encoding": {...}},
    {
      "hconcat": [
        {"mark": "rect", "encoding": {...}},
        {"mark": "bar", "width": 60, "encoding": {...}}
      ]
    }
  ]
}
```

## Concat Properties

| Property | Description |
|----------|-------------|
| `spacing` | Spacing between views |
| `bounds` | `"flush"` (no outer padding) or `"full"` (default) |
| `columns` | Max columns for general concat |

### Align and Center

Control axis alignment across concatenated views:

```json
{
  "align": "all",
  "center": true
}
```

## Resolve

**Default**: Independent scales and axes for position channels, shared scales/legends for non-position channels.

Override with `resolve`:

```json
{
  "resolve": {
    "scale": {"color": "independent"},
    "axis": {"y": "independent"}
  }
}
```

**Note**: Vega-Lite does not support shared axes for concatenated views.

## Concat Configuration

```json
{
  "config": {
    "concat": {
      "spacing": 15,
      "columns": 3
    }
  }
}
```

## Repeat Operator

Creates a view for each entry in an array of fields. Unlike facet, repeat replicates the full dataset in each view.

### Row/Column Repeat

```json
{
  "data": {"url": "data/penguins.json"},
  "repeat": {
    "row": ["Beak Length (mm)", "Beak Depth (mm)", "Flipper Length (mm)"],
    "column": ["Body Mass (g)", "Flipper Length (mm)", "Beak Depth (mm)"]
  },
  "spec": {
    "width": 150,
    "height": 150,
    "mark": "point",
    "encoding": {
      "x": {"field": {"repeat": "column"}, "type": "quantitative"},
      "y": {"field": {"repeat": "row"}, "type": "quantitative"},
      "color": {"field": "Species"}
    }
  }
}
```

### Repeated Histogram (Wrapped)

```json
{
  "repeat": ["Horsepower", "Miles_per_Gallon", "Acceleration", "Displacement"],
  "columns": 2,
  "spec": {
    "data": {"url": "data/cars.json"},
    "mark": "bar",
    "encoding": {
      "x": {"field": {"repeat": "repeat"}, "bin": true},
      "y": {"aggregate": "count"},
      "color": {"field": "Origin"}
    }
  }
}
```

### Layer Repeat

Map repeated fields as layers (not stacked, superimposed):

```json
{
  "data": {"url": "data/movies.json"},
  "repeat": {"layer": ["US Gross", "Worldwide Gross"]},
  "spec": {
    "mark": "line",
    "encoding": {
      "x": {"bin": true, "field": "IMDB Rating"},
      "y": {"aggregate": "mean", "field": {"repeat": "layer"}},
      "color": {"datum": {"repeat": "layer"}}
    }
  }
}
```

**Note**: Layer repeat superimposes views — no stacking or legend. Use `fold` transform + color encoding for stacked results.

### Scatterplot Matrix (SPLOM)

```json
{
  "data": {"url": "data/penguins.json"},
  "repeat": {
    "row": ["Beak Length (mm)", "Beak Depth (mm)", "Flipper Length (mm)", "Body Mass (g)"],
    "column": ["Body Mass (g)", "Flipper Length (mm)", "Beak Depth (mm)", "Beak Length (mm)"]
  },
  "spec": {
    "width": 150, "height": 150, "mark": "point",
    "encoding": {
      "x": {"field": {"repeat": "column"}, "type": "quantitative"},
      "y": {"field": {"repeat": "row"}, "type": "quantitative"},
      "color": {"field": "Species"}
    }
  }
}
```

## Marginal Histograms (Nested Concat)

Combine concat with shared binning for marginal distributions:

```json
{
  "data": {"url": "data/movies.json"},
  "spacing": 15,
  "bounds": "flush",
  "vconcat": [
    {
      "mark": "bar", "height": 60,
      "encoding": {"x": {"bin": true, "field": "IMDB Rating", "axis": null}, "y": {"aggregate": "count"}}
    },
    {
      "spacing": 15, "bounds": "flush",
      "hconcat": [
        {
          "mark": "rect",
          "encoding": {
            "x": {"bin": true, "field": "IMDB Rating"},
            "y": {"bin": true, "field": "Rotten Tomatoes Rating"},
            "color": {"aggregate": "count"}
          }
        },
        {
          "mark": "bar", "width": 60,
          "encoding": {
            "y": {"bin": true, "field": "Rotten Tomatoes Rating", "axis": null},
            "x": {"aggregate": "count"}
          }
        }
      ]
    }
  ],
  "config": {"view": {"stroke": "transparent"}}
}
```

## Repeat vs Facet Comparison

| Feature | `repeat` | `facet` |
|---------|----------|---------|
| Data per view | Full dataset | Partitioned subset |
| Field variation | Different fields, same data | Same fields, different subsets |
| Layer support | Yes (`repeat.layer`) | No |
| Resolution | Per-view independence | Shared by default |
| Use when | Same chart, different metrics | Compare categories of one metric |

## Composition Hierarchy

Vega-Lite supports **hierarchical composition** — any operator can be nested within another:

- `layer` → single or layered views only
- `facet` → any view spec
- `hconcat`/`vconcat`/`concat` → any view spec
- `repeat` → any view spec (in `spec`)

This enables building entire dashboards as a single specification.
