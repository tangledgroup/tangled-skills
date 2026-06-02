# Scales & Projections

## Contents
- Scale Properties
- Quantitative Scales
- Discrete Scales
- Discretizing Scales
- Scale Bins
- Scale Domains
- Scale Ranges
- Projection Properties
- Projection Types

## Scale Properties

Scales map data values (numbers, dates, categories) to visual values (pixels, colors, sizes).

| Property | Type | Description |
|----------|------|-------------|
| `name` | String | **Required.** Unique name (shared namespace with projections) |
| `type` | String | Scale type. Default: `"linear"` |
| `domain` | Array / Signal / DataRef | Input data values for the scale |
| `domainMax` | Number | Override maximum in domain (continuous scales only) |
| `domainMin` | Number | Override minimum in domain (continuous scales only) |
| `domainMid` | Number | Insert mid-point in two-element domain (diverging color scales) |
| `domainRaw` | Array | Directly override domain with raw values (for panning/zooming) |
| `interpolate` | String / Object | Interpolation method for range values: `"rgb"`, `"hsl"`, `"lab"`, `"hcl"`, `"cubehelix"`, etc. |
| `range` | Array / Scheme / String | Output visual values (pixels, colors, sizes) |
| `reverse` | Boolean | Reverse the order of the range (default: `false`) |
| `round` | Boolean | Round numeric outputs to integers (pixel snapping, default: `false`) |

## Quantitative Scales

Map continuous domains (numbers or dates) to continuous ranges.

| Property | Type | Description |
|----------|------|-------------|
| `bins` | Array / Object | Bin boundaries for axis/legend tick marks (≥5.0) |
| `clamp` | Boolean | Clamp output to range (default: `false`) |
| `padding` | Number | Expand domain by pixels on each side (range must be pixels) |
| `nice` | Boolean / Number | Extend domain to nice round values (default: `false`) |
| `zero` | Boolean | Include zero in domain (default: `true` for linear/sqrt/pow) |

### Scale Types

| Type | Formula | Notes |
|------|---------|-------|
| `linear` | y = mx + b | Proportional differences preserved. Default domain: [0,1], range: [0,1] |
| `log` | y = m·log(x) + b | Domain must be strictly positive or strictly negative. Property: `base` (default: 10) |
| `pow` | y = mx^k + b | Exponential transform. Property: `exponent` (default: 1) |
| `sqrt` | y = mx^0.5 + b | Shorthand for pow with exponent 0.5 |
| `symlog` | Symmetric log (≥5.0) | Supports non-positive numbers like log. Property: `constant` (default: 1) |
| `time` | Temporal domain | Uses local timezone. Default domain: [2000-01-01, 2000-01-02] |
| `utc` | Temporal domain | Uses UTC. Same properties as time |
| `sequential` | **Deprecated** (≥5.0) | Use linear scale with color-valued range instead |

### Time/UTC Scale `nice` Property
Can be a string for time interval: `"millisecond"`, `"second"`, `"minute"`, `"hour"`, `"day"`, `"week"`, `"month"`, `"year"`. Or an object: `{"interval": "month", "step": 3}` for quarterly boundaries.

## Discrete Scales

Map discrete domains to discrete ranges.

### Ordinal Scales
Lookup table from domain values to range values.

```json
{
  "name": "color",
  "type": "ordinal",
  "domain": {"data": "table", "field": "category"},
  "range": {"scheme": "category20"}
}
```

### Band Scales
Map discrete domain to continuous range with uniform bands (for bar charts).

| Property | Type | Description |
|----------|------|-------------|
| `align` | Number | Alignment within band (0–1, default: 0.5 = centered) |
| `domainImplicit` | Boolean | Auto-extend domain with new values (default: `false`) |
| `padding` | Number | Same paddingInner and paddingOuter (default: 0) |
| `paddingInner` | Number | Spacing within each band (default: 0) |
| `paddingOuter` | Number | Spacing at ends of range (default: 0) |

### Point Scales
Variant of band scale with zero internal band width (for scatterplots).

| Property | Type | Description |
|----------|------|-------------|
| `align` | Number | Alignment within range (0–1, default: 0.5) |
| `padding` | Number | Alias for paddingOuter (default: 0) |
| `paddingOuter` | Number | Outer spacing (default: 0) |

## Discretizing Scales

Break continuous domain into discrete segments.

### Quantile Scales
Map input values to quantile boundaries. Domain is sample values; range cardinality determines number of quantiles.

```json
{
  "name": "color",
  "type": "quantile",
  "domain": {"data": "table", "field": "value"},
  "range": {"scheme": "plasma", "count": 5}
}
```

### Quantize Scales
Divide continuous domain into uniform segments.

| Property | Type | Description |
|----------|------|-------------|
| `nice` | Boolean / Number | Extend to nice round values |
| `zero` | Boolean | Include zero in domain (default: `false`) |

