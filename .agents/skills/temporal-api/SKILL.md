---
name: temporal-api
description: ECMAScript Temporal API for date/time management replacing legacy Date. Provides timezone-aware arithmetic, calendar support, nanosecond precision, and immutable Plain types. Use when building JavaScript/TypeScript applications requiring date-time calculations, timezone conversions, calendar operations, duration arithmetic, DST-safe scheduling, or migrating from the legacy Date object.
license: MIT
author: Tangled <noreply@tangledgroup.com>
version: "0.1.0"
tags:
  - temporal
  - date-time
  - timezone
  - calendar
  - javascript
  - esmascript
  - duration
category: library
external_references:
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Temporal
  - https://tc39.es/proposal-temporal/docs/
  - https://tc39.es/proposal-temporal/docs/cookbook.html
---

# ECMAScript Temporal API

## Overview

Temporal is a global namespace (like `Math`) that provides a modern date/time API for ECMAScript, designed as a full replacement for the legacy `Date` object. It exposes over 200 utility methods across several classes, each handling a specific aspect of date and time management.

Temporal fixes the fundamental problems of `Date`:

- **Separate types** for date-only, time-only, zoned, and exact-time values — no ambiguous dual-role objects
- **First-class timezone support** with IANA identifiers, DST-safe arithmetic, and disambiguation controls
- **Nanosecond precision** via `epochNanoseconds` (bigint)
- **Immutable instances** — all operations return new objects, no mutating setters
- **Multiple calendar systems** beyond Gregorian (Hebrew, Chinese, Islamic, Japanese, etc.)
- **Strict string parsing** using RFC 9557 format based on ISO 8601 / RFC 3339

Temporal is not a constructor. All properties and methods are static. It is accessed as `Temporal.Instant`, `Temporal.PlainDate`, etc.

## When to Use

- Replacing legacy `Date` in new JavaScript/TypeScript projects
- Performing date-time arithmetic that must be DST-safe
- Working with multiple time zones (conversions, offsets, transitions)
- Scheduling recurring events at specific wall-clock times
- Computing durations between dates/times with constrained units
- Working with non-Gregorian calendars
- Parsing or serializing date-time strings in RFC 9557 / ISO 8601 format
- Converting between legacy `Date` and modern Temporal types

## Core Concepts

### Class Hierarchy

Temporal classes fall into two categories: **exact time** (anchored to a real moment) and **plain types** (no timezone association).

| Category | Class | Represents |
|----------|-------|------------|
| Exact time | `Temporal.Instant` | A fixed point in time (nanoseconds since Unix epoch), no timezone or calendar |
| Exact time | `Temporal.ZonedDateTime` | An instant + timezone + calendar — the broadest Temporal type |
| Plain | `Temporal.PlainDateTime` | Date + time without timezone |
| Plain | `Temporal.PlainDate` | Calendar date (year, month, day) without time or timezone |
| Plain | `Temporal.PlainTime` | Wall-clock time (hour through nanosecond) without date or timezone |
| Plain | `Temporal.PlainYearMonth` | Year + month without day (e.g., "October 2020 meeting") |
| Plain | `Temporal.PlainMonthDay` | Month + day without year (e.g., "Bastille Day: July 14") |
| Duration | `Temporal.Duration` | A length of time with signed units (years through nanoseconds) |

**Utility namespace:** `Temporal.Now` provides methods for getting the current system time in various formats.

### Shared Interface

All Temporal classes share common method patterns:

- **Construction**: `new Type(...)` or `Type.from(input)` — parse from string, object, or existing instance
- **Immutability**: `with(fields)` — return a new instance with specified fields changed
- **Arithmetic**: `add(duration)`, `subtract(duration)`, `since(other)`, `until(other)`
- **Comparison**: `equals(other)`, static `Type.compare(a, b)`
- **Serialization**: `toString()`, `toLocaleString()`, `toJSON()`

### Conversion Rules

Converting between exact and plain types requires explicit timezone choices:

- `Instant` → `ZonedDateTime`: call `toZonedDateTimeISO(timeZone)`
- `ZonedDateTime` → `PlainDateTime`: call `toPlainDateTime()` (drops timezone)
- `PlainDateTime` → `ZonedDateTime`: call `toZonedDateTime(timeZone, { disambiguation })` — must handle DST gaps/overlaps
- `Instant` has no date/time component properties; a timezone is required to access year, month, day, hour, etc.

### Representable Range

All date-bearing Temporal objects support approximately ±10⁸ days from the Unix epoch: `-271821-04-20` to `+275760-09-13`. Objects refusing construction outside this range throw.

## Quick Start

### Getting current time

```javascript
// Current exact instant
const now = Temporal.Now.instant();
now.epochMilliseconds; // number, like Date.now()

// Current date in system timezone
const today = Temporal.Now.plainDateISO();
today.toString(); // '2024-01-15'

// Current zoned date-time (instant + timezone + calendar)
const nowZoned = Temporal.Now.zonedDateTimeISO();
nowZoned.toString(); // '2024-01-15T10:30:00-05:00[America/New_York]'
```

### Constructing objects

```javascript
// From components
const date = new Temporal.PlainDate(2024, 6, 15);
const time = new Temporal.PlainTime(14, 30, 0);

// From strings (RFC 9557 format)
const instant = Temporal.Instant.from('2024-06-15T14:30:00Z');
const zoned = Temporal.ZonedDateTime.from('2024-06-15T14:30:00-04:00[America/New_York]');

// From object literals
const dt = Temporal.PlainDateTime.from({ year: 2024, month: 6, day: 15, hour: 14 });
```

### Basic arithmetic

```javascript
const date = Temporal.PlainDate.from('2024-06-15');
const later = date.add({ days: 7, months: 1 });
later.toString(); // '2024-07-22'

// Duration between two dates
const duration = date.until(later, { largestUnit: 'month' });
duration.months; // 1
duration.days; // 7
```

### Immutability and updating

```javascript
const date = Temporal.PlainDate.from('2024-06-15');
const modified = date.with({ day: 1 }); // original unchanged
modified.toString(); // '2024-06-01'
date.toString(); // '2024-06-15'
```

### Converting from legacy Date

```javascript
const legacy = new Date('2024-06-15T14:30:00Z');
const instant = legacy.toTemporalInstant();
const zoned = instant.toZonedDateTimeISO('America/New_York');
```

## Advanced Topics

**Temporal.Now and Instant**: Getting current time, epoch nanoseconds, exact-time arithmetic → [Temporal.Now and Instant](reference/01-temporal-now-and-instant.md)

**ZonedDateTime**: Timezone-aware operations, DST handling, offset transitions, calendar properties → [ZonedDateTime](reference/02-zoneddatetime.md)

**Plain Types**: PlainDate, PlainTime, PlainDateTime, PlainYearMonth, PlainMonthDay with shared patterns → [Plain Types](reference/03-plain-types.md)

**Duration and Balancing**: Duration construction, arithmetic, balancing modes, total(), rounding → [Duration and Balancing](reference/04-duration-and-balancing.md)

**Time Zones and Calendars**: IANA timezone identifiers, calendar systems, era/eraYear, monthCode, week properties → [Time Zones and Calendars](reference/05-timezones-and-calendars.md)

**String Formatting**: RFC 9557 serialization, parsing patterns, toString/toLocaleString, format FAQ → [String Formatting](reference/06-string-formatting.md)

**Cookbook Patterns**: Date interoperability, sorting, timezone conversion, business hours, recurring events, flight times → [Cookbook Patterns](reference/07-cookbook-patterns.md)
