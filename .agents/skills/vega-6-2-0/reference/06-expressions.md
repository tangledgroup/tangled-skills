# Expressions

## Contents
- Language Overview
- Bound Variables
- Constants
- Type Checking & Coercion
- Control Flow
- Math Functions
- Statistical Functions
- Date-Time Functions
- Array Functions
- String Functions
- Object Functions
- Formatting Functions
- RegExp Functions
- Color Functions
- Event Functions
- Data Functions
- Scale & Projection Functions
- Geographic Functions
- Tree Functions
- Browser & Logging

## Language Overview

The expression language is a restricted subset of JavaScript for custom calculations in Vega.

**Supported:** Arithmetic, logical, property access, boolean/number/string/object/array literals, ternary (`a ? b : c`) and `if(test, then, else)`.

**Not allowed:** Assignment operators (`=`, `+=`), pre/postfix updates (`++`), `new` expressions, control flow statements (`for`, `while`, `switch`), nested property calls (`foo.bar()`).

## Bound Variables

| Variable | Description |
|----------|-------------|
| `datum` | Current input data object. Access: `datum.value` or `datum['My Value']` |
| `event` | DOM event (in event handler context) |
| Signal names | Any in-scope signal value, e.g., `hover` |

## Constants

`NaN`, `E`, `LN2`, `LN10`, `LOG2E`, `LOG10E`, `MAX_VALUE`, `MIN_VALUE`, `PI`, `SQRT1_2`, `SQRT2`.

## Type Checking & Coercion

### Type Checking
| Function | Description |
|----------|-------------|
| `isArray(value)` | Is array |
| `isBoolean(value)` | Is boolean |
| `isDate(value)` | Is Date object (not timestamp/string) |
| `isDefined(value)` | ≥5.4 Not `undefined` (null and NaN are "defined") |
| `isNumber(value)` | Is number (NaN/Infinity count as numbers) |
| `isObject(value)` | Is object (includes arrays and Dates) |
| `isRegExp(value)` | Is RegExp |
| `isString(value)` | Is string |
| `isValid(value)` | ≥5.4 Not null, undefined, or NaN |

### Type Coercion
| Function | Description |
|----------|-------------|
| `toBoolean(value)` | → boolean (null/empty → null) |
| `toDate(value)` | → Date (uses Date.parse if no parser) |
| `toNumber(value)` | → number (null/empty → null) |
| `toString(value)` | → string (null/empty → null) |

## Control Flow

| Function | Description |
|----------|-------------|
| `if(test, thenValue, elseValue)` | Ternary equivalent: returns thenValue if test is truthy |

## Math Functions

`abs`, `acos`, `asin`, `atan`, `atan2(dy, dx)`, `ceil`, `clamp(value, min, max)`, `cos`, `exp`, `floor`, `hypot`, `log`, `max(v1, v2, ...)`, `min(v1, v2, ...)`, `pow(value, exponent)`, `random()`, `round`, `sin`, `sqrt`, `tan`.

Also: `isNaN`, `isFinite`.

## Statistical Functions

| Function | Description |
|----------|-------------|
| `sampleNormal([mean, stdev])` | ≥5.7 Sample from normal distribution |
| `cumulativeNormal(value[, mean, stdev])` | CDF of normal |
| `densityNormal(value[, mean, stdev])` | PDF of normal |
| `quantileNormal(probability[, mean, stdev])` | Inverse CDF of normal |
| `sampleLogNormal([mean, stdev])` | ≥5.7 Sample from log-normal |
| `cumulativeLogNormal(value[, mean, stdev])` | CDF of log-normal |
| `densityLogNormal(value[, mean, stdev])` | PDF of log-normal |
| `quantileLogNormal(probability[, mean, stdev])` | Inverse CDF of log-normal |
| `sampleUniform([min, max])` | ≥5.7 Sample from uniform distribution |
| `cumulativeUniform(value[, min, max])` | CDF of uniform |
| `densityUniform(value[, min, max])` | PDF of uniform |
| `quantileUniform(probability[, min, max])` | Inverse CDF of uniform |

## Date-Time Functions

