# Day.js TypeScript Definitions

Complete TypeScript type definitions for Day.js core API and all plugins.

## Core Types

### Main Export

```typescript
import dayjs from 'dayjs'

// Returns Dayjs instance
const now: dayjs.Dayjs = dayjs()
const parsed: dayjs.Dayjs = dayjs('2024-01-15')
```

### ConfigType

Input types for creating Day.js instances:

```typescript
type ConfigType = string | number | Date | Dayjs | null | undefined

dayjs('2024-01-15')      // string
dayjs(1705276800000)     // number (timestamp)
dayjs(new Date())        // Date
dayjs(dayjs('2024-01-15')) // Dayjs (clones)
dayjs(null)              // null (treated as now)
```

### Unit Types

```typescript
// Short unit names
type UnitTypeShort = 'd' | 'D' | 'M' | 'y' | 'h' | 'm' | 's' | 'ms'

// Long unit names
type UnitTypeLong = 'millisecond' | 'second' | 'minute' | 'hour' | 'day' | 'month' | 'year' | 'date'

// Plural forms
type UnitTypeLongPlural = 'milliseconds' | 'seconds' | 'minutes' | 'hours' | 'days' | 'months' | 'years' | 'dates'

// Combined type (all supported)
type UnitType = UnitTypeLong | UnitTypeLongPlural | UnitTypeShort

// For manipulation (add/subtract)
type ManipulateType = Exclude<OpUnitType, 'date' | 'dates'>

// For operations (startOf/endOf)
type OpUnitType = UnitType | "week" | "weeks" | 'w'

// For quarters
type QUnitType = UnitType | "quarter" | "quarters" | 'Q'
```

### Dayjs Interface

Complete type definition for Day.js instances:

```typescript
interface Dayjs {
  // Parsing
  clone(): Dayjs
  isValid(): boolean
  
  // Getters/Setters (year)
  year(): number
  year(value: number): Dayjs
  
  // Getters/Setters (month - zero-indexed)
  month(): number
  month(value: number): Dayjs
  
  // Getters/Setters (date)
  date(): number
  date(value: number): Dayjs
  
  // Getters/Setters (day of week - 0=Sunday, 6=Saturday)
  day(): 0 | 1 | 2 | 3 | 4 | 5 | 6
  day(value: number): Dayjs
  
  // Getters/Setters (hour)
  hour(): number
  hour(value: number): Dayjs
  
  // Getters/Setters (minute)
  minute(): number
  minute(value: number): Dayjs
  
  // Getters/Setters (second)
  second(): number
  second(value: number): Dayjs
  
  // Getters/Setters (millisecond)
  millisecond(): number
  millisecond(value: number): Dayjs
  
  // Generic getter/setter
  set(unit: UnitType, value: number): Dayjs
  get(unit: UnitType): number
  
  // Manipulation
  add(value: number, unit?: ManipulateType): Dayjs
  subtract(value: number, unit?: ManipulateType): Dayjs
  startOf(unit: OpUnitType): Dayjs
  endOf(unit: OpUnitType): Dayjs
  
  // Display
  format(template?: string): string
  diff(date?: ConfigType, unit?: QUnitType | OpUnitType, float?: boolean): number
  valueOf(): number
  unix(): number
  daysInMonth(): number
  toDate(): Date
  toJSON(): string
  toISOString(): string
  toString(): string
  utcOffset(): number
  
  // Query
  isBefore(date?: ConfigType, unit?: OpUnitType): boolean
  isSame(date?: ConfigType, unit?: OpUnitType): boolean
  isAfter(date?: ConfigType, unit?: OpUnitType): boolean
  
  // Locale
  locale(): string
  locale(preset: string | ILocale, object?: Partial<ILocale>): Dayjs
}
```

### ILocale Interface

Type definition for locale configuration:

```typescript
interface ILocale {
  name: string
  weekdays?: string[]
  weekdaysShort?: string[]
  weekdaysMin?: string[]
  months?: string[]
  monthsShort?: string[]
  weekStart?: number
  relativeTime?: {
    future?: string
    past?: string
    s?: string
    m?: string
    mm?: string
    h?: string
    hh?: string
    d?: string
    dd?: string
    M?: string
    MM?: string
    y?: string
    yy?: string
  }
  formats?: {
    LT?: string
    LTS?: string
    L?: string
    LL?: string
    LLL?: string
    LLLL?: string
  }
  invalidDate?: string
  ordinal?: (n: number) => string
  meridiem?: (hour: number, minute: number, isLower: boolean) => string
}
```

