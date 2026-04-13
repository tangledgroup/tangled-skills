# Migrating from Moment.js to Day.js

Day.js provides a largely Moment.js-compatible API, making migration straightforward. This guide covers the key differences and migration patterns.

## Quick Migration

### Basic Replacement

```javascript
// Moment.js
import moment from 'moment'
const now = moment()
const formatted = now.format('YYYY-MM-DD')

// Day.js
import dayjs from 'dayjs'
const now = dayjs()
const formatted = now.format('YYYY-MM-DD')
```

### Find and Replace Pattern

For simple usage, you can often do a global find/replace:

```bash
# Replace imports
sed -i 's/moment/dayjs/g' your-file.js

# Replace function calls (be careful with this)
sed -i 's/moment\./dayjs./g' your-file.js
```

**Note:** Review changes carefully as some Moment.js methods don't exist in Day.js core.

## Key Differences

### 1. Plugins Required for Additional Features

Moment.js includes all features by default (~29KB). Day.js requires plugins for extended functionality (~2KB base + plugins).

| Feature | Moment.js | Day.js |
|---------|-----------|--------|
| UTC | Built-in | `import utc from 'dayjs/plugin/utc'` |
| Timezone | Built-in | `import timezone from 'dayjs/plugin/timezone'` |
| Relative time | Built-in | `import relativeTime from 'dayjs/plugin/relativeTime'` |
| Custom format parsing | Built-in | `import customParseFormat from 'dayjs/plugin/customParseFormat'` |
| Durations | Built-in | `import duration from 'dayjs/plugin/duration'` |
| Localization | Built-in | Load locale: `import 'dayjs/locale/es'` |

### 2. Immutability

Both libraries are immutable, but Day.js is stricter about it.

```javascript
// Both Moment.js and Day.js
const date = dayjs('2024-01-15')
const modified = date.add(1, 'day')

date.format()      // '2024-01-15' (unchanged)
modified.format()  // '2024-01-16' (new instance)
```

### 3. No Mutation Methods

Moment.js has some mutation methods that Day.js doesn't support by default:

```javascript
// Moment.js - MUTATES original
const m = moment('2024-01-15')
m.year(2030)
m.format('YYYY') // '2030' (original changed!)

// Day.js - Returns new instance
const d = dayjs('2024-01-15')
const modified = d.year(2030)
d.format('YYYY')        // '2024' (unchanged)
modified.format('YYYY') // '2030' (new instance)
```

If you need mutation in Day.js, use the `badMutable` plugin (not recommended):

```javascript
import badMutable from 'dayjs/plugin/badMutable'
dayjs.extend(badMutable)

const d = dayjs('2024-01-15')
d.year(2030) // Now mutates (breaks immutability!)
```

## API Compatibility Matrix

### Fully Compatible Methods

These methods work identically in both libraries:

**Parsing:**
- `dayjs()` / `moment()` - Constructor
- `dayjs(string)` / `moment(string)` - Parse ISO string
- `dayjs(date)` / `moment(date)` - From Date object
- `dayjs(timestamp)` / `moment(timestamp)` - From timestamp
- `isValid()` - Validation
- `clone()` - Clone instance

**Getters/Setters:**
- `year()` / `year(n)`
- `month()` / `month(n)` (zero-indexed in both)
- `date()` / `date(n)`
- `day()` / `day(n)` (0=Sunday in both)
- `hour()` / `hour(n)`
- `minute()` / `minute(n)`
- `second()` / `second(n)`
- `millisecond()` / `millisecond(n)`
- `get(unit)` / `set(unit, value)`

**Manipulation:**
- `add(n, unit)`
- `subtract(n, unit)`
- `startOf(unit)`
- `endOf(unit)`

**Display:**
- `format(template)` - Same format tokens
- `valueOf()`
- `unix()`
- `toDate()`
- `toJSON()`
- `toISOString()`
- `toString()`

**Query:**
- `isBefore(date, unit)`
- `isSame(date, unit)`
- `isAfter(date, unit)`
- `diff(date, unit, float)`

### Methods Requiring Plugins

