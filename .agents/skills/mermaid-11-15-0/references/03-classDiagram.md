# Class Diagrams

UML class diagrams describing system structure: classes, attributes, methods, and relationships.

## Defining classes

### Explicit declaration

```
classDiagram
    class Animal
```

### Via relationship (defines both classes)

```
Vehicle <|-- Car
```

### Class with label

```
class Animal["Animal with a label"]
class `Class With Special! Chars`
```

Use backticks or `["label"]` for special characters in names.

## Members (attributes and methods)

### Colon syntax (one at a time)

```
class BankAccount
BankAccount : +String owner
BankAccount : +BigDecimal balance
BankAccount : +deposit(amount) bool
BankAccount : +withdrawal(amount) int
```

### Curly brace syntax (grouped)

```
class BankAccount{
    +String owner
    +BigDecimal balance
    +deposit(amount) bool
    +withdrawal(amount) int
}
```

Methods are identified by `()` parentheses. Everything else is an attribute. Return type follows a space after `()`.

### Generics (tilde syntax)

```
class Square~Shape~{
    int id
    List~int~ position
    getPoints() List~int~
    getDistanceMatrix() List~List~int~~
}
```

Nested generics supported. Comma-separated generics (`List~K, V~`) are not supported. When referencing the class in relationships, drop the generic type part.

### Visibility modifiers

| Symbol | Meaning |
| --- | --- |
| `+` | Public |
| `-` | Private |
| `#` | Protected |
| `~` | Package/Internal |

### Classifiers (suffix)

| Symbol | Meaning |
| --- | --- |
| `*` | Abstract method: `method()*` or `method() int*` |
| `$` | Static method: `method()$` or `method() String$` |
| `$` | Static field: `String field$` |

## Relationships

| Syntax | Type |
| --- | --- |
| `<\|--` | Inheritance (extends) |
| `*--` | Composition |
| `o--` | Aggregation |
| `-->` | Association |
| `--` | Link (solid) |
| `..>` | Dependency |
| `<\|..` | Realization |
| `..` | Link (dashed) |

### With labels

```
classA <|-- classB : implements
classC *-- classD : composition
```

### Two-way relations

```
Animal <|--|> Zebra
```

Syntax: `[RelationType][Link][RelationType]` where RelationType is `<\|`, `\*`, `o`, `>`, `<`, or `\|>`, and Link is `--` or `..`.

### Lollipop interfaces

```
bar ()-- foo    %% Interface bar connects to class foo
foo --() bar
```

Each lollipop interface is unique per connection.

### Cardinality / multiplicity

```
Customer "1" --> "*" Ticket
Student "1" --> "1..*" Course
```

| Notation | Meaning |
| --- | --- |
| `1` | Exactly one |
| `0..1` | Zero or one |
| `1..*` | One or more |
| `*` | Many |
| `n` | Exactly n |
| `0..n` | Zero to n |
| `1..n` | One to n |

## Annotations (stereotypes)

```
class Shape <<interface>>
<<Abstract>> Animal
class Color{
    <<enumeration>>
    RED
    BLUE
}
```

Common: `<<Interface>>`, `<<Abstract>>`, `<<Service>>`, `<<Enumeration>>`.

## Namespaces (v11.15.0+)

### Basic namespace

```
namespace BaseShapes {
    class Triangle
    class Rectangle {
      double width
      double height
    }
}
```

### Namespace labels

```
namespace Auth["Authentication Service"] {
    class UserService {
        +login()
    }
}
```

### Nested namespaces (v11.15.0+)

**Dot notation** (auto-creates intermediate namespaces):
```
namespace Company.Engineering.Backend {
    class Developer
}
```

**Syntactic nesting**:
```
namespace Platform {
    namespace Auth {
        class UserService
    }
}
```

### Compact rendering

```yaml
---
config:
  class:
    hierarchicalNamespaces: false
---
```

Only explicitly declared namespaces render as boxes. Auto-created ancestors are skipped.

## Direction

```
classDiagram
    direction RL
    Animal <|-- Duck
```

Options: `LR`, `RL`, `TB`, `TD`, `BT`.

## Notes

```
note "General note text"
note for MyClass "Note for this class"
```

## Interactions

```
link Shape "https://github.com" "Tooltip"
callback Shape "callbackFunction" "Tooltip"
click Shape href "https://github.com" "Tooltip"
click Shape call callbackFunction() "Tooltip"
```

Requires `securityLevel: 'loose'`.

## Styling

### Direct style

```
style Animal fill:#f9f,stroke:#333,stroke-width:4px
```

### Class definitions

```
classDef someclass fill:#f96
cssClass "nodeId1" className
cssClass "nodeId1,nodeId2" className
```

### Inline class

```
class Animal:::someclass
classDef someclass fill:#f96
```

### Default class

```
classDef default fill:#f9f,stroke:#333,stroke-width:4px;
```

## Configuration

```yaml
---
config:
  class:
    hideEmptyMembersBox: true   %% Hide empty members compartment
    hierarchicalNamespaces: true  %% Default: nested namespace rendering
---
```

## Comments

```
%% This whole line is a comment
classDiagram
    class Shape
```
