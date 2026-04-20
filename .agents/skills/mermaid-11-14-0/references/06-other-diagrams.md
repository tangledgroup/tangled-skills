# Other Diagram Types

## Pie Chart

```mermaid
pie title Pets adopted by volunteers
    "Dogs" : 386
    "Cats" : 85
    "Rats" : 15
```

| Option | Description | Default |
|---|---|---|
| `showData` | Show data values in legend | hidden |
| `title` | Chart title | none |
| `textPosition` | Label position (0=center, 1=edge) | 0.75 |

> Values must be positive numbers > 0.

## Mindmap

```mermaid
mindmap
    root((mindmap))
        Origins
            Long history
            Popularisation
        British popular psychology
            British contributions
            Non-British
        Methods
            Technique
            Research
```

## Git Graph

```mermaid
gitGraph
    commit id: "Alpha"
    commit id: "Beta"
    branch develop
    checkout develop
    commit id: "Feature"
    checkout main
    merge develop
    commit id: "Release" type: HIGHLIGHT
```

| Attribute | Syntax |
|---|---|
| Custom ID | `commit id: "custom_id"` |
| Type | `commit type: NORMAL \| REVERSE \| HIGHLIGHT` |
| Tag | `commit tag: "v1.0.0"` |

Commands: `commit`, `branch`, `checkout`/`switch`, `merge`

## C4 Diagrams

```mermaid
C4Context
    title System Context
    Person(user, "User", "Description")
    System(app, "App", "Description")
    Rel(user, app, "Uses")
```

Types: `C4Context`, `C4Container`, `C4Component`, `C4Dynamic`, `C4Deployment`

## Block Diagram

```mermaid
block
    columns 3
    A["Label"] B:2 C:2 D
    A --> B
    B --> D
    style B fill:#969,stroke:#333,stroke-width:4px
```

Blocks support nesting, column layout, and spanning.

## Timeline

```mermaid
timeline
    title History of Social Media
    2002 : LinkedIn
    2004 : Facebook : Google
    2005 : YouTube
    2006 : Twitter
```

Sections: `section Name` groups time periods.

## Kanban

```mermaid
kanban
    column TODO
        task1[Task 1]
    column DONE
        task2[Task 2]
```

## Sankey (v10.3.0+)

```mermaid
sankey
    Source, Destination, Value
    Agriculture 'waste', Bio-conversion, 124
```

CSV-like format: `nodeA, nodeB, value`

## Radar Chart

```mermaid
radar
    title My Capabilities
    axis JavaScript, Python, Rust, Go, SQL
    axis React, Django, Tokio, Fiber, PostgreSQL
    a["Me", 90, 70, 50, 60, 80, 85, 60, 70, 75]
    b["Friend", 70, 80, 40, 70, 60, 75, 55, 65, 60]
```

## Venn Diagram

```mermaid
venn
    A, B, AB
```

Sets overlap to show intersections.

## XY Chart

```mermaid
xychart-beta
    title "Sales Revenue"
    x-axis [jan, feb, mar, apr, may, jun]
    y-axis "Revenue ($)" 0 --> 100
    bar [20, 40, 65, 80, 55, 90]
    line [20, 40, 65, 80, 55, 90]
```

## Quadrant Chart

```mermaid
quadrantChart
    title Reach vs Engagement
    x-axis Low Reach --> High Reach
    y-axis Low Engagement --> High Engagement
    quadrant-1 We should expand
    quadrant-2 Need to promote
    quadrant-3 Re-evaluate
    quadrant-4 May be improved
    Campaign A: [0.3, 0.6]
    Campaign B: [0.45, 0.23]
```

## User Journey

```mermaid
userJourney
    title My Day
    section Home
        Wake up: 5: Alice
        Breakfast: 4: Alice
    section Work
        Commute: 6: Bob
        Code: 8: Alice
```

Sections defined with `section Name`. Steps have priority (1-10) and actor.

## Requirement Diagram

```mermaid
requirementDiagram
    requirement req1 {
        id: 1
        text: The system shall do something.
        risk: high
        verifymethod: test
    }
```

Types: `requirement`, `interface`, `performance`, `element`, `verification`

## Architecture Diagram

```mermaid
architecture-beta
    cluster:group1 {
        service:user_app(label: "User App")
    }
    db:postgres(label: "PostgreSQL")
    service:api(label: "API Server")
    
    service:api -rl- db:postgres
    service:user_app -dd-> service:api
```

Supports AWS, Azure, GCP services.

## ZenUML

```mermaid
zenuml
    -> create and show main window
    <- wait for user to click login
    -> authenticate user
    <- show dashboard
```

Simple linear interaction syntax.

## TreeView

```mermaid
tree
    root
        child1
            grandchild1
            grandchild2
        child2
```

## TreeMap

```mermaid
treemap
    title File sizes
    roundlimit 1
    root 1000000
    src 200000
    index.html 50000
```

## Ishikawa (Fishbone)

```mermaid
ishikawa
    id[Main Problem]
    direction right
    branch Cause1
        sub-branch Sub1
        sub-branch Sub2
    branch Cause2
```

## Use Case Diagram

```mermaid
useCaseDiagram
    actor Customer
    rectangle "Online Shop" {
        Customer --> (Place Order)
        (Place Order) --> (Process Payment)
    }
```

## Waveform Plot

```mermaid
waveformPlot
    title Signal Waveform
    xaxis Time
    yaxis Amplitude
    plot sineWave
```

## Packet Diagram

```mermaid
packet
    title TCP Header
    0-15: Source Port
    16-31: Destination Port
    32-63: Sequence Number
    64-95: Acknowledgment Number
```

Binary packet layout visualization.
