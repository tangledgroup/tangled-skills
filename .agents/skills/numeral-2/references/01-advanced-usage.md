# numeral-2 - Advanced Usage

This reference covers advanced topics, complete examples, and detailed configuration.

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
