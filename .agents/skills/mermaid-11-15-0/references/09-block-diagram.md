# Block Diagram Reference

## Description

Block diagrams give the author full control over shape positioning using a grid layout. Unlike flowcharts where auto-layout may move shapes, block diagrams let you explicitly place each block. Useful for system architectures, network diagrams, and process flows.

## Basic Syntax

```mermaid
block
    A
    B
    C
    A --> B
    B --> C
```

## Block Shapes

| Syntax | Shape | Example |
|--------|-------|---------|
| `A` | Default (rounded rect) | `A` |
| `A["Label"]` | Rectangle with label | `A["Server"]` |
| `A(("Label"))` | Circle/ellipse | `A(("DB"))` |
| `A<["Label"]>` | Left arrow | `A<["Input"]>` |
| `A>["Label"]>` | Right arrow | `A>["Output"]>` |
| `A^["Label"]>` | Up arrow | `A^["Up"]>` |
| `A_v["Label"]` | Down arrow | `A_v["Down"]>` |
| `Aspace` | Empty space | `space` |

## Grid Layout

### Columns

```mermaid
block
    columns 3
    A
    B
    C
```

Blocks are placed left-to-right, wrapping to the next row when the column count is reached.

### Rows and Columns Together

```mermaid
block
    columns 2
    A
    B
    C
    D
```

This creates a 2-column grid:
```
A | B
C | D
```

## Nested Blocks (Groups)

```mermaid
block
    columns 1
    A
    block:Group
        B
        C
    end
    D
    Group --> D
```

- `block:id` — Named group
- `block:id["Label"]` — Named group with label
- Reference the group by its `id` for connections

## Connectors

```mermaid
block
    A --> B
    A -.-> C
    A ==> D
```

Same connector syntax as flowcharts: `-->`, `---`, `-.->`, `==>`.

## Styling

```mermaid
block
    A
    style A fill:#f9f,stroke:#333,stroke-width:4px
```

## Examples

### Simple Pipeline

```mermaid
block
    columns 1
    db(("Database"))
    blockArrow<["Process"]>(down)
    block:Pipeline
        ETL
        Transform
        Load
    end
    space
    Dashboard
    Pipeline --> Dashboard
    style Dashboard fill:#9f6,stroke:#333
```

### System Architecture

```mermaid
block
    columns 3
    Client["Web Client"]
    space
    space
    LB["Load Balancer"]
    API1["API Server 1"]
    API2["API Server 1"]
    DB1[(DB 1)]
    DB2[(DB 2)]

    Client --> LB
    LB --> API1
    LB --> API2
    API1 --> DB1
    API2 --> DB2
```

### With Nested Blocks

```mermaid
block
    columns 1
    User["User"]
    block:Frontend
        Web["Web App"]
        Mobile["Mobile App"]
    end
    block:Backend
        API["API Gateway"]
        Auth["Auth Service"]
        Data["Data Service"]
    end
    DB[(Database)]

    User --> Frontend
    Frontend --> Backend
    Backend --> DB
```
