# Usage Examples

## Financial Dashboard

```javascript
// Revenue display with currency
const revenue = numeral(1234567.89).format('$0,0.00');
// "$1,234,567.89"

// Profit margin as percentage
const margin = numeral(0.2345).format('0.00%');
// "23.45%"

// Large number abbreviation for charts
const users = numeral(2456789).format('0.0a');
// "2.5m"

// Negative values with parentheses
const loss = numeral(-12345).format('($0,0)');
// "($12,345)"
```

## File Size Display

```javascript
// Decimal (SI) units
numeral(1536000).format('0.00 b');    // "1.50 MB"

// Binary (IEC) units
numeral(1536000).format('0.00 ib');   // "1.47 MiB"

// Parse back
numeral('1.50 MB').value();           // 1500000
```

## Time Formatting

```javascript
// Seconds to HH:MM:SS
numeral(3661).format('00:00:00');     // "01:01:01"

// Parse time string
numeral('01:01:01').value();          // 3661
```

## Floating-Point Safe Arithmetic

```javascript
// Standard JS has precision issues
0.1 + 0.2;                            // 0.30000000000000004

// Numeral handles it
numeral(0.1).add(0.2).value();        // 0.3
numeral(1.0).subtract(0.9).value();   // 0.1
numeral(0.1).multiply(0.2).value();   // 0.02
```

## Internationalization

```javascript
// German locale — comma as decimal, space as thousands separator
numeral.locale('de');
numeral(1234567.89).format('0,0.00');        // "1.234.567,89"
numeral(1234567.89).format('$0,0.00');       // "€1.234.567,89"

// French locale
numeral.locale('fr-fr');
numeral(1234).format('0,0');                 // "1 234"

// Reset to default
numeral.reset();
```

## Custom Zero and Null Display

```javascript
numeral.zeroFormat('—');
numeral.nullFormat('N/A');

numeral(0).format('0,0');       // "—"
numeral(null).format('0,0');    // "N/A"
numeral(1234).format('0,0');    // "1,234" (normal formatting)
```

## Rounding Control

```javascript
// Floor rounding
numeral(1234.9).format('0,0', Math.floor);   // "1,234"

// Ceiling rounding
numeral(1234.1).format('0,0', Math.ceil);    // "1,235"

// Default (round)
numeral(1234.5).format('0,0');               // "1,235"
```

## Notes

- Numeral.js does not fix JavaScript floating-point representation itself. Its arithmetic methods use a correction factor to reduce visible precision drift in common operations. For critical financial calculations, consider using a decimal library such as `decimal.js`.
- The built distribution (`numeral.min.js`) includes all formats and locales. Custom builds with only selected formats are possible from source but not officially distributed.
- The library is inspired by Moment.js in its API design philosophy — simple chainable interface with locale support.
