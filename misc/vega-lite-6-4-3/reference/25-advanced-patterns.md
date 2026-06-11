# Advanced Patterns

Compound chart types built from combinations of marks, transforms, and composition operators.

## Waterfall Charts

Show cumulative effect of sequentially introduced positive/negative values. Built with window transforms + layered bars/rules/text.

**Technique:** `window` sum for cumulative totals, `calculate` for previous sums, conditional color.

```json
{
  "transform": [
    {"window": [{"op": "sum", "field": "amount", "as": "sum"}]},
    {"calculate": "datum.sum - datum.amount", "as": "previous_sum"},
    {"calculate": "(datum.sum + datum.previous_sum) / 2", "as": "center"}
  ],
  "layer": [
    {
      "mark": "bar",
      "encoding": {"y": {"field": "previous_sum"}, "y2": {"field": "sum"}, "color": {"condition": [{"test": "datum.sum < datum.previous_sum", "value": "red"}], "value": "green"}}
    },
    {"mark": "rule", "encoding": {"x2": {"field": "lead"}, "y": {"field": "sum"}}},
    {"mark": "text", "encoding": {"y": {"field": "sum"}, "text": {"field": "sum"}}},
    {"mark": "text", "encoding": {"y": {"field": "center"}, "text": {"field": "amount"}}}
  ]
}
```

## Parallel Coordinates

Multi-dimensional data with folded variables and normalized values.

**Technique:** `fold` → `joinaggregate` for min/max → `calculate` for normalization → layered lines with manual axis ticks.

```json
{
  "transform": [
    {"fold": ["field1", "field2", "field3"]},
    {"joinaggregate": [{"op": "min", "field": "value", "as": "min"}, {"op": "max", "field": "value", "as": "max"}], "groupby": ["key"]},
    {"calculate": "(datum.value - datum.min) / (datum.max - datum.min)", "as": "norm_val"}
  ],
  "layer": [
    {"mark": "line", "encoding": {"x": {"field": "key"}, "y": {"field": "norm_val", "axis": null}, "color": {"field": "group"}}},
    {"mark": "text", "encoding": {"x": {"field": "key"}, "y": {"value": 0}, "text": {"aggregate": "max", "field": "max"}}}
  ]
}
```

## Ternary Plots

Three-component compositions (a + b + c = 1) plotted on triangular axes.

**Technique:** Calculate x/y from proportions: `x = 0.5 * (2*c + b)`, `y = 0.866 * b`. Layer triangle outlines, grid lines, and data points.

```json
{
  "transform": [
    {"calculate": "datum.High + datum.Medium + datum.Low", "as": "Total"},
    {"calculate": "datum.High / datum.Total", "as": "high_pct"},
    {"calculate": "datum.Medium / datum.Total", "as": "med_pct"},
    {"calculate": "datum.Low / datum.Total", "as": "low_pct"},
    {"calculate": "0.5 * (2 * datum.low_pct + datum.med_pct)", "as": "x"},
    {"calculate": "0.866 * datum.med_pct", "as": "y"}
  ]
}
```

## Isotype (Pictogram) Charts

Represent quantities with repeated icons or emojis.

### Emoji Bar Chart

```json
{
  "transform": [
    {"calculate": "{'cattle': '🐄', 'pigs': '🐖', 'sheep': '🐏'}[datum.animal]", "as": "emoji"},
    {"window": [{"op": "rank", "as": "rank"}], "groupby": ["country", "animal"]}
  ],
  "mark": {"type": "text", "baseline": "middle"},
  "encoding": {
    "x": {"field": "rank", "axis": null},
    "y": {"field": "animal", "axis": null},
    "row": {"field": "country"},
    "text": {"field": "emoji"},
    "size": {"value": 65}
  }
}
```

### SVG Shape Grid

Use custom SVG path shapes with `point` marks:

```json
{
  "transform": [
    {"calculate": "ceil(datum.id/10)", "as": "col"},
    {"calculate": "datum.id - datum.col*10", "as": "row"}
  ],
  "mark": {"type": "point", "filled": true},
  "encoding": {
    "x": {"field": "col"},
    "y": {"field": "row"},
    "shape": {"value": "M1.7 -1.7h-0.8c0.3 -0.2..."}
  }
}
```

## Connected Scatterplots

Scatterplot where points are connected in sequence (e.g., time).

**Technique:** `line` mark with `point: true` + `order` encoding.

```json
{
  "mark": {"type": "line", "point": true},
  "encoding": {
    "x": {"field": "miles"},
    "y": {"field": "gas"},
    "order": {"field": "year"}
  }
}
```

## QQ Plots

Compare empirical distributions to theoretical distributions.

**Technique:** `quantile` transform on two datasets, scatter the quantile values against each other.

```json
{
  "transform": [{"quantile": "measure", "step": 0.05}]
}
```

## Falkensee Diagrams

Time series with historical period backgrounds.

**Technique:** Layer `rect` marks (periods) behind `line` + `point` marks.

