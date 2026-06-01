# Error Marks (Errorbar and Errorband)

Error marks summarize error ranges using summary statistics. `errorbar` uses rule+tick marks, `errorband` uses area marks.

## Errorbar

### Basic Syntax

```json
{
  "data": {"url": "data/cars.json"},
  "mark": {"type": "errorbar", "extent": "ci"},
  "encoding": {
    "x": {"timeUnit": "year", "field": "Year"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

### Errorbar Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `extent` | string | Error range type (see below) |
| `orient` | string | `"vertical"` or `"horizontal"` |
| `color` | string | Color applied to whole errorbar |
| `opacity` | number | Opacity applied to whole errorbar |

### Sub-mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `rule` | object | Mark properties for the rule segments |
| `ticks` | boolean \| object | End ticks (`true` or mark properties) |

### Extent Types (Raw Data Aggregation)

| Value | Description |
|-------|-------------|
| `"stderr"` (default) | Standard error from mean |
| `"stdev"` | Standard deviation from mean |
| `"ci"` | Confidence interval (`ci0` to `ci1`) |
| `"iqr"` | Interquartile range (Q1 to Q3) |

### Errorbar with Raw Data

Vega-Lite aggregates automatically:

```json
{
  "mark": {"type": "errorbar", "extent": "stdev"},
  "encoding": {
    "x": {"field": "category"},
    "y": {"field": "value", "type": "quantitative"}
  }
}
```

### Errorbar with Pre-Aggregated Data (Low/High)

```json
{
  "mark": "errorbar",
  "encoding": {
    "x": {"field": "category"},
    "y": {"field": "low", "type": "quantitative"},
    "y2": {"field": "high"}
  }
}
```

### Errorbar with Pre-Aggregated Data (Center + Error)

**Symmetric error** (one error value):

```json
{
  "mark": "errorbar",
  "encoding": {
    "x": {"field": "category"},
    "y": {"field": "center", "type": "quantitative"},
    "yError": {"field": "error"}
  }
}
```

**Asymmetric error** (positive and negative):

```json
{
  "mark": "errorbar",
  "encoding": {
    "x": {"field": "category"},
    "y": {"field": "center"},
    "yError": {"field": "error_low"},   // negative value
    "yError2": {"field": "error_high"}  // positive value
  }
}
```

### 1D Errorbar (Global)

Single error range for entire dataset:

```json
{
  "mark": "errorbar",
  "encoding": {
    "x": {"aggregate": "mean", "field": "value"}
  }
}
```

### 2D Errorbar (Categorical)

```json
{
  "mark": {"type": "errorbar", "extent": "ci"},
  "encoding": {
    "x": {"timeUnit": "year", "field": "Year"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

### Custom Ticks

```json
{
  "mark": {"type": "errorbar", "extent": "ci", "ticks": true}
}
```

Or with custom styling:

```json
{
  "mark": {"type": "errorbar", "ticks": {"color": "teal"}}
}
```

### Errorbar Config

```json
{
  "config": {
    "errorbar": {
      "extent": "ci",
      "rule": {"strokeWidth": 2},
      "ticks": true
    }
  }
}
```

**Note**: `color`, `opacity`, and `orient` not supported in config.

---

## Errorband

Errorband is identical to errorbar but uses **area marks** instead of rules/ticks.

### Basic Syntax

```json
{
  "data": {"url": "data/cars.json"},
  "mark": {"type": "errorband", "extent": "ci"},
  "encoding": {
    "x": {"timeUnit": "year", "field": "Year"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

### Errorband Mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `extent` | string | Error range type (same as errorbar) |
| `orient` | string | `"vertical"` or `"horizontal"` |
| `color` | string | Color applied to whole errorband |
| `opacity` | number | Opacity applied to whole errorband |
| `interpolate` | string | Line interpolation method |
| `tension` | number | Cubic spline tension (0-1) |

### Sub-mark Properties

| Property | Type | Description |
|----------|------|-------------|
| `band` | object | Mark properties for the area band |
| `borders` | boolean \| object | Border lines (`true` or mark properties) |

### Errorband with Borders

```json
{
  "mark": {"type": "errorband", "extent": "ci", "borders": true}
}
```

### Custom Border Styling

```json
{
  "mark": {
    "type": "errorband",
    "extent": "ci",
    "borders": {"strokeDash": [6, 3], "opacity": 0.5}
  }
}
```

### Errorband with Pre-Aggregated Data

```json
{
  "mark": "errorband",
  "encoding": {
    "x": {"field": "date", "type": "temporal"},
    "y": {"field": "low", "type": "quantitative"},
    "y2": {"field": "high"}
  }
}
```

### 1D Errorband (Global)

```json
{
  "mark": "errorband",
  "encoding": {
    "x": {"field": "value", "type": "quantitative"},
    "y": {"aggregate": "mean", "field": "value"}
  }
}
```

### 2D Errorband (Time Series)

```json
{
  "mark": {"type": "errorband", "extent": "ci"},
  "encoding": {
    "x": {"timeUnit": "year", "field": "Year"},
    "y": {"field": "Miles_per_Gallon", "type": "quantitative"}
  }
}
```

### Errorband Config

```json
{
  "config": {
    "errorband": {
      "extent": "ci",
      "band": {"opacity": 0.3},
      "borders": true
    }
  }
}
```

## Tooltips

Custom tooltips override defaults:

```json
{
  "mark": "errorbar",
  "encoding": {
    "tooltip": {"field": "variety", "type": "ordinal"}
  }
}
```

## Errorbar vs Errorband Comparison

| Feature | `errorbar` | `errorband` |
|---------|-----------|-------------|
| Visual | Rules + ticks | Area band (+ borders) |
| Sub-marks | `rule`, `ticks` | `band`, `borders` |
| Interpolation | N/A | Supports all methods |
| Best for | Discrete categories | Continuous/time series |
| Layering | Overlay with points | Overlay with lines |

### Typical Compositions

**Errorbar + Points**:

```json
{
  "layer": [
    {"mark": "point", "encoding": {"x": {"field": "cat"}, "y": {"aggregate": "mean", "field": "val"}}},
    {"mark": "errorbar", "encoding": {"x": {"field": "cat"}, "y": {"field": "val"}}}
  ]
}
```

**Errorband + Line**:

```json
{
  "layer": [
    {"mark": "line", "encoding": {"x": {"field": "date"}, "y": {"aggregate": "mean", "field": "val"}}},
    {"mark": "errorband", "encoding": {"x": {"field": "date"}, "y": {"field": "val"}}}
  ]
}
```