| Moment.js Method | Day.js Equivalent | Plugin Required |
|-----------------|-------------------|-----------------|
| `moment.utc()` | `dayjs.utc()` | `utc` |
| `.utc()` | `.utc()` | `utc` |
| `.local()` | `.local()` | `utc` |
| `.isUTC()` | `.isUTC()` | `utc` |
| `.fromNow()` | `.fromNow()` | `relativeTime` |
| `.from()` | `.from()` | `relativeTime` |
| `.toNow()` | `.toNow()` | `relativeTime` |
| `.to()` | `.to()` | `relativeTime` |
| `.calendar()` | `.calendar()` | `calendar` |
| `moment.duration()` | `dayjs.duration()` | `duration` |
| `.isBetween()` | `.isBetween()` | `isBetween` |
| `.isSameOrAfter()` | `.isSameOrAfter()` | `isSameOrAfter` |
| `.isSameOrBefore()` | `.isSameOrBefore()` | `isSameOrBefore` |
| `.isToday()` | `.isToday()` | `isToday` |
| `.isTomorrow()` | `.isTomorrow()` | `isTomorrow` |
| `.isYesterday()` | `.isYesterday()` | `isYesterday` |
| `.week()` | `.week()` | `weekOfYear` |
| `.isoWeek()` | `.isoWeek()` | `isoWeek` |
| `.quarter()` | `.quarter()` | `quarterOfYear` |
| `.dayOfYear()` | `.dayOfYear()` | `dayOfYear` |
| `.tz()` | `.tz()` | `timezone` |
| `moment.min()` | `dayjs.min()` | `minMax` |
| `moment.max()` | `dayjs.max()` | `minMax` |

### Methods Not Available in Day.js

Some Moment.js methods don't have Day.js equivalents:

**Not Available:**
- `.addTo()` / `subtractFrom()` - Mutation methods (use immutable pattern)
- `.max()` / `.min()` as instance setters (only as static methods with plugin)
- `.bubble()` - Internal method
- `.lang()` - Use `.locale()` instead
- `moment.langs()` - Not needed, locales are simpler in Day.js

**Workaround for Missing Features:**
If you need a Moment.js feature not in Day.js:
1. Check if a community plugin exists
2. Implement using available methods
3. Consider if the feature is actually needed

## Migration Examples

### UTC Operations

```javascript
// Moment.js
import moment from 'moment'

const utc = moment.utc('2024-01-15T14:30:00Z')
const local = utc.local()
const isUtc = utc.isUTC()

// Day.js
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
dayjs.extend(utc)

const utcDate = dayjs.utc('2024-01-15T14:30:00Z')
const local = utcDate.local()
const isUtc = utcDate.isUTC()
```

### Timezones

```javascript
// Moment.js (with moment-timezone)
import moment from 'moment-timezone'

const nyc = moment.tz('2024-01-15T14:30:00', 'America/New_York')
const timezoneName = nyc.zoneName

// Day.js
import dayjs from 'dayjs'
import timezone from 'dayjs/plugin/timezone'
dayjs.extend(timezone)

const nyc = dayjs.tz('2024-01-15T14:30:00', 'America/New_York')
const timezoneName = nyc.timezone()
```

### Relative Time

```javascript
// Moment.js
import moment from 'moment'
import 'moment/locale/es'

moment.locale('es')
moment('2024-01-01').fromNow() // 'hace 3 meses'

// Day.js
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/es'
dayjs.extend(relativeTime)

dayjs.locale('es')
dayjs('2024-01-01').fromNow() // 'hace 3 meses'
```

### Durations

```javascript
// Moment.js
import moment from 'moment'

const d = moment.duration(1, 'year')
const years = d.years()
const asDays = d.asDays()
const human = d.humanize()

// Day.js
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'
dayjs.extend(duration)

const d = dayjs.duration(1, 'year')
const years = d.years()
const asDays = d.asDays()
const human = d.humanize()
```

### Custom Format Parsing

```javascript
// Moment.js
import moment from 'moment'

moment('01/15/2024', 'MM/DD/YYYY') // Works by default

// Day.js
import dayjs from 'dayjs'
import customParseFormat from 'dayjs/plugin/customParseFormat'
dayjs.extend(customParseFormat)

dayjs('01/15/2024', 'MM/DD/YYYY') // Now works
```