```json
{
  "layer": [
    {
      "mark": "rect",
      "data": {"values": [{"start": "1933", "end": "1945", "event": "Period 1"}]},
      "encoding": {"x": {"field": "start"}, "x2": {"field": "end"}, "color": {"field": "event"}}
    },
    {"mark": "line", "encoding": {"x": {"field": "year"}, "y": {"field": "value"}}},
    {"mark": "point", "encoding": {"x": {"field": "year"}, "y": {"field": "value"}}}
  ]
}
```

## Cumulative Running Averages

Running mean overlaid on raw data.

**Technique:** `window` with `frame: [null, 0]` and `op: "mean"`.

```json
{
  "transform": [
    {"timeUnit": "year", "field": "Year", "as": "year"},
    {"window": [{"op": "mean", "field": "value", "as": "avg"}], "sort": [{"field": "year"}], "frame": [null, 0]}
  ],
  "layer": [
    {"mark": "circle", "encoding": {"x": {"field": "year"}, "y": {"field": "value"}}},
    {"mark": "line", "encoding": {"x": {"field": "year"}, "y": {"field": "avg"}}}
  ]
}
```

## Top-K with Others

Show top K categories, aggregate remainder as "Others".

**Technique:** `window` row_number → `calculate` to group below threshold.

```json
{
  "transform": [
    {"aggregate": [{"op": "mean", "field": "value", "as": "avg"}], "groupby": ["category"]},
    {"window": [{"op": "row_number", "as": "rank"}], "sort": [{"field": "avg", "order": "descending"}]},
    {"calculate": "datum.rank <= 10 ? datum.category : 'All Others'", "as": "label"}
  ]
}
```

## Residual Graphs

Show deviation from a reference (mean, trend).

**Technique:** `joinaggregate` for reference → `calculate` for difference.

```json
{
  "transform": [
    {"joinaggregate": [{"op": "mean", "field": "value", "as": "avg"}]},
    {"calculate": "datum.value - datum.avg", "as": "residual"}
  ],
  "encoding": {
    "x": {"field": "date"},
    "y": {"field": "residual"},
    "color": {"field": "residual", "scale": {"domainMid": 0}}
  }
}
```

## Index Charts

Normalize all series to a common starting point.

**Technique:** Selection parameter + `lookup` from selection → `calculate` percentage change.

```json
{
  "layer": [
    {
      "params": [{"name": "index", "select": {"type": "point", "encodings": ["x"], "on": "pointerover", "nearest": true}}],
      "mark": "point",
      "encoding": {"opacity": {"value": 0}}
    },
    {
      "transform": [
        {"lookup": "symbol", "from": {"param": "index", "key": "symbol"}},
        {"calculate": "(datum.price - datum.index.price) / datum.index.price", "as": "indexed"}
      ],
      "mark": "line",
      "encoding": {"y": {"field": "indexed", "axis": {"format": "%"}}}
    }
  ]
}
```

## Sequence Lines

Plot mathematical functions using generated data.

**Technique:** `sequence` data source + `calculate` transform.

```json
{
  "data": {"sequence": {"start": 0, "stop": 12.7, "step": 0.1, "as": "x"}},
  "transform": [{"calculate": "sin(datum.x)", "as": "y"}],
  "mark": "line",
  "encoding": {"x": {"field": "x"}, "y": {"field": "y"}}
}
```

## Airport Connections (Geo + Lookup)

Interactive flight route visualization.

**Technique:** Layered geo + `lookup` transforms for coordinates + `nearest` selection.

```json
{
  "layer": [
    {"mark": "geoshape", "data": {"url": "us-10m.json"}},
    {
      "mark": "rule",
      "transform": [
        {"filter": {"param": "org", "empty": false}},
        {"lookup": "origin", "from": {"data": "airports.csv", "key": "iata", "fields": ["latitude", "longitude"]}},
        {"lookup": "destination", "from": {"data": "airports.csv", "key": "iata", "fields": ["latitude", "longitude"]}, "as": ["lat2", "lon2"]}
      ],
      "encoding": {"latitude": {"field": "latitude"}, "longitude": {"field": "longitude"}, "latitude2": {"field": "lat2"}, "longitude2": {"field": "lon2"}}
    },
    {
      "mark": "circle",
      "params": [{"name": "org", "select": {"type": "point", "on": "pointerover", "nearest": true}}],
      "encoding": {"latitude": {"field": "lat"}, "longitude": {"field": "lon"}}
    }
  ],
  "projection": {"type": "albersUsa"}
}
```

## Pattern Summary

| Pattern | Key Techniques | Marks Used |
|---------|---------------|------------|
| Waterfall | window sum, calculate previous | bar, rule, text |
| Parallel Coordinates | fold, joinaggregate normalize | line, text, tick |
| Ternary | calculate x/y from proportions | line, point, text |
| Isotype | rank, emoji calculate | text or point |
| Connected Scatterplot | order encoding, line+point | line (point: true) |
| QQ Plot | quantile transform | point |
| Falkensee | layered rects for periods | rect, line, point |
| Cumulative Avg | window mean with frame | circle, line |
| Top-K Others | row_number + calculate group | bar |
| Residual Graph | joinaggregate mean + delta | point |
| Index Chart | lookup from selection | point, line, rule, text |
| Sequence Lines | sequence data + calculate | line |
| Airport Connections | geo lookup, nearest selection | geoshape, rule, circle |
