# Class & State Diagrams

> **Source:** https://github.com/mermaid-js/mermaid/blob/mermaid%4011.14.0/docs/syntax/classDiagram.md, docs/syntax/stateDiagram.md
> **Loaded from:** SKILL.md (via progressive disclosure)

## Class Diagrams

### Basic Class Definition

```mermaid
classDiagram
    class BankAccount
    BankAccount : +String owner
    BankAccount : +BigDecimal balance
    BankAccount : +deposit(amount)
    BankAccount : +withdrawal(amount)
```

Or with braces:

```mermaid
classDiagram
class BankAccount{
    +String owner
    +BigDecimal balance
    +deposit(amount) bool
    +withdrawal(amount) int
}
```

### Visibility & Classifiers

| Prefix | Meaning |
|--------|---------|
| `+` | Public |
| `-` | Private |
| `#` | Protected |
| `~` | Package/Internal |

| Suffix | Meaning |
|--------|---------|
| `*` | Abstract method |
| `$` | Static (method or field) |

### Generic Types

```mermaid
classDiagram
class Square~Shape~{
    int id
    List~int~ position
    getPoints() List~int~
}
Square : -List~string~ messages
```

Nested generics supported; commas in generic args not supported.

### Relationships

| Syntax | Relationship |
|--------|-------------|
| `<\|--` | Inheritance |
| `*--` | Composition |
| `o--` | Aggregation |
| `-->` | Association |
| `--` | Link (solid) |
| `..>` | Dependency |
| `..\|>` | Realization |
| `..` | Link (dashed) |

With labels:
```mermaid
classDiagram
classA <|-- classB : implements
classC *-- classD : composition
```

### Two-way Relations

```mermaid
classDiagram
Animal <|--|> Zebra
```

Combines relation type (`<\|`, `*`, `o`, `>`, `<`, `\|>`) with link type (`--` solid, `..` dashed).

### Lollipop Interfaces

```mermaid
classDiagram
  class Class01 { int amount; draw() }
  Class01 --() bar
```

### Namespace

```mermaid
classDiagram
namespace BaseShapes {
    class Triangle
    class Rectangle { double width; double height; }
}
```

## State Diagrams (v2)

### Basic States & Transitions

```mermaid
stateDiagram-v2
    [*] --> Still
    Still --> Moving
    Moving --> [*]
    Still --> Crash : error
```

### State Declaration Styles

```mermaid
stateDiagram-v2
    stateId                    // Just ID
    state "Description" as s2  // With description
    s2 : Description            // ID with colon
```

### Composite States

```mermaid
stateDiagram-v2
    [*] --> First
    state First {
        [*] --> second
        second --> [*]
    }
```

Nested composite states supported to arbitrary depth.

### Choice & Fork/Join

```mermaid
stateDiagram-v2
    state if_state <<choice>>
    [*] --> IsPositive
    IsPositive --> if_state
    if_state --> False: n < 0
    if_state --> True : n >= 0

    state fork_state <<fork>>
    [*] --> fork_state
    fork_state --> State2
    fork_state --> State3
    state join_state <<join>>
    State2 --> join_state
    State3 --> join_state
    join_state --> State4
```

### Concurrency

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

### Notes

```mermaid
stateDiagram-v2
    State1: The state with a note
    note right of State1
        Important info!
    end note
    note left of State2 : Left note
```

### Direction

```mermaid
stateDiagram
    direction LR
    [*] --> A --> B --> C
```

### Styling (classDef)

```mermaid
stateDiagram-v2
    classDef movement font-style:italic
    classDef badBadEvent fill:#f00,color:white,font-weight:bold
    Still --> Moving
    class Moving movement
```

Limitations: cannot apply to start/end states or composite states.

### Comments

```mermaid
stateDiagram-v2
    [*] --> Still
%% this is a comment
    Still --> [*]
```
