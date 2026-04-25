# Day.js Core API Reference

This document covers all built-in Day.js methods without requiring plugins.

## Parsing

### Constructor - `dayjs(date?)`

Create a Day.js instance from various input types.

```javascript
import dayjs from 'dayjs'

// No argument - current date/time
dayjs() // Current moment

// From string (ISO 8601)
dayjs('2024-01-15')
dayjs('2024-01-15T14:30:00Z')

// From Date object
dayjs(new Date())

// From timestamp (milliseconds)
dayjs(1705312800000)

// From another Day.js instance (clones it)
dayjs(dayjs('2024-01-15'))

// From number (treated as timestamp)
dayjs(1705312800000)
```

### isValid()

Check if the Day.js object contains a valid date.

```javascript
dayjs('2024-01-15').isValid() // true
dayjs('invalid-date').isValid() // false
dayjs(NaN).isValid() // false
```

### clone()

Create a clone of the current instance.

```javascript
const original = dayjs('2024-01-15')
const cloned = original.clone()
cloned.isSame(original) // true
cloned === original // false (different instances)
```

## Getters & Setters

All getter/setter methods accept both singular and plural unit names, and are case-insensitive.

### Year - `year(value?)`

```javascript
// Get year
dayjs('2024-01-15').year() // 2024

// Set year
dayjs('2024-01-15').year(2030) // Dayjs instance with year 2030
```

### Month - `month(value?)`

Months are zero-indexed (January = 0).

```javascript
// Get month (0-11)
dayjs('2024-01-15').month() // 0 (January)

// Set month
dayjs('2024-01-15').month(5) // June 2024
dayjs('2024-01-15').month(13) // January 2025 (bubbles to next year)
```

### Date - `date(value?)`

Get/set the day of the month (1-31).

```javascript
// Get date
dayjs('2024-01-15').date() // 15

// Set date
dayjs('2024-01-15').date(31) // January 31, 2024
dayjs('2024-01-15').date(32) // February 1, 2024 (bubbles to next month)
```

### Day - `day(value?)`

Get/set the day of the week (0 = Sunday, 6 = Saturday).

```javascript
// Get day of week
dayjs('2024-01-15').day() // 1 (Monday)

// Set day of week
dayjs('2024-01-15').day(0) // Next Sunday
dayjs('2024-01-15').day(6) // Next Saturday
```

### Hour - `hour(value?)`

```javascript
// Get hour (0-23)
dayjs('2024-01-15T14:30:00').hour() // 14

// Set hour
dayjs('2024-01-15T14:30:00').hour(9) // 09:30:00
```

### Minute - `minute(value?)`

```javascript
// Get minute (0-59)
dayjs('2024-01-15T14:30:00').minute() // 30

// Set minute
dayjs('2024-01-15T14:30:00').minute(45) // 14:45:00
```

### Second - `second(value?)`

```javascript
// Get second (0-59)
dayjs('2024-01-15T14:30:30').second() // 30

// Set second
dayjs('2024-01-15T14:30:30').second(0) // 14:30:00
```

### Millisecond - `millisecond(value?)`

```javascript
// Get millisecond (0-999)
dayjs('2024-01-15T14:30:30.500').millisecond() // 500

// Set millisecond
dayjs('2024-01-15T14:30:30.500').millisecond(750) // 14:30:30.750
```

### Generic Setter - `set(unit, value)`

Set any unit using a generic method.

```javascript
dayjs().set('year', 2030)
dayjs().set('month', 5) // June (zero-indexed)
dayjs().set('date', 15)
dayjs().set('hour', 9)
dayjs().set('minute', 30)

// Case insensitive, supports plurals
dayjs().set('YEARS', 2030)
dayjs().set('months', 5)
```

### Generic Getter - `get(unit)`

Get any unit using a generic method.

```javascript
dayjs('2024-01-15').get('year') // 2024
dayjs('2024-01-15').get('month') // 0
dayjs('2024-01-15').get('date') // 15

// Case insensitive, supports plurals
dayjs().get('YEARS') // 2024
dayjs().get('months') // 0
```

## Manipulation

### Add - `add(value, unit?)`

Add time to the current instance (returns new instance).

```javascript
dayjs('2024-01-15').add(7, 'day')     // 2024-01-22
dayjs('2024-01-15').add(1, 'month')   // 2024-02-15
dayjs('2024-01-15').add(2, 'year')    // 2026-01-15
dayjs('2024-01-15').add(30, 'minute') // +30 minutes

// Unit is optional (defaults to milliseconds)
dayjs().add(5000) // Add 5000 milliseconds

// Supports plural and short forms
dayjs().add(7, 'days')
dayjs().add(7, 'd')
dayjs().add(1, 'hour')
dayjs().add(1, 'h')
```

**Supported units:** `millisecond`/`milliseconds`/`ms`, `second`/`seconds`/`s`, `minute`/`minutes`/`m`, `hour`/`hours`/`h`, `day`/`days`/`d`, `month`/`months`/`M`, `year`/`years`/`y`

### Subtract - `subtract(value, unit?)`

