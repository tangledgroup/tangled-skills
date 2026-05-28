# Data Types and Scales

## Contents

- Data Types
- Type Inference
- Scale Types
- Scale Properties
- Continuous Scales
- Discrete Scales
- Color Schemes
- Band Position

## Data Types

Vega-Lite uses five data types that describe semantic meaning, not primitive types:

| Type | Description | Typical Scale |
|------|-------------|---------------|
| `quantitative` | Numeric values with meaningful magnitude and zero | linear, log, pow, quantize, quantile, threshold |
| `temporal` | Date/time values (date strings or timestamps) | time, utc |
| `ordinal` | Ordered categories (ranked but not numeric) | ordinal, point, band |
| `nominal` | Unordered categories (labels, names) | ordinal, point, band |
| `geojson` | GeoJSON features for geoshape marks | — |

### Same Primitive, Different Types

Numeric data can be quantitative (`temperature`), ordinal (`rating 1-5`), or nominal (`zip code`). String data can be temporal (`"2024-01-15"`), ordinal (`"small", "medium", "large"`), or nominal (`"red", "blue"`).

### Type with Transforms

- With `bin`: type can be `"quantitative"` (linear bin scale) or `"ordinal"` (ordinal bin scale)
- With `timeUnit`: type can be `"temporal"` (default, temporal scale) or `"ordinal"` (ordinal scale)
- With `aggregate`: type refers to post-aggregation output type

## Type Inference

Vega-Lite auto-infers types in many cases:

- `"quantitative"` if field has `bin`, `aggregate` (except argmin/argmax), uses latitude/longitude, or has a quantitative scale type
- `"temporal"` if field has `timeUnit` or uses time/utc scale
- `"ordinal"` if field has custom `sort`, ordinal/point/band scale, or is the `order` channel
- `"nominal"` is the default for data fields without any of the above

For constant datum values: `"quantitative"` for numbers, `"nominal"` for strings, `"temporal"` for date-time objects.

## Scale Types

Scales transform data domain values to visual range values (pixels, colors, sizes).

### Continuous Scales

| Type | Description |
|------|-------------|
| `linear` | Linear mapping (default for quantitative) |
| `log` | Logarithmic scale. Requires positive values |
| `sqrt` | Square root scale |
| `pow` | Power scale with configurable exponent |
| `time` | Temporal scale for date/time values |
| `utc` | UTC temporal scale |

### Discrete Scales

| Type | Description |
|------|-------------|
| `ordinal` | Ordinal scale mapping discrete values to positions |
| `point` | Point scale placing values at evenly-spaced points within band |
| `band` | Band scale allocating bands of space for each value (default for nominal/ordinal position) |

### Discretizing Scales

| Type | Description |
|------|-------------|
| `quantize` | Continuous domain → discrete range, equal-width bins |
| `quantile` | Continuous domain → discrete range, equal-count bins |
| `threshold` | Continuous domain → discrete range at specified thresholds |

### Color Scales

| Type | Description |
|------|-------------|
| `sequential` | Single-hue color gradient (light to dark) |
| `diverging` | Two-hue gradient meeting at midpoint |
| `categorical` | Distinct colors for each category (default for nominal color) |

## Scale Properties

Common properties for all scales:

| Property | Type | Description |
|----------|------|-------------|
| `type` | String | Scale type |
| `domain` | Array \| Object | Input domain. Can be explicit array or `{"data": ..., "field": ...}` |
| `range` | Array \| Object | Output range (pixel values, colors, etc.) |
| `nice` | Boolean \| Number | Extend domain to nice round numbers. Default: `true` for position, `false` otherwise |
| `zero` | Boolean | Include zero in domain. Default: `true` for position with linear scale and bar/area/tick marks; `false` otherwise |
| `clamp` | Boolean | Clamp output values to range. Default: `false` |
| `round` | Boolean | Round output to integers. Default: `false` |
| `padding` / `paddingInner` / `paddingOuter` | Number | Padding for band scales |
| `reverse` | Boolean | Reverse domain/range mapping. Default: `false` |
| `unknown` | Any | Output value for data values not in domain. Default: `"#999"` for color, otherwise undefined |

### Continuous Scale Properties

| Property | Type | Description |
|----------|------|-------------|
| `exponent` | Number | Exponent for pow scale |
| `base` | Number | Base for log scale |
| `interpolate` | String | Interpolation method for color scales: `"linear"`, `"round"`, etc. |
| `zero` | Boolean | Whether to include zero in domain |

### Discrete Scale Properties

| Property | Type | Description |
|----------|------|-------------|
| `padding` | Number | Padding between bands (band scale). Default: `0.1` |
| `paddingInner` | Number | Inner padding between bands. Default: `0` |
| `paddingOuter` | Number | Outer padding at domain edges. Default: `0.5` |
| `round` | Boolean | Round band size to integers. Default: `true` |

### Color Scale Schemes

Set `scheme` on color scales for predefined color palettes:

```json
{
  "encoding": {
    "color": {
      "field": "category",
      "type": "nominal",
      "scale": {"scheme": "category20"}
    }
  }
}
```

Available schemes: `blues`, `greens`, `oranges`, `reds`, `brown`, `bluegreen`, `bluered`, `goldgreyn`, `grey`, `brbg`, `bgy`, `brgy`, `piyg`, `prgn`, `puor`, `rdbu`, `rdgy`, `rdylbu`, `rdylgn`, `spectral`, `deviant`, `albers`, `bilberiy`, `bluepurple`, `ion`, `magma`, `inferno`, `plasma`, `viridis`, `cividis`, `turbo`, `turbo`, `category10`, `category20`, `category20b`, `category20c`.

## Band Position

For band scales, control mark alignment within bands:

| Value | Description |
|-------|-------------|
| `bandCenter` (default) | Center mark within band |
| `bandLeft` | Align mark to left of band |
| `bandRight` | Align mark to right of band |

Set via encoding field definition:

```json
{
  "x": {
    "field": "month",
    "type": "ordinal",
    "band": "center"
  }
}
```

Or via config:

```json
{
  "config": {
    "scale": {"bandPosition": 0.5}
  }
}
```
