---
name: numeral-2
description: A JavaScript library for formatting and manipulating numbers. Use when formatting currency, percentages, bytes, time durations, ordinals, or exponential notation in browser or Node.js applications.
version: "0.2.0"
author: Your Name <email@example.com>
license: MIT
tags:
  - number-formatting
  - currency
  - percentage
  - bytes
  - localization
  - javascript
category: utility
---

# Numeral.js 2

Numeral.js is a JavaScript library for formatting and manipulating numbers. It provides consistent number formatting across different locales with support for currency, percentages, bytes, time durations, ordinals, abbreviations, and exponential notation.

## When to Use

- Formatting numbers for display (currency, percentages, file sizes)
- Localizing number formats for different regions (thousands separators, decimal points)
- Parsing formatted number strings back to numeric values
- Creating custom number format patterns
- Working with abbreviated large numbers (1.2m, 3.5b)
- Formatting time durations from seconds
- Displaying ordinal numbers (1st, 2nd, 3rd)

## Installation

### Browser

Include directly via script tag:

```html
<script src="numeral.min.js"></script>
```

Or from CDN:

```html
<script src="//cdnjs.cloudflare.com/ajax/libs/numeral.js/2.0.6/numeral.min.js"></script>
```

### Node.js

Install via npm:

```bash
npm install numeral
```

Require in your code:

```javascript
var numeral = require('numeral');
```

### AMD / RequireJS

Numeral.js works with AMD loaders:

```javascript
require(['numeral'], function(numeral) {
    // use numeral
});
```

## Quick Start

Create a numeral instance and format it:

```javascript
var myNumeral = numeral(1000);

myNumeral.format('0,0');        // "1,000"
myNumeral.format('0.000');      // "1000.000"
myNumeral.value();              // 1000
```

Parse formatted strings back to numbers:

```javascript
numeral('1,000').value();       // 1000
numeral('$1,000.23').value();   // 1000.23
numeral('(1,000)').value();     // -1000 (accounting negative)
```

## Core API

### Creating Instances

**From numbers:**

```javascript
numeral(1000);                  // Creates numeral instance
numeral(0);                     // Zero value
numeral(-500);                  // Negative value
numeral(NaN);                   // Returns null value
numeral(null);                  // Returns null value
```

**From strings:**

```javascript
numeral('1,000');               // Parses to 1000
numeral('$1,234.56');           // Parses to 1234.56
numeral('(500)');               // Parses to -500 (accounting notation)
```

**From existing numeral instances:**

```javascript
var a = numeral(1000);
var b = numeral(a);             // Creates new instance with same value
```

### Instance Methods

**`value()`** - Get the underlying numeric value:

```javascript
numeral(1000).value();          // 1000
numeral('1,000').value();       // 1000
numeral(null).value();          // null
numeral(NaN).value();           // null
```

**`format(formatString)`** - Format the number:

```javascript
numeral(1000).format('0,0');    // "1,000"
numeral(1000.456).format('0.00');// "1000.46"
```

**`set(value)`** - Set a new value:

```javascript
var n = numeral();
n.set(1000);
n.value();                      // 1000
```

**`add(value)`** - Add to the current value:

```javascript
numeral(1000).add(500).value(); // 1500
```

**`subtract(value)`** - Subtract from current value:

```javascript
numeral(1000).subtract(500).value(); // 500
```

**`multiply(value)`** - Multiply the value:

```javascript
numeral(1000).multiply(2).value();   // 2000
```

**`divide(value)`** - Divide the value:

```javascript
numeral(1000).divide(2).value();     // 500
```

**`difference(numeral)`** - Calculate difference between two numerals:

```javascript
var a = numeral(1000);
var b = numeral(750);
a.difference(b).value();      // 250
b.difference(a).value();      // -250
```

**`clone()`** - Create a copy of the instance:

```javascript
var a = numeral(1000);
var b = a.clone();
b.set(2000);
a.value();                    // 1000 (unchanged)
```

### Global Functions

**`numeral(value)`** - Create new instance:

```javascript
numeral(1000);
numeral('1,000');
```

**`numeral.isNumeral(obj)`** - Check if object is a numeral instance:

