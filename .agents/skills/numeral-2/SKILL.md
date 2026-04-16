---
name: numeral-2
description: A JavaScript library for formatting and manipulating numbers. Use when formatting currency, percentages, bytes, time durations, ordinals, or exponential notation in browser or Node.js applications.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
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

## See Also

- [Configuration and Format Types](references/01-format-types-and-localization.md) - Global configuration, format strings, types, and localization
