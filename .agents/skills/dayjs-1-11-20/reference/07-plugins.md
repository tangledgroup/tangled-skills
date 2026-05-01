# Plugins

Day.js ships with core functionality only. All extended features are provided as independent plugins loaded on demand via `dayjs.extend()`. This keeps the base library at ~2kB and lets you include only what you need.

## Loading Plugins

**Node.js:**

```javascript
import pluginName from 'dayjs/plugin/pluginName'
dayjs.extend(pluginName)
```

**Browser (CDN):**

Each plugin is available as a separate script that registers itself on the `window` object:

```html
<script src="https://cdn.jsdelivr.net/npm/dayjs/plugin/pluginName.js"></script>
<script>
  dayjs.extend(window.dayjs_plugin_pluginName)
</script>
```

You can load multiple plugins. They are applied in the order you call `extend()`.

## Writing a Custom Plugin

Template for building a Day.js plugin:

```javascript
export default (option, dayjsClass, dayjsFactory) => {
  // Add instance method — e.g., dayjs().myMethod()
  dayjsClass.prototype.myMethod = function(args) {}

  // Add static method — e.g., dayjs.myStatic()
  dayjsFactory.myStatic = (args) => {}

  // Override existing API
  const oldFormat = dayjsClass.prototype.format
  dayjsClass.prototype.format = function(args) {
    const result = oldFormat.bind(this)(args)
    return result  // return modified result
  }
}
```

The `option` parameter allows plugin configuration:

```javascript
dayjs.extend(somePlugin, { someOption: true })
```

## Official Plugins

### UTC

Adds `.utc()`, `.local()`, `.isUTC()` APIs to parse or display in UTC. Also adds `.utcOffset()` for setting custom offsets.

```javascript
import utc from 'dayjs/plugin/utc'
dayjs.extend(utc)

dayjs.utc().format()              // current time in UTC
dayjs().utc().format()            // convert local to UTC
dayjs().utc().local().format()    // convert back to local
dayjs().utcOffset(8)              // set UTC+08:00
```

### Timezone

Adds `.tz()`, `.tz.guess()`, `.tz.setDefault()` APIs for timezone conversion. Requires the `utc` plugin.

```javascript
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
dayjs.extend(utc)
dayjs.extend(timezone)

// Parse in a timezone
const d1 = dayjs.tz('2013-11-18 11:55', 'Asia/Taipei')
d1.format() // '2013-11-18T11:55:00+08:00'

// Convert to a timezone
const d2 = dayjs.utc('2013-11-18 11:55').tz('Asia/Taipei')
d2.format() // '2013-11-18T19:55:00+08:00'

// Guess user timezone
dayjs.tz.guess() // 'America/New_York'

// Set default timezone
dayjs.tz.setDefault('America/New_York')
```

Unlike Moment.js, `dayjs(dateValue)` always uses local timezone even with `setDefault`. Use `dayjs.tz(dateValue)` (without second parameter) to use the default timezone.

### Duration

Adds `.duration()` and `.isDuration()` APIs for time spans:

```javascript
import duration from 'dayjs/plugin/duration'
dayjs.extend(duration)

const d = dayjs.duration(100)                    // 100ms
const d2 = dayjs.duration({ days: 1, hours: 2 }) // 1 day 2 hours

// Use with add
dayjs().add(d2)
```

### RelativeTime

Adds `.from()`, `.to()`, `.fromNow()`, `.toNow()` for relative time strings:

```javascript
import relativeTime from 'dayjs/plugin/relativeTime'
dayjs.extend(relativeTime)

dayjs('1999-01-01').fromNow()   // '22 years ago'
dayjs('1999-01-01').fromNow(true) // '22 years' (no suffix)
dayjs().from(dayjs('1990-01-01')) // 'in 31 years'
```

### CustomParseFormat

Extends the constructor to parse strings with custom format patterns:

```javascript
import customParseFormat from 'dayjs/plugin/customParseFormat'
dayjs.extend(customParseFormat)

dayjs('05/02/69 1:02:03 PM -05:00', 'MM/DD/YY H:mm:ss A Z')
```

### AdvancedFormat

Adds more format tokens: `Q` (quarter), `Do` (ordinal day), `k`/`kk` (hour 1-24), `X`/`x` (Unix timestamps), `w`/`W` (week numbers).

```javascript
import advancedFormat from 'dayjs/plugin/advancedFormat'
dayjs.extend(advancedFormat)

dayjs().format('Q Do k kk X x')
```

### IsBetween

Adds `.isBetween(start, end, unit?, inclusivity?)`:

