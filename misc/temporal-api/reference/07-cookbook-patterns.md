# Cookbook Patterns

## Contents
- Legacy Date Interoperability
- Sorting Temporal Values
- Rounding Dates and Times
- Timezone Conversion Patterns
- Flight and Travel Calculations
- Recurring Events and Scheduling
- Business Hours
- Weekday Calculations

## Legacy Date Interoperability

### Date to Instant

```javascript
const legacy = new Date('2024-01-15T10:30:00Z');
const instant = legacy.toTemporalInstant();
instant.epochMilliseconds === legacy.getTime(); // true
```

### Date to ZonedDateTime

```javascript
// Via Instant, choosing an explicit timezone
const zoned = legacy
  .toTemporalInstant()
  .toZonedDateTimeISO('America/New_York');

// Using system timezone (browser only — unreliable on servers)
const zonedLocal = legacy.toTemporalInstant()
  .toZonedDateTimeISO(Temporal.Now.timeZoneId());
```

### Date to PlainDate

```javascript
// Date constructed with local timezone → PlainDate
const date = new Date(2024, 0, 1); // Jan 1, 2024 in local timezone
const plainDate = date
  .toTemporalInstant()
  .toZonedDateTimeISO(Temporal.Now.timeZoneId())
  .toPlainDate();

// Date constructed with UTC → PlainDate
const utcDate = new Date(Date.UTC(2024, 0, 1));
const plainUtc = utcDate
  .toTemporalInstant()
  .toZonedDateTimeISO('UTC')
  .toPlainDate();
```

### Instant/ZonedDateTime to Date

```javascript
const instant = Temporal.Instant.from('2024-01-15T10:30:00.000999Z');

// Direct conversion (truncates sub-millisecond precision)
const date = new Date(instant.epochMilliseconds);

// With rounding for millisecond precision
const dateRounded = new Date(
  instant.round({ smallestUnit: 'millisecond' }).epochMilliseconds
);
```

## Sorting Temporal Values

### Sort PlainDateTime values

```javascript
const events = [
  Temporal.PlainDateTime.from('2024-02-21T13:10'),
  Temporal.PlainDateTime.from('2024-02-20T08:45'),
  Temporal.PlainDateTime.from('2024-02-20T15:30'),
];

events.sort(Temporal.PlainDateTime.compare);
// [2024-02-20T08:45, 2024-02-20T15:30, 2024-02-21T13:10]
```

### Sort ISO date/time strings by exact time

```javascript
function sortInstantStrings(strings) {
  return strings
    .map(v => [v, Temporal.Instant.from(v)])
    .sort(([, i1], [, i2]) => Temporal.Instant.compare(i1, i2))
    .map(([str]) => str);
}

sortInstantStrings([
  '2024-04-01T11:02:00+02:00[Europe/Berlin]',
  '2024-04-01T10:00:00+01:00[Europe/London]',
  '2024-04-01T05:01:00-04:00[America/New_York]',
]);
// Correct chronological order regardless of offset
```

## Rounding Dates and Times

### Round time to whole hours

```javascript
const time = Temporal.PlainTime.from('12:38:28.138');
time.round({ smallestUnit: 'hour', roundingMode: 'floor' }); // '12:00:00'
```

### Round date to nearest month start

PlainDate has no `round()` method. Compute manually:

```javascript
const date = Temporal.PlainDate.from('2024-09-16');

const firstOfCurrent = date.with({ day: 1 });
const firstOfNext = firstOfCurrent.add({ months: 1 });

const sinceCurrent = date.since(firstOfCurrent);
const untilNext = date.until(firstOfNext);

const nearestMonth = Temporal.Duration.compare(sinceCurrent, untilNext) >= 0
  ? firstOfNext
  : firstOfCurrent;
nearestMonth.toString(); // '2024-10-01'
```

### Push date to next month start

```javascript
function roundToNextMonthStart(date, delayDays) {
  return date
    .add({ days: delayDays })
    .add({ months: 1 })  // constrains to end of month if needed
    .with({ day: 1 });
}

roundToNextMonthStart(Temporal.PlainDate.from('2024-06-01'), 15);
// '2024-07-01'
```

## Timezone Conversion Patterns

### Preserving exact time (change timezone display)

```javascript
const source = Temporal.ZonedDateTime.from('2024-01-15T00:00:00-06:00[America/Chicago]');
const inLA = source.withTimeZone('America/Los_Angeles');
inLA.toString(); // '2024-01-14T22:00:00-08:00[America/Los_Angeles]'
```

