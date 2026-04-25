# Day.js Plugins Reference

Day.js has 37 plugins that extend functionality. Each plugin must be loaded individually to keep bundle size minimal.

## Plugin Installation Pattern

```javascript
import dayjs from 'dayjs'
import pluginName from 'dayjs/plugin/pluginName'

// Extend dayjs with the plugin
dayjs.extend(pluginName)

// Use new methods
dayjs().newMethod()
```

## Core Functionality Plugins

### advancedFormat

Adds additional format tokens for quarters, ordinal numbers, 24-hour format, and Unix timestamps.

**Package:** `dayjs/plugin/advancedFormat`

**New Format Tokens:**
- `Q` / `QQ` / `QQQ` / `QQQQ` - Quarter (1-4)
- `Do` - Ordinal day of month (1st, 2nd, 3rd)
- `k` / `kk` - 24-hour format (0-23 / 00-23)
- `X` - Unix timestamp (seconds, rounded)
- `x` - Unix timestamp (milliseconds)

```javascript
import advancedFormat from 'dayjs/plugin/advancedFormat'
dayjs.extend(advancedFormat)

dayjs('2024-01-15').format('Q')    // '1' (Q1)
dayjs('2024-07-15').format('Q')    // '3' (Q3)
dayjs('2024-01-15').format('Do')   // '15th'
dayjs('2024-01-01').format('Do')   // '1st'
dayjs('2024-01-02').format('Do')   // '2nd'
dayjs('2024-01-03').format('Do')   // '3rd'

// 24-hour format (same as HH but included here)
dayjs('2024-01-15T14:30:00').format('k')  // '14'
dayjs('2024-01-15T14:30:00').format('kk') // '14'

// Unix timestamps
dayjs('2024-01-15T00:00:00Z').format('X') // '1705276800' (seconds)
dayjs('2024-01-15T00:00:00Z').format('x') // '1705276800000' (milliseconds)
```

### arraySupport

Accept arrays as input for parsing. Each element in the array is tried until a valid date is found.

**Package:** `dayjs/plugin/arraySupport`

```javascript
import arraySupport from 'dayjs/plugin/arraySupport'
dayjs.extend(arraySupport)

// Try each format until one works
const date = dayjs(['2024/01/15', 'MM/DD/YYYY', 'YYYY/MM/DD'])
date.format() // '2024-01-15T00:00:00+00:00'

// Array of date strings
dayjs(['invalid', '2024-01-15', 'also-invalid']).format() // Uses second valid entry
```

### customParseFormat

Parse dates with custom format strings instead of relying on ISO 8601.

**Package:** `dayjs/plugin/customParseFormat`

```javascript
import customParseFormat from 'dayjs/plugin/customParseFormat'
dayjs.extend(customParseFormat)

// Parse with explicit format
dayjs('01/15/2024', 'MM/DD/YYYY').format() // '2024-01-15T00:00:00...'
dayjs('15-01-2024', 'DD-MM-YYYY').format() // '2024-01-15T00:00:00...'

// Without plugin, only ISO strings work
dayjs('01/15/2024').format() // Invalid! (treats as YYYY=0001)

// Complex formats
dayjs('January 15, 2024', 'MMMM D, YYYY').format()
dayjs('1/15/24 2:30 PM', 'M/D/YY h:mm A').format()

// Array of formats (tries each until match)
dayjs('01-15-2024', ['MM/DD/YYYY', 'DD-MM-YYYY']).format()
```

### objectSupport

Accept objects with date components for creating instances.

**Package:** `dayjs/plugin/objectSupport`

```javascript
import objectSupport from 'dayjs/plugin/objectSupport'
dayjs.extend(objectSupport)

// Create from object
const date = dayjs({
  year: 2024,
  month: 0,    // Zero-indexed (January)
  date: 15,
  hour: 14,
  minute: 30,
  second: 0
})
date.format('YYYY-MM-DD HH:mm:ss') // '2024-01-15 14:30:00'

// Partial object (fills rest with current values)
dayjs({ year: 2030 }).format('YYYY') // '2030'

// Merge with existing instance
dayjs('2024-01-15').set({ month: 5, date: 20 }) // June 20, 2024
```

### preParsePostFormat

Add hooks that run before parsing and after formatting.

**Package:** `dayjs/plugin/preParsePostFormat`

