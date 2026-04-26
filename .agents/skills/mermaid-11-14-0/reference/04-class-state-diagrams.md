# Class and State Diagrams

## Class Diagrams

UML class diagrams describe system structure showing classes, attributes, operations, and relationships.

### Defining Classes

Two ways to define a class:

```mermaid
classDiagram
  class Animal
  Vehicle <|-- Car   %% defines both Vehicle and Car via relationship
```

Class labels with special characters:

```mermaid
classDiagram
  class Animal["Animal with a label"]
  class `Animal Class!`
```

### Members

Members are defined using `:` (one at a time) or `{}` (grouped):

```mermaid
classDiagram
  class BankAccount
  BankAccount : +String owner
  BankAccount : +BigDecimal balance
  BankAccount : +deposit(amount)
  BankAccount : +withdrawal(amount)

  class Animal{
    +int age
    +String gender
    +isMammal()
    +mate()
  }
```

Members with `()` are treated as methods; all others as attributes.

Visibility prefixes: `+` public, `-` private, `#` protected, `~` package/internal.

Static members use underlining in the label.

### Stereotypes

Add stereotypes with `<<stereotype>>`:

```mermaid
classDiagram
  <<interface>> Drawable
  class Shape{
    <<abstract>>
    +draw()
  }
```

### Relationships

- `<|--` — Inheritance (extension)
- `*--` — Composition
- `o--` — Aggregation
- `-->` — Association (directed)
- `--` — Association (undirected)
- `<..` — Dependency

With labels:

```mermaid
classDiagram
  Class01 <|-- AveryLongClass : Cool
  Class09 --> C2 : Where am I?
  Class09 --* C3
  Class09 --|> Class07
```

Multiplicity on relationships:

```mermaid
classDiagram
  Customer "1" --> "*" Ticket
```

### Notes

```mermaid
classDiagram
  note "From Duck till Zebra"
  note for Duck "can fly<br>can swim<br>can dive"
```

## State Diagrams

State diagrams describe system behavior through states and transitions. Use `stateDiagram-v2` for the modern renderer (recommended). Legacy `stateDiagram` is still supported.

### Basic Syntax

```mermaid
stateDiagram-v2
  [*] --> Still
  Still --> [*]
  Still --> Moving
  Moving --> Still
  Moving --> Crash
  Crash --> [*]
```

`[*]` represents start (when arrow points away) and stop (when arrow points to).

### States

Define states by id, with description, or using the `state` keyword:

```mermaid
stateDiagram-v2
  stateId
  state "Description text" as s2
  s3 : Another description
```

### Transitions

```mermaid
stateDiagram-v2
  s1 --> s2
  s1 --> s2: labeled transition
```

### Composite States

States within states using `state` keyword with `{}`:

```mermaid
stateDiagram-v2
  [*] --> First
  state First {
    [*] --> second
    second --> [*]
  }
```

Multiple nesting levels supported.

### Choice Points (fork/join)

```mermaid
stateDiagram-v2
  direction LR
  [*] --> StartState
  StartState --> {choicePoint}
  {choicePoint} --> State1: choice 1
  {choicePoint} --> State2: choice 2
```

### Parallel States (fork/join)

```mermaid
stateDiagram-v2
  state fork_state <<fork>>
  [*] --> fork_state
  fork_state --> State2
  fork_state --> State3

  state join_state <<join>>
  State2 --> join_state
  State3 --> join_state
  join_state --> State4
```

### History States

```mermaid
stateDiagram-v2
  state H1 <<history>>
  state H2 <<history>>
```

### Notes on States

```mermaid
stateDiagram-v2
  note right of state1 : Note text here
```
