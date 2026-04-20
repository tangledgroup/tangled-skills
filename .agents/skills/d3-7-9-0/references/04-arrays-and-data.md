# D3 Arrays and Data

## Summarizing

```javascript
d3.sum([1, 2, 3]);                                    // → 6
d3.sum(data, d => d.value);                             // Sum with accessor
d3.mean([1, 2, 3]);                                     // → 2
d3.median([1, 2, 3, 4]);                                // → 2.5
d3.quantile(sorted, p);                                 // Quantile (p in [0,1])
d3.quantileSorted(data, p, compare);                    // With comparator
d3.mode(data);                                          // Most frequent
d3.variance([1, 2, 3]);                                 // Sample variance
d3.deviation([1, 2, 3]);                                // Standard deviation
d3.min([1, 2, 3]);                                      // → 1
d3.max([1, 2, 3]);                                      // → 3
d3.extent([1, 2, 3]);                                   // → [1, 3]
d3.count(data);                                         // Count non-null

// Index variants
d3.minIndex(data, d => d.value);
d3.maxIndex(data, d => d.value);
d3.least(data, d => d.score);
d3.greatest(data, d => d.score);
```

### Floating-Point Sum

```javascript
// For better precision with floating-point numbers
d3.fcumsum(comparator)(array);
d3.fsum(array);
```

## Sorting

```javascript
d3.ascending(a, b);
d3.descending(a, b);

d3.sort(array, (a, b) => a.value - b.value);
d3.reverse(array);
d3.shuffle(array);                                      // Fisher-Yates
d3.shuffle(array, seed);                                // Seeded shuffle
d3.shuffler(seed);                                      // Reusable shuffler
d3.permute(array, indices);                             // Rearrange by indices
d3.quickselect(array, k);                               // Partial sort
```

## Grouping

```javascript
// Group by key
d3.group(data, d => d.category);
// → Map { "A" => [...], "B" => [...] }

// Nested groups
d3.group(data, d => d.region, d => d.category);
// → Map { "North" => Map { "A" => [...], ... }, ... }

// Groups as array
d3.groups(data, d => d.category);
// → [["A", [...] ], ["B", [...]]]

// Rollup (aggregate)
d3.rollup(data, v => d3.sum(v, d => d.value), d => d.category);
// → Map { "A" => 100, "B" => 200 }

// Index (group by key, take last value)
d3.index(data, d => d.id, d => d);
// → Map { "id1" => {...}, ... }

// Flat variants
d3.flatGroup(data, d => [d.region, d.category]);
d3.flatRollup(data, v => d3.sum(v), d => [d.region, d.category]);
```

## Binning

```javascript
const bin = d3.bin()
    .value(d => d.value)
    .domain([0, 100])
    .thresholds(10);

const bins = bin(data);
// → [{x0: 0, x1: 10, length: 5, ...}, ...]

// Auto-threshold methods
d3.thresholdFreedmanDiaconis(sortedValues, extent);
d3.thresholdScott(sortedValues, extent);
d3.thresholdSturges(sortedValues.length, extent);
```

## Bisecting

```javascript
d3.bisect(array, value);                        // Right bisect
d3.bisectLeft(array, value);                    // Left bisect
d3.bisectRight(array, value);                   // Right bisect
d3.bisectCenter(array, value);                  // Closest element

// Bisector for objects
const bisectDate = d3.bisector(d => d.date).left;
const index = bisectDate(data, targetDate);

// Bisector with comparator
d3.bisector((d, v) => d.value - v).left(data, targetValue);
```

## Set Operations

```javascript
d3.union([1, 2, 3], [2, 3, 4]);                 // → [1, 2, 3, 4]
d3.intersection([1, 2, 3], [2, 3, 4]);          // → [2, 3]
d3.difference([1, 2, 3], [2, 3, 4]);            // → [1]
d3.subset([1, 2], [1, 2, 3]);                   // → true
d3.superset([1, 2, 3], [1, 2]);                 // → true
d3.disjoint([1, 2], [3, 4]);                    // → true
```

## Transforming

