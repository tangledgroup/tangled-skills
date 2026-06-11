# Plain Types (PlainDate, PlainTime, PlainDateTime, PlainYearMonth, PlainMonthDay)

## Contents
- Overview
- Temporal.PlainDate
- Temporal.PlainTime
- Temporal.PlainDateTime
- Temporal.PlainYearMonth
- Temporal.PlainMonthDay
- Shared Patterns

## Overview

Plain types represent date or time values **without timezone association**. They are used for wall-clock times, calendar dates, and recurring events that should not shift when timezones change.

All plain types share common patterns: `from()` construction, `with()` updates, `add()`/`subtract()` arithmetic (where applicable), `since()`/`until()` differences, `equals()` comparison, and `toString()` serialization.

## Temporal.PlainDate

Represents a calendar date without time or timezone. Use for birthdays, holidays, event dates that span the whole day regardless of location.

### Construction

```javascript
// From components
const date = new Temporal.PlainDate(2024, 6, 15);

// From string
const date2 = Temporal.PlainDate.from('2024-06-15');

// From object
const date3 = Temporal.PlainDate.from({ year: 2024, month: 6, day: 15 });
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `year` | `number` | Calendar year |
| `month` | `number` | Month (1-12 in ISO) |
| `monthCode` | `string` | Month identifier (stable across leap months) |
| `day` | `number` | Day of month |
| `calendarId` | `string` | Calendar system identifier |
| `dayOfWeek` | `number` | 1=Monday through 7=Sunday (ISO) |
| `dayOfYear` | `number` | Day within the year |
| `weekOfYear` | `number` | Week number |
| `yearOfWeek` | `number` | Year the week belongs to |
| `daysInWeek` | `number` | Days in current week |
| `daysInMonth` | `number` | Days in current month |
| `daysInYear` | `number` | Days in current year |
| `monthsInYear` | `number` | Months in current year |
| `inLeapYear` | `boolean` | Whether year is a leap year |
| `era` | `string \| undefined` | Era name |
| `eraYear` | `number \| undefined` | Year within era |

### Methods

```javascript
const date = Temporal.PlainDate.from('2024-06-15');

// Update fields (immutable)
const modified = date.with({ day: 1, month: 7 });
modified.toString(); // '2024-07-01'

// Change calendar
const inHebrew = date.withCalendar('hebrew');

// Arithmetic
const nextWeek = date.add({ weeks: 1 });
const lastMonth = date.subtract({ months: 1 });

// Duration between dates
const diff = date.until(nextWeek, { largestUnit: 'day' });
diff.days; // 7

// Comparison
date.equals(Temporal.PlainDate.from('2024-06-15')); // true
Temporal.PlainDate.compare(date, nextWeek); // -1 (earlier)

// Conversion to other types
const dateTime = date.toPlainDateTime({ hour: 12 }); // add time → PlainDateTime
const zoned = date.toZonedDateTime({ plainTime: { hour: 12 }, timeZone: 'UTC' });
const yearMonth = date.toPlainYearMonth();
const monthDay = date.toPlainMonthDay();
```

**PlainDate has no `round()` method.** Date-only rounding is ambiguous. To round to nearest month start, compare distances manually (see cookbook).

## Temporal.PlainTime

Represents a wall-clock time without date or timezone. Use for alarm times, recurring daily events, operating hours.

### Construction

```javascript
// From components
const time = new Temporal.PlainTime(14, 30, 0, 0, 0, 500); // hour, min, sec, ms, us, ns

// From string
const time2 = Temporal.PlainTime.from('14:30:00.500');

// From object
const time3 = Temporal.PlainTime.from({ hour: 14, minute: 30, second: 0 });
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `hour` | `number` | Hour (0-23) |
| `minute` | `number` | Minute (0-59) |
| `second` | `number` | Second (0-59) |
| `millisecond` | `number` | Millisecond (0-999) |
| `microsecond` | `number` | Microsecond (0-999) |
| `nanosecond` | `number` | Nanosecond (0-999) |

### Methods

```javascript
const time = Temporal.PlainTime.from('14:38:28.138');

// Update
const modified = time.with({ hour: 15, minute: 0 });

// Arithmetic (wraps around midnight)
const later = time.add({ hours: 12, minutes: 30 });
later.toString(); // '03:08:28.138' (next day)

// Duration between times
const diff = time.until(later, { largestUnit: 'hour' });

// Rounding
time.round({ smallestUnit: 'minute' }); // '14:39:00'
time.round({ smallestUnit: 'hour', roundingMode: 'floor' }); // '14:00:00'

// Comparison
Temporal.PlainTime.compare(time, later); // -1
```

## Temporal.PlainDateTime

Represents a calendar date and wall-clock time without timezone. Use when you need both date and time but don't care about timezone (e.g., local event scheduling).

**ZonedDateTime ≡ PlainDateTime + timezone.** For use cases requiring timezone (especially arithmetic), prefer `ZonedDateTime` as it automatically adjusts for DST.

