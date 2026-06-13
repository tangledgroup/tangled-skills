# Gantt Diagram

## Contents
- Syntax and Task Format
- Date Formats
- Exclusions
- Task Tags (done, active, crit, milestone)
- Dependencies (after, until)
- Compact Mode
- Today Marker
- Styling
- Configuration

## Overview

Gantt charts visualize project schedules with tasks as horizontal bars along a timeline.

```mermaid
gantt
    title Project Schedule
    dateFormat YYYY-MM-DD
    section Planning
        Requirements :done, req, 2024-01-01, 14d
        Design       :active, des, after req, 10d
    section Development
        Sprint 1     :s1, after des, 14d
        Sprint 2     :after s1, 14d
```

## Syntax

### Title

Optional `title` at the top of the diagram.

### Sections

Group tasks with `section <name>`:

```mermaid
gantt
    section Backend
        API Dev :a1, 2024-01-01, 20d
    section Frontend
        UI Dev  :a2, after a1, 15d
```

### Task Format

`<label> :<metadata>`

Colon separates label from metadata. Metadata items are comma-separated.

```
<tag>, <id>, <start>, <end/duration>
```

Tags and ID are optional. Order of remaining items:
1. Single item = end date or duration
2. Two items = start + end/duration
3. Three items = id + start + end/duration

### Duration Units

| Unit | Suffix | Example |
|---|---|---|
| Milliseconds | ms | 500ms |
| Seconds | s | 30s |
| Minutes | m | 30m |
| Hours | h | 4h |
| Days | d | 3d |
| Weeks | w | 2w |
| Months | M | 1M |
| Years | y | 1y |

Decimals supported: `1.5d`.

## Date Formats

Set with `dateFormat`:

```mermaid
gantt
    dateFormat YYYY-MM-DD
```

Common formats: `YYYY-MM-DD`, `DD.MM.YYYY`, `Do Y`, `MM/DD/YYYY`.

## Exclusions

Exclude dates from duration calculations:

```mermaid
gantt
    excludes weekends
    %% or: excludes 2024-01-15, sunday
```

Configure weekend days (v11.0.0+):

```mermaid
gantt
    excludes weekends
    weekend friday
```

## Task Tags

| Tag | Description |
|---|---|
| `done` | Completed task (grayed out) |
| `active` | Currently active (highlighted) |
| `crit` | Critical path (red bar) |
| `milestone` | Zero-duration milestone (diamond) |

```mermaid
gantt
    Task 1 :done, a1, 2024-01-01, 5d
    Task 2 :active, a2, after a1, 5d
    Task 3 :crit, a3, after a2, 5d
    Launch :milestone, m1, 2024-02-01, 0d
```

## Dependencies

### after

Start after another task ends:

```mermaid
gantt
    Task A :a1, 2024-01-01, 5d
    Task B :after a1, 5d
    Task C :after a1 a2, 5d   ' after multiple tasks
```

### until (v10.9.0+)

Run until another task starts:

```mermaid
gantt
    Dev     :a1, 2024-01-01, until m1
    Release :milestone, m1, 2024-02-01, 0d
```

## Compact Mode

Reduce row height:

```mermaid
---
config:
  gantt:
    compact: true
---
gantt
    Task A :a1, 2024-01-01, 5d
```

## Today Marker

Show a vertical "today" line:

```mermaid
---
config:
  gantt:
    displayMode: compact
---
gantt
    title With Today Marker
    dateFormat YYYY-MM-DD
    Task :2024-01-01, 60d
```

## Styling

Use `classDef` and `class` for custom styling (same as flowcharts):

```mermaid
gantt
    Task A :a1, 2024-01-01, 5d
    classDef custom fill:#69f
    class a1 custom
```

## Configuration

```mermaid
---
config:
  gantt:
    useWidth: 800
    topPadding: 50
    leftPadding: 75
    barHeight: 20
    barGap: 4
    fontSize: 11
    sectionFontSize: 13
    numberSectionStyles: 4
    compact: true
---
gantt
    Task :a1, 2024-01-01, 5d
```