```javascript
import preParsePostFormat from 'dayjs/plugin/preParsePostFormat'
dayjs.extend(preParsePostFormat)

// Add custom locale with hooks
dayjs.locale('custom', {
  // Runs before parsing - can modify input string
  preParse: function (dateString) {
    return dateString.replace('TODAY', dayjs().format('YYYY-MM-DD'))
  },
  
  // Runs after formatting - can modify output string
  postFormat: function (formatString) {
    return formatString.toUpperCase()
  }
})

dayjs('TODAY', 'custom').format() // Uses today's date
```

## Duration Plugin

### duration

Create and manipulate time durations (not points in time).

**Package:** `dayjs/plugin/duration`

```javascript
import duration from 'dayjs/plugin/duration'
dayjs.extend(duration)

// Create duration from object
const d1 = dayjs.duration({ years: 1, months: 2, days: 3 })
d1.humanize() // 'about a year ago'

// Create from milliseconds
const d2 = dayjs.duration(90, 'minute')
d2.asMinutes() // 90

// Create from ISO 8601 string
const d3 = dayjs.duration('P1Y2M3D') // 1 year, 2 months, 3 days

// Getters (rounded)
d1.years()    // 1
d1.months()   // 2
d1.days()     // 3

// As getters (with decimals)
d1.asYears()      // 1.18...
d1.asDays()       // 428.5...
d1.asMilliseconds() // 37036800000

// Add/subtract durations
const d4 = d1.add(dayjs.duration(5, 'days'))
d4.days() // 8

const d5 = d1.subtract({ months: 1 })
d5.months() // 1

// Humanize
dayjs.duration(1, 'day').humanize() // 'a day'
dayjs.duration(1, 'day').humanize(true) // 'a day from now'
dayjs.duration(-1, 'day').humanize(true) // 'a day ago'

// Format
dayjs.duration({ hours: 2, minutes: 30 }).format() // '02:30:00'
dayjs.duration({ hours: 2, minutes: 30 }).format('HH:mm') // '02:30'

// Convert to Day.js for adding to dates
const now = dayjs()
const later = now.add(dayjs.duration(1, 'week'))

// Check if value is duration
dayjs.isDuration(d1) // true
```

**ISO 8601 Duration Format:** `P[n]Y[n]M[n]DT[n]H[n]M[n]S`
- `P` - Duration designator
- `Y` - Years, `M` - Months, `D` - Days
- `T` - Time designator
- `H` - Hours, `M` - Minutes, `S` - Seconds

Example: `P1Y2M3DT4H30M` = 1 year, 2 months, 3 days, 4 hours, 30 minutes

## Time Operation Plugins

### utc

Create and manipulate UTC instances.

**Package:** `dayjs/plugin/utc`

```javascript
import utc from 'dayjs/plugin/utc'
dayjs.extend(utc)

// Create UTC instance
const utcDate = dayjs.utc('2024-01-15T14:30:00Z')
utcDate.format() // '2024-01-15T14:30:00Z'

// Static method
dayjs.utc('2024-01-15').format() // UTC instance

// Convert to local time
const local = utcDate.local()
local.format() // Local timezone

// Check if instance is UTC
utcDate.isUTC() // true
local.isUTC()   // false

// Set specific UTC offset
dayjs('2024-01-15').utcOffset('+05:30').format() // +5:30 offset
dayjs('2024-01-15').utcOffset(-300).format()     // -5:00 offset (minutes)

// Preserve local time when converting to UTC
const localTime = dayjs('2024-01-15T14:30:00')
const asUtc = localTime.utc(true) // Keeps 14:30 as UTC time
```

### timezone

Full timezone support using IANA timezone database.

**Package:** `dayjs/plugin/timezone`

```javascript
import timezone from 'dayjs/plugin/timezone'
dayjs.extend(timezone)

// Create instance in specific timezone
const nyc = dayjs.tz('2024-01-15T14:30:00', 'America/New_York')
nyc.format() // Adjusted to EST/EDT

const lon = dayjs.tz('2024-01-15T14:30:00', 'Europe/London')
lon.format() // Adjusted to GMT/BST

// Get timezone name
dayjs.tz('2024-01-15', 'Asia/Tokyo').timezone() // 'Asia/Tokyo'

// Convert between timezones
const laTime = dayjs.tz('2024-01-15T10:00:00', 'America/Los_Angeles')
const nycTime = laTime.tz('America/New_York') // 13:00:00

// Handle DST automatically
dayjs.tz('2024-03-10T02:30:00', 'America/New_York') // DST spring forward
dayjs.tz('2024-11-03T02:30:00', 'America/New_York') // DST fall back
```

