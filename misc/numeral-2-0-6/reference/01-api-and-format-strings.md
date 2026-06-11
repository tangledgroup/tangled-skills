# API & Format Strings

## Instance Methods (Full Reference)

All instance methods return the numeral instance for chaining, except `format`, `value`, `input`, and `difference`.

**`format([string], [roundingFunction])`** — Format the value as a string. The optional `roundingFunction` accepts `Math.floor`, `Math.ceil`, or `Math.round` (default).

```javascript
numeral(1234567.89).format('0,0')       // "1,234,568"
numeral(1234567.89).format('0,0.00')    // "1,234,567.89"
numeral(1234567.89).format('0.0a')      // "1.2m"
numeral(0.95).format('0,0%')            // "95%"
```

**`value()`** — Get the underlying numeric value:

```javascript
numeral(1234.56).value()   // 1234.56
numeral(null).value()      // null
```

**`input()`** — Get the original input passed to the constructor:

```javascript
numeral('1,234.56').input()  // "1,234.56"
```

**`set(value)`** — Change the underlying value:

```javascript
numeral(100).set(200).value()  // 200
```

**`add(value)`** — Add with floating-point correction:

```javascript
numeral(0.1).add(0.2).value()  // 0.3 (not 0.30000000000000004)
```

**`subtract(value)`** — Subtract with floating-point correction:

```javascript
numeral(1.0).subtract(0.9).value()  // 0.1
```

**`multiply(value)`** — Multiply with floating-point correction:

```javascript
numeral(0.1).multiply(0.2).value()  // 0.02
```

**`divide(value)`** — Divide with floating-point correction:

```javascript
numeral(0.3).divide(0.1).value()  // 3
```

**`difference(value)`** — Absolute difference:

```javascript
numeral(10).difference(3)   // 7
numeral(3).difference(10)   // 7
```

**`clone()`** — Create a new numeral instance with the same value:

```javascript
const n = numeral(100);
const copy = n.clone();
```

## Format Strings

Numeral.js uses format strings composed of specific characters. Spaces before or after most tokens are supported and preserved in output.

### Number Formatting (`0`)

The `0` character represents a significant digit:

```javascript
numeral(1234567).format('0')         // "1234567"
numeral(1234567).format('0,0')       // "1,234,567"
numeral(1234567).format('0,0.00')    // "1,234,567.00"
numeral(1234.56789).format('0,0')    // "1,235"
numeral(1234.56789).format('0,0.00') // "1,234.57"
```

Leading zeros pad short numbers:

```javascript
numeral(5).format('000')   // "005"
numeral(42).format('000')  // "042"
```

### Optional Decimals (`[0]`)

Wrap trailing decimal `0`s in brackets to make them optional — omitted when zero:

```javascript
numeral(1234.5).format('0,0.[00]')   // "1,234.5"
numeral(1234.50).format('0,0.[00]')  // "1,234.5"
numeral(1234.56).format('0,0.[00]')  // "1,234.56"
numeral(1234).format('0,0.[00]')     // "1,234"
```

### Abbreviations (`a`)

The `a` token abbreviates large numbers:

```javascript
numeral(1234567).format('0a')         // "1m"
numeral(1234567).format('0.0a')       // "1.2m"
numeral(1234).format('0a')            // "1k"
numeral(1234567890).format('0a')      // "1b"
numeral(1234567890123).format('0a')   // "1t"
```

Force a specific abbreviation level with `ak`, `am`, `ab`, or `at`:

```javascript
numeral(1234567).format('0.0ab')  // "1,234.6b" (force billion scale)
numeral(1234).format('0.0am')     // "0.0m" (force million scale)
```

Space before `a` adds a space in output: `'0.0 a'` → `"1.2 m"`.

### Currency (`$`)

The `$` token uses the current locale's currency symbol. Position it before or after the number, with optional spaces:

```javascript
numeral(1234567.89).format('$0,0.00')      // "$1,234,567.89"
numeral(1234567.89).format('0,0.00$')      // "1,234,567.89$"
numeral(1234567.89).format('$ 0,0')        // "$ 1,234,568"
numeral(1234567.89).format('0,0 $')        // "1,234,568 $"
```

Multi-letter currency symbols (like `€`, `£`) are supported with proper spacing.

### Negative Numbers

Three styles:

**Minus sign** (default):

```javascript
numeral(-1234).format('0,0')        // "-1,234"
```

**Parentheses**:

```javascript
numeral(-1234).format('($0,0)')     // "($1,234)"
numeral(1234).format('($0,0)')      // "$1,234"
```

**Signed values** — use `+` or `-` to always show the sign:

```javascript
numeral(1234).format('+0,0')        // "+1,234"
numeral(-1234).format('-0,0')       // "-1,234"
numeral(1234).format('0,0+')        // "1,234+"
numeral(-1234).format('0,0-')       // "1,234-"
```

### Percentages (`%`)

The `%` token multiplies the value by 100 and appends the percent sign:

