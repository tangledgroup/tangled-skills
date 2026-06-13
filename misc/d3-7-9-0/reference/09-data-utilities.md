# Data Utilities

## Array Operations

**Grouping:**

```js
// Group into nested Map
const byCategory = d3.group(data, d => d.category);
// Map { "A" => [items...], "B" => [items...] }

// Group into nested arrays
const groups = d3.groups(data, d => d.category);
// [ ["A", [items...]], ["B", [items...]] ]

// Rollup: group and reduce
const totals = d3.rollup(data,
    v => d3.sum(v, d => d.value),
    d => d.category
);
// Map { "A" => 150, "B" => 200 }

// Multi-level grouping
const nested = d3.group(data,
    d => d.category,
    d => d.subcategory
);

// Index: group with key as identifier
const byId = d3.index(data, d => d.id);
// Map { "id1" => item1, "id2" => item2 }

// Flat group (single array of [key, values])
const flat = d3.flatGroup(data, d => d.category);
```

**Sorting:**

```js
d3.sort(data, d => d.value);           // ascending
d3.sort(data, d3.descending);          // descending numbers
d3.sort(data, (a, b) => a.name.localeCompare(b.name)); // custom

d3.groupSort(data, d => d3.sum(d, v => v.value), d => v.category);
// sort groups by aggregated value
```

**Set operations:**

```js
const a = [1, 2, 3], b = [2, 3, 4];
d3.union(a, b);         // [1, 2, 3, 4]
d3.intersection(a, b);  // [2, 3]
d3.difference(a, b);    // [1]
d3.disjoint(a, [5, 6]); // true
```

**Transforming:**

```js
d3.cross(["a", "b"], [1, 2]);      // [["a",1],["a",2],["b",1],["b",2]]
d3.merge([[1, 2], [3, 4]]);        // [1, 2, 3, 4]
d3.pairs([1, 2, 3]);               // [[1,2], [2,3]]
d3.transpose([[1, 2], [3, 4]]);    // [[1, 3], [2, 4]]
d3.zip(["a", "b"], [1, 2]);        // [["a", 1], ["b", 2]]
```

## Statistics

```js
const data = [3, 1, 4, 1, 5, 9, 2, 6];

d3.min(data);              // 1
d3.max(data);              // 9
d3.extent(data);           // [1, 9]
d3.sum(data);              // 31
d3.mean(data);             // 3.875
d3.median(data);           // 3.5
d3.quantile(data, 0.25);   // 1st quartile
d3.variance(data);         // variance
d3.deviation(data);        // standard deviation
d3.mode(data);             // most common value
d3.count(data);            // count of valid numbers

// With accessor
d3.max(data, d => d.value);
d3.sum(data, d => d.value);

// Full precision summation
d3.fsum(data);             // Kahan summation for accuracy
```

## Ticks

Generate human-friendly tick values:

```js
d3.ticks(0, 100, 10);       // [0, 10, 20, ..., 100]
d3.tickIncrement(0, 100, 10); // 10 (step size)
d3.tickStep(0, 100, 10);     // 10 (may be negative for reversed domains)
d3.nice([0.207, 0.793], 5);  // [0.2, 0.8] (extends to round numbers)
```

## CSV and TSV Parsing

```js
// Parse CSV string
const rows = d3.csvParse(csvString);
const typedRows = d3.csvParse(csvString, d => ({
    ...d,
    value: +d.value,
    date: new Date(d.date)
}));

// Parse with column type inference
const data = d3.csvParse(csvString, d3.autoType);

// Generate CSV string
const csv = d3.csvFormat(data);
const tsv = d3.tsvFormat(data);

// Delimiter variants
d3.tsvParse(tsvString);
d3.dsvFormat(";").parse(semiColonString);  // custom delimiter
```

## Fetch

Convenience wrappers around fetch() for common data formats:

```js
// Load CSV
const data = await d3.csv("data.csv");
const typedData = await d3.csv("data.csv", d3.autoType);
const customTyped = await d3.csv("data.csv", d => ({
    name: d.name,
    value: +d.value
}));

// Load TSV
const data = await d3.tsv("data.tsv");

// Load JSON
const data = await d3.json("data.json");

// Load text
const text = await d3.text("file.txt");

// Load XML
const xml = await d3.xml("file.xml");

// Load as ArrayBuffer
const buffer = await d3.arrayBuffer("file.bin");

// Load as Image
const image = await d3.image("image.png");

// Load as Blob
const blob = await d3.blob("file.dat");

// Custom delimiter
const data = await d3.dsvFormat(";").request("data.csv")();
```