```javascript
import isBetween from 'dayjs/plugin/isBetween'
dayjs.extend(isBetween)

dayjs('2010-10-20').isBetween('2010-10-19', '2010-10-25', 'day', '[)')
```

### Calendar

Adds `.calendar()` for human-readable calendar time:

```javascript
import calendar from 'dayjs/plugin/calendar'
dayjs.extend(calendar)

dayjs().calendar() // 'Today at 2:30 AM'
```

### LocalizedFormat

Adds locale-aware format tokens `L`, `LL`, `LLL`, `LLLL`, `LT`:

```javascript
import localizedFormat from 'dayjs/plugin/localizedFormat'
dayjs.extend(localizedFormat)

dayjs().format('LLLL') // 'Thursday, January 25, 2019 12:00 AM'
```

### LocaleData

Adds `.localeData()` to access locale properties:

```javascript
import localeData from 'dayjs/plugin/localeData'
dayjs.extend(localeData)

dayjs().localeData().firstDayOfWeek()
```

### MinMax

Adds static `.min()` and `.max()` methods:

```javascript
import minMax from 'dayjs/plugin/minMax'
dayjs.extend(minMax)

dayjs.max(dayjs(), dayjs('2018-01-01'), dayjs('2019-01-01'))
dayjs.min([dayjs(), dayjs('2018-01-01')])
```

### ObjectSupport

Extends constructor and manipulation methods to accept object arguments:

```javascript
import objectSupport from 'dayjs/plugin/objectSupport'
dayjs.extend(objectSupport)

dayjs({ year: 2010, month: 1, day: 12 })
dayjs().set({ year: 2010, month: 1 })
dayjs().add({ month: 1 })
```

### QuarterOfYear

Adds `.quarter()` getter/setter and extends `.add()`, `.subtract()`, `.startOf()`, `.endOf()` for `quarter` unit:

```javascript
import quarterOfYear from 'dayjs/plugin/quarterOfYear'
dayjs.extend(quarterOfYear)

dayjs('2010-04-01').quarter() // 2
```

### IsoWeek

Adds `.isoWeek()`, `.isoWeekday()`, `.isoWeekYear()` and extends `.startOf()`/`.endOf()` for `isoWeek` unit:

```javascript
import isoWeek from 'dayjs/plugin/isoWeek'
dayjs.extend(isoWeek)

dayjs().isoWeek()      // ISO week number
dayjs().isoWeekday()   // ISO day of week (Monday = 1)
```

### Weekday

Adds `.weekday()` for locale-aware day of week:

```javascript
import weekday from 'dayjs/plugin/weekday'
dayjs.extend(weekday)

dayjs().weekday(-7) // last Sunday (or Monday depending on locale)
dayjs().weekday(7)  // next Sunday
```

### ArraySupport

Allows constructing from arrays: `dayjs([year, month, day, ...])`.

### ToArray / ToObject

Adds `.toArray()` and `.toObject()` serialization:

```javascript
import toArray from 'dayjs/plugin/toArray'
import toObject from 'dayjs/plugin/toObject'
dayjs.extend(toArray)
dayjs.extend(toObject)

dayjs('2019-01-25').toArray()  // [2019, 0, 25, 0, 0, 0, 0]
dayjs('2019-01-25').toObject() // { years: 2019, months: 0, date: 25, ... }
```

### IsToday / IsYesterday / IsTomorrow

Simple boolean checks against the current date.

### IsSameOrAfter / IsSameOrBefore

Inclusive comparison variants of `isAfter`/`isBefore`.

### IsLeapYear

Adds `.isLeapYear()`:

```javascript
import isLeapYear from 'dayjs/plugin/isLeapYear'
dayjs.extend(isLeapYear)
dayjs('2000-01-01').isLeapYear() // true
```

### UpdateLocale

Allows modifying locale properties after loading:

```javascript
import updateLocale from 'dayjs/plugin/updateLocale'
dayjs.extend(updateLocale)
dayjs.updateLocale('en', { months: [...] })
```

### DevHelper

Provides hints and warnings during development. Automatically disabled in production when `process.env.NODE_ENV === 'production'`. Can be removed by minifiers like UglifyJS:

```javascript
import devHelper from 'dayjs/plugin/devHelper'
dayjs.extend(devHelper)
```

### PreParsePostFormat

Allows intercepting input before parsing and output after formatting. Useful for custom transformations.

### PluralGetSet

Adds support for plural unit names in `.get()` and `.set()`.

### WeekOfYear / WeekYear

Adds week-of-year and week-year getters and format tokens.

### BuddhistEra

Supports Buddhist Era calendar year formatting.

### BigIntSupport

Adds support for BigInt timestamps.
