# Transforms

## Contents

- Transform Execution Order
- Aggregate
- Bin
- Calculate
- Density
- Extent
- Filter
- Flatten
- Fold
- Impute
- Join Aggregate
- Loess
- Lookup
- Pivot
- Quantile
- Regression
- Sample
- Stack
- Time Unit
- Window

## Transform Execution Order

View-level `transform` array executes first, in order. Then inline encoding transforms execute in this fixed order: `bin` → `timeUnit` → `aggregate` → `sort` → `stack`.

```json
{
  "data": { ... },
  "transform": [
    {"filter": "datum.year > 2000"},
    {"calculate": "datum.a + datum.b", "as": "sum"}
  ],
  "mark": "bar",
  "encoding": {
    "x": {"bin": true, "field": "value"},
    "y": {"aggregate": "count"}
  }
}
```

## Aggregate

Compute aggregate values (sum, mean, etc.) grouped by unaggregated fields.

### In Encoding (inline)

```json
"y": {"aggregate": "mean", "field": "price", "type": "quantitative"}
```

### As Transform

```json
{
  "aggregate": [
    {"op": "mean", "field": "price", "as": "avgPrice"},
    {"op": "count", "as": "count"}
  ],
  "groupby": ["category"]
}
```

### Supported Operations

| Op | Description |
|----|-------------|
| `sum` / `mean` / `median` | Sum, mean, median |
| `min` / `max` | Minimum, maximum |
| `count` / `distinct` | Count all rows, count distinct values |
| `variance` / `stddev` | Variance, standard deviation |
| `argmin` / `argmax` | Full record at min/max value |

## Bin

Bin quantitative data into intervals.

### In Encoding (inline)

```json
"x": {"bin": true, "field": "IMDB Rating"}
```

### As Transform

```json
{
  "bin": true,
  "field": "IMDB Rating",
  "as": ["bin_start", "bin_end"]
}
```

### Bin Parameters

| Property | Type | Description |
|----------|------|-------------|
| `binned` | Boolean | Whether data is pre-binned. Default: `false` |
| `maxbins` | Number | Maximum number of bins. Default: inferred from view size |
| `nice` | Boolean | Use nice round bin boundaries. Default: `true` |
| `divide` | Number | Exact bin width |
| `step` | Number | Approximate pixel width per bin |
| `extent` | Array | Explicit `[min, max]` domain extent |

### Ordinal Bin

Use `"ordinal"` type with `bin` to get an ordinal scale over bins, preserving bin order without linear interpolation.

## Calculate

Create new fields using Vega expression syntax:

```json
{
  "calculate": "datum.open < datum.close ? 'up' : 'down'",
  "as": "direction"
}
```

Vega expressions support standard math, string, date, and array operations. Access fields via `datum.fieldName`.

## Density

Compute kernel density estimates:

```json
{
  "density": "IMDB Rating",
  "bandwidth": 0.3
}
```

### Parameters

| Property | Type | Description |
|----------|------|-------------|
| `density` | String | Field to compute density for |
| `bandwidth` | Number | Smoothing bandwidth. Default: auto-selected |
| `counts` | Boolean | Include raw counts. Default: `true` |
| `extend` | String | Extension beyond data extent: `"auto"` (default), `"data"`, or number |
| `groupby` | String[] | Group by fields for separate densities |

Output fields: `value` (x position), `density` (y value), optionally `count`.

## Extent

Compute the extent (min/max) of a field:

```json
{
  "extent": {"field": "price"},
  "as": ["priceMin", "priceMax"]
}
```

## Filter

Remove data rows based on predicates:

```json
{"filter": "datum.year > 2000"}
```

### Predicate Types

**Field predicate:**

```json
{
  "filter": {
    "field": "year",
    "range": [2000, 2010]
  }
}
```

Supported tests: `equal`, `oneOf`, `range`, `valid`, `lt`, `lte`, `gt`, `gte`.

**Parameter predicate:**

```json
{"filter": {"param": "brush"}}
```

**Composition:**

```json
{
  "filter": {
    "and": [
      {"field": "year", "gt": 2000},
      {"field": "price", "valid": true}
    ]
  }
}
```

## Flatten

Unpack array fields into separate rows:

```json
{
  "flatten": ["tags", "categories"],
  "as": ["tag", "category"]
}
```

Creates a row for each combination of array elements.

## Fold

Pivot multiple fields into key-value pairs (long form):

```json
{
  "fold": ["Beak Length (mm)", "Beak Depth (mm)", "Flipper Length (mm)"],
  "as": ["key", "value"]
}
```

Useful for parallel coordinate plots and multi-measure charts.

## Impute

Fill in missing combinations of data:

### In Encoding (inline)

```json
"x": {
  "timeUnit": "month",
  "field": "date",
  "type": "ordinal",
  "impute": {"method": "mean"}
}
```

### As Transform

```json
{
  "impute": "date",
  "key": {"field": "date", "timeUnit": "month"},
  "groupby": ["category"],
  "method": {"type": "mean", "field": "value"},
  "frame": [-null, null]
}
```

### Methods

| Method | Description |
|--------|-------------|
| `"value"` | Constant value |
| `"mean"` / `"median"` / `"max"` / `"min"` / `"zero"` / `"sequence"` | Aggregate or sequential imputation |

## Join Aggregate

Compute aggregates and join back to original data (like SQL window functions without partitioning):

