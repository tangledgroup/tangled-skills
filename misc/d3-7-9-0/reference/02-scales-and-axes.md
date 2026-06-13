# Scales and Axes

## Scale Fundamentals

Scales are functions that map an input domain to an output range. They are the bridge between abstract data values and visual encoding properties.

```js
// Basic linear scale: maps [0, 100] to [0, 500] pixels
const x = d3.scaleLinear()
    .domain([0, 100])
    .range([0, 500]);

x(50);   // 250
x(100);  // 500
x.invert(250);  // 50 (reverse mapping)
```

All scales support `.domain()`, `.range()`, and `.clamp()` methods. Continuous scales also support `.nice()`, `.ticks()`, and `.invert()`.

## Linear Scales

The most common scale type for quantitative data:

```js
const x = d3.scaleLinear()
    .domain([0, 1000])
    .range([0, width]);

// Clamp values outside domain to range extremes
x.clamp(true);
x(1500); // returns width (clamped)

// Extend domain to "nice" round numbers
x.domain().nice();

// Generate tick values
x.ticks(10); // [0, 100, 200, ..., 1000]
```

## Time Scales

Map Date objects to continuous ranges. Variants: `scaleTime`, `scaleUtc`, `scaleLocalTime`.

```js
const x = d3.scaleTime()
    .domain([new Date("2023-01-01"), new Date("2024-01-01")])
    .range([0, width]);

// Generate time-appropriate ticks
x.ticks(d3.timeMonth.every(1)); // monthly ticks
x.ticks("month");               // shorthand

// Format tick labels
const format = d3.timeFormat("%b %Y");
format(x.ticks()[0]); // "Jan 2023"
```

## Ordinal Scales

Map discrete values to outputs. The base ordinal scale provides `.domain()`, `.range()`, and `.unknown()` for handling missing values.

**Band scales** — for bar charts, categorical axes:

```js
const x = d3.scaleBand()
    .domain(["a", "b", "c", "d"])
    .range([0, width])
    .padding(0.1);

x("a");           // start position of band "a"
x.bandwidth();    // width of each band
x.step();         // distance between band starts
```

Padding can be set for inner gaps (`.padding()`) and outer margins (`.paddingOuter()`). Nested bands use `scaleBand().range([start, end])` on a parent band scale.

**Point scales** — for scatter plots with categorical positions:

```js
const x = d3.scalePoint()
    .domain(["a", "b", "c"])
    .range([marginLeft, width - marginRight])
    .padding(0.5);

x("a"); // exact center point for category "a"
```

## Power and Log Scales

**Power scales** raise values to an exponent:

```js
const r = d3.scaleSqrt()  // exponent 0.5, good for area encoding
    .domain([0, 1000])
    .range([0, 20]);

// Custom exponent
const pow = d3.scalePow().exponent(3);
```

Use `scaleSqrt` when encoding data as area (circle radius) so that perceived size is proportional to the data value.

**Log scales** for data spanning orders of magnitude:

```js
const x = d3.scaleLog()
    .domain([1, 10000])
    .range([0, width])
    .base(10);

x.ticks(); // [1, 10, 100, 1000, 10000]
```

Domain must be strictly positive (or strictly negative).

## Sequential and Diverging Scales

Map continuous data to color gradients:

```js
// Sequential: single hue gradient
const color = d3.scaleSequential(d3.interpolateViridis)
    .domain([0, 100]);

// Diverging: two hues meeting at midpoint
const color = d3.scaleDiverging(d3.interpolateRdBu)
    .domain([0, 50, 100]);
```

Common interpolators: `interpolateViridis`, `interpolateInferno`, `interpolatePlasma`, `interpolateMagma`, `interpolateSpectral`, `interpolateRdYlBu`.

## Quantile and Quantize Scales

Discretize continuous data into categories:

```js
// Quantile: equal number of observations per bin
const color = d3.scaleQuantile()
    .domain(data)
    .range(["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15", "#67000d"]);

color.quantiles(); // [threshold values]
color(50);         // color for value 50

// Quantize: equal-width bins
const color = d3.scaleQuantize()
    .domain([0, 100])
    .range(["green", "yellow", "orange", "red"]);
```

## Threshold Scales

Map input ranges to arbitrary outputs:

```js
const color = d3.scaleThreshold()
    .domain([0.3, 0.5, 0.7], [0, 1])
    .range(["red", "yellow", "green", "blue"]);

color(0.2); // "red"
color(0.4); // "yellow"
```

## Chromatic Color Schemes

D3 provides built-in color palettes:

```js
// Categorical (distinct colors)
const color = d3.scaleOrdinal(d3.schemeCategory10);
const color = d3.scaleOrdinal(d3.schemeTableau10);
const color = d3.scaleOrdinal(d3.schemeSet3);

// Sequential (gradient schemes, array of N colors)
d3.schemeViridis9[4];    // 5th color in 9-color Viridis scheme
d3.schemeBlues7;         // 7-color blue sequential scheme

// Diverging
d3.schemeRdYlBu9;        // red-yellow-blue diverging, 9 colors

// Cyclical
d3.schemePiYG9;          // pink-ivory-green cyclical
```

Available schemes: `Viridis`, `Inferno`, `Plasma`, `Magma`, `Cividis` (sequential); `RdYlBu`, `RdBu`, `BrBG`, `PiYG`, `PRGn`, `PuOr`, `RdGy`, `RdYlGn`, `Spectral` (diverging); `Accent`, `Dark2`, `Paired`, `Pastel1`, `Pastel2`, `Set1`, `Set2`, `Set3`, `Tableau10`, `Category10`, `Category20` (categorical).

## Axes

Axes are generators that produce tick marks, grid lines, and labels from scales:

```js
// Create axis generator
const xAxis = d3.axisBottom(xScale)
    .ticks(10)              // approximate number of ticks
    .tickFormat(d3.format(".2f"))  // format function
    .tickSize(-height);      // negative for grid lines

const yAxis = d3.axisLeft(yScale)
    .ticks(10)
    .tickFormat(d => `$${d}`);

// Apply axis to a <g> element
svg.append("g")
    .attr("transform", `translate(0,${height})`)
    .call(xAxis);

svg.append("g")
    .attr("transform", `translate(${marginLeft},0)`)
    .call(yAxis);
```

**Axis orientations:** `axisTop`, `axisRight`, `axisBottom`, `axisLeft`.

**Axis customization:**

```js
axis.tickArguments([count, specifier]);  // ticks count + format
axis.tickValues([10, 20, 30]);           // explicit tick positions
axis.tickFormat(d => d3.format("$,.0f")(d));
axis.tickSize(6);                        // tick mark length
axis.tickSizeInner(-height);             // grid lines across plot
axis.tickSizeOuter(6);                   // extent ticks
axis.tickPadding(8);                     // space between tick and label
```

**Styling axes with CSS:**

```css
.axis line, .axis path {
    stroke: #ccc;
    shape-rendering: crispEdges;
}
.axis text {
    font-size: 11px;
    fill: #666;
}
```
