# State Diagram Reference

## Description

State diagrams describe system behavior through states and transitions. Systems are modeled as a finite set of states with transitions between them triggered by events.

> **Note:** Use `stateDiagram-v2` for the modern renderer with full features. Plain `stateDiagram` uses the older renderer.

## Basic Syntax

```mermaid
stateDiagram-v2
    [*] --> Still
    Still --> [*]
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
```

- `[*]` — Start and end pseudo-states
- `-->` — Transition arrow

## States

### Simple State

```mermaid
stateDiagram-v2
    stateId
```

### State with Label

```mermaid
stateDiagram-v2
    state "State Label" as stateId
```

### Composite (Nested) States

```mermaid
stateDiagram-v2
    state Active {
        [*] --> Waiting
        Waiting --> Running
        Running --> [*]
    }
```

### Parallel States

```mermaid
stateDiagram-v2
    state active_processing <<parallel>> {
        state1
        state2
        state3
    }
```

### Choice (Decision) States

```mermaid
stateDiagram-v2
    state choice_state <<choice>>
```

## Transitions

### Basic Transition

```mermaid
stateDiagram-v2
    A --> B
```

### Labeled Transition

```mermaid
stateDiagram-v2
    Still -- is moving --> Moving
```

### Multiple Labels

```mermaid
stateDiagram-v2
    A -- click --> B
    A -- double click --> C
```

## Entry / Exit / Internal

```mermaid
stateDiagram-v2
    state StateName {
        [*] --> entry_state
        entry_state --> exit_state
        exit_state --> [*]
    }
    StateName : entry DoSomething()
    StateName : exit CleanUp()
```

## Choose (Conditional Transitions)

```mermaid
stateDiagram-v2
    state choice <<choice>>
    A --> choice
    choice --> B : cond1
    choice --> C : cond2
```

## Styling

```mermaid
stateDiagram-v2
    A --> B
    style A fill:#f9f,stroke:#333,stroke-width:4px
    style B fill:#bbf,stroke:#f96,stroke-width:2px
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `defaultRenderer` | Layout: `dagre`, `elk` | `dagre` |
| `diagramPadding` | Padding around diagram | `8` |
| `htmlLabels` | Use HTML labels | `true` |

## Examples

### Traffic Light

```mermaid
stateDiagram-v2
    [*] --> Green
    Green -- timer --> Yellow
    Yellow -- timer --> Red
    Red -- sensor --> Green
    Red -- timer --> Yellow
    Yellow --> Red
```

### Order Processing

```mermaid
stateDiagram-v2
    [*] --> Created
    Created --> Validated : validate()
    Created --> Rejected : invalid()
    Validated --> Processing : start()
    Processing --> Completed : finish()
    Processing --> Failed : error()
    Failed --> Processing : retry()
    Completed --> [*]
    Rejected --> [*]

    state Processing {
        [*] --> InProgress
        InProgress --> AwaitingPayment
        AwaitingPayment --> InProgress : payment received
    }
```

### With Composite States

```mermaid
stateDiagram-v2
    [*] --> Off
    Off --> On : power on
    On --> Off : power off

    state On {
        [*] --> Standby
        Standby --> Playing : play
        Playing --> Paused : pause
        Paused --> Playing : resume
        Playing --> Standby : stop
    }
```