### Preserving wall-clock time (map to instant in target timezone)

```javascript
const dt = Temporal.PlainDateTime.from('2024-03-10T10:00');
const instant = dt.toZonedDateTime('America/New_York', { disambiguation: 'compatible' })
  .toInstant();
```

### Converting future events across timezones

For future events, store as `PlainDateTime` + timezone (not as exact time), because DST rules may change:

```javascript
const meetings = [
  { dateTime: '2024-01-28T10:00', timeZone: 'America/Phoenix' },
  { dateTime: '2024-03-26T10:00', timeZone: 'America/New_York' },
];

const localTimes = meetings.map(({ dateTime, timeZone }) =>
  Temporal.PlainDateTime.from(dateTime)
    .toZonedDateTime(timeZone, { disambiguation: 'reject' })
    .withTimeZone('Asia/Tokyo')
    .toPlainDateTime()
);
```

### Daily occurrence at fixed local time

```javascript
function* dailyOccurrence(startDate, plainTime, timeZone) {
  for (let date = startDate; ; date = date.add({ days: 1 })) {
    yield date.toZonedDateTime({ plainTime, timeZone }).toInstant();
  }
}

// Daily at 8 AM California time
const iter = dailyOccurrence(
  Temporal.PlainDate.from('2024-03-10'),
  Temporal.PlainTime.from('08:00'),
  'America/Los_Angeles'
);
```

## Flight and Travel Calculations

### Flight duration

```javascript
const departure = Temporal.ZonedDateTime.from('2024-03-08T11:55:00+08:00[Asia/Hong_Kong]');
const arrival = Temporal.ZonedDateTime.from('2024-03-08T09:50:00-07:00[America/Los_Angeles]');

const flightTime = departure.until(arrival);
flightTime.toString(); // 'PT12H55M'
```

### Arrival from departure + duration

```javascript
const departure = Temporal.ZonedDateTime.from('2024-03-08T11:55:00+08:00[Asia/Hong_Kong]');
const flightTime = Temporal.Duration.from({ minutes: 775 });

const arrival = departure.add(flightTime).withTimeZone('America/Los_Angeles');
arrival.toString(); // '2024-03-08T09:50:00-07:00[America/Los_Angeles]'
```

## Recurring Events and Scheduling

### Next weekly occurrence

```javascript
function nextWeeklyOccurrence(now, weekday, eventTime, eventTimeZone) {
  const nowInEventTz = now.withTimeZone(eventTimeZone);
  const nextDate = nowInEventTz.toPlainDate().add({
    days: (weekday + 7 - nowInEventTz.dayOfWeek) % 7
  });
  let nextOccurrence = nextDate.toZonedDateTime({ plainTime: eventTime, timeZone: eventTimeZone });

  // If event already passed today, skip to next week
  if (Temporal.ZonedDateTime.compare(now, nextOccurrence) > 0) {
    nextOccurrence = nextOccurrence.add({ weeks: 1 });
  }

  return nextOccurrence.withTimeZone(now.timeZoneId);
}

// Weekly Thursdays at 08:45 California time
nextWeeklyOccurrence(
  Temporal.ZonedDateTime.from('2024-03-26T15:30:00+00:00[Europe/London]'),
  4, // Thursday
  Temporal.PlainTime.from('08:45'),
  'America/Los_Angeles'
);
```

### Nth weekday of month

```javascript
// First Tuesday of a month
function firstTuesday(yearMonth) {
  const first = yearMonth.toPlainDate({ day: 1 });
  return first.add({ days: (7 + 2 - first.dayOfWeek) % 7 });
}

firstTuesday(Temporal.PlainYearMonth.from('2024-06'));
// '2024-06-04'
```

### All occurrences of a weekday in a month

```javascript
function weeklyDaysInMonth(yearMonth, dayOfWeek) {
  const first = yearMonth.toPlainDate({ day: 1 });
  let next = first.add({ days: (7 + dayOfWeek - first.dayOfWeek) % 7 });
  const result = [];
  while (next.month === yearMonth.month) {
    result.push(next);
    next = next.add({ days: 7 });
  }
  return result;
}

// All Mondays in February 2024
weeklyDaysInMonth(Temporal.PlainYearMonth.from('2024-02'), 1);
// ['2024-02-05', '2024-02-12', '2024-02-19', '2024-02-26']
```

### Bridge holidays (long weekends)

