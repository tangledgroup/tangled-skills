# Query

Comparison methods for checking temporal relationships between Day.js instances.

## Is Before

Indicates whether the Day.js object is before another date-time:

```javascript
dayjs().isBefore(dayjs('2011-01-01'))           // default: milliseconds
dayjs().isBefore('2011-01-01', 'month')         // compares month and year
```

Pass a unit as the second parameter to limit granularity. When comparing by `month`, it checks month and year. When comparing by `day`, it checks day, month, and year.

## Is Same

Indicates whether the Day.js object is the same as another date-time:

```javascript
dayjs().isSame(dayjs('2011-01-01'))             // default: milliseconds
dayjs().isSame('2011-01-01', 'year')            // compares year only
dayjs().isSame('2011-01-01', 'month')           // compares month and year
```

When including a second parameter, it matches all units equal or larger. Passing `month` checks month and year. Passing `day` checks day, month, and year.

## Is After

Indicates whether the Day.js object is after another date-time:

```javascript
dayjs().isAfter(dayjs('2011-01-01'))            // default: milliseconds
dayjs().isAfter('2011-01-01', 'month')          // compares month and year
```

Same granularity rules as `isBefore` and `isSame`.

## Is Between (IsBetween plugin)

Indicates whether the Day.js object is between two other date-times:

```javascript
import isBetween from 'dayjs/plugin/isBetween'
dayjs.extend(isBetween)

dayjs('2010-10-20').isBetween('2010-10-19', dayjs('2010-10-25'))
// default: milliseconds, exclusive bounds '()'

dayjs().isBetween('2010-10-19', '2010-10-25', 'month')
// compares month and year
```

The fourth parameter controls inclusivity with bracket notation:

- `'()'` — excludes start and end (default)
- `'[]'` — includes both start and end
- `'[)'` — includes start, excludes end
- `'(]'` — excludes start, includes end

```javascript
dayjs('2016-10-30').isBetween('2016-01-01', '2016-10-30', 'day', '[)')
// true — includes Oct 30 as start boundary, excludes it as end
```

## Is Day.js

Check whether a variable is a Day.js object:

```javascript
dayjs.isDayjs(dayjs())     // true
dayjs.isDayjs(new Date())  // false
```

The `instanceof` operator works equally well:

```javascript
dayjs() instanceof dayjs   // true
```

## Is Leap Year (IsLeapYear plugin)

Indicates whether the Day.js object's year is a leap year:

```javascript
import isLeapYear from 'dayjs/plugin/isLeapYear'
dayjs.extend(isLeapYear)

dayjs('2000-01-01').isLeapYear() // true
dayjs('2019-01-01').isLeapYear() // false
```

## Is Today / Is Yesterday / Is Tomorrow (Plugin)

Simple boolean checks against the current date:

```javascript
import isToday from 'dayjs/plugin/isToday'
import isYesterday from 'dayjs/plugin/isYesterday'
import isTomorrow from 'dayjs/plugin/isTomorrow'

dayjs.extend(isToday)
dayjs.extend(isYesterday)
dayjs.extend(isTomorrow)

dayjs().isToday()       // true
dayjs().isYesterday()   // false
dayjs().isTomorrow()    // false
```

## Is Same Or After / Is Same Or Before (Plugin)

Inclusive comparison variants:

```javascript
import isSameOrAfter from 'dayjs/plugin/isSameOrAfter'
import isSameOrBefore from 'dayjs/plugin/isSameOrBefore'

dayjs.extend(isSameOrAfter)
dayjs.extend(isSameOrBefore)

dayjs().isSameOrAfter(dayjs())    // true (same moment)
dayjs().isSameOrBefore(dayjs())   // true (same moment)
```

## Min / Max (MinMax plugin)

Return the earliest or latest from multiple Day.js instances:

```javascript
import minMax from 'dayjs/plugin/minMax'
dayjs.extend(minMax)

dayjs.max(dayjs(), dayjs('2018-01-01'), dayjs('2019-01-01'))
dayjs.min([dayjs(), dayjs('2018-01-01'), dayjs('2019-01-01')])
```

Accepts both multiple arguments and an array of Day.js instances.
