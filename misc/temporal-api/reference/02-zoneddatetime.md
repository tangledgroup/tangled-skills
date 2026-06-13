# Temporal.ZonedDateTime

## Contents
- Overview
- Construction
- Properties (Date, Time, Calendar, Timezone, Epoch)
- Methods (Updating, Arithmetic, Conversion)
- DST Handling and Disambiguation
- Timezone Transitions

## Overview

`Temporal.ZonedDateTime` is the broadest Temporal type — a combination of an `Instant` (exact time), a timezone, and a calendar system. It represents a real event that has happened or will happen at a particular exact time from the perspective of a particular region on Earth.

Use `ZonedDateTime` when you need timezone-aware operations, especially DST-safe arithmetic and interoperability with iCalendar (RFC 5545).

```javascript
const zoned = Temporal.ZonedDateTime.from({
  timeZone: 'America/Los_Angeles',
  year: 1995, month: 12, day: 7,
  hour: 3, minute: 24, second: 30,
  millisecond: 0, microsecond: 3, nanosecond: 500
});
zoned.toString(); // '1995-12-07T03:24:30.0000035-08:00[America/Los_Angeles]'
```

## Construction

### Constructor

```javascript
// epochNanoseconds (bigint) + timezone + optional calendar
const zoned = new Temporal.ZonedDateTime(
  1705312200000000000n,           // nanoseconds since epoch
  'America/New_York',             // IANA timezone ID
  'iso8601'                        // calendar (default: 'iso8601')
);
```

### From string

```javascript
// RFC 9557 format with bracketed timezone annotation required
const zoned = Temporal.ZonedDateTime.from(
  '2024-01-15T10:30:00-05:00[America/New_York]'
);
```

### From object

```javascript
const zoned = Temporal.ZonedDateTime.from({
  timeZone: 'Asia/Tokyo',
  year: 2024, month: 1, day: 15,
  hour: 10, minute: 30
});
```

## Properties

### Date components

| Property | Type | Description |
|----------|------|-------------|
| `year` | `number` | Calendar year (can be negative for BCE) |
| `month` | `number` | Month of year (1-12 in ISO, varies by calendar) |
| `day` | `number` | Day of month |
| `dayOfWeek` | `number` | Day of week (1=Monday, 7=Sunday in ISO) |
| `dayOfYear` | `number` | Day of year (1+) |
| `weekOfYear` | `number` | Week number of year |
| `yearOfWeek` | `number` | Year the week belongs to (may differ from `year`) |
| `daysInWeek` | `number` | Number of days in this week |
| `daysInMonth` | `number` | Days in current month |
| `daysInYear` | `number` | Days in current year |
| `monthsInYear` | `number` | Months in current year |
| `inLeapYear` | `boolean` | Whether current year is a leap year |

### Time components

| Property | Type | Description |
|----------|------|-------------|
| `hour` | `number` | Hour (0-23) |
| `minute` | `number` | Minute (0-59) |
| `second` | `number` | Second (0-59) |
| `millisecond` | `number` | Millisecond (0-999) |
| `microsecond` | `number` | Microsecond (0-999) |
| `nanosecond` | `number` | Nanosecond (0-999) |

### Calendar components

| Property | Type | Description |
|----------|------|-------------|
| `calendarId` | `string` | Calendar identifier (e.g., `'iso8601'`, `'hebrew'`) |
| `era` | `string \| undefined` | Era name (e.g., `'ce'`, `'bce'`) |
| `eraYear` | `number \| undefined` | Year within era |

### Timezone components

| Property | Type | Description |
|----------|------|-------------|
| `timeZoneId` | `string` | IANA timezone identifier |
| `offset` | `string` | UTC offset string (e.g., `'-05:00'`) |
| `offsetNanoseconds` | `number` | UTC offset in nanoseconds |
| `hoursInDay` | `number` | Hours in this day (23, 24, or 25 during DST transitions) |

### Epoch time

| Property | Type | Description |
|----------|------|-------------|
| `epochMilliseconds` | `number` | Milliseconds since Unix epoch |
| `epochNanoseconds` | `bigint` | Nanoseconds since Unix epoch |

## Methods

### Updating (immutable)

```javascript
const zoned = Temporal.ZonedDateTime.from('2024-01-15T10:30:00-05:00[America/New_York]');

// Change specific fields
const updated = zoned.with({ hour: 14, minute: 0 });

// Change timezone (preserves exact time, adjusts wall-clock)
const inTokyo = zoned.withTimeZone('Asia/Tokyo');

// Change calendar
const inHebrew = zoned.withCalendar('hebrew');

// Replace time portion
const atNoon = zoned.withPlainTime({ hour: 12 });
```

