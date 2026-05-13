# Temporal.Now and Instant

## Contents
- Temporal.Now Methods
- Temporal.Instant Construction
- Temporal.Instant Properties
- Temporal.Instant Methods
- Interoperability with Legacy Date

## Temporal.Now Methods

`Temporal.Now` provides methods for getting the current system time in various formats. All methods return immutable instances.

| Method | Returns | Description |
|--------|---------|-------------|
| `Temporal.Now.instant()` | `Instant` | Current exact time as nanoseconds since epoch |
| `Temporal.Now.timeZoneId()` | `string` | System's IANA timezone identifier (e.g., `'America/New_York'`) |
| `Temporal.Now.zonedDateTimeISO([timeZone])` | `ZonedDateTime` | Current zoned date-time in ISO calendar, defaulting to system timezone |
| `Temporal.Now.plainDateISO([timeZone])` | `PlainDate` | Current calendar date in given timezone |
| `Temporal.Now.plainTimeISO([timeZone])` | `PlainTime` | Current wall-clock time in given timezone |
| `Temporal.Now.plainDateTimeISO([timeZone])` | `PlainDateTime` | Current date+time without timezone association |

```javascript
// Current instant (exact time, no timezone)
const now = Temporal.Now.instant();
now.epochMilliseconds; // 1705312201500

// Current date in system timezone
const today = Temporal.Now.plainDateISO();
today.toString(); // '2024-01-15'

// Current date in a specific timezone
const todayTokyo = Temporal.Now.plainDateISO('Asia/Tokyo');

// Current zoned date-time (instant + timezone + calendar)
const nowZoned = Temporal.Now.zonedDateTimeISO();
nowZoned.timeZoneId; // 'America/New_York' (system timezone)
```

**Server context warning:** `Temporal.Now.timeZoneId()` returns the user's timezone in browsers, but on servers the value may be unexpected. Avoid relying on it in server contexts — use an explicit timezone identifier instead.

## Temporal.Instant Construction

`Temporal.Instant` represents a fixed point in time (exact time), without regard to calendar or location. It is fundamentally the number of nanoseconds since the Unix epoch (1970-01-01T00:00:00Z).

```javascript
// From string (RFC 9557 format)
const instant = Temporal.Instant.from('2024-01-15T10:30:00Z');

// From epoch nanoseconds (bigint)
const instant2 = new Temporal.Instant(1705312200000000000n);

// From epoch milliseconds (number)
const instant3 = Temporal.Instant.fromEpochMilliseconds(1705312200000);

// From epoch nanoseconds (bigint)
const instant4 = Temporal.Instant.fromEpochNanoseconds(1705312200000000000n);

// From existing Instant (returns same instance)
const instant5 = Temporal.Instant.from(instant);
```

## Temporal.Instant Properties

| Property | Type | Description |
|----------|------|-------------|
| `epochMilliseconds` | `number` | Milliseconds since Unix epoch (same as `Date.getTime()`) |
| `epochNanoseconds` | `bigint` | Nanoseconds since Unix epoch (full precision) |

```javascript
const instant = Temporal.Instant.from('1969-07-20T20:17Z');
instant.epochMilliseconds;  // -14182980000
instant.epochNanoseconds;   // -14182980000000000000n
```

**Instant has no date/time component properties.** To access year, month, day, or hour, convert to `ZonedDateTime` first:

```javascript
const instant = Temporal.Now.instant();
// instant.year; // ERROR — Instant has no year property

const zoned = instant.toZonedDateTimeISO('America/New_York');
zoned.year; // 2024
zoned.month; // 1
```

## Temporal.Instant Methods

### Arithmetic

```javascript
const start = Temporal.Instant.from('2024-01-15T10:00:00Z');

// Add duration
const later = start.add({ hours: 3, minutes: 30 });
later.toString(); // '2024-01-15T13:30:00Z'

// Subtract duration
const earlier = start.subtract({ days: 1 });
earlier.toString(); // '2024-01-14T10:00:00Z'

// Duration between two instants
const diff = start.until(later, { largestUnit: 'hour' });
diff.hours; // 3

// With constrained units
const diffMinutes = start.until(later, { largestUnit: 'minute' });
diffMinutes.minutes; // 210
```

The `largestUnit` option constrains the result to no larger than the specified unit. Available units: `'year'`, `'month'`, `'week'`, `'day'`, `'hour'`, `'minute'`, `'second'`, `'millisecond'`, `'microsecond'`, `'nanosecond'`.

### Rounding

```javascript
const instant = Temporal.Instant.from('2024-01-15T10:38:28.138Z');

// Round to nearest minute
instant.round({ smallestUnit: 'minute' }); // '2024-01-15T10:39:00Z'

// Floor to whole hour
instant.round({ smallestUnit: 'hour', roundingMode: 'floor' }); // '2024-01-15T10:00:00Z'

// Ceiling to next second
instant.round({ smallestUnit: 'second', roundingMode: 'ceil' }); // '2024-01-15T10:38:29Z'
```

Rounding modes: `'halfExpand'` (default), `'halfUp'`, `'halfDown'`, `'halfEven'`, `'up'`, `'down'`, `'ceil'`, `'floor'`, `'expand'`, `'truncate'`.

### Comparison

```javascript
const a = Temporal.Instant.from('2024-01-15T10:00:00Z');
const b = Temporal.Instant.from('2024-01-15T11:00:00Z');

a.equals(b); // false

// Static compare: returns -1, 0, or 1
Temporal.Instant.compare(a, b); // -1 (a is earlier)
```

### Conversion to ZonedDateTime

```javascript
const instant = Temporal.Instant.from('2024-01-15T10:00:00Z');

// Convert to zoned date-time in a specific timezone
const zoned = instant.toZonedDateTimeISO('America/New_York');
zoned.toString(); // '2024-01-15T05:00:00-05:00[America/New_York]'
```

### Serialization

```javascript
const instant = Temporal.Instant.from('2024-01-15T10:30:00Z');

instant.toString(); // '2024-01-15T10:30:00Z'
instant.toString({ timeZone: 'America/Yellowknife' }); // '2024-01-15T03:30:00-07:00'
instant.toJSON(); // same as toString()
```

## Interoperability with Legacy Date

```javascript
// Date → Instant
const legacy = new Date('2024-01-15T10:30:00Z');
const instant = legacy.toTemporalInstant();

// Instant → Date (use epochMilliseconds)
const backToDate = new Date(instant.epochMilliseconds);

// Round before converting if you need millisecond precision
const rounded = instant.round({ smallestUnit: 'millisecond' });
const preciseDate = new Date(rounded.epochMilliseconds);

// For date-only extraction, always go through ZonedDateTime with explicit timezone
const plainDate = legacy
  .toTemporalInstant()
  .toZonedDateTimeISO('UTC')    // or Temporal.Now.timeZoneId() for local
  .toPlainDate();
```

**Key rule:** `Date` stores only an exact time (epoch milliseconds). It has no timezone. When converting to Temporal, `toTemporalInstant()` gives the equivalent exact time. To access calendar components (year, month, day), you must choose a timezone via `toZonedDateTimeISO()`.
