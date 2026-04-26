# Manipulation

Once you have a Day.js object, manipulate it with add, subtract, start-of/end-of, and timezone operations. All manipulation methods return new instances (immutability).

## Add

Returns a cloned instance with time added:

```javascript
const a = dayjs()
const b = a.add(7, 'day')
// a — original value, unchanged
// b — the result
```

Units support long form, plural, and short form. Long/plural forms are case-insensitive; short forms are case-sensitive:

```javascript
dayjs().add(1, 'year')        // 1 year from now
dayjs().add(15, 'minute')     // 15 minutes from now
dayjs().add(2, 'month')       // 2 months from now
dayjs().add(7, 'd')           // same as 'day'
dayjs().add(7, 'days')        // same as 'day'
dayjs().add(7, 'DAY')         // case insensitive
```

Supported units: `year`/`y`, `month`/`M`, `week`/`w`, `day`/`d`, `hour`/`h`, `minute`/`m`, `second`/`s`, `millisecond`/`ms`. Quarter (`quarter`/`Q`) requires the `QuarterOfYear` plugin.

When decimal values are passed for days and weeks, they are rounded to the nearest integer before adding.

You can also add durations (requires `Duration` plugin):

```javascript
dayjs().add(dayjs.duration({ days: 1 }))
```

## Subtract

Returns a cloned instance with time subtracted:

```javascript
dayjs().subtract(7, 'year')   // 7 years ago
dayjs().subtract(1, 'month')  // 1 month ago
dayjs().subtract(30, 'minute')
```

Same unit rules as `.add()`. Decimal values for days and weeks are rounded before subtracting.

## Start of Unit of Time

Returns a cloned instance set to the start of a unit:

```javascript
dayjs().startOf('year')       // Jan 1, 00:00:00.000
dayjs().startOf('month')      // 1st of month, 00:00:00.000
dayjs().startOf('week')       // start of week (locale-dependent)
dayjs().startOf('date')       // 00:00:00.000 today
dayjs().startOf('day')        // 00:00:00.000 today
dayjs().startOf('hour')       // XX:00:00.000
dayjs().startOf('minute')     // XX:YY:00.000
dayjs().startOf('second')     // XX:YY:ZZ.000
```

`isoWeek` requires the `IsoWeek` plugin. `quarter` requires the `QuarterOfYear` plugin.

## End of Unit of Time

Returns a cloned instance set to the end of a unit:

```javascript
dayjs().endOf('year')         // Dec 31, 23:59:59.999
dayjs().endOf('month')        // last day, 23:59:59.999
dayjs().endOf('day')          // 23:59:59.999 today
dayjs().endOf('hour')         // XX:59:59.999
```

## Method Chaining

All manipulation methods return Day.js instances, enabling fluent chains:

```javascript
dayjs('2019-01-25')
  .add(1, 'day')
  .subtract(1, 'year')
  .year(2009)
  .format('YYYY-MM-DD') // '2008-01-26'
```

## UTC Conversion (UTC plugin)

```javascript
import utc from 'dayjs/plugin/utc'
dayjs.extend(utc)

// Convert to UTC mode
dayjs().utc()                 // => Dayjs in UTC mode
dayjs.utc('2018-08-08')       // parse directly in UTC

// Convert back to local
dayjs().utc().local()         // => Dayjs in local mode

// Check if in UTC mode
dayjs().utc().isUTC()         // true
dayjs().isUTC()               // false
```

`dayjs().utc()` converts the current time to UTC. `dayjs().utc(true)` keeps the local time values but interprets them as UTC:

```javascript
dayjs('2016-05-03 22:15:01').utc(true).format()
// '2016-05-03T22:15:01Z'
```

## UTC Offset

Get the UTC offset in minutes:

```javascript
dayjs().utcOffset()           // e.g., -300 (EST is UTC-5, in minutes)
```

With the UTC plugin, set a specific offset. If input is between -16 and 16, it's interpreted as hours:

```javascript
dayjs().utcOffset(8)          // UTC+08:00 (hours)
dayjs().utcOffset(480)        // UTC+08:00 (minutes, equivalent)
dayjs().utcOffset('05:30')    // UTC+05:30
```

Once set, the offset is fixed (no automatic DST rules). Pass `true` as second argument to keep the same local time:

```javascript
dayjs.utc('2000-01-01T06:01:02Z').utcOffset(1, true).format()
// '2000-01-01T06:01:02+01:00'
```
