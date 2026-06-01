# Packet Diagrams, Ishikawa Diagrams, Event Modeling, and XY Charts

## Packet Diagrams

Network packet structure visualization.

### Basic Syntax

```mermaid
packet
  title IP Header
  0-3: "Version and IHL"
  4-7: "DSCP and ECN"
  8-15: "Total Length"
  16-31: "Identification"
  32-33: "Flags"
  34-47: "Fragment Offset"
  48-63: "Time to Live and Protocol"
  64-95: "Header Checksum"
```

- Format: `startBit-endBit: "Field Name"`
- Bits are 0-indexed
- Fields render as proportional segments

## Ishikawa Diagrams (Fishbone / Cause-Effect)

Root cause analysis diagrams.

### Basic Syntax

```mermaid
ishikawa
  title Fishbone Diagram
  reason
    root cause
      sub reason
        detail
  reason
    another cause
```

- Indentation defines hierarchy
- Top-level items are main categories (bones)
- Nested items are sub-causes

## Event Modeling Diagrams

Domain event flow visualization.

### Basic Syntax

```mermaid
eventDiagram
  title Event Storming Example
  domainEvent OrderPlaced
  command PlaceOrder
  command PlaceOrder --> OrderPlaced
  policy If OrderPlaced then SendConfirmation
```

- `domainEvent` — Domain events (typically past tense)
- `command` — Commands (imperative)
- `policy` — Business policies/rules
- Relationships with `-->`

## XY Charts (Beta)

Scatter, line, and bar charts.

### Basic Syntax

```mermaid
xychart-beta
  title "Sales Over Time"
  x-axis [Jan, Feb, Mar, Apr, May]
  y-axis "Revenue" 0 --> 100
  bar [30, 45, 35, 50, 65]
  line [25, 40, 38, 55, 60]
```

- `title` — Chart title
- `x-axis` — Categories (string array) or numeric range
- `y-axis` — Label and range (`min --> max`)
- `bar` — Bar series
- `line` — Line series
- `circle` — Scatter/point series

### Multiple Series

```mermaid
xychart-beta
  title "Comparison"
  x-axis [Q1, Q2, Q3, Q4]
  y-axis "Value" 0 --> 100
  bar [40, 60, 55, 70]
  bar [30, 50, 45, 65]
  line [35, 55, 50, 68]
```
