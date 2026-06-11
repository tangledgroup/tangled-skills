# Time Zones and Calendars

## Contents
- IANA Time Zone Identifiers
- Timezone Operations
- Calendar Systems
- Calendar Properties (era, eraYear, monthCode)
- Week Properties
- Listing Supported Calendars

## IANA Time Zone Identifiers

Temporal uses IANA Time Zone Database identifiers (e.g., `'America/New_York'`, `'Asia/Tokyo'`, `'UTC'`) to represent timezones. These are the same identifiers used by `Intl.DateTimeFormat` and operating systems worldwide.

```javascript
// Common timezone identifiers
const usEast = 'America/New_York';
const usWest = 'America/Los_Angeles';
const london = 'Europe/London';
const tokyo = 'Asia/Tokyo';
const utc = 'UTC';

// Fixed-offset identifiers (discouraged for persistent storage)
const fixedOffset = '+05:30'; // works but loses political context
```

**Prefer IANA identifiers over fixed offsets.** Offsets like `+05:30` don't encode DST rules or historical changes. A location's offset can change due to political decisions, but the IANA identifier always resolves correctly.

## Timezone Operations

### Converting between timezones

```javascript
const zoned = Temporal.ZonedDateTime.from('2024-01-15T10:30:00-05:00[America/New_York]');

// Same exact time, different timezone display
const inTokyo = zoned.withTimeZone('Asia/Tokyo');
inTokyo.toString(); // '2024-01-15T23:30:00+09:00[Asia/Tokyo]'

// The epoch time is unchanged
zoned.epochNanoseconds === inTokyo.epochNanoseconds; // true
```

### Getting UTC offset

```javascript
const zoned = Temporal.ZonedDateTime.from('2024-01-15T10:30:00-05:00[America/New_York]');

zoned.offset;             // '-05:00' (string)
zoned.offsetNanoseconds;  // -18000000000000 (nanoseconds)
zoned.hoursInDay;         // 24 (normal day)
```

During DST transitions, `hoursInDay` can be 23 (spring forward) or 25 (fall back).

### Finding timezone transitions

```javascript
const zoned = Temporal.ZonedDateTime.from('2024-06-15T12:00:00-04:00[America/New_York]');

// Next DST transition
const next = zoned.getTimeZoneTransition('next');
// Returns ZonedDateTime at the transition moment, or null if none known

// Previous DST transition
const prev = zoned.getTimeZoneTransition('previous');
```

### Start of day in a timezone

```javascript
const zoned = Temporal.ZonedDateTime.from('2024-01-15T14:30:00-05:00[America/New_York]');
const midnight = zoned.startOfDay();
midnight.toString(); // '2024-01-15T00:00:00-05:00[America/New_York]'
```

### Converting PlainDateTime to ZonedDateTime

When converting a zoneless `PlainDateTime` to `ZonedDateTime`, you must handle DST ambiguity:

```javascript
const dt = Temporal.PlainDateTime.from('2024-03-10T02:30'); // Spring forward gap

// 'compatible' (default): shift to nearest valid time
const z1 = dt.toZonedDateTime('America/New_York', { disambiguation: 'compatible' });

// 'reject': throw on ambiguous/nonexistent times
try {
  dt.toZonedDateTime('America/New_York', { disambiguation: 'reject' });
} catch (e) {
  // RangeError — 02:30 doesn't exist on this date
}
```

## Calendar Systems

Temporal supports multiple calendar systems. Default is ISO 8601 (Gregorian-based with week-numbering rules). Other calendars are available via `Intl.supportedValuesOf('calendar')`.

### Calendar types

| Type | Description | Examples |
|------|-------------|----------|
| Solar | Year = ~365.242 days, divided into months | Gregorian, Solar Hijri |
| Lunar | Month = ~29.5 days, 12 months per year | Islamic |
| Lunisolar | Lunar months with leap months to track solar year | Hebrew, Chinese |

### Using calendars