All fetch functions return Promises and support the standard `Request` options as a second argument.

## Formatting

Number and time formatting with locale support:

```js
// Number formatting
const format = d3.format(".2f");
format(3.14159);       // "3.14"
d3.format("$,.2f")(1234567.89);  // "$1,234,567.89"
d3.format(".1%")(0.856);         // "85.6%"
d3.format(".2s")(1500000);       // "1.50M"

// Format specifier: [fill][align][sign][symbol][0][width][,][.precision][type]
// Types: e/E (exponential), f (fixed), g (auto), % (percent), s (SI prefix), p (percent*100)

// Time formatting
const formatTime = d3.timeFormat("%Y-%m-%d");
formatTime(new Date(2024, 0, 15));  // "2024-01-15"

const parseTime = d3.timeParse("%Y-%m-%d");
parseTime("2024-01-15");             // Date object

// Common formats
d3.timeFormat("%B %d, %Y");   // "January 15, 2024"
d3.timeFormat("%b %d %H:%M"); // "Jan 15 14:30"
d3.utcFormat("%Y-%m-%dT%H:%M:%SZ"); // ISO 8601 UTC

// Localized formatting
const locale = d3.locale({
    dateTime: "%x, %X",
    date: "%-m/%-d/%Y",
    time: "%H:%M:%S",
    periods: ["AM", "PM"],
    days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    shortDays: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    months: ["January", "February", /* ... */],
    shortMonths: ["Jan", "Feb", /* ... */]
});
locale.format("%B %d, %Y");
```

## Time Arithmetic

Calendar-aware date operations:

```js
// Time intervals
d3.timeYear(new Date(2024, 5, 15));      // Jan 1, 2024
d3.timeYear.offset(date, 2);              // add 2 years
d3.timeYear.diff(d1, d2);                 // year difference
d3.timeYear.every(2);                     // every 2 years

// Available intervals
d3.timeMillisecond, d3.timeSecond, d3.timeMinute,
d3.timeHour, d3.timeDay, d3.timeWeek,
d3.timeMonth, d3.timeQuarter, d3.timeYear

// UTC variants
d3.utcDay, d3.utcWeek, d3.utcMonth, d3.utcYear

// Each interval supports: floor, ceil, round, offset, range, every
d3.timeDay.range(start, stop, step);
```

## Random Number Generation

```js
// Uniform distribution [0, 1)
const random = d3.randomUniform();
random(); // 0.42...

// Uniform with range
const random = d3.randomUniform(0, 100);

// Normal (Gaussian) distribution
const normal = d3.randomNormal(mean, deviation);

// Log-normal distribution
const logNormal = d3.randomLogNormal(mean, deviation);

// Bimodal distribution
const bimodal = d3.randomBimodal(separation);
```

## Color Manipulation

```js
// Parse color
const c = d3.color("steelblue");
c.rgb();           // { r: 70, g: 130, b: 180 }
c.brighter(0.5);   // lighter version
c.darker(2);       // darker version
c.formatHex();     // "#4682b4"
c.formatRgb();     // "rgb(70, 130, 180)"

// Color spaces
d3.rgb(70, 130, 180);
d3.hsl(207, 0.44, 0.49);
d3.lab(55, -6, -26);
d3.hcl(252, 32, 55);
d3.cubehelix(0.5, 0.7, 2.5);

// Interpolate colors
const gradient = d3.interpolateRgb("red", "blue");
gradient(0.5); // "rgb(128, 0, 128)"
```

## Contour and Delaunay

**Contour generation** from gridded data:

```js
const contours = d3.contours()
    .size([width, height])
    .thresholds([0, 0.25, 0.5, 0.75, 1]);

const polygons = contours(gridData);
// Returns array of GeoJSON polygons
```

**Density estimation:**

```js
const density = d3.contourDensity()
    .size([width, height])
    .bandwidth(20)
    .thresholds(20);

const contours = density(points); // points: [[x, y], ...]
```

**Delaunay triangulation and Voronoi diagrams:**

```js
const delaunay = d3.Delaunay(points.map(d => d.x), points.map(d => d.y));

// Voronoi cells
const voronoi = delaunay.voronoi([0, 0, width, height]);

// Triangles
delaunay.triangles;  // array of [i, j, k] vertex indices

// Nearest point
delaunay.find(x, y, radius);
```