## Static Methods

### dayjs.extend()

Add plugins with optional configuration:

```typescript
type PluginFunc<T = unknown> = (option: T, c: typeof Dayjs, d: typeof dayjs) => void

function extend<T = unknown>(plugin: PluginFunc<T>, option?: T): Dayjs

// Usage
import utc from 'dayjs/plugin/utc'
dayjs.extend(utc)

import relativeTime from 'dayjs/plugin/relativeTime'
dayjs.extend(relativeTime, {
  thresholds: [['s', 30], ['e', 45]]
})
```

### dayjs.locale()

Get or set global locale:

```typescript
function locale(): string
function locale(preset?: string | ILocale, object?: Partial<ILocale>, isLocal?: boolean): string

// Get current locale
const current: string = dayjs.locale()

// Set locale
dayjs.locale('es')

// Custom locale
dayjs.locale('custom', {
  weekdays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
})
```

### Utility Functions

```typescript
function isDayjs(d: any): d is Dayjs
function unix(t: number): Dayjs

// Usage
dayjs.isDayjs(dayjs()) // true
dayjs.unix(1705276800) // Dayjs instance
```

## Plugin Type Definitions

### UTC Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    utc(keepLocalTime?: boolean): Dayjs
    local(): Dayjs
    isUTC(): boolean
    utcOffset(offset: number | string, keepLocalTime?: boolean): Dayjs
  }
  
  export function utc(config?: ConfigType, format?: string, strict?: boolean): Dayjs
}

// Usage
const utcDate: Dayjs = dayjs.utc('2024-01-15')
const isUtc: boolean = utcDate.isUTC()
const local: Dayjs = utcDate.local()
```

### Duration Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    add(duration: Duration): Dayjs
    subtract(duration: Duration): Dayjs
  }
  
  interface DurationUnitsObjectType {
    milliseconds?: number
    seconds?: number
    minutes?: number
    hours?: number
    days?: number
    weeks?: number
    months?: number
    years?: number
  }
  
  type DurationUnitType = 'millisecond' | 'milliseconds' | 'second' | 'seconds' | 
                         'minute' | 'minutes' | 'hour' | 'hours' | 'day' | 'days' | 
                         'week' | 'weeks' | 'month' | 'months' | 'year' | 'years'
  
  interface Duration {
    clone(): Duration
    humanize(withSuffix?: boolean): string
    
    // Getters (rounded)
    milliseconds(): number
    seconds(): number
    minutes(): number
    hours(): number
    days(): number
    weeks(): number
    months(): number
    years(): number
    
    // As getters (with decimals)
    asMilliseconds(): number
    asSeconds(): number
    asMinutes(): number
    asHours(): number
    asDays(): number
    asWeeks(): number
    asMonths(): number
    asYears(): number
    as(unit: DurationUnitType): number
    
    // Generic getter
    get(unit: DurationUnitType): number
    
    // Manipulation
    add(time: number, unit?: DurationUnitType): Duration
    add(duration: Duration): Duration
    subtract(time: number, unit?: DurationUnitType): Duration
    subtract(duration: Duration): Duration
    
    // Display
    toJSON(): string
    toISOString(): string
    format(formatStr?: string): string
    locale(locale: string): Duration
  }
  
  type CreateDurationType = 
    ((units: DurationUnitsObjectType) => Duration) &
    ((time: number, unit?: DurationUnitType) => Duration) &
    ((ISO_8601: string) => Duration)
  
  export const duration: CreateDurationType
  export function isDuration(d: any): d is Duration
}

// Usage
const d: Duration = dayjs.duration({ years: 1, months: 2, days: 3 })
const years: number = d.years()
const asDays: number = d.asDays()
const human: string = d.humanize(true)
```

### RelativeTime Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    fromNow(withoutSuffix?: boolean): string
    from(compared: ConfigType, withoutSuffix?: boolean): string
    toNow(withoutSuffix?: boolean): string
    to(compared: ConfigType, withoutSuffix?: boolean): string
  }
}

// Usage
const str: string = dayjs('2024-01-01').fromNow() // '3 months ago'
const noSuffix: string = dayjs('2024-01-01').fromNow(true) // '3 months'
```

### Calendar Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    calendar(referenceTime?: ConfigType, formats?: object): string
  }
}

// Usage
const cal: string = dayjs().calendar()
const customCal: string = dayjs().calendar(null, {
  lastDay: '[Yesterday at] HH:mm',
  sameDay: '[Today at] HH:mm',
  nextDay: '[Tomorrow at] HH:mm',
  lastWeek: 'dddd [at] HH:mm',
  nextWeek: 'dddd [at] HH:mm',
  sameElse: 'MM/DD/YYYY'
})
```

