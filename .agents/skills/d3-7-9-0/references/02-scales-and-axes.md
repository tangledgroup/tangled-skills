# D3 Scales and Axes

## Linear Scale

```javascript
const scale = d3.scaleLinear()
    .domain([0, 100])          // Input range
    .range([0, width]);        // Output range

scale(50);                     // → width / 2
scale.invert(width / 2);      // → 50
scale.nice();                  // Nice domain: [0, 100] → [0, 100]
scale.ticks(5);                // → [0, 20, 40, 60, 80, 100]
scale.tickFormat(3);           // Format function for 3 significant digits
```

### Identity and Radial Scales
```javascript
d3.scaleIdentity();            // f(x) = x
d3.scaleRadial();              // For radial coordinates
```

## Time Scale

```javascript
const timeScale = d3.scaleTime()
    .domain([new Date(2020, 0, 1), new Date(2024, 0, 1)])
    .range([0, width]);

timeScale(new Date(2022, 6, 1));  // → x position
timeScale.ticks(d3.timeYear.every(1));
timeScale.tickFormat("%Y");
```

### UTC Time Scale
```javascript
d3.scaleUtc()
    .domain([new Date(Date.UTC(2020, 0, 1)), new Date(Date.UTC(2024, 0, 1))]);
```

## Power and Log Scales

```javascript
// Square root scale
const sqrt = d3.scaleSqrt()
    .domain([0, 100])
    .range([0, width]);

// Power scale with custom exponent
const pow = d3.scalePow()
    .exponent(2)
    .domain([0, 100])
    .range([0, width]);

// Log scale
const log = d3.scaleLog()
    .base(10)
    .domain([1, 1000])
    .range([0, width]);

// Symlog scale (handles zero and negative values)
const symlog = d3.scaleSymlog()
    .constant(1)
    .domain([-100, 100])
    .range([0, width]);
```

## Ordinal Scales

```javascript
const ordinal = d3.scaleOrdinal()
    .domain(["A", "B", "C"])
    .range(["red", "green", "blue"]);

// Implicit domain (first use)
ordinal("D");  // Returns next range value or undefined
ordinal.unknown(d3.scaleImplicit);  // Control unknown behavior
```

## Band and Point Scales

```javascript
// Band scale for bar charts
const band = d3.scaleBand()
    .domain(categories)
    .range([0, width])
    .padding(0.1)
    .align(0.5)              // 0 to 1, center alignment
    .round(true);            // Round pixel values

band("A");                  // → x position
band.bandwidth();           // → bar width
band.step();                // → bandwidth + padding

// Point scale for single points
const point = d3.scalePoint()
    .domain(categories)
    .range([0, width])
    .padding(0.5);
```

## Sequential Scales

```javascript
const sequential = d3.scaleSequential(d3.interpolateViridis)
    .domain([0, 100]);

// Log variant
d3.scaleSequentialLog()
    .domain([1, 1000])
    .interpolator(d3.interpolateViridis);

// Pow variant
d3.scaleSequentialPow()
    .exponent(2)
    .domain([0, 100]);

// Quantile variant
d3.scaleSequentialQuantile()
    .domain(data.map(d => d.value));
```

## Diverging Scales

```javascript
const diverging = d3.scaleDiverging()
    .domain([-100, 0, 100])
    .range(["blue", "white", "red"])
    .interpolator(d3.interpolateRdBu);

// Variants
d3.scaleDivergingLog();
d3.scaleDivergingPow();
d3.scaleDivergingSqrt();
d3.scaleDivergingSymlog();
```

## Quantize and Quantile Scales

```javascript
// Quantize: continuous domain → discrete range
const quantize = d3.scaleQuantize()
    .domain([0, 100])
    .range(["low", "medium", "high"]);

quantize.invertExtent("medium");  // → [33.33, 66.67]

// Quantile: data-driven thresholds
const quantile = d3.scaleQuantile()
    .domain(data.map(d => d.value))
    .range(["low", "medium", "high"]);

quantile.quantiles();   // → threshold values
quantile.invertExtent("medium");  // → [min, max] for that category
```

## Threshold Scale

```javascript
const threshold = d3.scaleThreshold()
    .domain([0, 50, 100])
    .range(["low", "medium", "high", "extreme"]);

threshold(25);           // → "low"
threshold.invertExtent("medium");  // → [50, 100]
```

## Axes

### Basic Axis

```javascript
const axis = d3.axisBottom(xScale)
    .ticks(5)
    .tickFormat(d => d + "%")
    .tickSize(10)
    .tickPadding(8);

svg.append("g")
    .attr("transform", `translate(0,${height})`)
    .call(axis);
```

### Axis Configuration

```javascript
axis.tickValues([0, 50, 100]);              // Specific tick values
axis.tickSize(5);                            // Inner + outer tick size
axis.tickSizeInner(5);                       // Inner tick only
axis.tickSizeOuter(0);                       // Outer tick (hide)
axis.tickPadding(8);                         // Space between tick and label
axis.tickArguments([10, "%"]);               // Set count + format together
```

### Styling Axes

```javascript
// Remove axis line
svg.select(".domain").remove();

// Style grid lines
svg.selectAll(".tick line")
    .attr("stroke", "#ccc")
    .attr("stroke-opacity", 0.3);

// Style tick text
svg.selectAll(".tick text")
    .attr("font-size", "11px")
    .attr("fill", "#666");
```

### Axis Factory Pattern

```javascript
function createAxis(scale, orient) {
    let axis = d3.axisBottom(scale);
    return function(selection) {
        selection.call(axis);
        selection.selectAll(".domain").remove();
        selection.selectAll(".tick line")
            .attr("stroke-opacity", 0.1);
    };
}
```
