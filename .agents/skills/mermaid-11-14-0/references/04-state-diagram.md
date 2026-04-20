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

## Entry/Exit Actions

```mermaid
stateDiagram-v2
    [*] --> Active
    Active -->Inactive : deactivate
    Inactive -->Active : activate
    state Active {
        [*] --> Running
        Running -->Paused : pause
        Paused -->Running : resume
    }
```

## Fork & Join

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

## Notes

```mermaid
stateDiagram-v2
    [*] --> State1
    State1 --> State2
    note right of State1 : This is a note
    note left of State2 : Another note
    note bottom of State2 : Third note
```

## Configuration

Sequence diagram-specific config:
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
