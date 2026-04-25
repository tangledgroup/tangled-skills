---
name: dayjs-1-11
description: Complete toolkit for date and time manipulation using Day.js 1.11, a minimalist 2kB library with Moment.js-compatible API. Use when parsing, validating, manipulating, and displaying dates in JavaScript applications requiring immutable operations, i18n support, and plugin extensibility.
version: "0.2.0"
author: Tangled <noreply@tangledgroup.com>
license: MIT
tags:
  - date
  - time
  - parsing
  - formatting
  - manipulation
  - i18n
  - plugins
  - immutable
category: utilities

external_references:
  - https://day.js.org/
  - https://github.com/iamkun/dayjs
---
## Overview
Complete toolkit for date and time manipulation using Day.js 1.11, a minimalist 2kB library with Moment.js-compatible API. Use when parsing, validating, manipulating, and displaying dates in JavaScript applications requiring immutable operations, i18n support, and plugin extensibility.

Day.js is a minimalist JavaScript library (~2KB) that parses, validates, manipulates, and displays dates and times for modern browsers with a largely Moment.js-compatible API. It provides immutable operations, chainable methods, internationalization support, and an extensive plugin ecosystem.

## When to Use
- Parsing date strings into manipulatable objects
- Formatting dates for display in various locales
- Adding/subtracting time periods (days, months, years)
- Comparing dates (isBefore, isAfter, isSame)
- Getting specific date components (year, month, day, hour)
- Working with UTC and timezone-aware dates
- Generating human-readable relative time strings
- Handling international date formats and locales
- Needing a lightweight alternative to Moment.js

## Core Concepts
This skill covers the key concepts and fundamental ideas related to this topic.

## Installation / Setup
### Installation

```bash
npm install dayjs
```

### Basic Usage

```javascript
import dayjs from 'dayjs'

// Parse
dayjs('2024-01-15') // Parse ISO string
dayjs(new Date())   // From native Date
dayjs(1705312800000) // From timestamp

// Format
dayjs().format('YYYY-MM-DD HH:mm:ss') // '2024-01-15 14:30:00'

// Manipulate
dayjs().add(7, 'day').subtract(1, 'month')

// Query
dayjs().isBefore(dayjs('2025-01-01')) // true
```

See [Core API Reference](reference/01-core-api.md) for complete method documentation.

## Plugin System
Day.js extends functionality through plugins. Import and extend as needed:

```javascript
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import relativeTime from 'dayjs/plugin/relativeTime'

// Extend dayjs with plugins
dayjs.extend(utc)
dayjs.extend(relativeTime)

// Use new methods
dayjs().utc() // UTC instance
dayjs('2024-01-01').fromNow() // '3 months ago'
```

### Available Plugins (37 total)

**Core Functionality:**
- `advancedFormat` - Additional format tokens (Q, Do, k, kk, X, x)
- `arraySupport` - Accept arrays as input for parsing
- `customParseFormat` - Parse dates with custom format strings
- `duration` - Create and manipulate time durations
- `objectSupport` - Accept objects for date creation
- `preParsePostFormat` - Hook into parse/format lifecycle

**Time Operations:**
- `utc` - UTC instance creation and manipulation
- `timezone` - Timezone support with TZ database
- `weekOfYear` - Get/set week of year (local)
- `isoWeek` - ISO 8601 week calculations
- `dayOfYear` - Day number within the year
- `quarterOfYear` - Quarter calculations

**Comparison & Query:**
- `isBetween` - Check if date is between two others
- `isSameOrAfter` - Inclusive "after or equal" check
- `isSameOrBefore` - Inclusive "before or equal" check
- `isToday` / `isTomorrow` / `isYesterday` - Relative day checks
- `minMax` - Find minimum/maximum dates

**Display & Localization:**
- `relativeTime` - Human-readable relative time ("2 hours ago")
- `calendar` - Calendar-style formatting ("Today at 3pm")
- `localizedFormat` - Locale-specific format tokens (L, l, LLL)
- `updateLocale` - Modify locale configurations
- `localeData` - Access locale configuration data

**Utility:**
- `clone` - Create explicit clones (already built-in)
- `format` - Extended formatting options
- `toDate` / `toObject` / `toArray` - Convert to different types
- `badMutable` - Allow mutable operations (breaks immutability)
- `devHelper` - Development warnings for common mistakes

**Localization:**
- `buddhistEra` - Buddhist calendar era support
- `bigIntSupport` - BigInt timestamp support
- `pluralGetSet` - Plural unit names in get/set
- `isMoment` - Check if object is Moment.js instance
- `isLeapYear` - Leap year detection

See [Plugin Reference](reference/02-plugins.md) for detailed documentation of all 37 plugins.

## Internationalization
Day.js supports 80+ locales out of the box:

```javascript
import 'dayjs/locale/es' // Load Spanish locale
import 'dayjs/locale/zh-cn' // Load Chinese Simplified

// Set global locale
dayjs.locale('es')

// Use locale per instance
dayjs().locale('zh-cn').format()

// Get current locale
dayjs.locale() // 'en'
```

See [Internationalization Guide](reference/03-i18n.md) for locale configuration and custom locale creation.

## Advanced Topics
## Advanced Topics

- [Core Api](reference/01-core-api.md)
- [Plugins](reference/02-plugins.md)
- [I18N](reference/03-i18n.md)
- [Type Definitions](reference/04-type-definitions.md)
- [Migration Guide](reference/05-migration-guide.md)

## Common Patterns
### Immutable Operations

All operations return new instances:

```javascript
const now = dayjs()
const tomorrow = now.add(1, 'day') // New instance
console.log(now.isSame(tomorrow))  // false - original unchanged
```

### Chaining

Methods can be chained for fluent syntax:

```javascript
const result = dayjs('2024-01-01')
  .add(1, 'year')
  .startOf('month')
  .format('YYYY-MM-DD') // '2025-01-01'
```

### Validation

Always validate parsed dates:

```javascript
const date = dayjs('invalid-date')
if (!date.isValid()) {
  console.error('Invalid date provided')
}
```

## Troubleshooting
**Plugin methods not available:** Ensure plugins are extended before use:
```javascript
dayjs.extend(utc) // Must call this first
dayjs().utc()     // Now .utc() is available
```

**Locale not working:** Load locale before setting it:
```javascript
import 'dayjs/locale/fr' // Import first
dayjs.locale('fr')       // Then set
```

**Custom format parsing:** Requires customParseFormat plugin:
```javascript
import customParseFormat from 'dayjs/plugin/customParseFormat'
dayjs.extend(customParseFormat)
dayjs('01/15/2024', 'MM/DD/YYYY') // Now works
```

See [Plugin Reference](reference/02-plugins.md) for plugin-specific issues and [Migration Guide](reference/05-migration-guide.md) for Moment.js compatibility notes.