Subtract time from the current instance (returns new instance).

```javascript
dayjs('2024-01-15').subtract(7, 'day')     // 2024-01-08
dayjs('2024-01-15').subtract(1, 'month')   // 2023-12-15
dayjs('2024-01-15').subtract(2, 'year')    // 2022-01-15

// Same unit support as add()
dayjs().subtract(30, 'minutes')
dayjs().subtract(2, 'h')
```

### Start Of - `startOf(unit)`

Set to the start of the specified unit.

```javascript
dayjs('2024-01-15T14:30:45.123').startOf('year')   // 2024-01-01T00:00:00.000
dayjs('2024-01-15T14:30:45.123').startOf('month')  // 2024-01-01T00:00:00.000
dayjs('2024-01-15T14:30:45.123').startOf('week')   // 2024-01-14T00:00:00.000 (Sunday)
dayjs('2024-01-15T14:30:45.123').startOf('day')    // 2024-01-15T00:00:00.000
dayjs('2024-01-15T14:30:45.123').startOf('hour')   // 2024-01-15T14:00:00.000
dayjs('2024-01-15T14:30:45.123').startOf('minute') // 2024-01-15T14:30:00.000
dayjs('2024-01-15T14:30:45.123').startOf('second') // 2024-01-15T14:30:45.000

// Supports plural forms
dayjs().startOf('days')
dayjs().startOf('months')
```

**Supported units:** `millisecond`, `second`, `minute`, `hour`, `day`, `week`/`weeks`, `month`, `quarter`, `year`

### End Of - `endOf(unit)`

Set to the end of the specified unit.

```javascript
dayjs('2024-01-15T14:30:45.123').endOf('year')   // 2024-12-31T23:59:59.999
dayjs('2024-01-15T14:30:45.123').endOf('month')  // 2024-01-31T23:59:59.999
dayjs('2024-01-15T14:30:45.123').endOf('week')   // 2024-01-20T23:59:59.999 (Saturday)
dayjs('2024-01-15T14:30:45.123').endOf('day')    // 2024-01-15T23:59:59.999
dayjs('2024-01-15T14:30:45.123').endOf('hour')   // 2024-01-15T14:59:59.999

// Supports plural forms
dayjs().endOf('years')
dayjs().endOf('months')
```

**Supported units:** Same as `startOf()`

## Display

### Format - `format(template?)`

Format the date as a string using format tokens.

```javascript
// Default format (ISO 8601 without milliseconds)
dayjs('2024-01-15T14:30:00').format() // '2024-01-15T14:30:00+00:00'

// Custom format strings
dayjs('2024-01-15T14:30:00').format('YYYY-MM-DD')        // '2024-01-15'
dayjs('2024-01-15T14:30:00').format('MM/DD/YYYY')        // '01/15/2024'
dayjs('2024-01-15T14:30:00').format('HH:mm:ss')          // '14:30:00'
dayjs('2024-01-15T14:30:00').format('YYYY [year] MM')    // '2024 year 01'

// Escape text with square brackets
dayjs('2024-01-15').format('Date: YYYY-MM-DD') // Error - treat as token
dayjs('2024-01-15').format('[Date:] YYYY-MM-DD') // 'Date: 2024-01-15'
```

**Format Tokens:**

| Token | Description | Example |
|-------|-------------|---------|
| `YYYY` | 4-digit year | 2024 |
| `YY` | 2-digit year | 24 |
| `MM` | 2-digit month (01-12) | 01 |
| `M` | Month (1-12) | 1 |
| `DD` | 2-digit day of month (01-31) | 15 |
| `D` | Day of month (1-31) | 15 |
| `HH` | 2-digit hour 24h (00-23) | 14 |
| `H` | Hour 24h (0-23) | 14 |
| `hh` | 2-digit hour 12h (01-12) | 02 |
| `h` | Hour 12h (1-12) | 2 |
| `mm` | 2-digit minute (00-59) | 30 |
| `m` | Minute (0-59) | 30 |
| `ss` | 2-digit second (00-59) | 45 |
| `s` | Second (0-59) | 45 |
| `SSS` | 3-digit millisecond (000-999) | 123 |
| `A` | AM/PM | PM |
| `a` | am/pm | pm |
| `d` | Day of week (0-6) | 1 |
| `dd` | Short weekday (locale) | Mon |
| `dddd` | Full weekday (locale) | Monday |
| `Z` | UTC offset (short) | +02:00 |

### Difference - `diff(date?, unit?, float?)`

Get the difference between two dates in the specified unit.

```javascript
const date1 = dayjs('2024-06-15')
const date2 = dayjs('2024-01-15')

// Default: milliseconds
date1.diff(date2) // 15552000000

// Specific units (rounded)
date1.diff(date2, 'day')     // 182
date1.diff(date2, 'month')   // 5
date1.diff(date2, 'year')    // 0

// Float for decimal results
date1.diff(date2, 'month', true) // 4.98...

// Compare to now
dayjs('2024-01-01').diff() // milliseconds from now (negative if in future)

// Supports all manipulation units
date1.diff(date2, 'hours')
date1.diff(date2, 'minutes')
```