### Threshold Scales
Map arbitrary domain subsets to discrete range values. Domain has N thresholds, range must have N+1 elements.

```json
{
  "name": "threshold",
  "type": "threshold",
  "domain": [0, 1],
  "range": ["red", "white", "blue"]
}
```

### Bin-Ordinal Scales
For use with data subdivided into bins (e.g., via `bin` transform). Provides bin-aware routines for legends.

| Property | Type | Description |
|----------|------|-------------|
| `bins` | Array / Object | Bin boundaries (signal reference or spec object) |

## Scale Bins

Bin boundaries for `bin-ordinal` scales and quantitative scale `bins` property:

| Property | Type | Description |
|----------|------|-------------|
| `start` | Number | Lowest bin boundary (default: min of domain) |
| `stop` | Number | Highest bin boundary (default: max of domain) |
| `step` | Number | **Required.** Bin interval width |

## Scale Domains

### Array Literal
```json
"domain": [0, 500]
```

### Signal Reference
```json
"domain": {"signal": "myDomain"}
```

### Data Reference (single field)
```json
"domain": {"data": "table", "field": "value"}
```

### Multi-Field Data Reference
```json
"domain": {
  "fields": [
    {"data": "table1", "field": "price"},
    {"data": "table2", "field": "cost"}
  ]
}
```

### Sorting Domains
```json
"domain": {
  "data": "table",
  "field": "category",
  "sort": {"op": "median", "field": "value", "order": "descending"}
}
```

Sort operations: `count`, `min`, `max`, `mean`, `median`. Multi-field domains only support `count`, `min`, `max`.

## Scale Ranges

| Value | Description |
|-------|-------------|
| `[0, 500]` | Array literal of range values |
| `{"signal": "myRange"}` | Signal reference |
| `{"scheme": "blueorange"}` | Color scheme |
| `"width"` / `"height"` | Pre-defined spatial ranges |
| `"symbol"` | Default plotting symbol set |
| `"category"` | Default categorical color scheme |
| `"diverging"` | Default diverging color scheme |
| `"ordinal"` / `"ramp"` | Sequential color schemes |
| `"heatmap"` | Sequential multi-hue scheme |

## Projection Properties

Cartographic projections map (longitude, latitude) to (x, y) coordinates. Projections and scales share the same namespace.

| Property | Type | Description |
|----------|------|-------------|
| `name` | String | **Required.** Unique name |
| `type` | String | Projection type (default: `"mercator"`, case-insensitive) |
| `clipAngle` | Number | Clipping circle radius in degrees |
| `clipExtent` | Array | Viewport pixel bounds `[[x0,y0],[x1,y1]]` |
| `scale` | Number | Scale factor (projection-specific default) |
| `translate` | Number[] | Translation offset [tx, ty]. Default: [480, 250] |
| `center` | Number[] | Center longitude/latitude in degrees. Default: [0, 0] |
| `rotate` | Number[] | Rotation angles [lambda, phi, gamma] in degrees. Default: [0, 0, 0] |
| `parallels` | Number[] | Standard parallels for conic projections |
| `pointRadius` | Number | Default radius for Point/MultiPoint geometries. Default: 4.5 |
| `precision` | Number | Adaptive resampling threshold in pixels. Default: √0.5 |
| `fit` | Object / Array[] | GeoJSON to auto-fit translate and scale |
| `extent` | Array[] | Pixel area for auto-fitting: `[[x0,y0],[x1,y1]]` |
| `size` | Number[] | Width and height for auto-fitting (equivalent to extent `[[0,0],[w,h]]`) |

## Projection Types

| Type | Description |
|------|-------------|
| `albers` | Albers equal-area conic (U.S.-centric) |
| `albersUsa` | Composite for lower 48 states, Hawaii, Alaska |
| `azimuthalEqualArea` | Azimuthal equal-area |
| `azimuthalEquidistant` | Azimuthal equidistant |
| `conicConformal` | Conic conformal (parallels default: [30°, 30°]) |
| `conicEqualArea` | Albers equal-area conic |
| `conicEquidistant` | Conic equidistant |
| `equalEarth` | Equal Earth projection (≥2018) |
| `equirectangular` | Plate carrée |
| `gnomonic` | Gnomonic |
| `identity` | Identity transform (supports reflectX/reflectY, ≥3.3) |
| `mercator` | Spherical Mercator (default) |
| `mollweide` | Equal-area pseudocylindrical (≥5.9) |
| `naturalEarth1` | Natural Earth projection (≥4.0) |
| `orthographic` | Orthographic |
| `stereographic` | Stereographic |
| `transverseMercator` | Transverse spherical Mercator |

## Registering Custom Projections

```javascript
// Register a custom projection from d3-geo-projection
vega.projection('winkel3', d3.geoWinkel3);

// Then use in spec:
{ "projections": [{ "name": "proj", "type": "winkel3" }] }
```

Or load extended projections via CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/vega-projection-extended@2"></script>
```
