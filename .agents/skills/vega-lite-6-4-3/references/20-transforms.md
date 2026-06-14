# Transforms Reference

Transforms process data before encoding. They are applied in order as an array of operations.

## Filter

Remove data rows matching a condition:

```vega-lite
"transform": [
  {"filter": "datum.year == 2000"},
  {"filter": "datum.Horsepower > 100"}
]
```

Multiple conditions with `and`/`or`:

```vega-lite
"transform": [
  {
    "filter": "datum.year >= 1990 && datum.year <= 2000"
  }
]
```

## Aggregate

Compute aggregations (also available inline in encoding):

```vega-lite
"transform": [
  {
    "groupby": ["Origin"],
    "fields": ["Horsepower"],
    "ops": ["mean"],
    "as": ["MeanHP"]
  }
]
```

Available ops: `sum`, `mean`, `median`, `min`, `max`, `count`, `stddev`, `variance`, `ci0`, `ci1`, `q1`, `q3`, `stdev`.

## Bin

Group continuous values into bins:

```vega-lite
"encoding": {
  "x": {"field": "Horsepower", "bin": true, "type": "quantitative"},
  "y": {"aggregate": "count"}
}
```

Custom bin configuration:

```vega-lite
"transform": [
  {"bin": {"field": "Horsepower", "maxbins": 10, "extent": [50, 250]}}
]
```

## TimeUnit

Truncate temporal fields to specific units:

```vega-lite
"encoding": {
  "x": {"timeUnit": "yearmonth", "field": "date", "type": "temporal"}
}
```

Available time units: `year`, `quarter`, `month`, `week`, `day`, `hour`, `minute`, `second`, and compositions like `yearmonth`, `yearmonthdate`, `monthdate`, `yearquarter`.

## Join Aggregate

Compute aggregate values across the entire dataset or groups, joined back to each row:

```vega-lite
"transform": [
  {
    "joinaggregate": [
      {"op": "mean", "field": "Horsepower", "as": "MeanHP"}
    ]
  }
]
```

With grouping:

```vega-lite
"transform": [
  {
    "joinaggregate": [
      {"op": "mean", "field": "Horsepower", "as": "MeanHP"}
    ],
    "groupby": ["Origin"]
  }
]
```

## Window

Compute window (running) aggregations:

```vega-lite
"transform": [
  {
    "window": [
      {"op": "mean", "field": "price", "as": "movingAvg"}
    ],
    "frame": [-5, 0]  // 5-row trailing window
  }
]
```

## Fold

Pivot multiple fields into key-value pairs (long format):

```vega-lite
"transform": [
  {"fold": ["Horsepower", "Miles_per_Gallon"]},
  {
    "calculate": "datum.key == 'Horsepower' ? datum.value / 100 : datum.value",
    "as": "normalized"
  }
]
```

## Calculate

Create computed fields:

```vega-lite
"transform": [
  {
    "calculate": "datum.Horsepower / datum.Miles_per_Gallon",
    "as": "hpPerMpg"
  }
]
```

## Flatten

Expand array fields into separate rows:

```vega-lite
"transform": [
  {"flatten": ["tags"]}
]
```

## Pivot

Transform rows into columns (wide format):

```vega-lite
"transform": [
  {
    "groupby": ["date"],
    "pivot": "symbol",
    "value": "price"
  }
]
```

## Impute

Fill in missing values for temporal sequences:

```vega-lite
"transform": [
  {
    "impute": "symbol",
    "key": {"field": "date", "timeUnit": "yearmonth"},
    "frame": [null, null],
    "groupby": ["symbol"]
  }
]
```

## Extend

Add fields from a join aggregate without grouping:

```vega-lite
"transform": [
  {
    "extend": [
      {"op": "sum", "field": "value", "as": "total"}
    ],
    "groupby": ["category"]
  }
]
```

## Stack

Manually stack data (usually automatic for bar/area):

```vega-lite
"transform": [
  {
    "stack": "value",
    "groupby": ["date"],
    "field1": "val0",
    "field2": "val1"
  }
]
```

## Gotchas

- Transforms are applied in order — each transform operates on the output of the previous one.
- `joinaggregate` computes across all rows and joins back; `aggregate` reduces to summary rows.
- `timeUnit` in transforms truncates dates; combine with `"format"` on axes for display control.
- `calculate` uses Vega expressions with `datum.` prefix for field references.
- `window` transforms require `frame` to define the window range (e.g., `[-5, 0]` for trailing 5 rows).
- For large datasets, apply `filter` and `sample` early in the transform pipeline for performance.
