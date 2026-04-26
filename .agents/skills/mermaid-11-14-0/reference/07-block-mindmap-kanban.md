# Block Diagrams, Mindmaps, and Kanban

## Block Diagrams

Layout-controlled component diagrams where the author has full control over shape positioning. Unlike flowcharts, block diagrams do not use automatic layout algorithms — blocks are placed exactly where you define them.

### Basic Structure

```mermaid
block
  a b c
```

Produces three blocks in a horizontal row.

### Columns

Define column count:

```mermaid
block
  columns 1
  db(("DB"))
  blockArrowId6<[" "]>(down)
  block:ID
    A
    B["A wide one in the middle"]
    C
  end
  space
  D
```

### Block Shapes

- `id` — Default block
- `id["label"]` — Block with label
- `id(("cylinder"))` — Cylinder shape
- `id<["label"]>(direction)` — Arrow block (direction: `up`, `down`, `left`, `right`)
- `space` — Empty space placeholder

### Styling

```mermaid
block
  A B C
  style B fill:#969,stroke:#333,stroke-width:4px
```

### Nested Blocks

```mermaid
block
  block:group1
    A
    B
  end
  block:group2
    C
    D
  end
  group1 --> group2
```

## Mindmaps

Hierarchical information organization using indentation-based syntax.

### Basic Syntax

Indentation defines hierarchy levels:

```mermaid
mindmap
  root((mindmap))
    Origins
      Long history
      ::icon(fa fa-book)
      Popularisation
        British author Tony Buzan
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

### Node Shapes

- `id` — Default (square)
- `id[label]` — Square
- `id(label)` — Rounded square
- `id((label))` — Circle
- `id))label((` — Bang
- `id)label(` — Cloud

### Icons

Attach icons with `::icon(fa fa-icon-name)`:

```mermaid
mindmap
  root
    Node1
      ::icon(fa fa-book)
    Node2
      ::icon(fa fa-cog)
```

## Kanban Diagrams

Visual workflow boards with columns and tasks.

### Basic Syntax

```mermaid
kanban
  todo[Todo]
    task1[Create Documentation]
  progress[In Progress]
    task2[Update Database]
  done[Done]
    task3[Deploy App]
```

### Task Metadata

Use `@{ ... }` for task metadata:

```mermaid
kanban
  todo[Todo]
    id1[Update Function]@{ ticket: MC-2037, assigned: 'knsv', priority: 'High' }
```

Supported metadata keys:

- `assigned` — Task owner
- `ticket` — Issue/ticket number
- `priority` — `Very High`, `High`, `Low`, `Very Low`
