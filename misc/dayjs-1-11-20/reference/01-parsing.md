# Parsing

Creating Day.js instances from various input types. Call `dayjs()` with one of the supported inputs to get a wrapper object around the native `Date`.

## Now

Call `dayjs()` with no arguments to get the current date and time:

```javascript
const now = dayjs()
```

This is equivalent to `dayjs(new Date())`. Day.js treats `dayjs(undefined)` the same as `dayjs()`. However, `dayjs(null)` produces an invalid instance.

## String (ISO 8601)

Pass an ISO 8601 string. Day.js natively parses strings in ISO format (a space instead of `T` is also accepted):

```javascript
dayjs('2018-04-04')                           // '2018-04-04T00:00:00'
dayjs('2018-04-04T16:00:00.000Z')             // with Z suffix (UTC)
dayjs('2018-04-13 19:18:17.040+02:00')        // with timezone offset
dayjs('2018-04-13 19:18')                     // partial time
```

Strings ending with `Z` are parsed as UTC. For consistent results parsing anything other than ISO 8601 strings, use the `customParseFormat` plugin.

## String + Format (CustomParseFormat plugin)

For arbitrary date formats, load the `customParseFormat` plugin:

```javascript
import customParseFormat from 'dayjs/plugin/customParseFormat'
dayjs.extend(customParseFormat)

dayjs('05/02/69 1:02:03 PM -05:00', 'MM/DD/YY H:mm:ss A Z')
// => 1969-05-02T18:02:03.000Z

dayjs('2018 Enero 15', 'YYYY MMMM DD', 'es')
// => 2018-01-15 (Spanish locale month name)

dayjs('1970-00-00', 'YYYY-MM-DD', true)  // strict parsing mode
```

The third parameter enables strict parsing, which rejects invalid dates that would otherwise be coerced.

## Unix Timestamp (milliseconds)

Pass an integer representing milliseconds since the Unix Epoch (Jan 1, 1970 00:00:00 UTC):

```javascript
dayjs(1318781876406) // => Dayjs instance
```

The argument must be a number.

## Unix Timestamp (seconds)

Use `dayjs.unix()` for second-level timestamps:

```javascript
dayjs.unix(1548381600) // => Dayjs instance
```

## Date Object

Wrap an existing `Date` object:

```javascript
dayjs(new Date())                          // now
dayjs(new Date(2018, 7, 8))                // August 8, 2018 (month zero-indexed)
```

## Object (ObjectSupport plugin)

With the `objectSupport` plugin, pass a plain object. Note that month is **1-indexed** in objects:

```javascript
import objectSupport from 'dayjs/plugin/objectSupport'
dayjs.extend(objectSupport)

dayjs({ year: 2018, month: 8, day: 8 })    // August 8, 2018
dayjs({ year: 2018, month: 7, date: 8 })   // 'date' key also accepted
```

## Array (ArraySupport plugin)

With the `arraySupport` plugin, pass an array mirroring `new Date()` parameters. Months are **zero-indexed**:

```javascript
import arraySupport from 'dayjs/plugin/arraySupport'
dayjs.extend(arraySupport)

dayjs([2010, 1, 14, 15, 25, 50, 125])      // Feb 14, 3:25:50.125 PM
dayjs([2010])                               // Jan 1
dayjs([2010, 6])                            // July 1
dayjs([2010, 6, 10])                        // July 10
```

`dayjs([])` returns the current time.

## UTC Mode (UTC plugin)

With the `utc` plugin, parse directly in UTC:

```javascript
import utc from 'dayjs/plugin/utc'
dayjs.extend(utc)

dayjs.utc('2018-08-08')     // parsed as UTC
dayjs.utc(new Date())        // current time in UTC mode
```

## Clone

Passing a Day.js instance to `dayjs()` clones it:

```javascript
const d1 = dayjs('2019-01-25')
const d2 = dayjs(d1)  // clone of d1
d2 === d1             // false — different instances, same time
```

## Validation

Check if a Day.js instance contains a valid date:

```javascript
dayjs('2018-08-08').isValid() // true
dayjs('not-a-date').isValid() // false
dayjs(null).isValid()         // false
```

Invalid dates still produce Day.js instances — they just fail `isValid()` checks. Calling `format()` on an invalid instance returns `'Invalid Date'`.
