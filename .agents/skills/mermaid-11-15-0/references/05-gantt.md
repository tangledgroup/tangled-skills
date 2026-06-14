# Gantt Chart Reference

## Description

Gantt charts illustrate project schedules with tasks as horizontal bars along a time axis. Tasks extend left-to-right showing start and end dates, durations, and dependencies.

> **Note:** Excluded dates extend task duration to the right (no gaps within a bar). If excluded dates fall between two consecutive tasks, the gap is shown blank.

## Basic Syntax

```mermaid
gantt
    title A Gantt Diagram
    dateFormat  YYYY-MM-DD
    section Section
        Task 1     :a1, 2014-01-01, 30d
        Task 2     :after a1, 20d
    section Another
        Task 3     :2014-01-12, 12d
        Task 4     :24d
```

## Directives

| Directive | Description | Example |
|-----------|-------------|---------|
| `title` | Chart title | `title My Project` |
| `dateFormat` | Date format string | `dateFormat YYYY-MM-DD` |
| `axisFormat` | X-axis display format | `axisFormat %Y-%m-%d` |
| ` excludes` | Excluded dates | `excludes weekends` |
| `section` | Task group | `section Phase 1` |

## Date Formats

Supported formats: `YYYY-MM-DD`, `DD-MM-YYYY`, `MM-DD-YYYY`, `ISO-8601`.

```mermaid
gantt
    dateFormat  YYYY-MM-DD
    title       Project Schedule
    excludes    weekends
```

## Task Syntax

```
Task Name : [status] id, start, duration
```

### Statuses

| Status | Description |
|--------|-------------|
| `done` | Completed task (gray) |
| `active` | In-progress task (blue) |
| `crit` | Critical path task (red) |
| *(none)* | Future/pending task |

Can combine: `crit, done`, `crit, active`.

### Duration Formats

| Format | Example | Meaning |
|--------|---------|---------|
| `Xd` | `30d` | X days |
| `Xh` | `24h` | X hours |
| `Xw` | `2w` | X weeks |
| `Xm` | `3m` | X months |
| `Xy` | `1y` | X years |

### Dependencies

```mermaid
gantt
    section Tasks
        Task A     :a1, 2024-01-01, 5d
        Task B     :after a1, 3d
        Task C     :after a1, 4d
        Task D     :after b1 and c1, 2d
```

### Milestones

```mermaid
gantt
    section Phase
        Planning   :a1, 2024-01-01, 5d
        Launch     :milestone, m1, after a1, 0d
```

## Exclusions

```mermaid
gantt
    excludes weekends
    excludes 2024-12-25
    excludes monday, friday
```

- `weekends` — Saturday and Sunday
- Day names: `monday`, `tuesday`, etc.
- Specific dates: `2024-12-25`

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `useWidth` | Maximum width in pixels | `100%` |
| `topPadding` | Top padding | `50` |
| `barHeight` | Height of task bars | `20` |
| `barGap` | Gap between bars | `4` |
| `topAxis` | Show top axis | `false` |
| `sectionFontSize` | Section font size | `16` |
| `numberSectionStyles` | Number of section styles | `4` |
| `displayMode` | `compact` or `default` | `default` |

## Examples

### Project Schedule

```mermaid
gantt
    dateFormat  YYYY-MM-DD
    title       Software Release Plan
    excludes    weekends

    section Planning
    Requirements        :done, req, 2024-01-01, 10d
    Design              :active, des, after req, 5d

    section Development
    Sprint 1            :crit, s1, after des, 14d
    Sprint 2            :crit, s2, after s1, 14d
    Sprint 3            :s3, after s2, 14d

    section Testing
    QA Testing          :after s3, 10d
    Bug Fixes           :after QA Testing, 5d

    section Release
    Beta Launch         :milestone, beta, after Bug Fixes, 0d
    Production          :milestone, prod, after beta, 0d
```

### Simple Timeline

```mermaid
gantt
    title Q1 2024 Roadmap
    dateFormat  YYYY-MM-DD
    axisFormat  %b

    section Product
    Feature A          :a1, 2024-01-01, 30d
    Feature B          :after a1, 20d

    section Marketing
    Campaign Launch    :2024-01-15, 14d
    Content Plan       :20d
```
