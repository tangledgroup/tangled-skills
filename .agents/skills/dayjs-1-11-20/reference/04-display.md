# Display

Once parsing and manipulation are done, display the Day.js object in various formats.

## Format

`.format()` converts a Day.js instance to a string using token patterns. Without arguments, returns an ISO 8601-like string:

```javascript
dayjs().format()                                    // '2020-04-02T08:02:17-05:00'
dayjs('2019-01-25').format('YYYY-MM-DD')           // '2019-01-25'
dayjs('2019-01-25').format('DD/MM/YYYY')           // '25/01/2019'
dayjs('2019-01-25').format('YYYY-MM-DDTHH:mm:ssZ') // '2019-01-25T00:00:00-02:00'
```

To escape literal characters, wrap them in square brackets: `[YYYYescape]`, `[Z]`.

### Core Format Tokens

- `YY` — 2-digit year (`19`)
- `YYYY` — 4-digit year (`2019`)
- `M` — Month, 1-12
- `MM` — Month, 01-12
- `MMM` — Abbreviated month name (`Jan`, locale-dependent)
- `MMMM` — Full month name (`January`, locale-dependent)
- `D` — Day of month, 1-31
- `DD` — Day of month, 01-31
- `d` — Day of week, 0-6 (Sunday = 0)
- `dd` — Minimal weekday abbreviation (`Su`, locale-dependent)
- `ddd` — Short weekday name (`Sun`, locale-dependent)
- `dddd` — Full weekday name (`Sunday`, locale-dependent)
- `H` — Hour, 0-23
- `HH` — Hour, 00-23
- `h` — Hour, 1-12
- `hh` — Hour, 01-12
- `m` — Minute, 0-59
- `mm` — Minute, 00-59
- `s` — Second, 0-59
- `ss` — Second, 00-59
- `SSS` — Millisecond, 000-999
- `Z` — UTC offset, `±HH:mm` (`+05:00`)
- `ZZ` — UTC offset, `±HHmm` (`+0500`)
- `A` — AM/PM
- `a` — am/pm

### Advanced Format Tokens (AdvancedFormat plugin)

The `advancedFormat` plugin adds:

- `Q` — Quarter, 1-4
- `Do` — Day of month with ordinal (`1st`, `2nd`, `31st`)
- `k` — Hour, 1-24
- `kk` — Hour, 01-24
- `X` — Unix timestamp in seconds
- `x` — Unix timestamp in milliseconds
- `w`/`ww` — Week of year (requires `WeekOfYear` plugin)
- `W`/`WW` — ISO week of year (requires `IsoWeek` plugin)
- `gggg` — Week year (requires `WeekYear` plugin)
- `GGGG` — ISO week year (requires `IsoWeek` plugin)
- `z` — Abbreviated timezone name (requires `Timezone` plugin)
- `zzz` — Full timezone name (requires `Timezone` plugin)

### Localized Format Tokens (LocalizedFormat plugin)

The `localizedFormat` plugin adds locale-aware format tokens:

```javascript
import localizedFormat from 'dayjs/plugin/localizedFormat'
dayjs.extend(localizedFormat)

dayjs().format('L')     // 01/25/2019
dayjs().format('LL')    // January 25, 2019
dayjs().format('LLL')   // January 25, 2019 12:00 AM
dayjs().format('LLLL')  // Thursday, January 25, 2019 12:00 AM
dayjs().format('LT')    // 12:00 AM
```

## Time From Now (RelativeTime plugin)

Returns a string of relative time from now:

```javascript
import relativeTime from 'dayjs/plugin/relativeTime'
dayjs.extend(relativeTime)

dayjs('1999-01-01').fromNow()       // '22 years ago'
dayjs('1999-01-01').fromNow(true)   // '22 years' (without suffix)
```

## Time From X (RelativeTime plugin)

Returns relative time from a comparison date:

```javascript
var a = dayjs('2000-01-01')
dayjs('1999-01-01').from(a)       // 'a year ago'
dayjs('1999-01-01').from(a, true) // 'a year' (without suffix)
```

## Time To Now / Time To X (RelativeTime plugin)

Returns relative time to now or to a comparison date:

```javascript
dayjs('1999-01-01').toNow()       // 'in 22 years'
dayjs('1999-01-01').toNow(true)   // '22 years' (without suffix)

var a = dayjs('2000-01-01')
dayjs('1999-01-01').to(a)         // 'in a year'
dayjs('1999-01-01').to(a, true)   // 'a year' (without suffix)
```

Relative time strings are localized by the current locale. Time is rounded to the nearest second.

## Calendar Time (Calendar plugin)

Displays time relative to a reference (defaults to now):

```javascript
import calendar from 'dayjs/plugin/calendar'
dayjs.extend(calendar)

dayjs().calendar()
// 'Today at 2:30 AM', 'Yesterday at 2:30 AM', 'Last Monday at 2:30 AM', etc.

dayjs().calendar(dayjs('2008-01-01'))  // custom reference time
```

Customize calendar output formats:

```javascript
dayjs().calendar(null, {
  sameDay: '[Today at] h:mm A',
  nextDay: '[Tomorrow at] h:mm A',
  nextWeek: 'dddd [at] h:mm A',
  lastDay: '[Yesterday at] h:mm A',
  lastWeek: '[Last] dddd [at] h:mm A',
  sameElse: 'DD/MM/YYYY'
})
```

## Difference

Returns the difference between two dates in milliseconds by default:

```javascript
const date1 = dayjs('2019-01-25')
const date2 = dayjs('2018-06-05')
date1.diff(date2)                     // 20214000000 (milliseconds)
date1.diff(date2, 'month')            // 7
date1.diff(date2, 'month', true)      // 7.645... (floating point)
```

Pass `true` as the third argument for a floating-point result instead of truncated integer.

Supported units: `year`, `month`, `week`, `day`, `hour`, `minute`, `second`, `millisecond`. Quarter requires `QuarterOfYear` plugin.

## Unix Timestamp

```javascript
// Milliseconds since epoch
dayjs('2019-01-25').valueOf() // 1548381600000
+dayjs(1548381600000)         // 1548381600000

// Seconds since epoch (floored)
dayjs('2019-01-25').unix()    // 1548381600
```

## Days in Month

```javascript
dayjs('2019-01-25').daysInMonth() // 31
dayjs('2019-02-01').daysInMonth() // 28 (or 29 in leap year)
```

## Serialization

Convert to native JavaScript types:

```javascript
// Native Date object
dayjs('2019-01-25').toDate()

// ISO 8601 string (for JSON serialization)
dayjs('2019-01-25').toJSON()  // '2019-01-25T02:00:00.000Z'

// String representation
dayjs('2019-01-25').toString() // 'Fri, 25 Jan 2019 02:00:00 GMT'

// Array (requires ToArray plugin)
import toArray from 'dayjs/plugin/toArray'
dayjs.extend(toArray)
dayjs('2019-01-25').toArray() // [2019, 0, 25, 0, 0, 0, 0]

// Object (requires ToObject plugin)
import toObject from 'dayjs/plugin/toObject'
dayjs.extend(toObject)
dayjs('2019-01-25').toObject()
// { years: 2019, months: 0, date: 25, hours: 0, minutes: 0, seconds: 0, milliseconds: 0 }
```