### IsBetween Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    isBetween(
      start: ConfigType, 
      end: ConfigType, 
      unit?: OpUnitType, 
      interval?: '()' | '[)' | '(]' | '[]'
    ): boolean
  }
}

// Usage
const between: boolean = dayjs('2024-06-15').isBetween('2024-01-01', '2024-12-31')
const inclusive: boolean = dayjs('2024-06-15').isBetween('2024-01-01', '2024-06-15', null, '[]')
```

### IsSameOrAfter / IsSameOrBefore Plugins

```typescript
declare module 'dayjs' {
  interface Dayjs {
    isSameOrAfter(date: ConfigType, unit?: OpUnitType): boolean
    isSameOrBefore(date: ConfigType, unit?: OpUnitType): boolean
  }
}
```

### IsToday / IsTomorrow / IsYesterday Plugins

```typescript
declare module 'dayjs' {
  interface Dayjs {
    isToday(): boolean
    isTomorrow(): boolean
    isYesterday(): boolean
  }
}
```

### MinMax Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    min(date?: ConfigType, ...dates: ConfigType[]): Dayjs
    max(date?: ConfigType, ...dates: ConfigType[]): Dayjs
  }
  
  export function min(...dates: ConfigType[]): Dayjs
  export function max(...dates: ConfigType[]): Dayjs
}

// Usage
const earliest: Dayjs = dayjs.min(dayjs('2024-03-01'), dayjs('2024-01-15'))
const latest: Dayjs = dayjs.max(dayjs('2024-03-01'), dayjs('2024-06-01'))
```

### WeekOfYear Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    week(): number
    week(value: number): Dayjs
  }
}
```

### ISO Week Plugins

```typescript
declare module 'dayjs' {
  interface Dayjs {
    isoWeek(): number
    isoWeek(value: number): Dayjs
    isoWeekYear(): number
    isoWeeksInYear(): number
  }
}

// Usage with startOf/endOf
dayjs('2024-01-15').startOf('isoWeek') // Monday
dayjs('2024-01-15').endOf('isoWeek')   // Sunday
```

### DayOfYear Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    dayOfYear(): number
    dayOfYear(value: number): Dayjs
  }
}
```

### QuarterOfYear Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    quarter(): number
    quarter(value: number): Dayjs
  }
}

// Usage with startOf/endOf
dayjs('2024-06-15').startOf('quarter') // April 1
dayjs('2024-06-15').endOf('quarter')   // June 30
```

### LocalizedFormat Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    format(template?: string): string // Supports L, LL, LLL, LLLL tokens
  }
}

// Usage
dayjs('2024-01-15').format('L')    // Locale-specific date
dayjs('2024-01-15').format('LL')   // Long date
dayjs('2024-01-15').format('LLL')  // Date with time
dayjs('2024-01-15').format('LLLL') // Full date with weekday
```

### LocaleData Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    localeData(): LocaleData
  }
  
  interface LocaleData {
    weekdays(): string[]
    weekdaysShort(): string[]
    weekdaysMin(): string[]
    months(): string[]
    monthsShort(): string[]
    firstDayOfWeek(): number
    firstDayOfWeek(firstDay: number): void
  }
}

// Usage
const data: LocaleData = dayjs().localeData()
const weekdays: string[] = data.weekdays()
const firstDay: number = data.firstDayOfWeek()
```

### UpdateLocale Plugin

```typescript
declare module 'dayjs' {
  export function updateLocale(locale: string, custom: Partial<ILocale>): void
}

// Usage
dayjs.updateLocale('en', {
  weekdays: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
})
```

### ToObject Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    toObject(): {
      years: number
      months: number
      date: number
      hours: number
      minutes: number
      seconds: number
      milliseconds: number
    }
  }
}

// Usage
const obj = dayjs('2024-01-15T14:30:45.123').toObject()
```

### ToArray Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    toArray(): [number, number, number, number, number, number, number]
    // Returns: [year, month, date, hour, minute, second, millisecond]
  }
}

// Usage
const arr: number[] = dayjs('2024-01-15T14:30:45.123').toArray()
```

### Timezone Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    timezone(): string
    tz(timezone?: string, keepLocalTime?: boolean): Dayjs
  }
  
  export function tz(
    date: ConfigType, 
    timezone?: string, 
    formatOrStrict?: string | boolean, 
    strict?: boolean
  ): Dayjs
}

// Usage
const nyc: Dayjs = dayjs.tz('2024-01-15T14:30:00', 'America/New_York')
const tzName: string = nyc.timezone()
```

