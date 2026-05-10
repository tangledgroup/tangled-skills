---
name: dayjs-1-11-20
description: Complete toolkit for date and time manipulation using Day.js 1.11.20, a minimalist 2kB library with Moment.js-compatible API. Use when parsing, validating, manipulating, and displaying dates in JavaScript applications requiring immutable operations, i18n support, and plugin extensibility.
version: "0.1.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - date
  - time
  - parsing
  - formatting
  - manipulation
  - i18n
  - plugins
  - immutable
category: utilities
external_references:
  - https://day.js.org/
  - https://github.com/iamkun/dayjs
---

# Day.js 1.11.20

## Overview

Day.js is a minimalist 2kB JavaScript library that parses, validates, manipulates, and displays dates and times for modern browsers and Node.js. It provides a largely Moment.js-compatible API while being immutable, chainable, and tree-shakeable. The core library ships with no plugins — functionality is extended on demand via a plugin system. Locales are loaded individually, keeping bundle size minimal.

Key characteristics:

- **2kB gzipped** — significantly smaller than Moment.js (~30kB)
- **Immutable** — all mutating operations return new instances
- **Chainable** — fluent API for composed date operations
- **I18n** — 80+ locales, loaded on demand (none included by default)
- **Plugin architecture** — 30+ official plugins, extend only what you need
- **Moment.js-compatible API** — drop-in replacement patterns

```javascript
import dayjs from 'dayjs'

dayjs('2018-08-08')                        // parse
dayjs().format('YYYY-MM-DD HH:mm:ss')      // display
dayjs().set('month', 3).month()            // get & set
dayjs().add(1, 'year')                     // manipulate
dayjs().isBefore(dayjs())                  // query
```

## When to Use

- Parsing date strings, timestamps, or Date objects into a manipulable format
- Formatting dates for display (ISO 8601, custom patterns, localized output)
- Adding, subtracting, or comparing dates and times
- Getting or setting individual date components (year, month, day, hour, etc.)
- Working with UTC or time zones
- Internationalizing date/time display across 80+ locales
- Replacing Moment.js to reduce bundle size
- Building immutable date pipelines with method chaining

## Core Concepts

### Immutability

Every Day.js operation that changes the date returns a **new** instance. The original is never modified:

```javascript
const d1 = dayjs('2019-01-25')
const d2 = d1.add(7, 'day')
d1.format('YYYY-MM-DD') // '2019-01-25' — unchanged
d2.format('YYYY-MM-DD') // '2019-02-01' — new instance
```

### Method Chaining

Operations return Day.js instances, enabling fluent chains:

```javascript
dayjs('2019-01-25')
  .add(1, 'day')
  .subtract(1, 'year')
  .year(2009)
  .format('YYYY-MM-DD') // '2008-01-26'
```

### Units

Day.js accepts units in multiple forms — long, plural, and short. Long and plural forms are case-insensitive; short forms are case-sensitive:

- `year` / `years` / `y`
- `month` / `months` / `M`
- `week` / `weeks` / `w`
- `day` / `days` / `d`
- `hour` / `hours` / `h`
- `minute` / `minutes` / `m`
- `second` / `seconds` / `s`
- `millisecond` / `milliseconds` / `ms`
- `date` / `dates` (day of month, distinct from day-of-week)

### The Dayjs Class

Instead of modifying `Date.prototype`, Day.js creates a wrapper around the native `Date` object. Internally it stores parsed values (`$y`, `$M`, `$D`, `$H`, `$m`, `$s`, `$ms`) for fast access. The internal `$d` property holds the underlying `Date` instance. Calling `dayjs()` with any supported input type returns this wrapper.

### Special Input Values

- `dayjs()` or `dayjs(undefined)` — current date and time
- `dayjs(null)` — invalid input (fails `isValid()`)
- `dayjs(dayjsInstance)` — clones the existing instance

## Installation / Setup

**Node.js (npm):**
```bash
npm install dayjs
```

```javascript
import dayjs from 'dayjs'
// or
const dayjs = require('dayjs')
```

**Browser (CDN):**
```html
<script src="https://cdn.jsdelivr.net/npm/dayjs/dayjs.min.js"></script>
<script>
  dayjs().format()
</script>
```

The global `dayjs` function is available after loading. Day.js works in all modern browsers and Node.js environments.

## Advanced Topics

**Parsing**: Creating Day.js instances from strings, timestamps, Date objects, and more → [Parsing](reference/01-parsing.md)

**Get and Set**: Reading and writing individual date components with overloaded getters/setters → [Get and Set](reference/02-get-set.md)

**Manipulation**: Adding, subtracting, start-of/end-of operations, and UTC conversion → [Manipulation](reference/03-manipulation.md)

**Display**: Formatting, relative time, calendar time, differences, and serialization → [Display](reference/04-display.md)

**Query**: Comparison methods for checking temporal relationships → [Query](reference/05-query.md)

**Internationalization (i18n)**: Loading locales, switching languages, and customization → [Internationalization](reference/06-i18n.md)

**Plugins**: Extending Day.js with 30+ official plugins including Duration, UTC, Timezone, and more → [Plugins](reference/07-plugins.md)