**Supported timezones:** All IANA timezone names (e.g., `America/New_York`, `Europe/London`, `Asia/Tokyo`)

### weekOfYear

Get and set the week number of the year (local week definition).

**Package:** `dayjs/plugin/weekOfYear`

```javascript
import weekOfYear from 'dayjs/plugin/weekOfYear'
dayjs.extend(weekOfYear)

// Get week number (1-53)
dayjs('2024-01-15').week() // 3

// Set week number
dayjs('2024-01-01').week(50) // Week 50 of 2024

// Week starts on Sunday by default (useful for US locale)
```

### isoWeek

ISO 8601 week calculations (weeks start on Monday).

**Package:** `dayjs/plugin/isoWeek`

```javascript
import isoWeek from 'dayjs/plugin/isoWeek'
dayjs.extend(isoWeek)

// Get ISO week number (1-53)
dayjs('2024-01-15').isoWeek() // 3

// Set ISO week number
dayjs('2024-01-01').isoWeek(50) // Week 50, Monday

// Get start/end of ISO week
dayjs('2024-01-15').startOf('isoWeek') // Monday of that week
dayjs('2024-01-15').endOf('isoWeek')   // Sunday of that week

// ISO week year (can differ from calendar year)
dayjs('2023-12-31').isoWeekYear() // 2024 (in ISO week 1 of 2024)
dayjs('2024-01-01').isoWeekYear() // 2024
```

### isoWeeksInYear

Get the number of ISO weeks in a year (52 or 53).

**Package:** `dayjs/plugin/isoWeeksInYear`

```javascript
import isoWeeksInYear from 'dayjs/plugin/isoWeeksInYear'
dayjs.extend(isoWeeksInYear)

dayjs('2024-01-01').isoWeeksInYear() // 52
dayjs('2020-01-01').isoWeeksInYear() // 53 (leap year with extra week)
```

### dayOfYear

Get and set the day number within the year (1-365/366).

**Package:** `dayjs/plugin/dayOfYear`

```javascript
import dayOfYear from 'dayjs/plugin/dayOfYear'
dayjs.extend(dayOfYear)

// Get day of year
dayjs('2024-01-01').dayOfYear() // 1
dayjs('2024-06-15').dayOfYear() // 167
dayjs('2024-12-31').dayOfYear() // 366 (leap year)

// Set day of year
dayjs('2024-01-01').dayOfYear(100) // April 9, 2024
```

### quarterOfYear

Get and set the quarter of the year.

**Package:** `dayjs/plugin/quarterOfYear`

```javascript
import quarterOfYear from 'dayjs/plugin/quarterOfYear'
dayjs.extend(quarterOfYear)

// Get quarter (1-4)
dayjs('2024-01-15').quarter() // 1
dayjs('2024-04-15').quarter() // 2
dayjs('2024-07-15').quarter() // 3
dayjs('2024-10-15').quarter() // 4

// Set quarter
dayjs('2024-01-01').quarter(3) // July 1, 2024 (start of Q3)

// Use with startOf/endOf
dayjs('2024-06-15').startOf('quarter') // April 1, 2024
dayjs('2024-06-15').endOf('quarter')   // June 30, 2024
```

## Comparison & Query Plugins

### isBetween

Check if a date is between two other dates.

**Package:** `dayjs/plugin/isBetween`

```javascript
import isBetween from 'dayjs/plugin/isBetween'
dayjs.extend(isBetween)

const date = dayjs('2024-06-15')

// Basic check (end exclusive)
date.isBetween('2024-01-01', '2024-12-31') // true
date.isBetween('2024-01-01', '2024-06-15') // false (end is exclusive)

// Inclusive end
date.isBetween('2024-01-01', '2024-06-15', null, '[]') // true

// With granularity
date.isBetween('2024-01-01', '2024-12-31', 'month') // true

// Different interval types
date.isBetween('2024-01-01', '2024-06-15', null, '()') // exclusive both ends
date.isBetween('2024-01-01', '2024-06-15', null, '[)') // default, start inclusive
date.isBetween('2024-01-01', '2024-06-15', null, '(]') // end inclusive
date.isBetween('2024-01-01', '2024-06-15', null, '[]') // both inclusive
```

