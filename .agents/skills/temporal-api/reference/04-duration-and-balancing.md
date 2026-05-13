# Duration and Balancing

## Contents
- Overview
- Construction
- Properties
- Arithmetic and Methods
- Balancing Modes
- Rounding and total()
- Serialization

## Overview

`Temporal.Duration` expresses a length of time with signed units from years down to nanoseconds. It is used for date-time arithmetic (`add`/`subtract`) and for measuring differences between Temporal objects (`since`/`until`).

Unlike other Temporal types, Duration units do not naturally wrap: a duration of "90 minutes" stays as 90 minutes unless you explicitly balance it to "1 hour 30 minutes."

```javascript
const dur = Temporal.Duration.from({ hours: 2, minutes: 30 });
dur.toString(); // 'PT2H30M'
```

## Construction

### Constructor

```javascript
// All units default to 0
const dur = new Temporal.Duration(
  0,   // years
  1,   // months
  0,   // weeks
  5,   // days
  2,   // hours
  30,  // minutes
  0,   // seconds
  0,   // milliseconds
  0,   // microseconds
  0    // nanoseconds
);
```

### From object

```javascript
const dur = Temporal.Duration.from({ months: 1, days: 5, hours: 2 });
```

### From string (ISO 8601 duration format)

```javascript
const dur = Temporal.Duration.from('P1M5DT2H'); // 1 month, 5 days, 2 hours
const dur2 = Temporal.Duration.from('PT90M');   // 90 minutes
```

## Properties

| Property | Type | Description |
|----------|------|-------------|
| `years` | `number` | Years component |
| `months` | `number` | Months component |
| `weeks` | `number` | Weeks component |
| `days` | `number` | Days component |
| `hours` | `number` | Hours component |
| `minutes` | `number` | Minutes component |
| `seconds` | `number` | Seconds component |
| `milliseconds` | `number` | Milliseconds component |
| `microseconds` | `number` | Microseconds component |
| `nanoseconds` | `number` | Nanoseconds component |
| `sign` | `number` | `-1`, `0`, or `1` (negative, zero, positive) |
| `blank` | `boolean` | `true` if all units are zero |

```javascript
const dur = Temporal.Duration.from({ hours: -2, minutes: 30 });
dur.sign; // -1
dur.blank; // false

const zero = Temporal.Duration.from({});
zero.blank; // true
```

## Arithmetic and Methods

### Adding and subtracting durations

```javascript
const dur1 = Temporal.Duration.from({ hours: 2, minutes: 30 });
const dur2 = Temporal.Duration.from({ minutes: 45 });

// Combine durations
const sum = dur1.add(dur2);
sum.toString(); // 'PT2H75M' (units don't auto-wrap)

// Subtract
const diff = dur1.subtract(dur2);
diff.toString(); // 'PT2H-15M' (mixed signs possible)
```

### Negation and absolute value

```javascript
const dur = Temporal.Duration.from({ hours: -3 });
dur.negated();  // PT3H
dur.abs();      // PT3H
```

### Using durations with other Temporal types

All arithmetic-capable Temporal types accept Duration objects, plain objects, or ISO duration strings:

```javascript
const date = Temporal.PlainDate.from('2024-06-15');

// Duration object
date.add(Temporal.Duration.from({ days: 7 }));

// Plain object (shorthand)
date.add({ days: 7, months: 1 });

// ISO string
date.add('P7D');
```

### Comparing durations

```javascript
const a = Temporal.Duration.from({ hours: 2 });
const b = Temporal.Duration.from({ minutes: 120 });

// Requires relativeTo for calendar-aware comparison
Temporal.Duration.compare(a, b, { relativeTo: Temporal.Now.zonedDateTimeISO() });
// Returns -1, 0, or 1

// For time-only durations (no calendar units), relativeTo is optional
const c = Temporal.Duration.from({ hours: 2 });
const d = Temporal.Duration.from({ minutes: 90 });
Temporal.Duration.compare(c, d); // 1 (2h > 90m)
```

