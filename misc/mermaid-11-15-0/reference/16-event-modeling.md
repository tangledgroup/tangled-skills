# Event Modeling Diagram

## Contents
- Timeline and Time Frames
- Entity Types
- Inline Data and Data Blocks
- Reset Frames
- Multiple Relations
- Patterns (State Change, State View, Translation, Automation)

## Overview

Event Modeling diagrams describe system behavior through time-based information flow. Available since v11.15.0.

```mermaid
eventmodeling
    tf 01 ui CartUI
    tf 02 cmd AddItem
    tf 03 evt ItemAdded
```

## Timeline and Time Frames

The timeline is composed of Time Frame definitions. Each frame has a unique number, entity type, and identifier.

### Compact Notation

| Token | Entity Type |
|---|---|
| `ui` | User Interface (Trigger) |
| `cmd` | Command |
| `evt` | Event |
| `rmo` | Read Model / View |
| `pcr` | Processor |

```mermaid
eventmodeling
    tf 01 ui CartUI
    tf 02 cmd AddItem
    tf 03 evt ItemAdded
```

### Relaxed Notation

```mermaid
eventmodeling
    timeframe 01 ui CartUI
    timeframe 02 command AddItem
    timeframe 03 event ItemAdded
```

## Inline Data

Add data examples inline with `{ }`:

```mermaid
eventmodeling
    tf 02 cmd AddItem { description: string, price: number }
```

## Data Blocks

Define complex data separately and reference with `[[id]]`:

```mermaid
eventmodeling
    tf 02 cmd AddItem [[AddItem01]]
    tf 03 evt ItemAdded [[ItemAdded]]

data AddItem01 {
  description: 'john'
  price: 20.4
}

data ItemAdded {
  description: string
  price: number
}
```

## Reset Frames

Break inference chain with `rf` / `resetframe`:

```mermaid
eventmodeling
    tf 01 ui CartUI
    tf 02 cmd AddItem
    tf 03 evt ItemAdded

    rf 04 evt External.InventoryChanged
    tf 05 pcr InventoryProcessor
    tf 06 cmd ChangeInventory
```

## Multiple Relations

Use `->>` to link a read model to multiple events:

```mermaid
eventmodeling
    rf 02 evt CartCreated
    rf 03 evt ItemAdded
    rf 04 evt ItemRemoved
    tf 01 rmo CartUI ->> 02 ->> 03 ->> 04
```

## Patterns

### State Change

UI triggers command which produces event:

```mermaid
eventmodeling
    tf 01 ui CartUI
    tf 02 cmd AddItem
    tf 03 evt ItemAdded
```

### State View

Event feeds read model which feeds UI:

```mermaid
eventmodeling
    tf 03 evt ItemAdded
    tf 02 rmo CartItems
    tf 04 ui CartUI
```

### Translation

External event processed into internal command:

```mermaid
eventmodeling
    tf 03 evt External.InventoryChanged
    tf 02 pcr InventoryProcessor
    tf 04 cmd ChangeInventory
    tf 05 evt Cart.InventoryChanged
```

### Automation

Command directly produces event (no UI):

```mermaid
eventmodeling
    tf 01 cmd ProcessOrder
    tf 02 evt OrderProcessed
```