### Local Time
| Function | Description |
|----------|-------------|
| `now()` | Current timestamp |
| `datetime(year, month[, day, hour, min, sec, millisec])` | New Date (month is 0-based) |
| `date(datetime)` | Day of month |
| `day(datetime)` | Day of week |
| `dayofyear(datetime)` | ≥5.11 Day of year (1-based) |
| `year(datetime)` | Year |
| `quarter(datetime)` | Quarter (0-3) |
| `month(datetime)` | Month (0-based) |
| `week(date)` | ≥5.11 Week number (Sunday-based) |
| `hours(datetime)` | Hours |
| `minutes(datetime)` | Minutes |
| `seconds(datetime)` | Seconds |
| `milliseconds(datetime)` | Milliseconds |
| `time(datetime)` | Epoch timestamp |
| `timezoneoffset(datetime)` | Offset to UTC |
| `timeOffset(unit, date[, step])` | ≥5.8 Offset date by time unit |
| `timeSequence(unit, start, stop[, step])` | ≥5.8 Array of dates in sequence |

### UTC Time
All local functions have UTC equivalents: `utc()`, `utcdate()`, `utcday()`, `utcdayofyear()`, `utcyear()`, `utcquarter()`, `utcmonth()`, `utcweek()`, `utchours()`, `utcminutes()`, `utcseconds()`, `utcmilliseconds()`, `utcOffset()`, `utcSequence()`.

## Array Functions

| Function | Description |
|----------|-------------|
| `extent(array)` | ≥4.0 [min, max], ignoring null/undefined/NaN |
| `clampRange(range, min, max)` | Clamp range span-preserving |
| `indexof(array, value)` | First index of value |
| `inrange(value, range)` | Value within range array bounds |
| `join(array[, separator])` | ≥5.3 Concatenate with commas |
| `lastindexof(array, value)` | Last index |
| `length(array)` | Array length |
| `lerp(array, fraction)` | Linear interpolation between first/last |
| `peek(array)` | Last element (non-destructive) |
| `pluck(array, field)` | ≥5.19 Extract field from array of objects |
| `reverse(array)` | ≥5.3 Reversed copy |
| `sequence([start,] stop[, step])` | Arithmetic sequence (stop exclusive) |
| `slice(array, start[, end])` | Array section |
| `sort(array)` | ≥5.31 Natural ascending sort |
| `span(array)` | Last - first element difference |

## String Functions

| Function | Description |
|----------|-------------|
| `indexof(string, substring)` | First index |
| `lastindexof(string, substring)` | Last index |
| `length(string)` | String length |
| `lower(string)` | Lowercase |
| `pad(string, length[, character, align])` | Pad to length (align: 'left', 'center', 'right') |
| `parseFloat(string)` | Parse float |
| `parseInt(string)` | Parse int |
| `replace(string, pattern, replacement)` | Replace first match |
| `slice(string, start[, end])` | String section |
| `split(string, separator[, limit])` | ≥4.3 Split into array |
| `substring(string, start[, end])` | Substring |
| `trim(string)` | ≥5.3 Remove whitespace |
| `truncate(string, length[, align, ellipsis])` | Truncate with optional ellipsis (default: …) |
| `upper(string)` | Uppercase |
| `btoa(string)` | ≥5.32 Base64 encode |
| `atob(string)` | ≥5.32 Base64 decode |
| `encodeURIComponent(string)` | URI encode |

## Object Functions

| Function | Description |
|----------|-------------|
| `merge(object1[, object2, ...])` | ≥4.0 Shallow merge (later keys overwrite) |

## Formatting Functions

| Function | Description |
|----------|-------------|
| `dayFormat(day)` | Weekday name (0-6) |
| `dayAbbrevFormat(day)` | Abbreviated weekday |
| `format(value, specifier)` | d3-format number → string |
| `monthFormat(month)` | Full month name (0-based) |
| `monthAbbrevFormat(month)` | Abbreviated month |
| `timeUnitSpecifier(units[, specifiers])` | ≥5.8 Generate time format specifier |
| `timeFormat(value, specifier)` | Date → local string (d3-time-format) |
| `timeParse(string, specifier)` | Parse string to Date (local) |
| `utcFormat(value, specifier)` | Date → UTC string |
| `utcParse(value, specifier)` | Parse string to Date (UTC) |

