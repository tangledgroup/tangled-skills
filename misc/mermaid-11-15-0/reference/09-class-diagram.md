# Class Diagram

## Contents
- Defining Classes
- Members (Fields and Methods)
- Relationships
- Cardinality/Multiplicity
- Namespaces
- Annotations
- Notes
- Direction
- Interaction
- Styling
- Configuration

## Overview

Class diagrams model the structure of systems using classes, interfaces, enums, and their relationships.

```mermaid
classDiagram
    class Animal
    Animal : +String name
    Animal : +eat()
    class Dog
    Dog : +fetch()
    Animal <|-- Dog
```

## Defining Classes

### Basic Class

```mermaid
classDiagram
    class Animal
```

### With Members

List fields and methods after the class declaration:

```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +eat() void
        +toString() String
    }
```

Or inline shorthand (one per line):

```mermaid
classDiagram
    class Animal
    Animal : +String name
    Animal : +eat()
```

### Visibility Prefixes

| Symbol | Meaning |
|---|---|
| `+` | Public |
| `-` | Private |
| `#` | Protected |
| `~` | Package/internal |

### Static and Abstract

Underscore prefix for static, strikethrough (double underscore) for abstract:

```mermaid
classDiagram
    class Shape {
        +static int count
        +abstract ~draw()
    }
```

### Types (Class, Interface, Enum)

```mermaid
classDiagram
    class NormalClass
    interface Drawable
    enum Color { RED, GREEN, BLUE }
```

## Relationships

| Syntax | Line | Arrowhead | Meaning |
|---|---|---|---|
| `--` | Solid | None | Association |
| `*--` | Solid | Diamond | Composition |
| `o--` | Solid | Hollow diamond | Aggregation |
| `|--` | Solid | None | Same as association |
| `<|--` | Solid | Hollow triangle | Inheritance (generalization) |
| `..>` | Dotted | Open arrow | Dependency |
| `..|>` | Dotted | Hollow triangle | Realization (implements) |
| `*..` | Dotted | Diamond | Shared composition |
| `o..` | Dotted | Hollow diamond | Shared aggregation |

```mermaid
classDiagram
    Animal <|-- Dog
    Animal o-- Leg
    Dog *-- Tail
    Dog ..> Toy : uses
    class Drawable
    Dog ..|> Drawable
```

## Cardinality/Multiplicity

Add multiplicity to relationship ends:

```mermaid
classDiagram
    Customer "1" --> "*" Order
    Order "1" --> "1..*" Item
```

Supported values: `0..1`, `0..*`, `1..*`, `1`, `*`, `0`, and specific ranges like `2..5`.

## Namespaces

Group classes in namespaces:

```mermaid
classDiagram
    namespace Shapes {
        class Circle
        class Square
    }
    Circle -- Square
```

## Annotations

Annotate relationships with text labels:

```mermaid
classDiagram
    Customer --> Place : makes
    Place --> Order : creates
```

## Comments

Use `%%` for line comments:

```mermaid
classDiagram
    %% This is a comment
    class Foo
```

## Direction

Set layout direction:

```mermaid
classDiagram
    direction RL
    class A
    class B
    A --> B
```

Valid directions: `TB`, `BT`, `LR`, `RL`.

## Notes

Add notes to classes:

```mermaid
classDiagram
    note "This is a note for Animal" as N1
    class Animal
    N1 .. Animal
```

## Interaction (Click Events)

```mermaid
classDiagram
    class Animal
    click Animal href "https://example.com" _blank
```

Requires `securityLevel: 'loose'`.

## Styling

### Direct Styling

```mermaid
classDiagram
    class Animal
    style Animal fill:#f9f,stroke:#333,stroke-width:4px
```

### Classes

```mermaid
classDiagram
    class Animal:::cls1
    class Dog:::cls2
    classDef cls1 fill:#f96
    classDef cls2 fill:#69f
```

## Configuration

```mermaid
---
config:
  class:
    htmlLabels: true
    defaultLinkColor: "#333"
---
classDiagram
    A --> B
```
