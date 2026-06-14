# Gantt Charts

Project schedule visualization with tasks, sections, milestones, and critical paths.

## Syntax

```
gantt
    title Project Title
    dateFormat  YYYY-MM-DD
    excludes    weekends
    axisFormat  %Y-%m-%d

    section Development
        Task A       :done,  a1, 2024-01-01, 30d
        Task B       :active, a2, after a1, 20d
        Task C       :         a3, after a2, 5d

    section Testing
        Review       :crit, r1, after a1, 10d
        Milestone    :milestone, m1, 2024-03-01, 0d
```

## Task metadata format

`Tag(s), ID, Start, Duration/End`

### Tags (optional, must come first)

| Tag | Meaning |
| --- | --- |
| `done` | Completed task |
| `active` | Currently in progress |
| `crit` | Critical path (red bar) |
| `milestone` | Single-point marker (diamond) |

### Start options

| Syntax | Meaning |
| --- | --- |
| `2024-01-01` | Explicit date (per `dateFormat`) |
| `after taskId` | After another task ends |
| `after t1 t2` | After multiple tasks end |

### Duration/End options

| Syntax | Meaning |
| --- | --- |
| `30d` | Duration (see units below) |
| `2024-02-01` | Explicit end date |
| `until taskId` | Until another task starts (v10.9.0+) |

### Duration units

| Unit | Suffix |
| --- | --- |
| Milliseconds | `ms` |
| Seconds | `s` |
| Minutes | `m` |
| Hours | `h` |
| Days | `d` |
| Weeks | `w` |
| Months | `M` |
| Years | `y` |

Decimals supported (e.g., `1.5d`).

## Excludes

```
excludes weekends
excludes 2024-07-04, 2024-12-25
excludes sunday
weekend friday        %% Fri-Sat weekend (v11.0.0+)
```

Excluded dates extend task duration to the right (no gaps within tasks).

## Vertical markers

```
vert label : vert, v1, 2024-01-15, 0d
```

Vertical lines across the chart at specific dates.

## Date formats

### Input (`dateFormat`)

Uses day.js format: `YYYY-MM-DD`, `DD/MM/YYYY`, `HH:mm`, etc.

### Output (`axisFormat`)

Uses d3-time-format: `%Y-%m-%d`, `%b %Y`, `%H:%M`, etc.
