# Process & Timeline Diagrams

> **Source:** https://github.com/mermaid-js/mermaid/blob/mermaid%4011.14.0/docs/syntax/gantt.md, docs/syntax/timeline.md, docs/syntax/kanban.md, docs/syntax/userJourney.md, docs/syntax/mindmap.md, docs/syntax/ishikawa.md
> **Loaded from:** SKILL.md (via progressive disclosure)

## Gantt Charts

### Basic Syntax

```mermaid
gantt
    title A Gantt Diagram
    dateFormat YYYY-MM-DD
    section Design
        Task A :a1, 2014-01-01, 30d
        Task B :after a1, 20d
    section Development
        Task C :2014-01-12, 12d
```

### Task Metadata

Format: `Task name :status, id, start, end/length`

| Status | Meaning |
|--------|---------|
| (none) | Future/normal |
| `done` | Completed |
| `active` | In progress |
| `crit` | Critical path |
| `milestone` | Instant in time |

### Duration Units

| Unit | Suffix | Example |
|------|--------|---------|
| Milliseconds | `ms` | `500ms` |
| Seconds | `s` | `30s` |
| Minutes | `m` | `30m` |
| Hours | `h` | `4h` |
| Days | `d` | `3d` |
| Weeks | `w` | `2w` |
| Months | `M` | `1M` |
| Years | `y` | `1y` |

### Date Dependencies

- `after taskID` — starts after another task ends
- `until taskID` — ends when another task starts (v10.9.0+)
- Multiple: `after A B C` — waits for all listed tasks

### Configuration

```mermaid
gantt
    title Project
    excludes weekends
    weekend friday
    dateFormat YYYY-MM-DD
    tickInterval 1week
    weekday monday
    axisFormat %Y-%m-%d
    section Design
        Task :done, des1, 2014-01-06, 2014-01-08
```

`excludes` accepts `YYYY-MM-DD`, day names ("sunday"), or "weekends". Weekend default: Sat+Sun; set to Friday+Saturday with `weekend friday`.

### Milestones & Vertical Markers

```mermaid
gantt
    dateFormat HH:mm
    Initial milestone : milestone, m1, 17:49, 2m
    Task A : 10m
    Final vert : vert, v2, 17:58, 4m
```

### Compact Mode

```yaml
---
displayMode: compact
---
gantt
    title A Gantt Diagram
    section Section
    A task :a1, 2014-01-01, 30d
    Another task :a2, 2014-01-20, 25d
```

## Timeline Diagram

### Basic Syntax

```mermaid
timeline
    title History of Social Media
    2002 : LinkedIn
    2004 : Facebook : Google
    2005 : YouTube
```

### Sections

```mermaid
timeline
    title Industrial Revolution
    section 17th-20th century
        Industry 1.0 : Machinery, Water power
        Industry 2.0 : Electricity
    section 21st century
        Industry 4.0 : Internet, Robotics
```

### Direction (v11.14.0+)

```mermaid
timeline TD
  title MermaidChart 2023 Timeline
    section Q1
      Bullet 1 : sub-point
```

## Kanban Diagram

### Basic Syntax

```mermaid
kanban
  Todo
    [Create Documentation]
    docs[Create Blog post]@{ ticket: MC-2037, assigned: 'knsv', priority: 'High' }
  In Progress
    id6[Build renderer]
  Done
    id5[define getData]
```

### Task Metadata

| Key | Values |
|-----|--------|
| `assigned` | Assignee name |
| `ticket` | Ticket number (linked via `ticketBaseUrl`) |
| `priority` | 'Very High', 'High', 'Low', 'Very Low' |

### Configuration

```yaml
---
config:
  kanban:
    ticketBaseUrl: 'https://jira/browse/#TICKET#'
---
```

## User Journey Diagram

### Syntax

```mermaid
journey
    title My working day
    section Go to work
      Make tea: 5: Me
      Go upstairs: 3: Me
      Do work: 1: Me, Cat
    section Go home
      Sit down: 5: Me
```

Score is 1–5. Actors are comma-separated names.

## Mindmap

### Syntax

Indentation defines hierarchy.

```mermaid
mindmap
  root((mindmap))
    Origins
      Long history
      ::icon(fa fa-book)
    Popularisation
      British popular psychology author Tony Buzan
    Research
      On effectiveness
      On Automatic creation
        Uses
            Creative techniques
            Strategic planning
    Tools
      Pen and paper
      Mermaid
```

### Shapes

| Shape | Syntax |
|-------|--------|
| Square | `id[I am a square]` |
| Rounded | `id(I am rounded)` |
| Circle | `id((I am circle))` |
| Bang | `id))I am a bang((` |
| Cloud | `id)I am a cloud(` |
| Hexagon | `id{{I am hex}}` |
| Default | `idText` |

Icons: `::icon(fa fa-book)` after a node.

## Ishikawa / Fishbone Diagram (v11.12.3+)

```mermaid
ishikawa-beta
    Blurry Photo
    Process
        Out of focus
        Shutter speed too slow
    User
        Shaky hands
    Equipment
        LENS
            Inappropriate lens
            Dirty lens
    Environment
        Too dark
```

First line = problem/event. Indentation = cause hierarchy.
