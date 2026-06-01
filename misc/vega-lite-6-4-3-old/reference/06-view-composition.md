# View Composition

## Contents

- Layer
- Facet
- Concat (hconcat / vconcat / concat)
- Repeat
- Resolve

## Layer

Overlay multiple marks on the same view. Layers share data, transform, params, and encoding from parent spec unless overridden.

```json
{
  "data": {"values": [{"a": "A", "b": 28}, {"a": "B", "b": 55}]},
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

### Layer Properties

Each layer can specify its own `mark`, `encoding`, `data`, and `transform`. Unspecified properties are inherited from the parent. Layers render in array order (first = bottom, last = top).

### Dual-Axis Chart

Use `resolve: {"scale": {"y": "independent"}}` to give each layer independent scales:

```json
{
  "data": {"url": "data/weather.csv"},
  "transform": [{"filter": "datum.location == \"Seattle\""}],
  "encoding": {
    "x": {"timeUnit": "month", "field": "date", "axis": {"format": "%b"}}
  },
  "layer": [
    {
      "mark": {"type": "area", "opacity": 0.3, "color": "#85C5A6"},
      "encoding": {
        "y": {"aggregate": "average", "field": "temp_max", "title": "Temp (°C)",
              "scale": {"domain": [0, 30]}, "axis": {"titleColor": "#85C5A6"}},
        "y2": {"aggregate": "average", "field": "temp_min"}
      }
    },
    {
      "mark": {"type": "line", "stroke": "#85A9C5", "interpolate": "monotone"},
      "encoding": {
        "y": {"aggregate": "average", "field": "precipitation", "title": "Precip (in)",
              "axis": {"titleColor": "#85A9C5"}}
      }
    }
  ],
  "resolve": {"scale": {"y": "independent"}}
}
```

## Facet

Split a single plot into a grid of sub-plots (trellis / small multiples).

### Using Encoding Channels

```json
{
  "data": {"url": "data/population.json"},
  "transform": [{"filter": "datum.year == 2000"}],
  "width": {"step": 17},
  "mark": "bar",
  "encoding": {
    "row": {"field": "gender"},
    "y": {"aggregate": "sum", "field": "people"},
    "x": {"field": "age"},
    "color": {"field": "gender", "scale": {"range": ["#675193", "#ca8861"]}}
  }
}
```

### Flexible Facet

```json
{
  "data": {"url": "data/movies.json"},
  "mark": "point",
  "encoding": {
    "facet": {"field": "MPAA Rating", "type": "ordinal", "columns": 2},
    "x": {"field": "Worldwide Gross", "type": "quantitative"},
    "y": {"field": "US DVD Sales", "type": "quantitative"}
  }
}
```

### Facet Spec (object form)

For more control, use the `facet` spec type:

```json
{
  "facet": {"row": {"field": "gender"}},
  "spec": {
    "data": {"url": "data/population.json"},
    "mark": "bar",
    "encoding": {
      "y": {"aggregate": "sum", "field": "people"},
      "x": {"field": "age"}
    }
  }
}
```

### Facet Channels

| Channel | Description |
|---------|-------------|
| `row` | Vertical facet (rows of plots) |
| `column` | Horizontal facet (columns of plots) |
| `facet` | Flexible auto-arranged grid |

Facet field definitions support: `header`, `sort`, `title`, `format`. Use `columns` property on `facet` to set number of columns.

## Concat (hconcat / vconcat / concat)

Arrange multiple views side by side or stacked.

### Horizontal Concatenation (`hconcat`)

```json
{
  "hconcat": [
    {
      "data": {"url": "data/cars.json"},
      "mark": "bar",
      "encoding": {
        "x": {"bin": true, "field": "Horsepower"},
        "y": {"aggregate": "count"}
      }
    },
    {
      "data": {"url": "data/cars.json"},
      "mark": "bar",
      "encoding": {
        "x": {"bin": true, "field": "Miles_per_Gallon"},
        "y": {"aggregate": "count"}
      }
    }
  ]
}
```

### Vertical Concatenation (`vconcat`)

```json
{
  "data": {"url": "data/weather.csv"},
  "transform": [{"filter": "datum.location === 'Seattle'"}],
  "vconcat": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"timeUnit": "month", "field": "date", "type": "ordinal"},
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

### General Concatenation (`concat`)

Wrappable grid layout:

```json
{
  "concat": [spec1, spec2, spec3, spec4],
  "columns": 2
}
```

### Nested Concatenation

Concat can be nested for complex layouts (e.g., marginal histograms with heatmap center):

```json
{
  "vconcat": [
    {
      "mark": "bar",
      "height": 60,
      "encoding": {
        "x": {"bin": true, "field": "IMDB Rating", "axis": null},
        "y": {"aggregate": "count", "scale": {"domain": [0, 1000]}}
      }
    },
    {
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
          "mark": "bar",
          "width": 60,
          "encoding": {
            "y": {"bin": true, "field": "Rotten Tomatoes Rating", "axis": null},
            "x": {"aggregate": "count", "scale": {"domain": [0, 1000]}}
          }
        }
      ]
    }
  ],
  "config": {"view": {"stroke": "transparent"}}
}
```

### Concat Properties

| Property | Type | Description |
|----------|------|-------------|
| `spacing` | Number \| Object | Spacing between sub-views. Default: `20` |
| `align` | String \| Object | `"all"` (default), `"each"`, `"none"` |
| `bounds` | String | `"full"` (default) or `"flush"` |
| `center` | Boolean \| Object | Center subviews. Default: `false` |

## Repeat

Iterate a spec template across different fields, reducing repetition.

### Column Repeat

```json
{
  "data": {"url": "data/movies.json"},
  "repeat": {"column": ["US Gross", "Worldwide Gross"]},
  "spec": {
    "mark": "bar",
    "encoding": {
      "x": {"bin": true, "field": {"repeat": "column"}},
      "y": {"aggregate": "count"}
    }
  }
}
```

### Layer Repeat

```json
{
  "data": {"url": "data/movies.json"},
  "repeat": {"layer": ["US Gross", "Worldwide Gross"]},
  "spec": {
    "mark": "line",
    "encoding": {
      "x": {"bin": true, "field": "IMDB Rating", "type": "quantitative"},
      "y": {"aggregate": "mean", "field": {"repeat": "layer"}, "type": "quantitative"},
      "color": {"datum": {"repeat": "layer"}, "type": "nominal"}
    }
  }
}
```

### Repeat Types

| Type | Description |
|------|-------------|
| `row` | Repeat across rows |
| `column` | Repeat across columns |
| `layer` | Repeat as layered views |

Reference repeated values using `{"repeat": "row"}` or `{"repeat": "column"}` or `{"repeat": "layer"}` in field definitions and datum values.

## Resolve

Control whether scales, axes, and legends are shared (`"shared"`) or independent (`"independent"`) across composed views.

```json
{
  "layer": [...],
  "resolve": {
    "scale": {"y": "independent"},
    "legend": {"color": "independent"},
    "axis": {"x": "shared"}
  }
}
```

### Resolve Properties

| Property | Values | Description |
|----------|--------|-------------|
| `scale` | `"shared"` / `"independent"` per channel | Whether scales are shared across views |
| `axis` | `"shared"` / `"independent"` per channel | Whether axes are shared |
| `legend` | `"shared"` / `"independent"` per channel | Whether legends are shared |

Default: `"shared"` for all. Use `"independent"` when views need different scale domains (e.g., dual-axis charts, faceted plots with different ranges).
