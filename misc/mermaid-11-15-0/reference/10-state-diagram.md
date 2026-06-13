# State Diagram

## Contents
- States and Transitions
- Start and End States
- Composite States
- Choice Points
- Forks and Joins
- Concurrency
- Notes
- Direction
- Styling (classDefs)
- Comments

## Overview

State diagrams model system behavior in terms of states and transitions between them. Use `stateDiagram-v2` (recommended) or legacy `stateDiagram`.

```mermaid
stateDiagram-v2
    [*] --> Still
    Still --> Moving
    Moving --> Crash
    Crash --> [*]
```

## States

### Simple State

```mermaid
stateDiagram-v2
    stateId
```

### Named State with Description

```mermaid
stateDiagram-v2
    state "Description text" as s1
    s2 : Another description
```

## Transitions

```mermaid
stateDiagram-v2
    s1 --> s2: transition label
```

Undefined states in transitions are auto-created.

## Start and End States

`[*]` represents the special start/end state. Direction determines role:

```mermaid
stateDiagram-v2
    [*] --> Active   ' [*] as source = start
    Inactive --> [*]  ' [*] as target = end
```

## Composite States

Nest states within states using `state ... { }`:

```mermaid
stateDiagram-v2
    [*] --> First
    state First {
        [*] --> Inner
        Inner --> [*]
    }
```

Supports unlimited nesting depth. Transitions between composite states are allowed, but not between internal states of different composites.

## Choice Points

Model decision points with `<<choice>>`:

```mermaid
stateDiagram-v2
    state if_state <<choice>>
    [*] --> Check
    Check --> if_state
    if_state --> True : if condition
    if_state --> False : else
```

## Forks and Joins

Split and merge flows with `<<fork>>` and `<<join>>`:

```mermaid
stateDiagram-v2
    state fork_state <<fork>>
    [*] --> fork_state
    fork_state --> PathA
    fork_state --> PathB

    state join_state <<join>>
    PathA --> join_state
    PathB --> join_state
    join_state --> Done
    Done --> [*]
```

## Concurrency

Use `--` separator inside composite states for concurrent regions:

```mermaid
stateDiagram-v2
    [*] --> Active
    state Active {
        [*] --> NumLockOff
        NumLockOff --> NumLockOn : EvNumLockPressed
        --
        [*] --> CapsLockOff
        CapsLockOff --> CapsLockOn : EvCapsLockPressed
    }
```

## Notes

```mermaid
stateDiagram-v2
    State1
    note right of State1
        Multi-line note text
    end note
    note left of State2 : Single line note.
```

## Direction

Set layout direction (global and per-composite-state):

```mermaid
stateDiagram-v2
    direction LR
    [*] --> A
    A --> B
    state B {
        direction TB
        a --> b
    }
```

Valid: `TB`, `BT`, `LR`, `RL`.

## Styling with classDefs

```mermaid
stateDiagram-v2
    [*] --> Still
    Still --> Moving
    Moving --> Crash
    classDef bad fill:#f00,color:white,font-weight:bold
    class Crash bad
```

Or inline with `:::`:

```mermaid
stateDiagram-v2
    [*] --> Still
    Still --> Moving:::active
    classDef active font-style:italic
```

Limitations: cannot apply to start/end states or within composite states.

## Comments

Use `%%` for line comments (own line or end-of-statement):

```mermaid
stateDiagram-v2
    [*] --> Still
    Still --> Moving %% inline comment
```
