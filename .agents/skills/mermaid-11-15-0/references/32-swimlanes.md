# Swimlanes Diagram (v11.15.0+)

Swimlane diagrams show processes divided by responsibility. Each lane is a `subgraph` representing an actor, team, or system. Nodes and edges use flowchart-style syntax.

## Syntax

Declare with `swimlane`, optionally add a direction (`TB`, `TD`, `BT`, `LR`, `RL`). Default is `TB`.

```
swimlane LR
  subgraph Customer
    request[Request service]
    receive[Receive update]
  end

  subgraph Support
    triage[Triage request]
    answer[Send answer]
  end

  subgraph Engineering
    investigate[Investigate issue]
    fix[Prepare fix]
  end

  request --> triage
  triage -->|Known issue| answer
  triage -->|Needs code change| investigate
  investigate --> fix --> answer
  answer --> receive
```

### Lanes

Top-level `subgraph` blocks render as swimlanes. Give lanes stable ids with display labels:

```
subgraph sales [Sales team]
  lead[Qualify lead]
  quote[Prepare quote]
end
```

### Nodes

Use flowchart-style shapes inside lanes:

| Syntax       | Shape             | Common use        |
|--------------|-------------------|-------------------|
| `id[Text]`   | Rectangle         | Task / activity   |
| `id(Text)`   | Rounded rectangle | Step / event      |
| `id([Text])` | Stadium           | Start / end       |
| `id{Text}`   | Decision          | Branching question|
| `id((Text))` | Circle            | Connector         |

### Edges

Edges use flowchart syntax and can cross lanes:

| Syntax             | Meaning                |
|--------------------|------------------------|
| `A --> B`          | Arrow                  |
| `A --- B`          | Line (no arrowhead)    |
| `A -->\|Label\| B` | Arrow with label       |
| `A -.-> B`         | Dotted arrow           |
| `A ==> B`          | Thick arrow            |

### Styling

Apply `classDef` and `class` to nodes across lanes:

```
classDef attention fill:#fff2cc,stroke:#d6a500,color:#111;
class review attention;
```

### Accessibility

Use `accTitle` and `accDescr` at the top of the diagram:

```
swimlane LR
  accTitle: Support escalation
  accDescr: A request flows from customer through support to engineering.
```

## Gotchas

- Use a regular flowchart when ownership is not the focus.
- Place decision nodes in the lane that owns the decision.
- Label cross-lane handoffs with `-->|Label\|` when responsibility changes.
- Split large processes into multiple diagrams when lanes stop fitting in one view.
- For full shape, edge, and styling reference, see `01-flowchart.md`.