### Arithmetic

```javascript
const zoned = Temporal.ZonedDateTime.from('2024-01-15T10:30:00-05:00[America/New_York]');

// Add duration (DST-safe — wall-clock adjusts automatically)
const later = zoned.add({ hours: 24 });

// Subtract duration
const earlier = zoned.subtract({ days: 7 });

// Duration between two zoned date-times
const diff = zoned.until(later, { largestUnit: 'day' });

// With overflow control
const constrained = zoned.add({ months: 1 }, { overflow: 'constrain' });
```

### Rounding

```javascript
const zoned = Temporal.ZonedDateTime.from('2024-01-15T10:38:28.138Z[America/New_York]');

// Round to nearest hour
zoned.round({ smallestUnit: 'hour' });

// Floor to start of day
zoned.startOfDay(); // equivalent to round to day with floor
```

### Timezone transitions

```javascript
const zoned = Temporal.ZonedDateTime.from('2024-01-15T10:30:00-05:00[America/New_York]');

// Next DST transition
const next = zoned.getTimeZoneTransition('next');
// Returns ZonedDateTime at transition, or null if no known future transition

// Previous DST transition
const prev = zoned.getTimeZoneTransition('previous');
```

### Conversion to other types

```javascript
const zoned = Temporal.ZonedDateTime.from('2024-01-15T10:30:00-05:00[America/New_York]');

// To exact instant
const instant = zoned.toInstant();

// To plain date (drops time and timezone)
const date = zoned.toPlainDate();

// To plain time
const time = zoned.toPlainTime();

// To plain datetime (drops timezone, keeps date+time)
const dateTime = zoned.toPlainDateTime();
```

### Comparison

```javascript
const a = Temporal.ZonedDateTime.from('2024-01-15T10:30:00-05:00[America/New_York]');
const b = Temporal.ZonedDateTime.from('2024-01-15T16:30:00+01:00[Europe/London]');

a.equals(b); // true — same exact instant

// Static compare (by exact time)
Temporal.ZonedDateTime.compare(a, b); // 0
```

## DST Handling and Disambiguation

When converting a `PlainDateTime` to `ZonedDateTime`, the wall-clock time may be ambiguous (during DST "fall back") or nonexistent (during DST "spring forward"). Use the `disambiguation` option:

```javascript
const dateTime = Temporal.PlainDateTime.from('2024-03-10T02:30'); // Spring forward gap in US

// 'compatible' (default): shift forward to nearest valid time
const zoned1 = dateTime.toZonedDateTime('America/New_York', { disambiguation: 'compatible' });

// 'earlier': use the earlier of the two possible instants
const zoned2 = dateTime.toZonedDateTime('America/New_York', { disambiguation: 'earlier' });

// 'later': use the later of the two possible instants
const zoned3 = dateTime.toZonedDateTime('America/New_York', { disambiguation: 'later' });

// 'reject': throw if ambiguous or nonexistent
const zoned4 = dateTime.toZonedDateTime('America/New_York', { disambiguation: 'reject' });
```

**Disambiguation modes:**
- `'compatible'` — Default. For spring-forward gaps, shifts to the time just after the gap. For fall-back overlaps, uses the earlier instant (matching legacy `Date` behavior).
- `'earlier'` — Picks the earlier of two possible instants during overlap; for gaps, picks the time before the gap.
- `'later'` — Picks the later of two possible instants during overlap; for gaps, picks the time after the gap.
- `'reject'` — Throws if the wall-clock time is ambiguous or nonexistent.

## Timezone Transitions

Use `getTimeZoneTransition()` to find DST change points:

```javascript
const zoned = Temporal.ZonedDateTime.from('2024-06-15T12:00:00-04:00[America/New_York]');

// Next transition (fall back in November)
const nextTransition = zoned.getTimeZoneTransition('next');
nextTransition.toString(); // '2024-11-03T02:00:00-04:00[America/New_York]'

// Previous transition (spring forward in March)
const prevTransition = zoned.getTimeZoneTransition('previous');
prevTransition.toString(); // '2024-03-10T02:00:00-05:00[America/New_York]'
```

For timezones without DST (e.g., `'America/Regina'`), `getTimeZoneTransition()` returns `null`.