## RegExp Functions

| Function | Description |
|----------|-------------|
| `regexp(pattern[, flags])` | Create RegExp instance |
| `test(regexp[, string])` | Test pattern against string |

## Color Functions

Color functions return objects that coerce to CSS RGB strings.

| Function | Description |
|----------|-------------|
| `rgb(r, g, b[, opacity])` or `rgb(specifier)` | RGB color |
| `hsl(h, s, l[, opacity])` or `hsl(specifier)` | HSL color |
| `lab(l, a, b[, opacity])` or `lab(specifier)` | CIE LAB color |
| `hcl(h, c, l[, opacity])` or `hcl(specifier)` | HCL (hue, chroma, luminance) |
| `luminance(specifier)` | ≥5.7 Relative luminance (WCAG) |
| `contrast(color1, color2)` | ≥5.7 Contrast ratio (1-21, WCAG) |

## Event Functions

Only valid in event handler expressions.

| Function | Description |
|----------|-------------|
| `item()` | Current scenegraph item target of event |
| `group([name])` | Ancestor group mark item |
| `xy([item])` | [x, y] coordinates of event |
| `x([item])` | X coordinate |
| `y([item])` | Y coordinate |
| `pinchDistance(event)` | Distance between two touch points |
| `pinchAngle(event)` | Angle between two touch points |
| `inScope(item)` | Is item a descendant of handler's group? |

## Data Functions

| Function | Description |
|----------|-------------|
| `data(name)` | Array of data objects for named dataset |
| `indata(name, field, value)` | Test if dataset contains matching datum |

## Scale & Projection Functions

| Function | Description |
|----------|-------------|
| `scale(name, value[, group])` | Apply scale/projection to value |
| `invert(name, value[, group])` | Invert scale/projection |
| `copy(name[, group])` | Clone scale/projection instance |
| `domain(name[, group])` | Get scale domain array |
| `range(name[, group])` | Get scale range array |
| `bandwidth(name[, group])` | Band width for band scale |
| `bandspace(count[, paddingInner, paddingOuter])` | Steps needed in band scale |
| `gradient(scale, p0, p1[, count])` | Linear color gradient from continuous scheme |

### Panning Functions
| Function | Description |
|----------|-------------|
| `panLinear(domain, delta)` | Pan linear domain by fractional delta |
| `panLog(domain, delta)` | Pan log domain |
| `panPow(domain, delta, exponent)` | Pan power domain |
| `panSymlog(domain, delta, constant)` | Pan symmetric log domain |

### Zooming Functions
| Function | Description |
|----------|-------------|
| `zoomLinear(domain, anchor, scaleFactor)` | Zoom linear domain at fractional anchor |
| `zoomLog(domain, anchor, scaleFactor)` | Zoom log domain |
| `zoomPow(domain, anchor, scaleFactor, exponent)` | Zoom power domain |
| `zoomSymlog(domain, anchor, scaleFactor, constant)` | Zoom symlog domain |

## Geographic Functions

For GeoJSON features with a named projection.

| Function | Description |
|----------|-------------|
| `geoArea(projection, feature[, group])` | Projected planar area (or steradians if null) |
| `geoBounds(projection, feature[, group])` | Projected bounding box [[x0,y0],[x1,y1]] |
| `geoCentroid(projection, feature[, group])` | Projected centroid |
| `geoScale(projection[, group])` | Scale value for projection |

## Tree Functions

For hierarchies built with `stratify` or `nest` transforms.

| Function | Description |
|----------|-------------|
| `treePath(name, source, target)` | Shortest path through hierarchy |
| `treeAncestors(name, node)` | Array of ancestors from node to root |

## Browser & Logging

| Function | Description |
|----------|-------------|
| `containerSize()` | [clientWidth, clientHeight] of parent DOM element |
| `screen()` | window.screen object (or {}) |
| `windowSize()` | [innerWidth, innerHeight] |
| `warn(value1[, value2, ...])` | Log warning and return last argument |
