# Composition Reference

Vega-Lite supports composing multiple views into complex visualizations through layering, concatenation, repetition, and faceting.

## Layer

Overlay multiple marks on the same coordinate system:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Bar chart with error bars.",
  "data": {"url": "data/cars.json"},
  "layer": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"field": "Origin", "type": "nominal"},
        "y": {"aggregate": "mean", "field": "Horsepower"}
      }
    },
    {
      "mark": "errorbar",
      "encoding": {
        "x": {"field": "Origin", "type": "nominal"},
        "y": {"aggregate": "mean", "field": "Horsepower"},
        "yError": {"ci": 0.95, "field": "Horsepower"}
      }
    }
  ]
}
```

Layer with different data sources:

```vega-lite
{
  "layer": [
    {
      "data": {"url": "data/world-110m.json", "format": {"type": "topojson", "feature": "countries"}},
      "projection": {"type": "equirectangular"},
      "mark": "geoshape"
    },
    {
      "data": {"url": "data/earthquakes.tsv"},
      "projection": {"type": "equirectangular"},
      "mark": "circle",
      "encoding": {
        "longitude": {"field": "Longitude"},
        "latitude": {"field": "Latitude"}
      }
    }
  ]
}
```

## HConcat (Horizontal Concatenation)

Place views side by side:

```vega-lite
{
  "hconcat": [
    {
      "mark": "bar",
      "encoding": {
        "x": {"field": "Origin", "type": "nominal"},
        "y": {"aggregate": "mean", "field": "Horsepower"}
      }
    },
    {
      "mark": "bar",
      "encoding": {
        "x": {"field": "Origin", "type": "nominal"},
        "y": {"aggregate": "mean", "field": "Miles_per_Gallon"}
      }
    }
  ],
  "data": {"url": "data/cars.json"}
}
```

## VConcat (Vertical Concatenation)

Stack views vertically:

```vega-lite
{
  "vconcat": [
    {"mark": "bar", "encoding": {"x": {"field": "Origin"}, "y": {"aggregate": "mean", "field": "Horsepower"}}},
    {"mark": "bar", "encoding": {"x": {"field": "Origin"}, "y": {"aggregate": "mean", "field": "Miles_per_Gallon"}}}
  ],
  "data": {"url": "data/cars.json"}
}
```

## Concat (Auto-Layout)

Let Vega-Lite choose the layout:

```vega-lite
{
  "concat": [
    {"mark": "bar", "encoding": {"x": {"field": "Origin"}, "y": {"aggregate": "mean", "field": "Horsepower"}}},
    {"mark": "bar", "encoding": {"x": {"field": "Origin"}, "y": {"aggregate": "mean", "field": "Miles_per_Gallon"}}}
  ],
  "data": {"url": "data/cars.json"}
}
```

## Facet

Split a single view into panels by a categorical field:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Faceted bar chart by origin.",
  "data": {"url": "data/cars.json"},
  "facet": {"field": "Origin", "type": "nominal"},
  "spec": {
    "mark": "bar",
    "encoding": {
      "x": {"field": "Cylinders", "type": "ordinal"},
      "y": {"aggregate": "count"}
    }
  }
}
```

## Column Facet

Facet by columns:

```vega-lite
{
  "column": {"field": "Origin", "type": "nominal"},
  "data": {"url": "data/cars.json"},
  "spec": {
    "mark": "bar",
    "encoding": {
      "x": {"field": "Cylinders", "type": "ordinal"},
      "y": {"aggregate": "count"}
    }
  }
}
```

## Repeat

Repeat a view across different fields:

```vega-lite
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "description": "Repeat bar chart across different metrics.",
  "data": {"url": "data/cars.json"},
  "repeat": {"row": ["Horsepower", "Miles_per_Gallon"]},
  "spec": {
    "mark": "bar",
    "encoding": {
      "x": {"field": "Origin", "type": "nominal"},
      "y": {"aggregate": "mean", "field": {"repeat": "row"}}
    }
  }
}
```

## Repeat Layer

Combine repeat with layer:

```vega-lite
{
  "data": {"url": "data/cars.json"},
  "repeat": {"row": ["Horsepower", "Miles_per_Gallon"]},
  "spec": {
    "layer": [
      {
        "mark": "circle",
        "encoding": {
          "x": {"field": {"repeat": "row"}, "type": "quantitative"},
          "y": {"field": "Weight_in_lbs", "type": "quantitative"}
        }
      },
      {
        "mark": "line",
        "encoding": {
          "x": {"field": {"repeat": "row"}, "bin": true},
          "y": {"aggregate": "mean", "field": "Weight_in_lbs"}
        }
      }
    ]
  }
}
```

## Gotchas

- In `layer`, all views share the same data by default. Override with per-layer `"data"` for different sources.
- `facet` and `column` use a `spec` property containing the inner view definition.
- `repeat` uses `{"repeat": "row"}` or `{"repeat": "column"}` inside encoding fields to reference repeated values.
- Nested composition is supported: layer within facet, concat within layer, etc.
- Shared axes in hconcat/vconcat are aligned automatically; use `"resolve": {"scale": {"y": "independent"}}` for independent scales.
