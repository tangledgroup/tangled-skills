# String Formatting

## Contents
- RFC 9557 Format
- toString() Serialization
- toLocaleString() Human-Readable Output
- Parsing Strings
- String FAQ

## RFC 9557 Format

All Temporal types serialize to and parse from the RFC 9557 format, based on ISO 8601 / RFC 3339. Full form:

```
YYYY-MM-DDTHH:mm:ss.sssssssssZ/±HH:mm[time_zone_id][u-ca=calendar_id]
```

Each type requires only the components it represents:

| Type | Format Example |
|------|----------------|
| `Instant` | `2024-01-15T10:30:00Z` |
| `ZonedDateTime` | `2024-01-15T10:30:00-05:00[America/New_York]` |
| `PlainDateTime` | `2024-01-15T10:30:00` |
| `PlainDate` | `2024-01-15` |
| `PlainTime` | `10:30:00.123456789` |
| `PlainYearMonth` | `2024-01` |
| `PlainMonthDay` | `--01-15` |
| `Duration` | `P1Y2M3DT4H5M6S` (ISO 8601 duration) |

**Key additions over legacy ISO 8601:**
- Microsecond and nanosecond precision (up to 9 decimal places)
- Bracketed timezone annotation: `[America/New_York]`
- Calendar annotation: `u-ca=hebrew`

## toString() Serialization

`toString()` produces a machine-readable RFC 9557 string. All Temporal types support it.

```javascript
// Instant — always UTC
Temporal.Instant.from('2024-01-15T10:30:00Z').toString();
// '2024-01-15T10:30:00Z'

// Instant with timezone display option
Temporal.Instant.from('2024-01-15T10:30:00Z').toString({ timeZone: 'America/Yellowknife' });
// '2024-01-15T03:30:00-07:00'

// ZonedDateTime — includes offset and timezone name
Temporal.ZonedDateTime.from('2024-01-15T10:30:00-05:00[America/New_York]').toString();
// '2024-01-15T10:30:00-05:00[America/New_York]'

// PlainDate
Temporal.PlainDate.from('2024-01-15').toString();
// '2024-01-15'

// Duration — ISO 8601 duration format
Temporal.Duration.from({ years: 1, days: 5, hours: 3 }).toString();
// 'P1Y5DT3H'
```

**`Instant.toString()` with `timeZone` option:** Produces a wall-clock string in the given timezone with offset but without the bracketed timezone name. Use `ZonedDateTime.toString()` when you need to preserve the timezone identity.

## toLocaleString() Human-Readable Output

`toLocaleString()` produces localized, human-readable strings using `Intl.DateTimeFormat` or `Intl.DurationFormat`:

```javascript
const date = Temporal.PlainDate.from('2024-01-15');

date.toLocaleString('en-US');              // '1/15/2024'
date.toLocaleString('en-GB');              // '15/01/2024'
date.toLocaleString('de-DE');              // '15.1.2024'

// With format options
date.toLocaleString('en-US', {
  year: 'numeric', month: 'long', day: 'numeric'
}); // 'January 15, 2024'

// ZonedDateTime with timezone display
const zoned = Temporal.ZonedDateTime.from('2024-01-15T10:30:00-05:00[America/New_York]');
zoned.toLocaleString('en-US', {
  hour: 'numeric', minute: 'numeric', timeZoneName: 'short'
}); // '10:30 AM EST'

// Duration (requires Intl.DurationFormat support)
const dur = Temporal.Duration.from({ hours: 2, minutes: 30 });
dur.toLocaleString('en-US'); // '2 hours, 30 minutes'
```

## Parsing Strings

Each Temporal type parses strings via its `from()` static method. The string must match the type's RFC 9557 format:

```javascript
// Instant — requires 'Z' or offset
Temporal.Instant.from('2024-01-15T10:30:00Z');
Temporal.Instant.from('2024-01-15T10:30:00+05:30');

// ZonedDateTime — requires bracketed timezone
Temporal.ZonedDateTime.from('2024-01-15T10:30:00-05:00[America/New_York]');

// PlainDateTime — no timezone or offset allowed
Temporal.PlainDateTime.from('2024-01-15T10:30:00');

// PlainDate
Temporal.PlainDate.from('2024-01-15');

// PlainTime
Temporal.PlainTime.from('10:30:00.123456789');
```

### Parsing offset-only strings into ZonedDateTime

Strings with offsets but no bracketed timezone (e.g., `'2024-01-15T10:30:00-05:00'`) cannot be parsed as `ZonedDateTime` because the timezone name is required. Parse as `Instant` first, then convert:

```javascript
// Parse offset string as Instant
const instant = Temporal.Instant.from('2024-01-15T10:30:00-05:00');

// Convert to ZonedDateTime with known timezone
const zoned = instant.toZonedDateTimeISO('America/New_York');
```

### String passthrough in APIs

Most Temporal methods that accept Temporal objects also accept strings as shorthand:

```javascript
const date = Temporal.PlainDate.from('2024-01-15');

// String instead of Duration object
date.add('P7D'); // same as date.add(Temporal.Duration.from('P7D'))

// String in comparison
Temporal.PlainDate.compare(date, '2024-02-01'); // -1

// String in since/until
date.until('2024-06-15', { largestUnit: 'month' });
```

## String FAQ

### What type to use for parsing a particular string?

| String format | Parse with |
|--------------|------------|
| `2024-01-15T10:30:00Z` | `Temporal.Instant.from()` |
| `2024-01-15T10:30:00-05:00[America/New_York]` | `Temporal.ZonedDateTime.from()` |
| `2024-01-15T10:30:00` | `Temporal.PlainDateTime.from()` |
| `2024-01-15` | `Temporal.PlainDate.from()` |
| `10:30:00` | `Temporal.PlainTime.from()` |
| `2024-01` | `Temporal.PlainYearMonth.from()` |
| `--01-15` | `Temporal.PlainMonthDay.from()` |

### Why is the bracketed timezone required for ZonedDateTime?

The offset alone (`-05:00`) doesn't identify a timezone — multiple regions share the same offset. The bracketed name (`[America/New_York]`) ensures the correct DST rules are applied when doing arithmetic or converting dates.

### Why can't I parse UTC "Z" strings with Plain types?

`Z` indicates UTC, which is a timezone concept. Plain types have no timezone. To extract components from a UTC string, parse as `Instant` first, then convert:

```javascript
const instant = Temporal.Instant.from('2024-01-15T10:30:00Z');
const date = instant.toZonedDateTimeISO('UTC').toPlainDate();
```

### Why doesn't Temporal parse localized formats like MM/DD/YY?

Temporal only parses machine-readable RFC 9557 strings. For human input, use `HTMLInputElement.valueAsDate` or parse with a dedicated library, then convert to Temporal.

### Can I use a string in place of an object?

Yes. Most Temporal APIs accept strings as shorthand for the corresponding type. The string is parsed inline using the type's `from()` method.