**Intervals:**
- `()` - Both ends exclusive
- `[)` - Start inclusive, end exclusive (default)
- `(]` - Start exclusive, end inclusive
- `[]` - Both ends inclusive

### isSameOrAfter

Check if date is the same as or after another date.

**Package:** `dayjs/plugin/isSameOrAfter`

```javascript
import isSameOrAfter from 'dayjs/plugin/isSameOrAfter'
dayjs.extend(isSameOrAfter)

dayjs('2024-06-15').isSameOrAfter('2024-06-15') // true (same)
dayjs('2024-06-16').isSameOrAfter('2024-06-15') // true (after)
dayjs('2024-06-14').isSameOrAfter('2024-06-15') // false (before)

// With granularity
dayjs('2024-06-15T10:00:00').isSameOrAfter('2024-06-15T15:00:00', 'day') // true
```

### isSameOrBefore

Check if date is the same as or before another date.

**Package:** `dayjs/plugin/isSameOrBefore`

```javascript
import isSameOrBefore from 'dayjs/plugin/isSameOrBefore'
dayjs.extend(isSameOrBefore)

dayjs('2024-06-15').isSameOrBefore('2024-06-15') // true (same)
dayjs('2024-06-14').isSameOrBefore('2024-06-15') // true (before)
dayjs('2024-06-16').isSameOrBefore('2024-06-15') // false (after)
```

### isToday, isTomorrow, isYesterday

Check relative to current day.

**Package:** `dayjs/plugin/isToday`, `dayjs/plugin/isTomorrow`, `dayjs/plugin/isYesterday`

```javascript
import isToday from 'dayjs/plugin/isToday'
import isTomorrow from 'dayjs/plugin/isTomorrow'
import isYesterday from 'dayjs/plugin/isYesterday'
dayjs.extend(isToday)
dayjs.extend(isTomorrow)
dayjs.extend(isYesterday)

dayjs().isToday()       // true
dayjs().add(1, 'day').isTomorrow()   // true
dayjs().subtract(1, 'day').isYesterday() // true

// Specific dates
dayjs('2024-01-15').isToday() // Depends on current date
```

### minMax

Find minimum or maximum dates from multiple instances.

**Package:** `dayjs/plugin/minMax`

```javascript
import minMax from 'dayjs/plugin/minMax'
dayjs.extend(minMax)

// Find minimum (earliest)
const earliest = dayjs.min(
  dayjs('2024-03-01'),
  dayjs('2024-01-15'),
  dayjs('2024-06-01')
)
earliest.format() // '2024-01-15T00:00:00...'

// Find maximum (latest)
const latest = dayjs.max(
  dayjs('2024-03-01'),
  dayjs('2024-01-15'),
  dayjs('2024-06-01')
)
latest.format() // '2024-06-01T00:00:00...'

// Also available as instance methods
dayjs('2024-03-01').min(dayjs('2024-01-15')) // 2024-01-15
dayjs('2024-03-01').max(dayjs('2024-06-01')) // 2024-06-01
```

## Display & Localization Plugins

### relativeTime

Display human-readable relative time strings.

**Package:** `dayjs/plugin/relativeTime`

```javascript
import relativeTime from 'dayjs/plugin/relativeTime'
dayjs.extend(relativeTime)

// Time from now
dayjs('2024-01-01').fromNow() // 'a month ago'
dayjs().add(7, 'day').fromNow() // 'in a week'

// Time to now
dayjs('2025-01-01').toNow() // 'in a year'
dayjs().subtract(1, 'day').toNow() // 'a day ago'

// Compare two dates
dayjs('2024-06-01').from('2024-01-01') // '5 months ago'
dayjs('2024-01-01').to('2024-06-01') // 'in 5 months'

// Without suffix (just duration)
dayjs('2024-01-01').fromNow(true) // 'a month'
dayjs().add(7, 'day').fromNow(true) // 'a week'

// Custom thresholds
dayjs.extend(relativeTime, {
  thresholds: [
    ['s', 30],                 // seconds
    ['m', 45],                 // minutes
    ['h', 90],                 // hours
    ['d', 30],                 // days
    ['M', 45],                 // months
    ['y', 1.5],                // years
    ['L', Infinity]            // long format
  ]
})
```

### calendar

Display dates in calendar-style format (Yesterday, Today, Tomorrow).

**Package:** `dayjs/plugin/calendar`