```javascript
numeral.isNumeral(numeral(1000));  // true
numeral.isNumeral(1000);           // false
```

**`numeral.validate(string, locale)`** - Validate formatted number string:

```javascript
numeral.validate('1,000', 'en');   // true
numeral.validate('$1,000.23', 'en');// true
numeral.validate('1.0.00', 'en');  // false
```

**`numeral.version`** - Get library version:

```javascript
numeral.version;                    // "2.0.6"
```

## Global Configuration

**`defaultFormat(formatString)`** - Set default format for `.format()` without arguments:

```javascript
numeral.defaultFormat('0,0');
numeral(1000).format();             // "1,000"
```

**`zeroFormat(string)`** - Set custom string for zero values:

```javascript
numeral.zeroFormat('N/A');
numeral(0).format('0,0');           // "N/A"
```

**`nullFormat(string)`** - Set custom string for null values:

```javascript
numeral.nullFormat('Unknown');
numeral(null).format('0,0');        // "Unknown"
```

**`reset()`** - Reset all options to defaults:

```javascript
numeral.reset();
```

**`options`** - Access configuration object:

```javascript
numeral.options.currentLocale;      // Current locale
numeral.options.zeroFormat;         // Current zero format
numeral.options.nullFormat;         // Current null format
numeral.options.defaultFormat;      // Current default format
numeral.options.scalePercentBy100;  // Percentage scaling option
```

## Format Strings

### Basic Number Formatting

**Thousands separators:**

```javascript
numeral(1000).format('0,0');        // "1,000"
numeral(1234567).format('0,0');     // "1,234,567"
```

**Decimal places:**

```javascript
numeral(1000.12345).format('0.0');  // "1000.1"
numeral(1000.12345).format('0.00'); // "1000.12"
numeral(1000.12345).format('0.000');// "1000.123"
```

**Combined:**

```javascript
numeral(1234567.891).format('0,0.00'); // "1,234,567.89"
```

### Optional Decimals

Use square brackets for optional decimal places:

```javascript
numeral(10000).format('0[.]00');         // "10000" (no decimals shown)
numeral(10000.1).format('0[.]00');       // "10000.10"
numeral(10000.123).format('0[.]00');     // "10000.12"
numeral(10000.456).format('0[.]00');     // "10000.46"
numeral(10000.001).format('0[.]00');     // "10000" (rounds to whole)

// Optional trailing decimals
numeral(10000.45).format('0[.]00[0]');   // "10000.45"
numeral(10000.456).format('0[.]00[0]');  // "10000.456"
```

### Leading Zeros

Specify minimum digit count with leading zeros:

```javascript
numeral(4).format('000');        // "004"
numeral(10).format('00000');     // "00010"
numeral(0).format('00.0');       // "00.0"
numeral(0.23).format('000.[00]');// "000.23"
```

With thousands separators:

```javascript
numeral(1000).format('000,0');   // "1,000"
numeral(1000).format('00000,0'); // "01,000"
numeral(1000).format('0000000,0');// "0,001,000"
```

### Signed Numbers

**Always show sign:**

```javascript
numeral(1230).format('+0,0');    // "+1,230"
numeral(-1230).format('+0,0');   // "-1,230"

// Sign only for negative
numeral(1230).format('-0,0');    // "1,230"
numeral(-1230).format('-0,0');   // "-1,230"
```

**Suffix sign:**

```javascript
numeral(-1230.4).format('0,0.0-');// "1,230.4-"
numeral(1230.4).format('0,0.0-'); // "1,230.4"
```

**Accounting notation (parentheses):**

```javascript
numeral(10000).format('(0,0)');  // "10,000"
numeral(-10000).format('(0,0)'); // "(10,000)"
```

### Abbreviations

Use `a` to abbreviate large numbers:

```javascript
numeral(1460).format('0a');           // "1k"
numeral(1230974).format('0.0a');      // "1.2m"
numeral(2000000000).format('0.0a');   // "2.0b"
```

**With space before abbreviation:**

```javascript
numeral(-104000).format('0 a');       // "-104 k"
numeral(1230974).format('0.0 a');     // "1.2 m"
```

