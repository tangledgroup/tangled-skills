# Class Diagram Reference

## Description

UML class diagrams describe system structure by showing classes, their attributes, operations (methods), and relationships. Used for conceptual modeling and detailed design-to-code translation.

## Basic Syntax

```mermaid
classDiagram
    Animal <|-- Duck
    class Duck{
        +String beakColor
        +swim()
        +quack()
    }
```

## Class Definition

### Compact Notation

```mermaid
classDiagram
    class Animal
    Animal : +int age
    Animal : +String gender
    Animal : +isMammal()
    Animal : +mate()
```

### Full Block Notation

```mermaid
classDiagram
    class Duck{
        +String beakColor
        -int sizeInFeet
        #bool isWild
        +swim() void
        +quack() String
    }
```

### Visibility Modifiers

| Symbol | Meaning |
|--------|---------|
| `+` | Public |
| `-` | Private |
| `#` | Protected |
| `~` | Package/internal |

## Relationships

| Syntax | Relationship | Description |
|--------|-------------|-------------|
| `A -- B` | Association | Simple link |
| `A --> B` | Directed association | A depends on B |
| `A o-- B` | Aggregation | Whole-part (weak) |
| `A *-- B` | Composition | Whole-part (strong) |
| `A <|-- B` | Inheritance | B extends A |
| `A <|.. B` | Dependency/Implementation | B uses/implements A |
| `A -- B : label` | Labeled association | |
| `A o-- B : 1` | Aggregation with multiplicity | |
| `A *-- B : *` | Composition with multiplicity | |

### Multiplicity

| Symbol | Meaning |
|--------|---------|
| `0..1` | Zero or one |
| `0..*` / `*` | Zero or more |
| `1..1` / `` | Exactly one |
| `1..*` | One or more |
| `n..m` | Between n and m |

## Notes

```mermaid
classDiagram
    note "From Duck till Zebra"
    Animal <|-- Duck
    note for Duck "can fly<br>can swim<br>can dive"
```

## Enumerations

```mermaid
classDiagram
    enum Color {
        RED
        GREEN
        BLUE
    }
```

## Interfaces

```mermaid
classDiagram
    class Animal{
        +makeSound()
    }
    class Dog{
        +bark()
    }
    Animal <|.. Dog : implements
```

## Class Styling

```mermaid
classDiagram
    class Shape{
        +area() double
    }
    style Shape fill:#f9f,stroke:#333,stroke-width:2px
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `diagramPadding` | Padding around diagram | `8` |
| `htmlLabels` | Use HTML labels | `true` |
| `wrap` | Wrap text in class members | `false` |

## Examples

### Inheritance Hierarchy

```mermaid
classDiagram
    note "From Duck till Zebra"
    Animal <|-- Duck
    note for Duck "can fly<br>can swim<br>can dive"
    Animal <|-- Fish
    Animal <|-- Zebra
    Animal : +int age
    Animal : +String gender
    Animal : +isMammal()
    Animal : +mate()
    class Duck{
        +String beakColor
        +swim()
        +quack()
    }
    class Fish{
        -int sizeInFeet
        -canEat()
    }
    class Zebra{
        +bool is_wild
        +run()
    }
```

### Composition and Aggregation

```mermaid
classDiagram
    Car *-- Engine : has
    Car o-- Wheel : 4
    Engine --> Oil : uses
    class Car{
        +String model
        +start()
    }
    class Engine{
        +int horsepower
        +run()
    }
    class Wheel{
        +double radius
        +rotate()
    }
    class Oil{
        +int viscosity
    }
```