### Construction

```javascript
// From components
const dt = new Temporal.PlainDateTime(2024, 6, 15, 14, 30, 0);

// From string
const dt2 = Temporal.PlainDateTime.from('2024-06-15T14:30:00');

// From object
const dt3 = Temporal.PlainDateTime.from({ year: 2024, month: 6, day: 15, hour: 14 });
```

### Properties

Combines all `PlainDate` properties (year, month, day, calendar info) and all `PlainTime` properties (hour through nanosecond).

### Methods

```javascript
const dt = Temporal.PlainDateTime.from('2024-06-15T14:30:00');

// Update
const modified = dt.with({ hour: 16, minute: 45 });

// Change calendar
const inHebrew = dt.withCalendar('hebrew');

// Replace time portion
const atNoon = dt.withPlainTime({ hour: 12 });

// Arithmetic
const later = dt.add({ days: 1, hours: 2 });

// Duration
const diff = dt.until(later, { largestUnit: 'day' });

// Rounding
dt.round({ smallestUnit: 'hour' });

// Conversion to ZonedDateTime (requires timezone choice)
const zoned = dt.toZonedDateTime('America/New_York', { disambiguation: 'compatible' });

// Conversion to plain types
const date = dt.toPlainDate();
const time = dt.toPlainTime();

// Comparison
Temporal.PlainDateTime.compare(dt, later); // -1
```

### Combining PlainDate and PlainTime

```javascript
const date = Temporal.PlainDate.from('2024-06-15');
const time = Temporal.PlainTime.from({ hour: 12 });

// Combine into PlainDateTime
const dateTime = date.toPlainDateTime(time);
dateTime.toString(); // '2024-06-15T12:00:00'
```

## Temporal.PlainYearMonth

Represents year and month without day. Use for monthly events, billing cycles, calendar month headers.

### Construction

```javascript
const ym = Temporal.PlainYearMonth.from('2024-06');
const ym2 = Temporal.PlainYearMonth.from({ year: 2024, month: 6 });
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `year` | `number` | Calendar year |
| `month` | `number` | Month (1-12) |
| `monthCode` | `string` | Month identifier |
| `daysInMonth` | `number` | Days in this month |
| `daysInYear` | `number` | Days in this year |
| `monthsInYear` | `number` | Months in this year |
| `inLeapYear` | `boolean` | Whether year is a leap year |
| `era` | `string \| undefined` | Era name |
| `eraYear` | `number \| undefined` | Year within era |

### Methods

```javascript
const ym = Temporal.PlainYearMonth.from('2024-06');

ym.daysInMonth; // 30

// Convert to full date (supply a day)
const date = ym.toPlainDate({ day: 15 });
date.toString(); // '2024-06-15'

// First day of month
const first = ym.toPlainDate({ day: 1 });

// Last day of month
const last = ym.toPlainDate({ day: ym.daysInMonth });

// Arithmetic
const nextMonth = ym.add({ months: 1 });
```

## Temporal.PlainMonthDay

Represents month and day without year. Use for birthdays, anniversaries, recurring annual events.

### Construction

```javascript
const md = Temporal.PlainMonthDay.from('07-14'); // Bastille Day
const md2 = Temporal.PlainMonthDay.from({ month: 7, day: 14 });
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `month` | `number` | Month (1-12) |
| `monthCode` | `string` | Month identifier |
| `day` | `number` | Day of month |

### Methods

```javascript
const md = Temporal.PlainMonthDay.from('07-14');

// Convert to full date (supply a year)
const thisYear = md.toPlainDate({ year: 2024 });
thisYear.toString(); // '2024-07-14'
thisYear.dayOfWeek; // 5 (Friday)

const in2030 = md.toPlainDate({ year: 2030 });
in2030.dayOfWeek; // 7 (Sunday)
```

**Note:** `PlainMonthDay` has no arithmetic methods (`add`, `subtract`, `since`, `until`) since month-day values without a year don't have meaningful duration semantics.

## Shared Patterns

### Overflow handling

When setting a day that exceeds the target month's length, use `overflow` option:

```javascript
const date = Temporal.PlainDate.from('2024-01-31');

// 'constrain' (default): clamp to last valid day
date.with({ month: 2 }); // '2024-02-29' (leap year)

// 'reject': throw if invalid
try {
  date.with({ month: 4 }, { overflow: 'reject' }); // throws — April has no 31st
} catch (e) {
  // RangeError
}
```

### Static compare for sorting

All plain types have a `compare()` static method usable with `Array.prototype.sort()`:

```javascript
const dates = [
  Temporal.PlainDate.from('2024-03-15'),
  Temporal.PlainDate.from('2024-01-10'),
  Temporal.PlainDate.from('2024-06-01'),
];

dates.sort(Temporal.PlainDate.compare);
// ['2024-01-10', '2024-03-15', '2024-06-01']
```