```javascript
// Cross product
d3.cross([1, 2], ["a", "b"]);
// → [[1, "a"], [1, "b"], [2, "a"], [2, "b"]]

// Merge arrays
d3.merge([[1, 2], [3, 4]]);
// → [1, 2, 3, 4]

// Pairs
d3.pairs([1, 2, 3, 4]);
// → [[1, 2], [2, 3], [3, 4]]

// Transpose
d3.transpose([[1, 2, 3], [4, 5, 6]]);
// → [[1, 4], [2, 5], [3, 6]]

// Zip
d3.zip([1, 2, 3], ["a", "b", "c"]);
// → [[1, "a"], [2, "b"], [3, "c"]]
```

### Transforms

```javascript
// Array transforms (functional)
d3.map(array, fn);
d3.filter(array, predicate);
d3.reduce(array, reducer, initialValue);
```

## Ticks and Range

```javascript
d3.ticks(start, stop, count);                   // → [0, 2, 4, 6, 8, 10]
d3.tickIncrement(start, stop, count);
d3.tickStep(start, stop, count);
d3.nice(start, stop, count);                    // Nice range

d3.range(0, 10);                                // → [0, 1, ..., 9]
d3.range(0, 10, 2);                             // → [0, 2, 4, 6, 8]
```

## Blurring

```javascript
d3.blur(imageData, radius);                     // Blur image data
d3.blur2(imageData, radiusX, radiusY);
d3.blurImage(source, target, radius);           // Canvas blur
```

## Interning

```javascript
// InternMap: Map with automatic string interning
const map = new d3.InternMap(data);

// InternSet: Set with automatic string interning
const set = new d3.InternSet(array);
```

## Random Distributions (d3-random)

```javascript
d3.randomUniform(min, max);
d3.randomNormal(mean, deviation);
d3.randomExponential(scale);
d3.randomBeta(alpha, beta);
d3.randomGamma(shape, scale);
d3.randomPoisson(lambda);
d3.randomInt(min, max);
d3.randomLcg(seed);
```

## Time Utilities (d3-time)

```javascript
// Time intervals
d3.timeMillisecond;
d3.timeSecond;
d3.timeMinute;
d3.timeHour;
d3.timeDay;
d3.timeWeek;
d3.timeMonth;
d3.timeYear;

// Range and count
d3.timeDay.range(new Date(2024, 0, 1), new Date(2024, 0, 8));
d3.timeMonth.count(d3.timeYear, date);

// Filtering
const weekdays = d3.timeDay.filter(d => d.getDay() !== 0 && d.getDay() !== 6);

// Tick intervals
d3.timeTicks(start, stop, count);
```

### Time Formatting (d3-time-format)

```javascript
const parse = d3.timeParse("%Y-%m-%d");
const date = parse("2024-01-15");

const format = d3.timeFormat("%B %d, %Y");
format(date);  // → "January 15, 2024"

// UTC variants
d3.utcParse("%Y-%m-%d");
d3.utcFormat("%Y-%m-%d");
```

## CSV/TSV Parsing (d3-dsv)

```javascript
const data = d3.csvParse(csvText);
data[0];  // → {name: "A", value: "42"}

// Auto-type conversion
d3.csvParse(csvText, d3.autoType);

// Parse rows with callback
d3.csvParseRows(csvText, (row, i) => [i, ...row.map(Number)]);

// Format
d3.csvFormat(data);
d3.csvFormatRow(["A", "B"]);
d3.csvFormatValue("Hello, World");

// TSV variants
d3.tsvParse(tsvText);
d3.tsvFormat(data);
```

## Fetching Data (d3-fetch)

```javascript
const data = await d3.csv("data.csv");
const json = await d3.json("data.json");
const text = await d3.text("data.txt");
const xml = await d3.xml("data.xml");
const svg = await d3.svg("data.svg");
const html = await d3.html("snippet.html");
const image = await d3.image("photo.jpg");
const buffer = await d3.buffer("file.bin");
```

## Formatting Numbers (d3-format)

```javascript
const format = d3.format(",.2f");
format(1234567.89);  // → "1,234,567.89"

// Format specifiers
d3.format(".0%")(0.42);   // → "42%"
d3.format("+d")(42);       // → "+42"
d3.format("05d")(7);       // → "00007"
d3.format(",.0f")(1e6);    // → "1,000,000"

// Prefixes
d3.formatPrefix.auto(1e6);  // → {symbol: "M", scale: d => d / 1e6}
```
