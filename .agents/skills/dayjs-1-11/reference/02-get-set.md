# Get and Set

Day.js uses overloaded getters and setters. Calling without arguments reads the value; calling with an argument returns a new instance with that value set. All setters return a new Day.js instance (immutability).

## Generic Get / Set

Use `.get()` and `.set()` for dynamic unit access. Units are case-insensitive and support plural and short forms:

```javascript
dayjs().get('year')         // same as dayjs().year()
dayjs().get('month')        // 0-11
dayjs().get('date')
dayjs().get('hour')
dayjs().get('minute')
dayjs().get('second')
dayjs().get('millisecond')

dayjs().set('date', 1)
dayjs().set('month', 3)     // April
dayjs().set('second', 30)
```

These are equivalent to calling the specific getter/setter:

```javascript
dayjs().set(unit, value) === dayjs()[unit](value)
dayjs().get(unit) === dayjs()[unit]()
```

For multiple sets, chain calls:

```javascript
dayjs().set('hour', 5).set('minute', 55).set('second', 15)
```

## Year

```javascript
dayjs().year()              // e.g. 2024
dayjs().year(2000)          // => Dayjs
```

## Month

Months are **zero-indexed**: January = 0, December = 11.

```javascript
dayjs().month()             // 0-11
dayjs().month(0)            // => Dayjs (January)
dayjs().month(11)           // => Dayjs (December)
```

## Date of Month

```javascript
dayjs().date()              // 1-31
dayjs().date(15)            // => Dayjs
```

Exceeding the valid range bubbles to the next month.

## Day of Week

Returns 0 (Sunday) through 6 (Saturday):

```javascript
dayjs().day()               // 0-6
dayjs().day(1)              // => Dayjs (set to Monday)
```

## Hour

```javascript
dayjs().hour()              // 0-23
dayjs().hour(14)            // => Dayjs
```

## Minute

```javascript
dayjs().minute()            // 0-59
dayjs().minute(30)          // => Dayjs
```

## Second

```javascript
dayjs().second()            // 0-59
dayjs().second(30)          // => Dayjs
```

## Millisecond

```javascript
dayjs().millisecond()       // 0-999
dayjs().millisecond(1)      // => Dayjs (set to 1ms)
```

## UTC Mode Getters/Setters

When in UTC mode (via the `utc` plugin), getters and setters map to their UTC equivalents:

```javascript
import utc from 'dayjs/plugin/utc'
dayjs.extend(utc)

dayjs.utc().second(30).valueOf()  // equivalent to new Date().setUTCSeconds(30)
dayjs.utc().second()              // equivalent to new Date().getUTCSeconds()
```

## Overflow Behavior

When setting a value beyond the valid range, Day.js bubbles up to the next unit:

```javascript
dayjs('2019-01-31').set('date', 40) // rolls into March
dayjs('2019-01-01').month(13)       // rolls into 2020
dayjs().hour(25)                     // rolls to next day, hour 1
```
