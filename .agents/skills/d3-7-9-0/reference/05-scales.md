# Scales

> **Source:** https://d3js.org/d3-scale
> **Loaded from:** SKILL.md (via progressive disclosure)

Scales map a dimension of abstract data to a visual representation. Most often used for position encoding, but can represent color, stroke width, symbol size, or any visual encoding.

## Continuous Scales

### Linear Scale — d3.scaleLinear()

Maps continuous quantitative input domain to continuous output range using linear transformation: y = mx + b. Default choice for quantitative data — preserves proportional differences.

```js
const x = d3.scaleLinear([10, 130], [0, 960]);
x(20); // 80
x(50); // 320

// Color encoding
const color = d3.scaleLinear([10, 100], ["brown", "steelblue"]);
color(20); // "rgb(154, 52, 57)"

// Piecewise (multi-stop)
const color = d3.scaleLinear([-1, 0, 1], ["red", "white", "green"]);
color(-0.5); // "rgb(255, 128, 128)"
```

**Key methods:**
- `.domain([min, max])` — set input domain (two or more numbers)
- `.range([min, max])` — set output range (any values interpolatable)
- `.rangeRound([min, max])` — set range with rounded interpolator (avoids antialiasing artifacts)
- `.clamp(true)` — clamp output to range for out-of-domain inputs
- `.invert(value)` — map from range back to domain (interaction, mouse position)
- `.ticks(count)` — generate human-friendly tick values
- `.tickFormat(count, format?)` — create a format function for ticks
- `.unknown(value)` — set output for undefined/NaN input

### Time Scale — d3.scaleUtc() / d3.scaleTime()

Like linear scale but for Date objects. Use `d3.scaleUtc()` for UTC dates, `d3.scaleTime()` for local dates.

```js
const x = d3.scaleUtc()
  .domain([new Date("2023-01-01"), new Date("2024-01-01")])
  .range([marginLeft, width - marginRight]);
```

### Pow Scale — d3.scalePow()

For quantitative data with a wide range. Applies a power transform before linear mapping.

```js
const x = d3.scalePow()
  .exponent(0.5)
  .domain([0, 100])
  .range([0, 960]);
```

### Log Scale — d3.scaleLog()

For quantitative data spanning several orders of magnitude.

```js
const x = d3.scaleLog()
  .domain([1, 1000000])
  .range([0, 960]);
```

### Symlog Scale — d3.scaleSymlog()

Like log scale but handles zero and negative values.

```js
const x = d3.scaleSymlog()
  .domain([-100, 100])
  .range([0, 960]);
```

## Discrete Scales

### Ordinal Scale — d3.scaleOrdinal()

Maps categorical data to a range of values. Supports implicit domain construction.

```js
const color = d3.scaleOrdinal(["a", "b", "c"], ["red", "green", "blue"]);
color("a"); // "red"

// Implicit domain (auto-discovers from usage)
const color = d3.scaleOrdinal(["red", "green", "blue"]);
color("b"); // "red" — first in range
color.domain(); // ["b", ...] inferred

// With scheme
const color = d3.scaleOrdinal(d3.schemeTableau10);
color("a"); // "#4e79a7"
```

**Key methods:**
- `.domain([...])` — set domain (optional for implicit)
- `.range([...])` — set range (required)
- `.unknown(value)` — set output for unknown values (default: implicit)

### Band Scale — d3.scaleBand()

For categorical data as position encoding with bands (gaps between bars).

```js
const x = d3.scaleBand()
  .domain(["A", "B", "C", "D"])
  .range([0, width])
  .padding(0.1);

x("A"); // 4 (start position)
x.bandwidth(); // ~150 (width of each band)
x.step(); // ~160 (band + gap)
```

**Key methods:**
- `.padding(n)` — set padding between bands (0–1, default 0.2)
- `.paddingInner()` / `.paddingOuter()` — fine-grained padding control
- `.bandwidth()` — width of each band
- `.step()` — total step size (band + gap)

### Point Scale — d3.scalePoint()

Like band scale but without gaps. Points are centered in the range.

```js
const x = d3.scalePoint()
  .domain(["A", "B", "C"])
  .range([0, width])
  .padding(0.5);
```

## Color Scales

### Sequential Scale — d3.scaleSequential()

Maps quantitative data to a sequential color interpolation. Paired with interpolators from d3-interpolate or schemes from d3-scale-chromatic.

```js
const color = d3.scaleSequential(d3.interpolateViridis)
  .domain([0, 100]);

const color = d3.scaleSequential(d3.interpolate)
  .range(["#f7fbff", "#08306b"]);
```

### Diverging Scale — d3.scaleDiverging()

For data with a meaningful midpoint (e.g., negative to positive).

```js
const color = d3.scaleDiverging(d3.interpolateRdBu)
  .domain([-1, 0, 1]);
```

### Quantize Scale — d3.scaleQuantize()

Maps continuous domain to discrete range (equal-width binning).

```js
const color = d3.scaleQuantize()
  .domain([0, 100])
  .range(["low", "medium", "high"]);
color(25); // "low"
```

### Quantile Scale — d3.scaleQuantile()

Maps continuous domain to discrete range based on data distribution quantiles.

```js
const color = d3.scaleQuantile()
  .domain(data.map(d => d.value))
  .range(["red", "orange", "green"]);
```

### Threshold Scale — d3.scaleThreshold()

Maps discrete domain thresholds to range values.

```js
const color = d3.scaleThreshold()
  .domain([0, 10, 20])
  .range(["low", "medium", "high", "critical"]);
color(5); // "low"
color(15); // "medium"
```

## Common Scale Methods

All scales share these methods:

- `.copy()` — create an independent copy of the scale
- `.ticks(count, format?)` — generate human-friendly tick values
- `.tickFormat(count, format?)` — create a format function for ticks
- `.nice(count?)` — extend domain to nice round numbers
- `.clamp(boolean)` — clamp output (continuous scales only)
- `.unknown(value)` — set output for undefined/NaN

## Usage Pattern

```js
// 1. Declare scales
const x = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.x)])
  .range([marginLeft, width - marginRight])
  .nice();

const y = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.y)])
  .range([height - marginBottom, marginTop]);

const color = d3.scaleOrdinal(d3.schemeTableau10);

// 2. Use in shape generators or element attributes
line.x(d => x(d.x)).y(d => y(d.y));
circle.attr("fill", d => color(d.category));
```
