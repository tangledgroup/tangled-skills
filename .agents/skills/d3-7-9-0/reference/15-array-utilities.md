# Array Utilities

> **Source:** https://d3js.org/d3-array
> **Loaded from:** SKILL.md (via progressive disclosure)

## Statistics

### Mean, Median, Sum

```js
d3.mean(array, accessor);       // arithmetic mean
d3.median(array, accessor);      // median value
d3.sum(array, accessor);         // sum of values
d3.variance(array, accessor);    // sample variance
d3.deviation(array, accessor);   // sample standard deviation
```

### Min, Max, Extent

```js
d3.min(array, accessor);                    // minimum value
d3.max(array, accessor);                    // maximum value
d3.extent(array, accessor);                 // [min, max]
d3.quickselect(array, k, accessor);         // in-place partial sort
```

### Quantile

```js
// Sorted array required
d3.quantile(sortedNumbers, p);    // p in [0,1]
d3.quantileSorted(sortedNumbers, p); // same, assumes sorted
d3.quantile(array, p, accessor);  // with accessor (sorts internally)
```

## Sorting

```js
// In-place sort, returns array
array.sort(d3.ascending);
array.sort(d3.descending);

// With accessor
array.sort((a, b) => d3.ascending(a.value, b.value));
```

## Bisecting — Binary Search

```js
d3.bisect(sortedArray, value);           // rightmost insertion point
d3.bisectRight(sortedArray, value);      // same
d3.bisectLeft(sortedArray, value);       // leftmost insertion point
d3.bisectRightBy(array, value, accessor);
d3.bisectLeftBy(array, value, accessor);
```

## Binning

```js
const bin = d3.bin()
  .value(d => d.value)
  .domain([0, 100])
  .thresholds(10);

const bins = bin(data);
// [{x0: 0, x1: 10, length: 5, ...}, …]
```

**Configuration:**
- `.value(fn)` — accessor for bin value
- `.domain([min, max])` — auto-computed if omitted
- `.thresholds(thresholds)` — explicit thresholds or count

## Grouping

```js
// Group by key
const groups = d3.group(data, d => d.category);
// Map<category, [datum1, datum2, …]>

// Nested grouping
const nested = d3.groupSort(data, g => d3.sum(g, d => d.value), d => d.region);

// Cross product
const cross = d3.cross(rows, columns);
```

## Interning

```js
const interner = d3.intern();
interner(value); // returns interned reference (same ref for equal values)
```

## Blur

```js
// Gaussian blur on array
d3.blur(array, sigma);       // in-place
d3.blurBy(array, accessor);  // with accessor, returns new array
```

## Sets

```js
// Set operations return new sets
d3.setIntersection(setA, setB);
d3.setUnion(setA, setB);
d3.setDifference(setA, setB);
d3.setSymmetricDifference(setA, setB);
```

## Ticks

```js
d3.ticks(start, stop, count);        // human-friendly tick values
d3.tickStep(start, stop, count);     // step size for ticks
```

## Complete Example

```js
const data = await d3.csv("sales.csv");

// Statistics
const avg = d3.mean(data, d => d.revenue);
const total = d3.sum(data, d => d.revenue);
const [min, max] = d3.extent(data, d => d.revenue);

// Group by region
const byRegion = d3.group(data, d => d.region);

// Bin revenue
const histogram = d3.bin()
  .value(d => d.revenue)
  .thresholds(20)(data);

// Filter to top regions
const sorted = Array.from(byRegion.entries())
  .sort((a, b) => d3.sum(b[1], d => d.revenue) - d3.sum(a[1], d => d.revenue));
```
