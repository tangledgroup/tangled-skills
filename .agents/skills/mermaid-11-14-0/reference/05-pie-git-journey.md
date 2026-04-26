# Pie Charts, Git Graphs, and User Journeys

## Pie Charts

Proportional data visualization with circular slices.

### Basic Syntax

```mermaid
pie title Pets adopted by volunteers
  "Dogs" : 386
  "Cats" : 85
  "Rats" : 15
```

- `showData` — Render actual values after legend text (optional)
- `title <text>` — Chart title (optional)
- Values must be **positive numbers > 0**
- Slices ordered clockwise in definition order

### Configuration

- `textPosition` — Axial position of labels (0.0 center to 1.0 edge), default `0.75`

```mermaid
---
config:
  pie:
    textPosition: 0.5
---
pie showData
  title Key elements
  "Calcium" : 42.96
  "Potassium" : 50.05
```

## Git Graph Diagrams

Visualize git commit history and branching strategies.

### Basic Operations

- `commit` — New commit on current branch
- `branch <name>` — Create and switch to new branch
- `checkout <name>` / `switch <name>` — Switch to existing branch
- `merge <name>` — Merge branch into current
- `cherry-pick <id>` — Cherry-pick a commit
- `reset <type>` — Reset (types: `soft`, `hard`, `mixed`)

Default branch is `main`.

### Custom Commit IDs

```mermaid
gitGraph
  commit id: "Alpha"
  commit id: "Beta"
  commit id: "Gamma"
```

### Commit Types

- `NORMAL` — Solid circle (default)
- `REVERSE` — Crossed solid circle
- `HIGHLIGHT` — Filled rectangle

```mermaid
gitGraph
  commit id: "Normal"
  commit id: "Reverse" type: REVERSE
  commit id: "Highlight" type: HIGHLIGHT
```

### Tags

```mermaid
gitGraph
  commit id: "v1.0" tag: "v1.0.0"
  commit id: "rc1" type: REVERSE tag: "RC_1"
```

### Full Example

```mermaid
gitGraph
  commit
  commit
  branch develop
  checkout develop
  commit
  commit
  checkout main
  merge develop
  commit
  commit
```

## User Journey Diagrams

Describe user workflows at a high level, revealing areas for improvement.

### Syntax

```mermaid
journey
  title My working day
  section Go to work
    Make tea: 5: Me
    Go upstairs: 3: Me
    Do work: 1: Me, Cat
  section Go home
    Go downstairs: 5: Me
    Sit down: 5: Me
```

- `title` — Optional title
- `section` — Groups related tasks (required)
- Task syntax: `Task name: <score>: <comma-separated actors>`
- Score is a number between **1 and 5** inclusive