```javascript
// Create a date in a specific calendar
const date = Temporal.PlainDate.from({
  year: 2024, month: 6, day: 15,
  calendar: 'hebrew'
});
date.calendarId; // 'hebrew'

// Switch calendar (same instant, different representation)
const zoned = Temporal.Now.zonedDateTimeISO();
const inHebrew = zoned.withCalendar('hebrew');
const inIso = zoned.withCalendar('iso8601');

// List supported calendars
const calendars = Intl.supportedValuesOf('calendar');
// ['buddhist', 'chinese', 'coptic', 'ethiopic', 'hebrew', 'islamic', ...]
```

### Calendar-aware date components

Every date in a calendar is identified by `year`, `month`, and `day`. These properties have consistent semantics across calendars:

- `year` — Monotonically increasing integer (can be zero or negative). Year 1 (or 0) is the calendar epoch.
- `month` — Positive integer from 1 to `monthsInYear`. Resets to 1 as year advances.
- `day` — Positive integer, resets as month advances. May not start at 1 or increment by 1 in all calendars.

**Always use `daysInMonth`, `daysInYear`, and `monthsInYear` instead of assuming fixed values.**

```javascript
const date = Temporal.PlainDate.from('2024-02-15');
date.daysInMonth;   // 29 (leap year)
date.daysInYear;    // 366
date.monthsInYear;  // 12
date.inLeapYear;    // true
```

## Calendar Properties

### era and eraYear

For calendars that use eras (e.g., Gregorian: CE/BCE, Japanese: Reiwa/Heisei), years can be identified by `era` + `eraYear` instead of `year`:

```javascript
const date = Temporal.PlainDate.from({ year: -1, calendar: 'iso8601' });
date.era;      // 'bce'
date.eraYear;  // 2

// Year 0 in Gregorian = 1 BCE (astronomical year numbering)
const yearZero = Temporal.PlainDate.from({ year: 0, calendar: 'iso8601' });
yearZero.era;      // 'bce'
yearZero.eraYear;  // 1
```

**Rules:**
- Always use `era` and `eraYear` as a pair — never one without the other
- Don't mix `year` with `era`/`eraYear` when designating a year
- `era` and `eraYear` may be `undefined` for calendars without eras
- Don't assume `era` is user-friendly — use `toLocaleString()` for display

### monthCode

`monthCode` provides a stable identifier for a month that doesn't change due to leap months:

```javascript
// In lunisolar calendars, two months with the same monthCode
// but different year contexts may have different `month` values
const date = Temporal.PlainDate.from('2024-06-15');
date.month;       // 6
date.monthCode;   // '-06' (ISO month code)
```

**Rules:**
- Don't combine `month` and `monthCode` — pick one representation
- Use `month` for ordering (looping through months)
- Use `monthCode` for naming/storing (birthdays, recurring events)
- Don't assume `monthCode` is user-friendly — use `toLocaleString()` for display

## Week Properties

Weeks are cultural constructs, not astronomical. Most calendars use 7-day weeks, but weeks can have 4-8+ days or variable lengths.

```javascript
const date = Temporal.PlainDate.from('2024-01-15');
date.dayOfWeek;    // 2 (Tuesday)
date.weekOfYear;   // 3
date.yearOfWeek;   // 2024
date.daysInWeek;   // 7
```

**Rules:**
- Always use `weekOfYear` and `yearOfWeek` as a pair — don't use `weekOfYear` with `year`
- `yearOfWeek` may differ from `year` at year boundaries (a week can span two years)
- `weekOfYear` and `yearOfWeek` may be `undefined` for calendars without week concepts
- Current Temporal API does not support constructing dates from year-week-day — these are informational only

## Listing Supported Calendars

```javascript
// Get all calendar identifiers supported by the runtime
const calendars = Intl.supportedValuesOf('calendar');
console.log(calendars);
// ['buddhist', 'chinese', 'coptic', 'ethiopic', 'ethiopic-amete-alem',
//  'generic-gregorian', 'hebrew', 'indian', 'islamic', 'islamic-civil',
//  'islamic-umalqura', 'islamic-tbla', 'islamic-rgsa', 'japanese',
//  'persian', 'roc']

// Get all timezone identifiers
const timezones = Intl.supportedValuesOf('timeZone');
```

Support varies by runtime (browser, Node.js, Deno). Always check availability before using non-ISO calendars.
