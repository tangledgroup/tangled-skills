---
name: numeral-2-0-6
description: A JavaScript library for formatting and manipulating numbers. Use when formatting currency, percentages, bytes, time durations, ordinals, exponential notation, or abbreviations in browser or Node.js applications.
---

# Numeral.js 2.0.6

## Overview

Numeral.js is a lightweight JavaScript library (~6 KB minified) for formatting and manipulating numbers. It provides a fluent API for converting raw numeric values into human-readable strings — currency, percentages, file sizes, ordinals, time durations, exponential notation, and abbreviated forms (k, m, b, t).

It supports 34 built-in locales with localized delimiters, abbreviations, ordinal rules, and currency symbols. Locales are registered via `numeral.register()` and switched at runtime with `numeral.locale()`.

The library handles floating-point precision issues in arithmetic operations through an internal correction factor, making it suitable for financial calculations where `0.1 + 0.2 !== 0.3` matters.

## When to Use

- Formatting numbers as currency (`$1,234.56`, `€1.234,56`)
- Displaying percentages (`45.5%`)
- Showing file sizes in human-readable form (`2.35 MB`, `1.0 GiB`)
- Abbreviating large numbers (`2.5k`, `3.1m`)
- Formatting ordinal numbers (`1st`, `2nd`, `3rd`, `4th`)
- Converting seconds to time strings (`1:05:30`)
- Exponential notation formatting (`1.23e+5`)
- Parsing formatted number strings back to numeric values (auto-unformat on construction)
- Performing arithmetic with reduced floating-point drift (`add`, `subtract`, `multiply`, `divide`)

## Installation

```bash
npm install numeral
```

```html
<!-- CDN -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/numeral.js/2.0.6/numeral.min.js"></script>
```

CommonJS / ES module usage:

```javascript
const numeral = require('numeral');
// or
import numeral from 'numeral';
```

## Core API

### Construction

Create a numeral instance from a number, string, or null:

```javascript
numeral(1234.56)        // → Numeral { _value: 1234.56 }
numeral('1,234.56')     // → Numeral { _value: 1234.56 } (auto-unformat)
numeral(null)           // → Numeral { _value: null }
numeral(NaN)            // → Numeral { _value: null }
numeral(0)              // → Numeral { _value: 0 }
```

String inputs are automatically parsed using the current locale's delimiters and abbreviations. The old `unformat()` method was removed in v2.0 — unformatting now happens at construction time.

### Instance Methods

**`format([string], [roundingFunction])`** — Format the value as a string:

```javascript
numeral(1234567.89).format('0,0')       // "1,234,568"
numeral(1234567.89).format('0,0.00')    // "1,234,567.89"
numeral(1234567.89).format('0.0a')      // "1.2m"
numeral(0.95).format('0,0%')            // "95%"
```

**`value()`** — Get the underlying numeric value.
**`input()`** — Get the original input passed to the constructor.
**`set(value)`** — Change the underlying value.
**`add(value)`** / **`subtract(value)`** / **`multiply(value)`** / **`divide(value)`** — Arithmetic with floating-point correction.
**`difference(value)`** — Absolute difference.
**`clone()`** — Create a new numeral instance with the same value.

### Global Options

```javascript
numeral.locale('de');                    // switch to German
numeral.defaultFormat('$0,0.00');        // default for .format() with no arg
numeral.zeroFormat('—');                 // custom string for zero values
numeral.nullFormat('N/A');               // custom string for null values
numeral.reset();                         // reset all options to defaults
numeral.options.scalePercentBy100 = false;  // disable percent scaling
```

### Registration and Validation

```javascript
// Register a custom locale
numeral.register('locale', 'custom', {
    delimiters: { thousands: "'", decimal: '.' },
    abbreviations: { thousand: 'k', million: 'm', billion: 'b', trillion: 't' },
    ordinal: function(number) { return 'th'; },
    currency: { symbol: '¤' }
});

// Validate a string as a properly formatted number
numeral.validate('1,234.56')              // true
numeral.validate('1,23,456')              // false
```

## Built-in Locales

Numeral.js ships with 34 locales: `bg`, `chs`, `cs`, `da-dk`, `de`, `de-ch`, `en` (default), `en-au`, `en-gb`, `en-za`, `es-es`, `fr-fr`, `it-it`, `ja`, `ko`, `lt`, `lv`, `nb-no`, `nl-nl`, `pl`, `pt-br`, `pt-pt`, `ro`, `ru`, `sk`, `sl`, `sr`, `sv`, `tr`, `uk`, `vi`, and others.

## Migration Notes (v1.x to v2.0)

- **`unformat()` removed** — Parsing happens at construction: `numeral('1,234')`
- **`language` renamed to `locale`** — Use `numeral.locale()` and `numeral.localeData()`
- **Formats are separate files** — Loaded via `numeral.register('format', name, {})`
- **Locales standardized** — All lowercase keys
- **Bytes format changed** — `b` is base 1000 (decimal), `ib` is base 1024 (binary/IEC)
- **`NaN` treated as `null`** — No longer throws an error

## Advanced Topics

**API Reference**: Instance methods, format strings, rounding — [API & Format Strings](reference/01-api-and-format-strings.md)
**Usage Examples**: Financial dashboards, file sizes, i18n, arithmetic — [Usage Examples](reference/02-usage-examples.md)
