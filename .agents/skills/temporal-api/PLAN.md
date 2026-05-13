# ☑ Plan: Create temporal-api skill

**Depends On:** NONE
**Created:** 2026-05-13T00:00:00Z
**Updated:** 2026-05-13T00:00:00Z
**Current Phase:** ☑ Phase 4
**Current Task:** ☑ Task 4.4

## ☑ Phase 1 Content Analysis & Structure Design

- ☑ Task 1.1 Analyze all fetched sources (MDN overview, TC39 intro, cookbook, individual API docs) and identify distinct reference domains
  - Group content into: core classes (Instant/ZonedDateTime/Plain*), Temporal.Now, Duration/balancing, time zones & calendars, string parsing/formatting, Date interoperability, cookbook recipes
- ☑ Task 1.2 Decide simple vs complex structure and define the reference file breakdown
  - This is a complex skill (8+ distinct domains). Plan: SKILL.md as hub + 6-7 reference files

## ☑ Phase 2 Write SKILL.md (Hub)

- ☑ Task 2.1 Write YAML header with validated name `temporal-api`, description, tags, version `0.1.0`
- ☑ Task 2.2 Write Overview section covering what Temporal is and why it replaces Date
- ☑ Task 2.3 Write When to Use section with specific trigger scenarios
- ☑ Task 2.4 Write Core Concepts section covering the class hierarchy (Instant → ZonedDateTime → Plain* types, Duration)
- ☑ Task 2.5 Write Quick Start section with essential patterns (getting current time, constructing objects, basic arithmetic)
- ☑ Task 2.6 Write Advanced Topics section linking to all reference files

## ☑ Phase 3 Write Reference Files

- ☑ Task 3.1 Write `reference/01-temporal-now-and-instant.md` — Temporal.Now methods, Instant construction/properties/arithmetic
  (depends on: Task 1.2)
- ☑ Task 3.2 Write `reference/02-zoneddatetime.md` — ZonedDateTime properties, time zone methods, DST handling, transitions
  (depends on: Task 1.2)
- ☑ Task 3.3 Write `reference/03-plain-types.md` — PlainDate, PlainTime, PlainDateTime, PlainYearMonth, PlainMonthDay with shared patterns
  (depends on: Task 1.2)
- ☑ Task 3.4 Write `reference/04-duration-and-balancing.md` — Duration construction, arithmetic, balancing modes, total(), rounding
  (depends on: Task 1.2)
- ☑ Task 3.5 Write `reference/05-timezones-and-calendars.md` — IANA time zones, calendar systems, era/eraYear, monthCode, week properties
  (depends on: Task 1.2)
- ☑ Task 3.6 Write `reference/06-string-formatting.md` — RFC 9557 format, toString/toLocaleString/toJSON, parsing patterns, FAQ highlights
  (depends on: Task 1.2)
- ☑ Task 3.7 Write `reference/07-cookbook-patterns.md` — Curated cookbook recipes: Date interop, sorting, rounding, timezone conversion, business hours, flight times, recurring events
  (depends on: Task 1.2)

## ☑ Phase 4 Validate & Finalize

- ☑ Task 4.1 Run structural validator against the skill directory
  (depends on: Task 3.7)
- ☑ Task 4.2 Perform LLM judgment checks: content accuracy, no hallucination, consistent terminology, concise writing
  (depends on: Task 4.1)
- ☑ Task 4.3 Fix any issues found by validator or review
  (depends on: Task 4.2)
- ☑ Task 4.4 Regenerate README.md skills table
  (depends on: Task 4.3)
