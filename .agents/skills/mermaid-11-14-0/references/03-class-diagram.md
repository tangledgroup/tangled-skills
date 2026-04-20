# Class Diagram Syntax

Class diagrams describe the structure of a system showing classes, attributes, operations, and relationships.

## Basic Class Definition

```mermaid
classDiagram
    class BankAccount
    BankAccount : +String owner
    BankAccount : +BigDecimal balance
    BankAccount : +deposit(amount)
    BankAccount : +withdrawal(amount)
```

## Two Ways to Define Members

**Colon syntax (one at a time):**
```mermaid
classDiagram
class BankAccount
BankAccount : +String owner
BankAccount : +deposit(amount)
```

**Brace syntax (grouped):**
```mermaid
classDiagram
class BankAccount{
    +String owner
    +BigDecimal balance
    +deposit(amount)
    +withdrawal(amount)
}
```

## Visibility Modifiers

| Prefix | Meaning |
|---|---|
| `+` | Public |
| `-` | Private |
| `#` | Protected |
| `~` | Package/Internal |

## Class Member Classifiers

**Method classifiers** (after `()` or return type):
| Suffix | Meaning |
|---|---|
| `*` | Abstract e.g., `method()*` |
| `$` | Static e.g., `method()$` |

**Field classifiers** (at end):
| Suffix | Meaning |
|---|---|
| `$` | Static e.g., `String field$` |

## Return Types

```mermaid
classDiagram
class BankAccount{
    +deposit(amount) bool
    +withdrawal(amount) int
}
```

## Generic Types

Use tilde `~` to denote generics:

```mermaid
classDiagram
class Square~Shape~{
    int id
    List~int~ position
    setPoints(List~int~ points)
    getPoints() List~int~
}
```

> Note: Nested generics like `List<List<int>>` are supported. Generics with commas like `Map<K,V>` are not.

## Class Labels

```mermaid
classDiagram
    class Animal["Animal with a label"]
    class `Animal Class!`  --back:-- `Car Class`
```

## Relationships

| Syntax | Relationship |
|---|---|
| `A <|-- B` | Inheritance (B inherits A) |
| `A *-- B` | Composition |
| `A o-- B` | Aggregation |
| `A -- B` | Association |
| `A ..|> B` | Realization |
| `A ..> B` | Dependency |
| `A --> B` | General association |

### Cardinality

```mermaid
classDiagram
    Class01 "*" --> "1-4" Class04
    Class03 o-- Class02
    Class05 o--* Class06
```

### Labels on Relationships

```mermer
classDiagram
    Class01 "1" <|--|"*" Class02 : extends
    Class03 *-- Class04 : contains
    Class05 "1" -->* "many" Class06
```

## Full Example

```mermaid
classDiagram
    note "From Duck till Zebra"
    Animal <|-- Duck
    note for Duck "can fly<br>can swim<br>can dive"
    Animal <|-- Fish
    Animal <|-- Zebra
    Animal : +int age
    Animal : +String gender
    Animal: +isMammal()
    Animal: +mate()
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

## Interfaces

```mermaid
classDiagram
    class Drawable {
        <<interface>>
        +draw()
    }
    class Circle {
        +double radius
        +draw()
    }
    Drawable <|.. Circle
```

## Enums

```mermaid
classDiagram
    class Color {
        <<enumeration>>
        RED
        GREEN
        BLUE
    }
```
