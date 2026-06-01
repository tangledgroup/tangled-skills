# Transforms

Transforms derive new data from existing data. Applied in order within the `transform` array. Each transform reads the output of the previous one.

## Transform Overview

| Transform | Purpose |
|-----------|---------|
| `aggregate` | Group and summarize data |
| `bin` | Discretize numeric fields into bins |
| `calculate` | Create new fields from expressions |
| `density` | Kernel density estimation |
| `extent` | Find field extent into a parameter |
| `filter` | Remove records by predicate |
| `flatten` | Expand array fields into rows |
| `fold` | Collapse fields into key-value pairs (wide → long) |
| `impute` | Fill in missing data points |
| `joinaggregate` | Augment records with aggregate values |
| `loess` | Locally-estimated regression trend lines |
| `lookup` | Join data from a secondary source |
| `pivot` | Transpose rows into columns (long → wide) |
| `quantile` | Calculate empirical quantiles |
| `regression` | Fit parametric regression models |
| `sample` | Random subsample of data |
| `stack` | Compute stacked offsets |
| `timeUnit` | Discretize temporal fields |
| `window` | Sliding window calculations |

---

## Aggregate

Summarize data into groups. Produces one record per group.

```json
{
  "transform": [
    {"aggregate": [{"op": "mean", "field": "Acceleration", "as": "avg_accel"}], "groupby": ["Cylinders"]}
  ]
}
```

### Operations

| Op | Description |
|----|-------------|
| `count`, `sum`, `mean`, `variance`, `variancep`, `stdev`, `stdevp`, `median`, `q1`, `q3`, `iqr`, `min`, `max` | Standard aggregations |
| `argmin`, `argmax` | Record with min/max value |
| `argsort` | Records sorted by field |

### Encoding vs Transform

In encoding: `"y": {"aggregate": "mean", "field": "value"}` — simpler, auto-grouping.
In transform: explicit control over groupby and multiple ops.

---

## Bin

Discretize a numeric field into bins.

```json
{
  "transform": [{"bin": true, "field": "IMDB Rating", "as": "binned_rating"}]
}
```

### Bin Parameters

| Property | Description |
|----------|-------------|
| `maxbins` | Maximum number of bins (actual may be fewer) |
| `step` | Width of each bin |
| `extent` | [min, max] domain for binning |
| `anchor` | Anchor value for boundaries |

### Binned Data Flag

For pre-binned data, use `bin: {"binned": true}` in encoding with `field` and `field_end`.

---

## Calculate