```javascript
numeral(0.95).format('0%')          // "95%"
numeral(0.95).format('0.00%')       // "95.00%"
numeral(0.1234).format('0.000%')    // "12.340%"
numeral(0.5).format('0 %')          // "50 %" (space before %)
```

Control scaling with the `scalePercentBy100` option:

```javascript
numeral.options.scalePercentBy100 = false;
numeral(95).format('0%')  // "95%" (no multiplication)
```

### Ordinals (`o`)

The `o` token appends the locale-specific ordinal suffix:

```javascript
numeral(1).format('0o')    // "1st"
numeral(2).format('0o')    // "2nd"
numeral(3).format('0o')    // "3rd"
numeral(4).format('0o')    // "4th"
numeral(11).format('0o')   // "11th"
numeral(12).format('0o')   // "12th"
```

Space before `o` adds a space: `'0 o'` → `"1 st"`.

### Bytes (`b`, `ib`)

Format file sizes using decimal (base 1000) or binary (base 1024) units:

```javascript
// Decimal — base 1000
numeral(1234).format('0.00 b')       // "1.23 KB"
numeral(1234567).format('0.00 b')    // "1.23 MB"
numeral(1234567890).format('0.00 b') // "1.23 GB"

// Binary — base 1024
numeral(1234).format('0.00 ib')       // "1.21 KiB"
numeral(1234567).format('0.00 ib')    // "1.18 MiB"
numeral(1234567890).format('0.00 ib') // "1.15 GiB"
```

Suffixes: `B`, `KB`/`KiB`, `MB`/`MiB`, `GB`/`GiB`, `TB`/`TiB`, `PB`/`PiB`, `EB`/`EiB`, `ZB`/`ZiB`, `YB`/`YiB`.

Space before `b` or `ib` adds a space in output.

### Exponential Notation (`e+`, `e-`)

Format numbers in scientific notation:

```javascript
numeral(123456789).format('0.00e+0')  // "1.23e+8"
numeral(0.001234).format('0.00e-0')   // "1.23e-3"
```

The digits after `e+` or `e-` control the minimum exponent width (leading zeros).

### Time (`:`)

Convert seconds to a time string:

```javascript
numeral(3934).format('00:00:00')  // "01:05:34"
numeral(125).format('00:00')      // "02:05"
numeral(3661).format('0:00:00')   // "1:01:01"
```

Parse time strings back to seconds via construction:

```javascript
numeral('01:05:34').value()  // 3934
numeral('02:05').value()     // 125
```

### Basis Points (`BPS`)

Format financial basis points (1 bp = 0.01%):

```javascript
numeral(0.1234).format('0,0 BPS')  // "12,340 BPS"
numeral(0.005).format('0 BPS')     // "50 BPS"
```

## Global Options (Full Reference)

**`numeral.locale([key])`** — Get or set the current locale:

```javascript
numeral.locale()          // "en"
numeral.locale('de')      // switch to German
numeral(1234567.89).format('0,0')  // "1.234.568" (German delimiters)
```

**`numeral.localeData([key])`** — Get locale data object:

```javascript
numeral.localeData()             // current locale data
numeral.localeData('de')         // German locale data
// Returns: { delimiters, abbreviations, ordinal, currency }
```

**`numeral.defaultFormat(format)`** — Set default format for `.format()` with no argument:

```javascript
numeral.defaultFormat('$0,0.00');
numeral(1234.5).format();  // "$1,234.50"
```

**`numeral.zeroFormat(format)`** — Custom string for zero values:

```javascript
numeral.zeroFormat('—');
numeral(0).format('0,0');  // "—"
```

**`numeral.nullFormat(format)`** — Custom string for null values:

```javascript
numeral.nullFormat('N/A');
numeral(null).format('0,0');  // "N/A"
```

**`numeral.reset()`** — Reset all options to defaults (locale → 'en', zeroFormat → null, nullFormat → null, defaultFormat → '0,0').

**`numeral.options`** — Access the current options object directly:

```javascript
numeral.options.currentLocale           // "en"
numeral.options.scalePercentBy100       // true (default)
numeral.options.scalePercentBy100 = false;  // disable percent scaling
```

## Registration API

**`numeral.register(type, name, definition)`** — Register a format or locale:

```javascript
numeral.register('locale', 'custom', {
    delimiters: { thousands: "'", decimal: '.' },
    abbreviations: { thousand: 'k', million: 'm', billion: 'b', trillion: 't' },
    ordinal: function(number) { return 'th'; },
    currency: { symbol: '¤' }
});

numeral.locale('custom');
numeral(1234567).format('0,0')  // "1'234'567"
```

Format definitions include `regexps` (matching patterns) and `format`/`unformat` functions. See the source `src/formats/` directory for examples of custom format implementations.

## Validation

**`numeral.validate(value, [culture])`** — Validate a string as a properly formatted number:

```javascript
numeral.validate('1,234.56')              // true
numeral.validate('$1,234.56')             // true
numeral.validate('1.234,56', 'de')        // true (German locale)
numeral.validate('1,23,456')              // false
numeral.validate('')                      // false
```

The optional `culture` parameter specifies the locale for validation. If omitted or unknown, uses the current locale.
