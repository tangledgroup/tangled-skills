# Data — Arrays, Format, Fetch, Time

> **Source:** https://d3js.org/d3-array, d3-format, d3-fetch, d3-time
> **Loaded from:** SKILL.md (via progressive disclosure)

## Array Utilities — d3-array

### Summarizing Statistics

```js
d3.mean(data, d => d.value);
d3.median(data, d => d.value);
d3.min(data, d => d.value);
d3.max(data, d => d.value);
d3.extent(data, d => d.value); // [min, max]
d3.sum(data, d => d.value);
d3.quantile(sortedData, p); // sorted array required
d3.runes(string); // iterate over Unicode runes
```

### Sorting

```js
d3.sort(data, (a, b) => a.value - b.value);
// Sort in-place and return
data.sort((a, b) => d3.ascending(a.value, b.value));
d3.descending(a, b); // reverse ascending
```

### Bisecting — Binary Search

```js
const index = d3.bisect(sortedArray, target);
const index = d3.bisectRight(sortedArray, target);  // after equal elements
const index = d3.bisectLeft(sortedArray, target);   // before equal elements
const index = d3.bisectRightBy(array, target, accessor);
```

### Binning

```js
const bin = d3.bin()
  .value(d => d.value)
  .domain([0, 100])
  .thresholds(10);

const bins = bin(data);
// [{x0: 0, x1: 10, length: 5, ...}, …]
```

### Grouping

```js
const groups = d3.group(data, d => d.category);
// Map<category, [datum, …]>

const cross = d3.cross(rows, columns);
// Cartesian product of two arrays
```

### Interning

```js
const interner = d3.intern();
interner(value); // returns interned reference
```

## Data Loading — d3-fetch

All functions return promises. Auto-detects types (numbers, dates).

```js
// CSV: auto-parses headers and types
const data = await d3.csv("data.csv");
// [{name: "A", value: 42}, …]

// TSV
const data = await d3.tsv("data.tsv");

// JSON
const data = await d3.json("data.json");

// Text
const text = await d3.text("data.txt");

// XML
const xml = await d3.xml("data.xml");

// HTML
const html = await d3.html("page.html");
```

### Custom Parsing

```js
const data = await d3.csv("data.csv", d => ({
  date: d3.timeParse("%Y-%m-%d")(d.date),
  value: +d.value
}));
```

## Number Formatting — d3-format

Format numbers with locale-aware precision, prefixes, and separators.

```js
// Basic number
d3.format("6.2f")(1234.567); // " 1234.57"

// Percentage
d3.format(".0%")(0.75); // "75%"

// Bytes
d3.format(".1s")(1e9); // "1.0GB"

// Currency
d3.format("$,.2f")(42.5); // "$42.50"

// Exponential
d3.format(".2e")(0.001); // "1.00e-3"

// Prefixes (k, M, G, T, P, E, Z, Y)
d3.format(".2s")(42e6); // "42.00M"
```

### Format Specifiers

| Specifier | Description | Example |
|-----------|-------------|---------|
| `f` | Fixed-point | `"6.2f"` → `" 1234.57"` |
| `e` | Exponential | `".2e"` → `"1.00e+00"` |
| `g` | Significant digits | `".3g"` → `"123"` |
| `%` | Percentage | `".0%"` → `"75%"` |
| `s` | SI prefix | `".1s"` → `"1.0k"` |
| `d` | Integer | `"06d"` → `"000123"` |
| `o` | Octal | `"o"` |
| `x` / `X` | Hexadecimal | `"x"` / `"X"` |
| `c` | Character | `"c"` |
| `r` | Round to integer | `"r"` |

### Locale

```js
// Euro locale
d3.formatLocale({
  "decimal": ",",
  "thousands": ".",
  "grouping": [3],
  "currency": ["€", ""],
  "percent": " ‰",
  "minusSign": "−",
  "plusSign": "+",
  "currency": ["€", ""]
});

const formatEuro = d3.formatLocale(locale)("€ ,.0f");
formatEuro(1234.5); // "€ 1.235"
```

## Time Scales — d3-time

### Time Intervals

```js
d3.timeDay(new Date());          // midnight today
d3.timeWeek(new Date());         // Sunday this week
d3.timeMonth(new Date());        // first day of month
d3.timeYear(new Date());         // Jan 1 this year

// Custom intervals
const sunday = d3.timeWeek;
const monday = d3.timeWeekOn({date: new Date(), hour: 0, weekday: 1});
```

### Time Ranges

```js
d3.timeDay.range(start, stop, count);
d3.timeWeek.range(start, stop, count);
d3.timeMonth.range(start, stop, count);
d3.timeYear.range(start, stop, count);
```

### Time Parsing

```js
const parse = d3.timeParse("%Y-%m-%d");
const date = parse("2024-01-15");

const parseDateTime = d3.timeParse("%Y-%m-%d %H:%M:%S");
```

### Time Formatting

```js
const format = d3.timeFormat("%Y-%m-%d");
format(new Date()); // "2024-01-15"

// Common directives
// %Y - 4-digit year
// %m - 2-digit month
// %d - 2-digit day
// %H - 24-hour
// %M - minute
// %S - second
// %A - full weekday name
```

## Random — d3-random

```js
const rand = d3.randomUniform(0, 10);
rand(); // number between 0 and 10

const normal = d3.randomNormal(0, 1);
normal(); // normally distributed

const exponential = d3.randomExponential(5);
exponential();
```