Create new fields using [Vega expressions](https://vega.github.io/vega/docs/api/expression/).

```json
{
  "transform": [{"calculate": "datum.open < datum.close ? 'up' : 'down'", "as": "direction"}]
}
```

Reference current data object via `datum`. Supports all JavaScript math, string, and array operations.

---

## Density

Kernel density estimation for smooth distribution curves.

```json
{
  "transform": [{"density": "Horsepower", "groupby": ["Origin"], "bandwidth": 20}]
}
```

### Properties

| Property | Description |
|----------|-------------|
| `density` | Field to estimate density for |
| `groupby` | Fields to group by (separate curves) |
| `bandwidth` | Smoothing bandwidth |
| `extent` | [min, max] extent of output points |
| `steps` | Number of subdivision steps |
| `counts` | Multiply densities by group size (for stacked areas) |
| `cumulative` | Cumulative density |
| `as` | Output field name (default `"density"`) |

### Stacked Density

Use shared `extent`, fixed `steps`, and `counts: true` for proportional stacked areas.

---

## Extent

Find the min/max of a field and store in a parameter.

```json
{
  "transform": [{"extent": "b", "param": "b_extent"}]
}
```

Output: `{min: 19, max: 91}` accessible via `param.b_extent`.

---

## Filter

Remove records by predicate.

```json
{
  "transform": [{"filter": "datum.location == 'Seattle'"}]
}
```

### Predicate Forms

**Expression string:** `"datum.value > 60"`

**Field predicates:**

| Predicate | Example |
|-----------|---------|
| `equal` | `{"field": "color", "equal": "red"}` |
| `lt`, `lte` | `{"field": "height", "lt": 180}` |
| `gt`, `gte` | `{"field": "score", "gte": 0}` |
| `range` | `{"field": "x", "range": [0, 5]}` |
| `oneOf` | `{"field": "color", "oneOf": ["red", "blue"]}` |
| `valid` | `{"field": "value", "valid": true}` |

**Parameter predicate:** `{"param": "brush"}` — filter by selection.

**Composition:** `{"and": [...], "or": [...], "not": {...}}`

---

## Flatten

Expand array-valued fields into separate rows.

```json
{
  "transform": [{"flatten": ["foo", "bar"]}]
}
```

Shorter arrays are padded with `null`. Use `as` to rename output fields.

---

## Fold

Collapse multiple fields into key-value pairs (wide → long format).

```json
{
  "transform": [{"fold": ["gold", "silver", "bronze"]}]
}
```

Output adds `key` (field name) and `value` (field value). Use `as: [key_name, value_name]` to customize.

### Fold vs Flatten

- `fold`: known field names → key/value pairs
- `flatten`: array-valued fields → one row per element

---

## Impute

Fill in missing data points.

### In Encoding (Auto-Grouping)

```json
{
  "encoding": {
    "x": {"field": "a", "impute": {"value": 0}},
    "y": {"field": "b"}
  }
}
```

### Via Transform

```json
{
  "transform": [
    {"impute": "b", "key": "a", "groupby": ["c"], "value": 0}
  ]
}
```

### Properties

| Property | Description |
|----------|-------------|
| `keyvals` | Explicit key values to impute (array or `{start, stop, step}` sequence) |
| `method` | `"mean"`, `"median"`, `"min"`, `"max"` (instead of constant value) |
| `frame` | Window `[preceding, following]` for method calculations |
| `value` | Constant imputation value |

---

## Join Aggregate

Augment each record with aggregate values (preserves original rows).

```json
{
  "transform": [
    {"joinaggregate": [{"op": "sum", "field": "Count", "as": "Total"}], "groupby": ["category"]}
  ]
}
```

### Common Patterns

**Percent of total:** joinaggregate sum → calculate `datum.Count / datum.Total`

**Difference from mean:** joinaggregate mean → calculate residual

---

## Loess

Locally-estimated scatterplot smoothing for trend lines.

```json
{
  "transform": [{"loess": "y", "on": "x", "bandwidth": 0.5}]
}
```

### Properties

| Property | Description |
|----------|-------------|
| `loess` | Response field |
| `on` | Predictor field |
| `bandwidth` | Smoothing parameter (0-1) |
| `groupby` | Separate curves per group |

---

## Lookup

Join data from a secondary source (one-sided join).

```json
{
  "transform": [
    {"lookup": "person", "from": {"data": "secondary", "key": "name", "fields": ["age", "height"]}}
  ]
}
```

### Lookup Selection

Use `{"param": "selection_name"}` instead of data reference for interactive lookups.

---

## Pivot

Transpose unique field values into columns (long → wide).

```json
{
  "transform": [{"pivot": "type", "value": "count", "groupby": ["country"]}]
}
```

Inverse of `fold`. Supports `op` for aggregation, `limit` for max columns.

---

## Quantile

Calculate empirical quantiles.

```json
{
  "transform": [{"quantile": "measure", "probs": [0.25, 0.5, 0.75]}]
}
```

Or with `step`: `{"quantile": "measure", "step": 0.05}` for equal-sized steps.

Output: `[{prob: 0.25, value: 1.34}, ...]`

---

## Regression

Fit parametric regression models.

```json
{
  "transform": [{"regression": "y", "on": "x", "method": "linear"}]
}
```

### Methods

| Method | Formula |
|--------|---------|
| `linear` | y = a + b\*x |
| `log` | y = a + b\*log(x) |
| `exp` | y = a\*e^(b\*x) |
| `pow` | y = a\*x^b |
| `quad` | y = a + b\*x + c\*x² |
| `poly` | y = a + b\*x + ... + k\*x^n (use `order`) |

### Properties

| Property | Description |
|----------|-------------|
| `params` | If `true`, output model parameters instead of trend line points |
| `extent` | [min, max] for output x values |

---

## Sample

Random subsample using reservoir sampling.

```json
{"transform": [{"sample": 500}]}
```

Maintains representative sample as data flows through.

---

## Stack

Compute stacked offsets for bars and areas.

### In Encoding (Auto)

Adding a `color` field to bar/area marks auto-stacks. Use `stack: "normalize"` for percentage, `stack: "center"` for streamgraph, `stack: null` for layering.

### Via Transform

```json
{
  "transform": [
    {"stack": "population", "groupby": ["age"], "offset": "zero", "sort": [{"field": "gender"}], "as": ["pop_lo", "pop_hi"]}
  ]
}
```

| Offset | Description |
|--------|-------------|
| `"zero"` (default) | Standard stacking from zero |
| `"normalize"` | Percentage stacked (0-1) |
| `"center"` | Streamgraph (centered around 0) |

---

## Time Unit

Discretize temporal fields. Prefer in encoding over transform.

### Units

`year`, `quarter`, `month`, `date`, `week`, `day`, `dayofyear`, `hours`, `minutes`, `seconds`, `milliseconds`. Composable: `yearmonthdate`, `monthdate`.

Prefixes: `utc` (UTC time), `binned` (pre-binned data).

### In Encoding

```json
{"x": {"timeUnit": "month", "field": "date", "type": "ordinal"}}
```

### Via Transform

```json
{"transform": [{"timeUnit": "month", "field": "date", "as": "month_of_year"}]}
```

### Parameters

| Property | Description |
|----------|-------------|
| `step` | Bin size (e.g., 5 for 5-minute intervals) |
| `maxbins` | Maximum number of time bins |
| `utc` | Use UTC time |

---

## Window

Sliding window calculations over sorted groups.

```json
{
  "transform": [
    {
      "window": [{"op": "sum", "field": "count", "as": "cumulative"}],
      "sort": [{"field": "bin_start"}],
      "frame": [null, 0]
    }
  ]
}
```

### Properties

| Property | Description |
|----------|-------------|
| `frame` | `[preceding, following]` — `null` = unbounded, `0` = current row |
| `ignorePeers` | Whether to include peer values in frame |
| `groupby` | Partition data into separate windows |
| `sort` | Order records within each partition |

### Window-Only Operations

| Op | Parameter | Description |
|----|-----------|-------------|
| `row_number` | — | Consecutive row number from 1 |
| `rank` | — | Rank with gaps for ties |
| `dense_rank` | — | Rank without gaps |
| `percent_rank` | — | Percentage rank (0-1) |
| `cume_dist` | — | Cumulative distribution |
| `ntile` | number | Quantile bucket assignment |
| `lag` | offset | Value from preceding row |
| `lead` | offset | Value from following row |
| `first_value` | — | First value in frame |
| `last_value` | — | Last value in frame |
| `nth_value` | n | Nth value in frame |

### Common Patterns

**Cumulative sum:** `frame: [null, 0]`, `op: "sum"`

**Running average:** `frame: [null, 0]`, `op: "mean"`

**Top-K:** `rank` + filter on rank

**Difference from previous:** `lag` with offset 1

---

## Transform Order

Transforms execute in array order. Common pipelines:

1. `filter` → reduce data early
2. `calculate` → derive helper fields
3. `bin` / `timeUnit` → discretize
4. `aggregate` / `joinaggregate` → summarize
5. `window` → sliding calculations
6. `fold` / `flatten` → reshape
