# Histograms

Histograms discretize numeric values into bins and count occurrences per bin. Built using `bar` marks with binned encodings.

## Basic Histogram

```json
{
  "data": {"url": "data/movies.json"},
  "mark": "bar",
  "encoding": {
    "x": {"bin": true, "field": "IMDB Rating"},
    "y": {"aggregate": "count"}
  }
}
```

## Binning Approaches

### Bin in Encoding (Simplest)

Set `bin: true` directly on the encoding field. Vega-Lite auto-counts:

```json
{
  "encoding": {
    "x": {"bin": true, "field": "value"},
    "y": {"aggregate": "count"}
  }
}
```

### Bin via Transform (More Control)

Use `bin` transform to create a new field, then encode with `bin: "binned"`:

```json
{
  "transform": [{"bin": true, "field": "IMDB Rating", "as": "binned_rating"}],
  "mark": "bar",
  "encoding": {
    "x": {"field": "binned rating", "bin": {"binned": true, "step": 1}},
    "x2": {"field": "binned rating_end"},
    "y": {"aggregate": "count"}
  }
}
```

Transform approach is more verbose but allows intermediate calculations before encoding.

## Bin Parameters

| Property | Type | Description |
|----------|------|-------------|
| `maxbins` | number | Maximum number of bins (actual may be fewer due to nice rounding) |
| `step` | number | Width of each bin |
| `steps` | [number, number] | Min/max step range |
| `extent` | [number, number] | Domain extent for binning |
| `anchor` | number | Anchor value for bin boundaries |
| `base` | number | Base value for log bins |
| `divide` | number | Divide bins by this value |
| `minstep` | number | Minimum step size |
| `nice` | boolean | Use nice round numbers for boundaries |

### Custom Max Bins

```json
{
  "encoding": {
    "x": {"bin": {"maxbins": 30}, "field": "IMDB Rating"}
  }
}
```

### Bin Spacing

Control gap between bars with `binSpacing` on the mark:

```json
{
  "mark": {"type": "bar", "binSpacing": 3}
}
```

## Histogram Variants

### Ordinal Histogram

Set binned field type to `"ordinal"` for ordinal scale (allows custom sorting, skips empty bins):

```json
{
  "encoding": {
    "x": {"bin": true, "field": "IMDB Rating", "type": "ordinal"},
    "y": {"aggregate": "count"}
  }
}
```

Sort by count:

```json
{
  "encoding": {
    "x": {"bin": true, "field": "value", "type": "ordinal", "sort": "-y"}
  }
}
```

### Relative Frequency Histogram

Use bin transform + joinaggregate to compute proportions:

```json
{
  "transform": [
    {"bin": true, "field": "Horsepower", "as": "bin_hp"},
    {"aggregate": [{"op": "count", "as": "Count"}], "groupby": ["bin_hp", "bin_hp_end"]},
    {"joinaggregate": [{"op": "sum", "field": "Count", "as": "Total"}]},
    {"calculate": "datum.Count/datum.Total", "as": "Percent"}
  ],
  "mark": "bar",
  "encoding": {
    "x": {"field": "bin_hp", "bin": {"binned": true, "step": 60}},
    "x2": {"field": "bin_hp_end"},
    "y": {"field": "Percent", "axis": {"format": ".1~%"}}
  }
}
```

### Log-Scaled Histogram

Bin on log-transformed values, then inverse-transform for axis:

```json
{
  "transform": [
    {"calculate": "log(datum.x)/log(10)", "as": "log_x"},
    {"bin": true, "field": "log_x", "as": "bin_log_x"},
    {"calculate": "pow(10, datum.bin_log_x)", "as": "x1"},
    {"calculate": "pow(10, datum.bin_log_x_end)", "as": "x2"}
  ],
  "mark": "bar",
  "encoding": {
    "x": {"field": "x1", "scale": {"type": "log", "base": 10}},
    "x2": {"field": "x2"},
    "y": {"aggregate": "count"}
  }
}
```

### Nonlinear Bins

Use `calculate` transform before binning for custom bin boundaries.

## Alternative Mark Types

### Circle Histogram

Replace `bar` with `circle` mark for dot-density style:

```json
{
  "mark": "circle",
  "encoding": {
    "x": {"bin": true, "field": "value"},
    "y": {"aggregate": "count"},
    "size": {"aggregate": "count"}
  }
}
```

### Tick Histogram

Use `tick` mark for strip-chart style:

```json
{
  "mark": "tick",
  "encoding": {
    "x": {"bin": true, "field": "value"},
    "y": {"aggregate": "count"}
  }
}
```

## Binned Data (Pre-Binned)

When data is already binned externally, use `bin: "binned"`:

```json
{
  "encoding": {
    "x": {"field": "bin_start", "bin": {"binned": true, "step": 2}},
    "x2": {"field": "bin_end"}
  }
}
```

## Invalid Data Handling

Filter out nulls before binning:

```json
{
  "config": {"mark": {"invalid": "filter"}}
}
```

Other options: `"break"` (gaps), `"show"` (render with defaults).