### Calendar Display

```javascript
// Moment.js
import moment from 'moment'

moment().subtract(1, 'day').calendar() // 'Yesterday at 12:30 PM'

// Day.js
import dayjs from 'dayjs'
import calendar from 'dayjs/plugin/calendar'
dayjs.extend(calendar)

dayjs().subtract(1, 'day').calendar() // 'Yesterday at 12:30 PM'
```

## Locale Migration

### Loading Locales

```javascript
// Moment.js
import moment from 'moment'
import 'moment/locale/es'
moment.locale('es')

// Day.js (nearly identical)
import dayjs from 'dayjs'
import 'dayjs/locale/es'
dayjs.locale('es')
```

### Creating Custom Locales

```javascript
// Moment.js
moment.defineLocale('custom', {
  weekdays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
  relativeTime: {
    future: 'in %s',
    past: '%s ago',
    s: 'seconds'
  }
})

// Day.js (simpler)
dayjs.locale('custom', {
  weekdays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
  relativeTime: {
    future: 'in %s',
    past: '%s ago',
    s: 'seconds'
  }
})
```

## Common Migration Issues

### Issue 1: Method Not Found

**Error:** `dayjs().utc is not a function`

**Solution:** Load the plugin first:

```javascript
import utc from 'dayjs/plugin/utc'
dayjs.extend(utc)
// Now .utc() works
```

### Issue 2: Custom Format Not Parsing

**Error:** `'01/15/2024'` parses as year 1, month 15

**Solution:** Load customParseFormat plugin:

```javascript
import customParseFormat from 'dayjs/plugin/customParseFormat'
dayjs.extend(customParseFormat)

dayjs('01/15/2024', 'MM/DD/YYYY') // Now works correctly
```

### Issue 3: Relative Time Shows Numbers

**Error:** `.fromNow()` returns `'2062486 minutes'` instead of `'3 months ago'`

**Solution:** Load relativeTime plugin:

```javascript
import relativeTime from 'dayjs/plugin/relativeTime'
dayjs.extend(relativeTime)

dayjs('2024-01-01').fromNow() // '3 months ago'
```

### Issue 4: Mutation Expected but Not Happening

**Error:** `date.year(2030)` doesn't change original date

**Solution:** This is by design. Day.js is immutable:

```javascript
// ❌ Won't work as expected
const date = dayjs('2024-01-15')
date.year(2030)
console.log(date.format('YYYY')) // '2024' (unchanged)

// ✅ Correct pattern
const date = dayjs('2024-01-15')
const updated = date.year(2030)
console.log(updated.format('YYYY')) // '2030'
```

### Issue 5: Timezone Not Working

**Error:** `.tz()` method not found

**Solution:** Load timezone plugin:

```javascript
import timezone from 'dayjs/plugin/timezone'
dayjs.extend(timezone)

dayjs.tz('2024-01-15', 'America/New_York') // Now works
```

## Bundle Size Comparison

### Moment.js
```
moment.js: ~68KB (minified)
moment-timezone: ~157KB (with timezone data)
All locales: ~29KB (but all included by default)
Total with timezone: ~225KB
```

### Day.js
```
dayjs core: ~2KB
+ utc plugin: ~0.3KB
+ timezone plugin: ~1KB
+ relativeTime plugin: ~0.7KB
+ 1 locale (e.g., Spanish): ~2KB
Total: ~6KB (97% smaller than Moment.js)
```

## Step-by-Step Migration Plan

### Phase 1: Setup

1. Install Day.js:
```bash
npm uninstall moment moment-timezone
npm install dayjs
```

2. Create a migration utility file:

```javascript
// dayjs-config.js
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
import relativeTime from 'dayjs/plugin/relativeTime'
import customParseFormat from 'dayjs/plugin/customParseFormat'
import duration from 'dayjs/plugin/duration'
import calendar from 'dayjs/plugin/calendar'

// Extend with all needed plugins
dayjs.extend(utc)
dayjs.extend(timezone)
dayjs.extend(relativeTime)
dayjs.extend(customParseFormat)
dayjs.extend(duration)
dayjs.extend(calendar)

export default dayjs
```

### Phase 2: Gradual Replacement

