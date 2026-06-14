# State Diagrams

Describe system behavior through states and transitions. Syntax is plantUml-compatible.

Use `stateDiagram-v2` (recommended) or `stateDiagram` (older renderer).

## States

```
stateId                            %% Simple state
state "Description" as s2          %% Named state with alias
s2 : This is a description         %% Description via colon
```

Spaces in names: define with alias, reference by id.

## Transitions

```
s1 --> s2                          %% Basic transition
s1 --> s2: label                   %% Labeled transition
[*] --> Start                      %% Start pseudo-state
End --> [*]                        %% End pseudo-state
```

Undefined states in transitions are auto-created.

## Composite states

```
state First {
    [*] --> inner1
    inner1 --> inner2
    inner2 --> [*]
}
First --> Second                   %% Transition between composites
```

Composite states can be nested to arbitrary depth. Transitions between internal states of different composites are not allowed.

## Choice points

```
state if_state <<choice>>
IsPositive --> if_state
if_state --> False: if n < 0
if_state --> True: if n >= 0
```

## Forks and joins

```
state fork_state <<fork>>
    [*] --> fork_state
    fork_state --> State2
    fork_state --> State3

state join_state <<join>>
    State2 --> join_state
    State3 --> join_state
    join_state --> State4
```

## Concurrency (regions)

Use `--` separator inside composite states:

```
state Active {
    [*] --> NumLockOff
    NumLockOff --> NumLockOn : EvNumLockPressed
    --
    [*] --> CapsLockOff
    CapsLockOff --> CapsLockOn : EvCapsLockPressed
}
```

## Direction

```
stateDiagram-v2
    direction LR     %% LR, RL, TB, TD, BT
    [*] --> A
    A --> B
```

Direction can be set per composite state too.

## Notes

```
note right of State1
    Important information!
end note
note left of State2 : Short note.
```

## Styling

### classDef

```
classDef badEvent fill:#f00,color:white,font-weight:bold,stroke:yellow
class Crash badEvent
class Moving, Crash movementStyle
```

### Inline with `:::`

```
[*] --> Still:::notMoving
Still --> Moving:::movement
Crash:::badEvent --> [*]
```

> **Limitation**: Cannot apply classDef to start/end pseudo-states or within composite states (as of current version).

## Comments

```
stateDiagram-v2
    [*] --> Still
    Still --> Moving %% inline comment
%% full-line comment
```