### BuddhistEra Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    format(template?: string): string // Supports BEEE token for Buddhist year
  }
}

// Usage
dayjs('2024-01-15').format('BEEE') // '2567'
```

### IsLeapYear Plugin

```typescript
declare module 'dayjs' {
  interface Dayjs {
    isLeapYear(): boolean
  }
}
```

### IsMoment Plugin

```typescript
declare module 'dayjs' {
  export function isMoment(d: any): d is any // Returns true for Moment.js instances
}
```

## Type Guards

### Checking Instance Types

```typescript
import dayjs from 'dayjs'
import duration from 'dayjs/plugin/duration'
dayjs.extend(duration)

// Check if Day.js instance
if (dayjs.isDayjs(value)) {
  // value is Dayjs
  const year: number = value.year()
}

// Check if Duration instance
const d = dayjs.duration(1, 'day')
if (dayjs.isDuration(d)) {
  // d is Duration
  const days: number = d.days()
}
```

## Generic Plugin Definition

Create custom plugins with proper typing:

```typescript
import { PluginFunc } from 'dayjs'

interface MyPluginOptions {
  customOption?: string
}

const myPlugin: PluginFunc<MyPluginOptions> = (options, DayjsClass, dayjs) => {
  // Add method to Dayjs prototype
  DayjsClass.prototype.myCustomMethod = function() {
    return `Custom: ${options.customOption || 'default'}`
  }
  
  // Or add static method
  ;(dayjs as any).myStaticMethod = () => 'static'
}

// Extend with options
dayjs.extend(myPlugin, { customOption: 'value' })

// Use new method
dayjs().myCustomMethod() // 'Custom: value'
```

## Complete Example with All Types

```typescript
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import duration from 'dayjs/plugin/duration'
import relativeTime from 'dayjs/plugin/relativeTime'
import customParseFormat from 'dayjs/plugin/customParseFormat'

// Extend with plugins
dayjs.extend(utc)
dayjs.extend(duration)
dayjs.extend(relativeTime)
dayjs.extend(customParseFormat)

// Type-safe usage
const now: dayjs.Dayjs = dayjs()
const parsed: dayjs.Dayjs = dayjs('15/01/2024', 'DD/MM/YYYY')
const utcDate: dayjs.Dayjs = dayjs.utc('2024-01-15')

// Getters/setters
const year: number = now.year()
const withYear: dayjs.Dayjs = now.year(2030)

// Manipulation
const tomorrow: dayjs.Dayjs = now.add(1, 'day')
const lastWeek: dayjs.Dayjs = now.subtract(7, 'days')

// Duration
const d: dayjs.Duration = dayjs.duration({ years: 1, months: 2 })
const days: number = d.days()
const asHours: number = d.asHours()

// Relative time
const relative: string = parsed.fromNow() // '3 months ago'

// Type guards
if (dayjs.isDayjs(value)) {
  const isValid: boolean = value.isValid()
}

if (dayjs.isDuration(d)) {
  const human: string = d.humanize()
}
```

## Common Type Errors and Solutions

### Error: Property does not exist on type 'Dayjs'

**Cause:** Plugin not loaded or extended.

**Solution:** Extend plugin first:

```typescript
// ❌ Error - utc() doesn't exist
dayjs().utc()

// ✅ Correct
import utc from 'dayjs/plugin/utc'
dayjs.extend(utc)
dayjs().utc() // Now works
```

### Error: Argument type not assignable

**Cause:** Using wrong unit type.

**Solution:** Use correct unit types:

```typescript
// ❌ Error - 'date' not valid for add/subtract
dayjs().add(1, 'date')

// ✅ Correct
dayjs().add(1, 'day')
dayjs().add(1, 'days')
dayjs().add(1, 'd')
```

### Error: Plugin types not merging

**Cause:** TypeScript can't find plugin type definitions.

**Solution:** Ensure plugin is imported from correct path:

```typescript
// ✅ Correct import paths
import utc from 'dayjs/plugin/utc'
import duration from 'dayjs/plugin/duration'
import relativeTime from 'dayjs/plugin/relativeTime'
```

## Declaration Files Structure

Day.js provides type definitions in:

- `index.d.ts` - Core types and Dayjs interface
- `locale/index.d.ts` - Locale types (ILocale)
- `plugin/*.d.ts` - Individual plugin types

All types are automatically included when installing `dayjs` via npm.