```javascript
function bridgePublicHolidays(holiday, year) {
  const date = holiday.toPlainDate({ year });
  switch (date.dayOfWeek) {
    case 1: case 3: case 5: return [date];         // Mon/Wed/Fri — single day
    case 2: return [date.subtract({ days: 1 }), date]; // Tue — take Mon off
    case 4: return [date, date.add({ days: 1 })];   // Thu — take Fri off
    case 6: case 7: return [];                       // Weekend — no work day
  }
}

bridgePublicHolidays(Temporal.PlainMonthDay.from('05-01'), 2024);
// ['2024-05-01'] (Wednesday, no bridge)

bridgePublicHolidays(Temporal.PlainMonthDay.from('05-01'), 2023);
// ['2023-04-30', '2023-05-01'] (Tuesday, bridge Monday)
```

## Business Hours

### Check if business is open at a given time

```javascript
function getBusinessState(now, businessHours, soonWindow) {
  const compare = Temporal.ZonedDateTime.compare;

  for (const delta of [-1, 0]) {
    const openDate = now.toPlainDate().add({ days: delta });
    const index = (openDate.dayOfWeek + 7) % 7; // 0-based
    if (!businessHours[index]) continue;

    const { open: openTime, close: closeTime } = businessHours[index];
    const open = openDate.toZonedDateTime({ plainTime: openTime, timeZone: now.timeZoneId });
    const isWrap = Temporal.PlainTime.compare(closeTime, openTime) < 0;
    const closeDate = isWrap ? openDate.add({ days: 1 }) : openDate;
    const close = closeDate.toZonedDateTime({ plainTime: closeTime, timeZone: now.timeZoneId });

    if (compare(now, open) >= 0 && compare(now, close) < 0) {
      return compare(now, close.subtract(soonWindow)) >= 0 ? 'closing soon' : 'open';
    }
    if (compare(now.add(soonWindow), open) >= 0 && compare(now.add(soonWindow), close) < 0) {
      return 'opening soon';
    }
  }
  return 'closed';
}

// Saturday night at a bar (closes at 2 AM Sunday)
const businessHours = [
  null, // Sun — closed all day (handled by wrap from Sat)
  null, // Mon
  { open: Temporal.PlainTime.from('11:00'), close: Temporal.PlainTime.from('20:30') }, // Tue
  { open: Temporal.PlainTime.from('11:00'), close: Temporal.PlainTime.from('20:30') }, // Wed
  { open: Temporal.PlainTime.from('11:00'), close: Temporal.PlainTime.from('22:00') }, // Thu
  { open: Temporal.PlainTime.from('11:00'), close: Temporal.PlainTime.from('00:00') }, // Fri
  { open: Temporal.PlainTime.from('11:00'), close: Temporal.PlainTime.from('02:00') }, // Sat
];

getBusinessState(
  Temporal.ZonedDateTime.from('2024-04-07T00:00:00+02:00[Europe/Berlin]'), // Saturday midnight
  businessHours,
  Temporal.Duration.from({ minutes: 30 })
); // 'open'
```

## Countdown and Record Tracking

### Countdown to an event

```javascript
const target = Temporal.Instant.from('2024-06-15T13:00:00-07:00[America/Los_Angeles]');
const duration = Temporal.Now.instant().until(target);

`${duration.toLocaleString()} ${duration.sign < 0 ? 'since' : 'until'} the event`;
```

### Alert before breaking a record

```javascript
function instantBeforeRecord(start, record, noticeWindow) {
  return start.add(record).subtract(noticeWindow);
}

const raceStart = Temporal.Instant.from('2024-08-13T21:27:00-03:00[America/Sao_Paulo]');
const record = Temporal.Duration.from({ minutes: 26, seconds: 17, milliseconds: 530 });
const notice = Temporal.Duration.from({ minutes: 1 });

instantBeforeRecord(raceStart, record, notice);
// Instant when to send "1 minute left to break the record!" notification
```

## Manipulating Day of Month

```javascript
const date = Temporal.PlainDate.from('2024-04-14');

// Third day of next month
date.add({ months: 1 }).with({ day: 3 }); // '2024-05-03'

// Last day of current month
date.with({ day: date.daysInMonth }); // '2024-04-30'

// Same day in different month (constrain to valid day)
date.with({ month: 2 }); // '2024-02-14'

// Reject if invalid
try {
  Temporal.PlainDate.from('2024-05-31').with({ month: 4 }, { overflow: 'reject' });
} catch (e) { /* April has no 31st */ }
```