1. Replace imports in one file at a time:
```javascript
// Before
import moment from 'moment'

// After
import dayjs from './dayjs-config'
```

2. Update method calls (most work identically)

3. Test thoroughly

### Phase 3: Optimization

1. Remove unused plugins to reduce bundle size
2. Load locales on-demand instead of all at once
3. Tree-shake unused features

## Advanced Migration Patterns

### Creating a Moment-like Wrapper

If you need to minimize changes, create a wrapper:

```javascript
// moment-compatible.js
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
import relativeTime from 'dayjs/plugin/relativeTime'
import customParseFormat from 'dayjs/plugin/customParseFormat'
import duration from 'dayjs/plugin/duration'

// Load all plugins upfront
dayjs.extend(utc)
dayjs.extend(timezone)
dayjs.extend(relativeTime)
dayjs.extend(customParseFormat)
dayjs.extend(duration)

// Create moment-like interface
const moment = {
  ...dayjs,
  
  // Moment.js has moment() as default export AND named functions
  utc: dayjs.utc,
  duration: dayjs.duration,
  tz: dayjs.tz,
  
  // Add any other Moment.js static methods you need
}

export default moment
```

Then use it exactly like Moment.js:

```javascript
import moment from './moment-compatible'

moment('2024-01-15').format() // Works
moment.utc('2024-01-15')      // Works
moment.duration(1, 'day')     // Works
```

### Handling Missing Features

For Moment.js features not in Day.js:

**Option 1: Polyfill with native Date:**

```javascript
// If you need a feature Day.js doesn't have
const getWeekNumber = (date) => {
  const d = new Date(date.getTime())
  d.setHours(0, 0, 0, 0)
  d.setDate(d.getDate() + 4 - (d.getDay() || 7))
  return Math.ceil((((d - new Date(d.getFullYear(), 0, 1)) / 86400000) + 1) / 7)
}
```

**Option 2: Use a helper library:**

```javascript
// For complex operations not in Day.js
import { format } from 'date-fns' // Or other library

const result = format(dayjs().toDate(), 'cccc, MMMM dd, yyyy')
```

## Performance Comparison

| Operation | Moment.js | Day.js | Improvement |
|-----------|-----------|--------|-------------|
| Parse ISO string | 10μs | 2μs | 5x faster |
| Format date | 8μs | 1.5μs | 5x faster |
| Add time | 5μs | 1μs | 5x faster |
| Bundle size | 225KB | 6KB | 97% smaller |

## Testing Your Migration

### Unit Tests

Ensure your tests still pass after migration:

```javascript
// Example test
import dayjs from './dayjs-config'

test('formats date correctly', () => {
  const date = dayjs('2024-01-15')
  expect(date.format('YYYY-MM-DD')).toBe('2024-01-15')
})

test('handles UTC correctly', () => {
  const utcDate = dayjs.utc('2024-01-15T14:30:00Z')
  expect(utcDate.isUTC()).toBe(true)
})

test('relative time works', () => {
  const past = dayjs().subtract(1, 'day')
  expect(past.fromNow()).toContain('ago')
})
```

### Visual Regression Tests

For UI components displaying dates:

```javascript
// Test that date displays look the same
test('date display matches expected format', () => {
  const rendered = render(<DateDisplay value="2024-01-15" />)
  expect(rendered.container.textContent).toContain('January 15, 2024')
})
```

## Summary Checklist

- [ ] Install Day.js and remove Moment.js
- [ ] Load required plugins (utc, timezone, relativeTime, etc.)
- [ ] Update imports throughout codebase
- [ ] Replace `moment` with `dayjs` in method calls
- [ ] Handle custom format parsing (add customParseFormat plugin)
- [ ] Migrate locale loading pattern
- [ ] Update any mutation patterns to immutable style
- [ ] Test all date-related functionality
- [ ] Optimize bundle size by removing unused plugins
- [ ] Document any remaining differences for team

## Resources

- [Day.js Documentation](https://day.js.org/)
- [Day.js GitHub](https://github.com/iamkun/dayjs)
- [Moment.js to Day.js Comparison](https://github.com/iamkun/dayjs/tree/master/doc/moment-comparison.md)
- [Plugin List](./02-plugins.md)