### Value Of - `valueOf()`

Get the timestamp in milliseconds.

```javascript
dayjs('2024-01-15T00:00:00Z').valueOf() // 1705276800000
+dayjs('2024-01-15')                     // 1705276800000 (shorthand)
```

### Unix Timestamp - `unix()`

Get the Unix timestamp in seconds.

```javascript
dayjs('2024-01-15T00:00:00Z').unix() // 1705276800
```

### Days In Month - `daysInMonth()`

Get the number of days in the current month.

```javascript
dayjs('2024-01-15').daysInMonth() // 31
dayjs('2024-02-15').daysInMonth() // 29 (leap year)
dayjs('2023-02-15').daysInMonth() // 28 (non-leap year)
```

### To Date - `toDate()`

Convert to native JavaScript Date object.

```javascript
const date = dayjs('2024-01-15').toDate()
date instanceof Date // true
```

### To JSON - `toJSON()`

Serialize as ISO 8601 string (used by JSON.stringify).

```javascript
dayjs('2024-01-15T14:30:00').toJSON() // '2024-01-15T14:30:00.000Z'
JSON.stringify({ date: dayjs('2024-01-15') }) // '{"date":"2024-01-15T00:00:00.000Z"}'
```

### To ISO String - `toISOString()`

Format as ISO 8601 string.

```javascript
dayjs('2024-01-15T14:30:00').toISOString() // '2024-01-15T14:30:00.000Z'
```

### To String - `toString()`

Format as RFC 2822 string.

```javascript
dayjs('2024-01-15T14:30:00').toString() // 'Mon, 15 Jan 2024 14:30:00 GMT'
```

### UTC Offset - `utcOffset()`

Get the UTC offset in minutes.

```javascript
dayjs().utcOffset() // Varies by timezone (e.g., -300 for EST, 0 for UTC)
```

## Query

### Is Before - `isBefore(date?, unit?)`

Check if this date is before another date.

```javascript
dayjs('2024-01-15').isBefore(dayjs('2024-02-01')) // true
dayjs('2024-01-15').isBefore('2024-01-15')        // false
dayjs('2024-01-15').isBefore('2024-01-16', 'day') // true

// Granularity check
dayjs('2024-01-15T10:00:00').isBefore('2024-01-15T15:00:00', 'day') // false (same day)
```

### Is Same - `isSame(date?, unit?)`

Check if this date is the same as another date.

```javascript
dayjs('2024-01-15').isSame(dayjs('2024-01-15')) // true (milliseconds)
dayjs('2024-01-15T10:00:00').isSame('2024-01-15T15:00:00') // false

// Granularity check
dayjs('2024-01-15T10:00:00').isSame('2024-01-15T15:00:00', 'day')   // true
dayjs('2024-01-15').isSame('2024-01-20', 'month')                    // true
dayjs('2024-01-15').isSame('2025-01-15', 'year')                     // false
```

### Is After - `isAfter(date?, unit?)`

Check if this date is after another date.

```javascript
dayjs('2024-02-01').isAfter(dayjs('2024-01-15')) // true
dayjs('2024-01-15').isAfter('2024-01-15')        // false

// Granularity check
dayjs('2024-01-15T15:00:00').isAfter('2024-01-15T10:00:00', 'day') // false (same day)
```

## Static Methods

### Unix - `dayjs.unix(seconds)`

Create instance from Unix timestamp (seconds).

```javascript
dayjs.unix(1705276800) // 2024-01-15T00:00:00.000Z
```

### Locale - `dayjs.locale(preset?, object?)`

Get or set the global locale.

```javascript
// Get current locale
dayjs.locale() // 'en'

// Set locale (requires locale to be loaded first)
import 'dayjs/locale/es'
dayjs.locale('es') // Returns 'es'

// Custom locale
dayjs.locale('custom', {
  weekdays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
})
```

### Extend - `dayjs.extend(plugin, options?)`

Add a plugin to Day.js.

```javascript
import utc from 'dayjs/plugin/utc'
dayjs.extend(utc)

// With options
import relativeTime from 'dayjs/plugin/relativeTime'
dayjs.extend(relativeTime, {
  thresholds: [['s', 30], ['e', 45]]
})
```

### Is Dayjs - `dayjs.isDayjs(value)`

Check if a value is a Day.js instance.

```javascript
dayjs.isDayjs(dayjs()) // true
dayjs.isDayjs(new Date()) // false
dayjs.isDayjs('2024-01-15') // false
```

## Chaining Examples

```javascript
// Complex date calculation
const result = dayjs('2024-01-15')
  .add(1, 'year')      // 2025-01-15
  .subtract(3, 'month') // 2024-10-15
  .startOf('day')       // 2024-10-15T00:00:00
  .format('YYYY-MM-DD') // '2024-10-15'

// Age calculation
const age = dayjs().diff(dayjs('1990-05-15'), 'year')

// Business days from now
const nextWeek = dayjs().add(7, 'day').format('MMMM D, YYYY') // 'January 22, 2024'
```