```javascript
import calendar from 'dayjs/plugin/calendar'
dayjs.extend(calendar)

// Default calendar format
dayjs().subtract(1, 'day').calendar() // 'Yesterday at 12:30 PM'
dayjs().calendar()                     // 'Today at 12:30 PM'
dayjs().add(1, 'day').calendar()       // 'Tomorrow at 12:30 PM'
dayjs().add(7, 'day').calendar()       // '01/22/2024'

// With reference time
const refTime = dayjs('2024-06-15T12:00:00')
dayjs('2024-06-14').calendar(refTime) // 'Yesterday at 12:00 AM'
dayjs('2024-06-15').calendar(refTime) // 'Today at 12:00 AM'

// Custom formats
dayjs().calendar(null, {
  lastDay: '[Yesterday at] HH:mm',
  sameDay: '[Today at] HH:mm',
  nextDay: '[Tomorrow at] HH:mm',
  lastWeek: 'dddd [at] HH:mm',
  nextWeek: 'dddd [at] HH:mm',
  sameElse: 'MM/DD/YYYY'
})
```

### localizedFormat

Add locale-specific format tokens (L, LL, LLL, LLLL).

**Package:** `dayjs/plugin/localizedFormat`

```javascript
import localizedFormat from 'dayjs/plugin/localizedFormat'
dayjs.extend(localizedFormat)

// Locale-aware formats
import 'dayjs/locale/es'
dayjs.locale('es')

dayjs('2024-01-15').format('L')    // '1/15/2024' (US format)
dayjs('2024-01-15').format('LL')   // 'January 15, 2024'
dayjs('2024-01-15').format('LLL')  // 'January 15, 2024, 12:00 PM'
dayjs('2024-01-15').format('LLLL') // 'Tuesday, January 15, 2024, 12:00 PM'

// Different locales have different formats
dayjs.locale('en')
dayjs('2024-01-15').format('L') // '1/15/2024'

dayjs.locale('de')
dayjs('2024-01-15').format('L') // '15.01.2024'

dayjs.locale('ja')
dayjs('2024-01-15').format('L') // '2024/1/15'
```

**Format tokens:**
- `L` - Date (locale-specific)
- `LL` - Long date
- `LLL` - Date with time
- `LLLL` - Full date with weekday and time
- `l`, `ll`, `lll`, `lll` - Short versions

### updateLocale

Modify existing locale configurations.

**Package:** `dayjs/plugin/updateLocale`

```javascript
import updateLocale from 'dayjs/plugin/updateLocale'
dayjs.extend(updateLocale)

// Modify current locale
dayjs.updateLocale('en', {
  weekdays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
  months: [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ]
})

// Modify relativeTime thresholds
dayjs.updateLocale('en', {
  relativeTime: {
    future: 'in %s',
    past: '%s ago',
    s: 'a few seconds',
    m: 'a minute',
    mm: '%d minutes',
    h: 'an hour',
    hh: '%d hours',
    d: 'a day',
    dd: '%d days',
    M: 'a month',
    MM: '%d months',
    y: 'a year',
    yy: '%d years'
  }
})
```

### localeData

Access locale configuration data programmatically.

**Package:** `dayjs/plugin/localeData`

```javascript
import localeData from 'dayjs/plugin/localeData'
dayjs.extend(localeData)

// Get locale data
const data = dayjs().localeData()

data.weekdays()     // ['Sunday', 'Monday', ...]
data.weekdaysShort() // ['Sun', 'Mon', ...]
data.weekdaysMin()   // ['Su', 'Mo', ...]

data.months()       // ['January', 'February', ...]
data.monthsShort()  // ['Jan', 'Feb', ...]

data.firstDayOfWeek() // 0 (Sunday) or 1 (Monday) depending on locale

// Set locale data
dayjs.localeData().firstDayOfWeek(1) // Week starts on Monday
```

## Utility Plugins

### clone

Explicit cloning method (already built-in, plugin is redundant in modern versions).

**Package:** `dayjs/plugin/clone`

```javascript
import clone from 'dayjs/plugin/clone'
dayjs.extend(clone)

const original = dayjs('2024-01-15')
const cloned = original.clone()

cloned.isSame(original) // true
cloned === original     // false
```

Note: `clone()` is available without this plugin in Day.js 1.10+.

### toObject

Convert Day.js instance to plain object.

**Package:** `dayjs/plugin/toObject`