## Balancing Modes

Balancing converts a duration into a normalized form where each unit stays within its natural range. Temporal uses three balancing settings:

### `balance: 'basic'` (default for `round()`)

Uses fixed conversion rates regardless of calendar context:
- 1 year = 12 months
- 1 month = 30 days
- 1 week = 7 days
- 1 day = 24 hours
- 1 hour = 60 minutes
- etc.

```javascript
const dur = Temporal.Duration.from({ minutes: 90 });
dur.round({ largestUnit: 'hour', smallestUnit: 'minute' });
// PT1H30M — 90 minutes balanced to 1h 30m
```

### `balance: 'wall'`

Uses actual calendar rules, requiring a `relativeTo` reference point. This matters for months (28-31 days) and years (365-366 days):

```javascript
const dur = Temporal.Duration.from({ days: 60 });

// With relativeTo, knows that Jan+Feb 2024 = 31+29 = 60 days
dur.round(
  { largestUnit: 'month', smallestUnit: 'day' },
  { relativeTo: Temporal.ZonedDateTime.from('2024-01-01T00:00[UTC]') }
);
// P2M — exactly 2 months from Jan 1, 2024
```

### `balance: 'condense'`

Balances into the fewest possible units by pushing everything into the largest unit:

```javascript
const dur = Temporal.Duration.from({ hours: 25, minutes: 90 });
dur.round({ largestUnit: 'hour', balance: 'condense' });
// PT27H — all condensed into hours, no minutes
```

### Balancing in arithmetic

When you `add()` or `subtract()` a duration to a Temporal object, the result is automatically balanced according to calendar rules. The duration itself is not modified:

```javascript
const date = Temporal.PlainDate.from('2024-01-31');
const nextMonth = date.add({ months: 1 });
nextMonth.toString(); // '2024-02-29' (constrained to last day of Feb)
```

## Rounding and total()

### round()

Round a duration to specified precision:

```javascript
const dur = Temporal.Duration.from({ hours: 2, minutes: 38, seconds: 45 });

// Round to nearest minute
dur.round({ smallestUnit: 'minute' }); // PT2H39M

// Round to nearest hour with floor
dur.round({ smallestUnit: 'hour', roundingMode: 'floor' }); // PT2H

// Balance to largest unit
dur.round({ largestUnit: 'hour', smallestUnit: 'second' }); // PT2H38M45S
```

### total()

Convert the entire duration to a single numeric value in a specified unit:

```javascript
const dur = Temporal.Duration.from({ hours: 2, minutes: 30 });

// Total in seconds (basic conversion)
dur.total({ unit: 'second' }); // 9000

// Total in days using wall calendar (needs relativeTo for calendar units)
const dayDur = Temporal.Duration.from({ days: 1, hours: 6 });
dayDur.total({ unit: 'day' }); // 1.25
```

For durations with calendar units (years, months, weeks, days), `total()` requires `relativeTo`:

```javascript
const dur = Temporal.Duration.from({ months: 1, days: 5 });
dur.total(
  { unit: 'day' },
  { relativeTo: Temporal.ZonedDateTime.from('2024-01-01T00:00[UTC]') }
);
// 36 (31 days in Jan + 5)
```

## Serialization

```javascript
const dur = Temporal.Duration.from({ years: 1, months: 2, days: 3, hours: 4 });
dur.toString(); // 'P1Y2M3DT4H'
dur.toJSON();   // 'P1Y2M3DT4H'

// With sign display
const neg = Temporal.Duration.from({ hours: -2 });
neg.toString(); // '-PT2H'

// Human-readable (if Intl.DurationFormat is available)
dur.toLocaleString('en-US'); // '1 year, 2 months, 3 days, 4 hours'
```

ISO 8601 duration format: `P[n]Y[n]M[n]DT[n]H[n]M[n]S` — years/months before the `T`, time units after.
