# State Diagram Syntax

State diagrams describe the behavior of systems in terms of states and transitions.

## Basic States & Transitions

```mermaid
stateDiagram-v2
    [*] --> Still
    Still --> [*]
    Still --> Moving
    Moving --> Still
    Moving --> Crash
    Crash --> [*]
```

> Note: `stateDiagram` (without `-v2`) is the older renderer. Use `stateDiagram-v2` for new diagrams.

## Declaring States

### Simple ID
```mermaid
stateDiagram-v2
    stateId
```

### With Description (colon syntax)
```mermaid
stateDiagram-v2
    s2 : This is a state description
```

### With State Keyword
```mermaid
stateDiagram-v2
    state "This is a description" as s2
```

### Spaces in State Names

Use double quotes for names with spaces:
```mermaid
stateDiagram-v2
    "My State Name" : A state with spaces
```

## Setting Diagram Direction

```mermaid
stateDiagram-v2
    direction LR
    [*] --> A
    A --> B
```

Supported directions: `TB`, `BT`, `LR`, `RL`.

## Start & End States

| Syntax | Meaning |
|---|---|
| `[*] --> s1` | Entry point |
| `s1 --> [*]` | Exit point |

## Composite (Nested) States

```mermaid
stateDiagram-v2
    [*] --> First
    state First {
        [*] --> second
        second --> [*]
    }
```

Named composite:
```mermaid
stateDiagram-v2
    [*] --> NamedComposite
    NamedComposite: Another Composite
    state NamedComposite {
        [*] --> namedSimple
        namedSimple --> [*]
        namedSimple: Another simple
    }
```

## Transitions with Labels

```mermaid
stateDiagram-v2
    s1 --> s2: A transition
    s2 --> s3: success
    s3 --> s1: failure
```

## Choice Nodes

Diamond-shaped decision points using `<<choice>>`:

```mermaid
stateDiagram-v2
    state if_state <<choice>>
    [*] --> IsPositive
    IsPositive --> if_state
    if_state --> False: if n < 0
    if_state --> True : if n >= 0
```

## Forks

Split execution into parallel paths:

```mermaid
stateDiagram-v2
    [*] --> Ready
    Ready --> Processing
    state Processing {
        [*] --> ForkPoint
        ForkPoint --> ReadInput : fork
        ForkPoint --> ProcessData : fork
        ReadInput --> JoinPoint : join
        ProcessData --> JoinPoint : join
        JoinPoint --> [*]
    }
```

## Concurrency

Use `--` within composite states to define concurrent regions:

```mermaid
stateDiagram-v2
    [*] --> Active
    state Active {
        [*] --> NumLockOff
        NumLockOff --> NumLockOn : EvNumLockPressed
        NumLockOn --> NumLockOff : EvNumLockPressed
        --
        [*] --> CapsLockOff
        CapsLockOff --> CapsLockOn : EvCapsLockPressed
        CapsLockOn --> CapsLockOff : EvCapsLockPressed
        --
        [*] --> ScrollLockOff
        ScrollLockOff --> ScrollLockOn : EvScrollLockPressed
        ScrollLockOn --> ScrollLockOff : EvScrollLockPressed
    }
```

## Notes

```mermaid
stateDiagram-v2
    [*] --> State1
    State1 --> State2
    note right of State1 : This is a note
    note left of State2 : Another note
    note bottom of State2 : Third note
```

## Styling with classDefs

```mermaid
stateDiagram-v2
    classDef done fill:#9f9,stroke:#333;
    classDef active fill:#ff9,stroke:#333;
    [*] --> Still
    Still --> Moving
    Moving --> Crash
    Crash --> [*]
    class Still active;
    class Crash done;
```

### classDef Syntax

```txt
classDef styleName property:value,property2:value2;
class state1,state2 styleName;
state :::styleName
```

**Limitations:**
- Cannot be applied to start/end states
- Cannot be applied within composite states

### Apply via `class` statement

```mermaid
stateDiagram-v2
    classDef done fill:#9f9,stroke:#333;
    classDef active fill:#ff9,stroke:#333;
    [*] --> Still
    Still --> Moving
    Moving --> Crash
    Crash --> [*]
    class Still,Moving active;
    class Crash done;
```

### Apply via `:::` operator

```mermaid
stateDiagram-v2
    classDef done fill:#9f9,stroke:#333;
    [*] --> Still
    Still --> Moving :::done
    Moving --> Crash
    Crash --> [*]
```

## Setting Diagram Direction

```mermaid
stateDiagram-v2
    direction LR
    [*] --> A
    A --> B
```

Supported directions: `TB`, `BT`, `LR`, `RL`.

## Comments

```mermaid
stateDiagram-v2
    [*] --> State1
    %% This is a comment
    State1 --> State2
```

## Configuration

State diagram-specific config:
```
sequence:
    width: number
    height: number
    messageAlign: left | center | right
    mirrorActors: boolean
    useMaxWidth: boolean
    rightAngles: boolean
    showSequenceNumbers: boolean
    wrap: boolean
```