```javascript
import toObject from 'dayjs/plugin/toObject'
dayjs.extend(toObject)

const obj = dayjs('2024-01-15T14:30:45.123').toObject()
// {
//   years: 2024,
//   months: 0,
//   date: 15,
//   hours: 14,
//   minutes: 30,
//   seconds: 45,
//   milliseconds: 123
// }
```

### toArray

Convert Day.js instance to array of components.

**Package:** `dayjs/plugin/toArray`

```javascript
import toArray from 'dayjs/plugin/toArray'
dayjs.extend(toArray)

const arr = dayjs('2024-01-15T14:30:45.123').toArray()
// [2024, 0, 15, 14, 30, 45, 123]
//   year, month, date, hour, minute, second, millisecond
```

## Specialized Plugins

### buddhistEra

Support for Buddhist calendar era (BE = AD + 543).

**Package:** `dayjs/plugin/buddhistEra`

```javascript
import buddhistEra from 'dayjs/plugin/buddhistEra'
dayjs.extend(buddhistEra)

// Format with Buddhist year
dayjs('2024-01-15').format('BEEE') // '2567'

// Parse Buddhist year
dayjs('2567-01-15', 'BEEE-MM-DD').format('YYYY') // '2024'
```

### bigIntSupport

Support for BigInt timestamps.

**Package:** `dayjs/plugin/bigIntSupport`

```javascript
import bigIntSupport from 'dayjs/plugin/bigIntSupport'
dayjs.extend(bigIntSupport)

// Use BigInt for large timestamps
const date = dayjs(BigInt(1705276800000n))
date.valueOf() // Returns BigInt
```

### pluralGetSet

Allow plural unit names in get/set operations.

**Package:** `dayjs/plugin/pluralGetSet`

```javascript
import pluralGetSet from 'dayjs/plugin/pluralGetSet'
dayjs.extend(pluralGetSet)

// Already supported in core, but plugin ensures consistency
dayjs().get('years')   // 2024
dayjs().set('months', 5) // June
```

### negativeYear

Support for negative years (BC dates).

**Package:** `dayjs/plugin/negativeYear`

```javascript
import negativeYear from 'dayjs/plugin/negativeYear'
dayjs.extend(negativeYear)

// Parse BC dates
dayjs('-500-01-01').format('YYYY') // '-0500'

// Manipulate BC dates
dayjs('-500-01-01').add(100, 'year').format('YYYY') // '-0400'
```

### isLeapYear

Check if a year is a leap year.

**Package:** `dayjs/plugin/isLeapYear`

```javascript
import isLeapYear from 'dayjs/plugin/isLeapYear'
dayjs.extend(isLeapYear)

dayjs('2024-01-01').isLeapYear() // true
dayjs('2023-01-01').isLeapYear() // false
```

### isMoment

Check if a value is a Moment.js instance (for migration).

**Package:** `dayjs/plugin/isMoment`

```javascript
import isMoment from 'dayjs/plugin/isMoment'
dayjs.extend(isMoment)

// Returns true for Moment.js instances, false otherwise
dayjs.isMoment(momentInstance) // true if moment is loaded
```

### devHelper

Development helper that warns about common mistakes.

**Package:** `dayjs/plugin/devHelper`

```javascript
import devHelper from 'dayjs/plugin/devHelper'
dayjs.extend(devHelper)

// Will console.warn if you try to mutate a Day.js object
const date = dayjs()
date.year(2030) // Warns: "Mutation is not allowed"
```

### badMutable

Allow mutable operations (breaks immutability guarantee).

**Package:** `dayjs/plugin/badMutable`

```javascript
import badMutable from 'dayjs/plugin/badMutable'
dayjs.extend(badMutable)

// WARNING: This breaks Day.js immutability!
const date = dayjs('2024-01-15')
date.year(2030) // Mutates original instance
date.format('YYYY') // '2030' (original changed!)
```

Use only when you specifically need mutation and understand the risks.

### weekday

Get/set weekday with configurable first day of week.

**Package:** `dayjs/plugin/weekday`

```javascript
import weekday from 'dayjs/plugin/weekday'
dayjs.extend(weekday)

// Get weekday (0 = first day of week, typically Monday in many locales)
dayjs('2024-01-15').weekday() // 1 (Monday = 0 in ISO locale)

// Set weekday
dayjs('2024-01-15').weekday(3) // Thursday of that week
```