**Force specific abbreviation level:**

```javascript
numeral(5444333222111).format('0,0 ak');// "5,444,333,222 k"
numeral(5444333222111).format('0,0 am');// "5,444,333 m"
numeral(5444333222111).format('0,0 ab');// "5,444 b"
numeral(5444333222111).format('0,0 at');// "5 t"
```

Supported abbreviations: `k` (thousand), `m` (million), `b` (billion), `t` (trillion)

## Format Types

### Currency

Use `$` in format string for currency formatting:

```javascript
numeral(1000.234).format('$0,0.00');      // "$1,000.23"
numeral(-1000.234).format('$0,0.00');     // "-$1,000.23"
```

**Currency symbol position:**

```javascript
numeral(1000.23).format('$ 0,0.00');      // "$ 1,000.23"
numeral(1000.23).format('0,0.00 $');      // "1,000.23 $"
```

**Accounting notation with currency:**

```javascript
numeral(-1000).format('($0,0)');          // "($1,000)"
numeral(-1000).format('$(0,0)');          // "$(1,000)"
numeral(-1000).format('$ (0,0)');         // "$ (1,000)"
```

**Currency with abbreviations:**

```javascript
numeral(1230974).format('($0.00 a)');     // "$1.23 m"
```

**Negative sign variations:**

```javascript
numeral(-1000).format('$-0,0');           // "$-1,000"
numeral(-1000).format('$ -0,0');          // "$ -1,000"
```

### Percentage

Use `%` in format string:

```javascript
numeral(0.9863).format('0%');             // "99%"
numeral(0.9863).format('0.0%');           // "98.6%"
numeral(0.9863).format('0.00%');          // "98.63%"
```

**Optional decimals:**

```javascript
numeral(1).format('0[.]00%');             // "100%"
numeral(0.9863).format('0[.]00%');        // "98.63%"
```

**Disable auto-scaling by 100:**

```javascript
numeral.options.scalePercentBy100 = false;
numeral(50).format('0%');                 // "50%" (not "5000%")
```

### Bytes / File Sizes

**Decimal bytes (base 1000):**

```javascript
numeral(1000).format('0.0b');             // "1.0 KB"
numeral(1000000).format('0.0b');          // "1.0 MB"
numeral(1000000000).format('0.0b');       // "1.0 GB"
```

**Binary bytes (base 1024):**

```javascript
numeral(1024).format('0.0ib');            // "1.0 KiB"
numeral(1048576).format('0.0ib');         // "1.0 MiB"
numeral(1073741824).format('0.0ib');      // "1.0 GiB"
```

**With space before unit:**

```javascript
numeral(1000).format('0.0 b');            // "1.0 KB"
numeral(1024).format('0.0 ib');           // "1.0 KiB"
```

**Parse byte strings back to numbers:**

```javascript
numeral('1.5 KB').value();                // 1500
numeral('2.5 MiB').value();               // 2621440
```

Supported units: B, KB/MB/GB/TB/PB/EB/ZB/YB (decimal) and KiB/MiB/GiB/TiB/PiB/EiB/ZiB/YiB (binary)

### Time Durations

Format seconds as time strings:

```javascript
numeral(10).format('0:0:0');              // "0:0:10"
numeral(65).format('0:0:0');              // "1:0:5"
numeral(3661).format('0:0:0');            // "1:1:1"
```

**Parse time strings back to seconds:**

```javascript
numeral('1:30').value();                  // 90 (1 minute 30 seconds)
numeral('1:2:30').value();                // 3750 (1 hour 2 minutes 30 seconds)
```

### Ordinals

Use `o` in format string for ordinal suffixes:

```javascript
numeral(1).format('0o');                  // "1st"
numeral(2).format('0o');                  // "2nd"
numeral(3).format('0o');                  // "3rd"
numeral(4).format('0o');                  // "4th"
numeral(11).format('0o');                 // "11th"
numeral(12).format('0o');                 // "12th"
numeral(13).format('0o');                 // "13th"
numeral(21).format('0o');                 // "21st"
```

**With thousands separators:**