```json
{
  "joinaggregate": [
    {"op": "mean", "field": "yield", "as": "avgYield"}
  ],
  "groupby": ["site"]
}
```

Common use: computing residuals, percentage of total, or adding summary statistics to each row.

## Loess

Local regression smoothing:

```json
{
  "loess": "price",
  "on": "date",
  "groupby": ["symbol"],
  "bandwidth": 0.25
}
```

### Parameters

| Property | Type | Description |
|----------|------|-------------|
| `loess` | String | Field to predict (response) |
| `on` | String | Field to regress on (predictor) |
| `groupby` | String[] | Grouping fields |
| `bandwidth` | Number | Smoothing parameter [0,1]. Default: `0.35` |
| `extent` | String | `"full"` (default) or `"data"` |

Output field: `loess_<fieldName>`.

## Lookup

Join data from another source by key:

```json
{
  "lookup": "id",
  "from": {
    "data": {"url": "data/unemployment.tsv"},
    "key": "id",
    "fields": ["rate"]
  }
}
```

### Parameters

| Property | Type | Description |
|----------|------|-------------|
| `lookup` | String | Key field in primary data |
| `from.data` | Data | Secondary data source |
| `from.key` | String | Key field in secondary data |
| `from.fields` | String[] | Fields to bring from secondary data |
| `as` | String \| String[] | Output field name(s) |
| `default` | Object | Default values for non-matching rows |

## Pivot

Pivot data from long to wide format:

```json
{
  "pivot": "key",
  "value": "value",
  "groupby": ["id"],
  "rename": {"A": "colA", "B": "colB"}
}
```

## Quantile

Compute quantiles of a distribution:

```json
{
  "quantile": "price",
  "as": ["q", "val"],
  "probs": [0.25, 0.5, 0.75]
}
```

Output: one row per probability with quantile value.

## Regression

Fit regression lines:

```json
{
  "regression": "price",
  "on": "date",
  "groupby": ["symbol"],
  "method": "linear"
}
```

### Parameters

| Property | Type | Description |
|----------|------|-------------|
| `regression` | String | Response field |
| `on` | String | Predictor field |
| `groupby` | String[] | Grouping fields |
| `method` | String | `"linear"` (default), `"log"`, `"exp"`, `"pow"` |
| `extent` | Object | `{start: ..., end: ...}` for prediction range |
| `predict` | String | Field to predict (defaults to regression field) |

Output fields: `<on>`, `regression_<regressionField>`.

## Sample

Randomly sample N rows:

```json
{
  "sample": 500
}
```

Use for large datasets to improve performance. Supports `seed` for reproducibility.

## Stack

Stack values along a position channel (for stacked bar/area charts).

### In Encoding (inline)

```json
"y": {
  "aggregate": "sum",
  "field": "count",
  "stack": "zero"
}
```

### As Transform

```json
{
  "stack": "count",
  "groupby": ["date"],
  "field": "count_stack",
  "offset": "zero"
}
```

### Offset Types

| Offset | Description |
|--------|-------------|
| `"zero"` | Standard stacking from zero baseline (default) |
| `"center"` | Centered stacking (streamgraph) |
| `"normalize"` | Normalized to 100% |

Output fields: `<field>_stack` (start), `<field>_stack2` (end).

## Time Unit

Extract temporal units from date/time fields.

### In Encoding (inline)

```json
"x": {"timeUnit": "month", "field": "date", "type": "ordinal"}
```

### As Transform

```json
{
  "timeUnit": "yearmonth",
  "field": "date",
  "as": "ym"
}
```

### Time Unit Types

| Type | Description |
|------|-------------|
| `year` / `quarter` / `month` / `week` / `day` / `dayofyear` | Single units |
| `hours` / `minutes` / `seconds` / `milliseconds` | Time units |
| `yearquarter` / `yearmonth` / `yearmonthdate` / `yearmonthdatehours` | Compound units |
| `monthdate` / `monthdatehours` / `dayhour` / `dayhours` | Compound without year |
| `hoursminutes` / `minutesseconds` | Time compound units |

Add `"utc"` prefix for UTC time (e.g., `"yearmonthutc"`).

### Time Unit Parameters

```json
{
  "timeUnit": {"type": "month", "step": 3},
  "field": "date"
}
```

`step` controls granularity grouping (e.g., `step: 3` groups months into quarters).

## Window

Compute window (running) aggregations:

```json
{
  "window": [
    {"op": "sum", "field": "amount", "as": "runningTotal"},
    {"op": "mean", "field": "amount", "as": "movingAvg", "frame": [-3, 0]}
  ],
  "sort": [{"field": "date", "order": "ascending"}]
}
```

### Window Operations

| Op | Description |
|----|-------------|
| `sum` / `mean` / `min` / `max` / `count` | Aggregations over window |
| `variance` / `stddev` | Variance, standard deviation |
| `row_number` / `rank` / `dense_rank` | Ranking operations |
| `percent_rank` / `cume_dist` | Relative rank |
| `ntile` | Bucket number (N buckets) |
| `lag` / `lead` | Previous/next value (with optional offset) |
| `first_value` / `last_value` / `nth_value` | Specific position values |
| `over` | Running count of non-null values |
| `ignore_nulls` | Boolean flag for null handling |

### Frame

Controls the window range relative to current row:

- `[null, null]` — entire partition (default)
- `[-5, 0]` — current row and 5 preceding
- `[0, 5]` — current row and 5 following
- `[-2, 2]` — symmetric window of 5 rows
