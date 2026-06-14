# Event Modeling Diagrams (v11.15.0+)

Describe systems through information flow over time. Entities organized in swimlanes forming a timeline.

## Basic syntax

```
eventmodeling
    tf 01 ui CartUI
    tf 02 cmd AddItem
    tf 03 evt ItemAdded
    tf 04 agg ShoppingCart
    tf 05 policy ValidateStock
```

### Entity types (shorthand)

| Shorthand | Full form | Description |
| --- | --- | --- |
| `ui` | — | User interface trigger |
| `cmd` | `command` | Command |
| `evt` | `event` | Domain event |
| `agg` | `aggregate` | Aggregate root |
| `policy` | — | Policy/automation |
| `view` | — | Read model/view |
| `processor` | — | Processor trigger |

### Time frames

Each time frame has a unique number and entity identifier. Numbers don't need to be sequential, just unique.

## Relaxed notation

```
eventmodeling
    timeframe 01 ui CartUI
    timeframe 02 command AddItem
    timeframe 03 event ItemAdded
```

Full keywords instead of shorthand.

## Patterns

### State View

Show current system state via views.

### State Change

UI → Command → Event → Aggregate.

### Translation

Event → Policy → Command/View.

### Automation

Policy-driven reactions to events.