```javascript
numeral(1001).format('0,0o');             // "1,001st"
```

### Exponential Notation

Use `e+` or `e-` for exponential format:

```javascript
numeral(123456789).format('0.00e+');      // "1.23e+8"
numeral(0.000123).format('0.00e-');       // "1.23e-4"
```

### Basis Points (BPS)

Format numbers as basis points:

```javascript
numeral(0.015).format('0 bps');           // "150 bps"
```

Parse basis points back to numbers:

```javascript
numeral('150 bps').value();               // 0.015
```

## Localization

### Setting Locale

```javascript
numeral.locale('en-gb');                  // Set to British English
numeral.locale('de');                     // Set to German
numeral.locale('fr');                     // Set to French
```

Get current locale:

```javascript
numeral.locale();                         // Returns current locale name
```

### Available Locales

Numeral.js includes these locales (use lowercase):

- `en` - English (US)
- `en-gb` - English (UK)
- `de` - German
- `de-ch` - German (Switzerland)
- `fr` - French
- `fr-ch` - French (Switzerland)
- `es` - Spanish
- `it` - Italian
- `nl` - Dutch
- `pt-br` - Portuguese (Brazil)
- `da-dk` - Danish
- `cs` - Czech
- `bg` - Bulgarian
- `chs` - Chinese (Simplified)
- `cht` - Chinese (Traditional)
- `ru` - Russian
- `fi` - Finnish
- `no` - Norwegian
- `pl` - Polish
- `sl` - Slovenian
- `sv-se` - Swedish
- `he` - Hebrew
- `hu` - Hungarian
- `el` - Greek
- `tr` - Turkish
- `ko` - Korean
- `ja` - Japanese
- `th` - Thai

### Locale Configuration

Each locale defines:

```javascript
{
    delimiters: {
        thousands: ',',      // Thousands separator
        decimal: '.'         // Decimal separator
    },
    abbreviations: {
        thousand: 'k',
        million: 'm',
        billion: 'b',
        trillion: 't'
    },
    ordinal: function(number) {
        // Function returning ordinal suffix
        return 'th';
    },
    currency: {
        symbol: '$'          // Currency symbol
    }
}
```

### Registering Custom Locales

```javascript
numeral.register('locale', 'my-locale', {
    delimiters: {
        thousands: '.',
        decimal: ','
    },
    abbreviations: {
        thousand: 'k',
        million: 'mio',
        billion: 'mia',
        trillion: 'b'
    },
    ordinal: function(number) {
        return '.';
    },
    currency: {
        symbol: '€'
    }
});

// Use the locale
numeral.locale('my-locale');
numeral(1000.5).format('$0,0.00');  // "€1.000,50"
```

### Loading Locales

Locales must be loaded before use. Each locale is a separate file:

**Browser:**
```html
<script src="numeral.js"></script>
<script src="locales/de.js"></script>
<script src="locales/fr.js"></script>
```

**Node.js:**
```javascript
var numeral = require('numeral');
require('numeral/locales/de');
require('numeral/locales/fr');

numeral.locale('de');
```

## Custom Formats

Register custom format types:

```javascript
numeral.register('format', 'custom', {
    regexps: {
        format: /(:)/,  // Regex to detect this format in format string
        unformat: /(:)/ // Regex to detect this format when parsing
    },
    format: function(value, format, roundingFunction) {
        // Custom formatting logic
        return 'custom: ' + value;
    },
    unformat: function(string) {
        // Custom parsing logic
        return Number(string.replace('custom: ', ''));
    }
});

// Use the custom format
numeral(1000).format(':0,0');  // "custom: 1,000"
```

## Utility Functions

### Rounding

Numeral.js uses standard rounding by default. You can pass custom rounding functions:

```javascript
// Always round up
numeral(1000.1).format('0', function(value) {
    return Math.ceil(value);
});  // "1001"

// Always round down
numeral(1000.9).format('0', function(value) {
    return Math.floor(value);
});  // "1000"
```

### Options Object

Access and modify global options:

```javascript
// Get current options
numeral.options.currentLocale;     // "en"
numeral.options.zeroFormat;        // null
numeral.options.nullFormat;        // null
numeral.options.defaultFormat;     // "0,0"
numeral.options.scalePercentBy100; // true

// Modify options directly
numeral.options.scalePercentBy100 = false;
```

## Common Patterns

### Displaying Prices

```javascript
// Standard currency
numeral(price).format('$0,0.00');

// Without cents for whole dollars
numeral(price).format('$0,0[.]00');

// Accounting style negatives
numeral(price).format('($0,0.00)');
```

### Displaying Statistics

```javascript
// With abbreviations
numeral(users).format('0.0a');      // "1.2m users"

// Percentages
numeral(ratio).format('0[.]0%');    // "98.5%"

// File sizes
numeral(size).format('0.0ib');      // "2.5 GiB"
```

### Formatted Input Parsing

```javascript
// Parse user input with various formats
function parseUserInput(input) {
    return numeral(input).value();
}

parseUserInput('$1,234.56');   // 1234.56
parseUserInput('1,234.56');    // 1234.56
parseUserInput('(500)');       // -500
parseUserInput('1.5k');        // 1500
```

### Conditional Formatting

```javascript
function formatValue(value, type) {
    switch(type) {
        case 'currency':
            return numeral(value).format('$0,0.00');
        case 'percentage':
            return numeral(value).format('0[.]0%');
        case 'bytes':
            return numeral(value).format('0.0ib');
        default:
            return numeral(value).format('0,0');
    }
}
```

## Browser Compatibility

Numeral.js works in all modern browsers and includes polyfills for older environments. It supports:

- Chrome, Firefox, Safari, Edge (all versions)
- Internet Explorer 9+
- Node.js (all versions)
- AMD loaders (RequireJS)
- CommonJS (Browserify, Webpack)

## Troubleshooting

### Numbers not parsing correctly

Ensure the locale matches the number format:

```javascript
// German format with German locale
numeral.locale('de');
numeral('1.000,50').value();  // 1000.50
```

### Currency symbol not showing

Check that `$` is in the format string:

```javascript
numeral(1000).format('$0,0.00');  // "$1,000.00" ✓
numeral(1000).format('0,0.00');   // "1,000.00" ✗ (no currency)
```

### Percentage not scaling correctly

Check the `scalePercentBy100` option:

```javascript
numeral.options.scalePercentBy100 = true;  // Default: 0.5 → "50%"
numeral(0.5).format('0%');                 // "50%"

numeral.options.scalePercentBy100 = false; // 0.5 → "0%"
numeral(0.5).format('0%');                 // "0%"
```

### Locale not working

Ensure the locale file is loaded before setting it:

```javascript
// Browser - load locale script first
// <script src="locales/de.js"></script>

// Node.js - require locale first
require('numeral/locales/de');
numeral.locale('de');
```

### Custom format not triggering

Ensure the format string matches the registered regex:

```javascript
numeral.register('format', 'custom', {
    regexps: {
        format: /(:)/  // Must match something in your format string
    },
    format: function(value, format) {
        return 'result';
    }
});

numeral(1000).format(':0,0');  // Works (contains :)
numeral(1000).format('0,0');   // Doesn't trigger (no :)
```

## Migration from v1.x

Key breaking changes in v2.0:

1. **Locale files renamed** - All locale filenames are now lowercase
2. **`language()` → `locale()`** - Function renamed for consistency
3. **Unformat on init** - `numeral().unformat(string)` removed; use `numeral(string)` instead
4. **Bytes format changed** - Use `b` for base 1000, `ib` for base 1024
5. **NaN handling** - `numeral(NaN)` now returns null instead of throwing error

```javascript
// v1.x
numeral.language('de');
numeral().unformat('1.000,50');

// v2.x
numeral.locale('de');
numeral('1.000,50').value();
```

## Performance Tips

- Reuse numeral instances when possible
- Set default format once rather than specifying every time
- Cache locale settings if processing many numbers in same locale
- Use simple format strings for better performance

## Limitations

- Does not fix JavaScript floating-point precision issues
- Maximum safe integer limited by JavaScript Number type
- Locale files must be explicitly loaded (not auto-included)
- Custom formats require manual registration
