# Layer Composition

The `layer` operator superimposes multiple views on top of each other. Only single or layered views can be layered (not facet/concat/repeat).

## Basic Syntax

```json
{
  "data": {"url": "data/mydata.json"},
  "layer": [
    {"mark": "bar", "encoding": {...}},
    {"mark": "line", "encoding": {...}}
  ]
}
```

Common properties (`data`, `transform`, `encoding`, `title`) can be shared at the top level. Per-layer properties override shared ones.

## Shared vs Independent Resolution

**Default**: Layered views share scales, axes, and legends (domains are unioned).

**Independent scales**: Use `resolve` to decouple:

```json
{
  "resolve": {"scale": {"y": "independent"}}
}
```

## Bar + Line Overlay

```json
{
  "layer": [
    {
      "mark": "bar",
      "encoding": {"x": {"field": "a", "type": "nominal"}, "y": {"field": "b"}}
    },
    {
      "mark": "line",
      "encoding": {"x": {"field": "a", "type": "nominal"}, "y": {"field": "b"}, "color": {"value": "red"}}
    }
  ]
}
```

## Dual-Axis Charts

Independent y-scales with colored axis titles:

```json
{
  "data": {"url": "data/weather.csv"},
  "transform": [{"filter": "datum.location == 'Seattle'"}],
  "encoding": {"x": {"timeUnit": "month", "field": "date"}},
  "layer": [
    {
      "mark": {"type": "area", "opacity": 0.3, "color": "#85C5A6"},
      "encoding": {
        "y": {"aggregate": "average", "field": "temp_max", "title": "Avg Temp (°C)", "axis": {"titleColor": "#85C5A6"}},
        "y2": {"aggregate": "average", "field": "temp_min"}
      }
    },
    {
      "mark": {"type": "line", "stroke": "#85A9C5"},
      "encoding": {
        "y": {"aggregate": "average", "field": "precipitation", "title": "Precipitation (in)", "axis": {"titleColor": "#85A9C5"}}
      }
    }
  ],
  "resolve": {"scale": {"y": "independent"}}
}
```

## Text Labels on Bars

```json
{
  "encoding": {"y": {"field": "a", "type": "nominal"}, "x": {"field": "b", "scale": {"domain": [0, 60]}}},
  "layer": [
    {"mark": "bar"},
    {
      "mark": {"type": "text", "align": "left", "baseline": "middle", "dx": 3},
      "encoding": {"text": {"field": "b"}}
    }
  ]
}
```

## Bar + Circle (Grouped)

```json
{
  "transform": [{"calculate": "datum.value/2", "as": "half"}],
  "encoding": {"x": {"field": "category"}, "xOffset": {"field": "group"}},
  "layer": [
    {"mark": "bar", "encoding": {"y": {"field": "value"}, "color": {"field": "group"}}},
    {"mark": {"type": "circle", "thickness": 2, "color": "black"}, "encoding": {"y": {"field": "half"}}}
  ]
}
```

## Cumulative Histograms

Bin transform + window transform for cumulative counts:

```json
{
  "transform": [
    {"bin": true, "field": "IMDB Rating", "as": "bin_rating"},
    {"aggregate": [{"op": "count", "as": "count"}], "groupby": ["bin_rating", "bin_rating_end"]},
    {"filter": "datum.bin_rating !== null"},
    {"sort": [{"field": "bin_rating"}], "window": [{"op": "sum", "field": "count", "as": "Cumulative"}], "frame": [null, 0]}
  ],
  "encoding": {"x": {"field": "bin_rating", "bin": "binned"}, "x2": {"field": "bin_rating_end"}},
  "layer": [
    {"mark": "bar", "encoding": {"y": {"field": "Cumulative"}}},
    {"mark": {"type": "bar", "color": "yellow", "opacity": 0.5}, "encoding": {"y": {"field": "count"}}}
  ]
}
```

## Candlestick Charts

Rule for wicks + bar for body:

```json
{
  "data": {"url": "data/ohlc.json"},
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"type": "quantitative", "scale": {"zero": false}},
    "color": {"condition": {"test": "datum.open < datum.close", "value": "#06982d"}, "value": "#ae1325"}
  },
  "layer": [
    {"mark": "rule", "encoding": {"y": {"field": "low"}, "y2": {"field": "high"}}},
    {"mark": "bar", "encoding": {"y": {"field": "open"}, "y2": {"field": "close"}}}
  ]
}
```

## Scatter + Errorband

```json
{
  "encoding": {"x": {"timeUnit": "year", "field": "Year"}},
  "layer": [
    {"mark": {"type": "errorband", "extent": "ci"}, "encoding": {"y": {"field": "Miles_per_Gallon"}}},
    {"mark": "line", "encoding": {"y": {"aggregate": "mean", "field": "Miles_per_Gallon"}}}
  ]
}
```

## Boxplot + Raw Data Points

Overlay raw data on boxplots:

```json
{
  "layer": [
    {
      "mark": {"type": "boxplot", "outliers": false},
      "encoding": {"y": {"field": "age", "type": "ordinal"}, "x": {"field": "people"}}
    },
    {
      "mark": "circle",
      "encoding": {
        "y": {"field": "age", "type": "ordinal"},
        "x": {"field": "people"},
        "color": {"value": "black"},
        "opacity": {"value": 0.2}
      }
    }
  ]
}
```

## Likert Charts

Multi-layer: circles for ratings, tick for median, text for labels:

```json
{
  "data": {"name": "medians"},
  "layer": [
    {"mark": "circle", "data": {"name": "values"}, "encoding": {"x": {"field": "value"}, "size": {"aggregate": "count"}}},
    {"mark": "tick", "encoding": {"x": {"field": "median"}, "color": {"value": "black"}}},
    {"mark": {"type": "text", "x": -5, "align": "right"}, "encoding": {"text": {"field": "lo"}}},
    {"mark": {"type": "text", "x": 255, "align": "left"}, "encoding": {"text": {"field": "hi"}}}
  ]
}
```

## Rolling Means with Points

Window transform in layers:

```json
{
  "layer": [
    {"mark": "point", "encoding": {"x": {"field": "date"}, "y": {"field": "price"}}},
    {"mark": "line", "encoding": {"x": {"field": "date"}, "y": {"field": "rolling_mean"}}}
  ]
}
```

## Key Layer Patterns

| Pattern | Layers | Technique |
|---------|--------|-----------|
| Bar + Line | bar, line | Same x/y encoding |
| Dual-Axis | area, line | `resolve: {scale: {y: "independent"}}` |
| Annotations | bar, text | Text mark with `dx`, `dy` offsets |
| Candlestick | rule, bar | Rule for wicks, bar for body |
| Error Bands | errorband, line | Composite + primitive marks |
| Boxplot + Jitter | boxplot, circle | Outliers: false, opacity on points |
| Likert | circle, tick, text | Multiple datasets via `datasets` |
| Cumulative | bar (×2) | Window transform with frame |

## Layer Constraints

- Only **single** or **layered** views can be layered
- Cannot layer facet, concat, or repeat operators
- Data can be shared at top level or specified per-layer
- Encoding can be shared at top level and extended per-layer
- Scale domains are unioned by default (use `resolve` for independence)
