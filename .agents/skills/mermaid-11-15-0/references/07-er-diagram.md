# ER Diagram Reference

## Description

Entity-Relationship (ER) diagrams model data structures using entities, attributes, and relationships. Uses crow's foot notation for cardinality. Useful for database design and domain modeling.

## Basic Syntax

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
```

## Entities

### Simple Entity

```mermaid
erDiagram
    CUSTOMER
```

### Entity with Attributes

```mermaid
erDiagram
    CUSTOMER {
        string name
        string email
        int age
    }
```

## Relationships (Crow's Foot Notation)

| Left Side | Right Side | Meaning |
|-----------|------------|---------|
| `||` | `o{` | One to zero or many |
| `||` | `\|{` | One to many (at least one) |
| `}|` | `o{` | Zero or one to zero or many |
| `}|` | `\|{` | Zero or one to many |
| `||` | `o\|` | One to zero or one |
| `||` | `||` | One to one |
| `}|` | `o\|` | Zero or one to zero or one |
| `}|` | `||` | Zero or one to one |

### Line Styles

| Symbol | Meaning |
|--------|---------|
| `--` | Solid line |
| `..` | Dashed line |

### Full Syntax

```
ENTITY1 <left_cardinality><line_style><right_cardinality> ENTITY2 : "relationship label"
```

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : "places"
    ORDER ||--|{ ITEM : "contains"
    CUSTOMER }|..|{ ADDRESS : "has"
```

## Examples

### Simple ER Diagram

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
    CUSTOMER {
        string name
        string email
        int customerId
    }
    ORDER {
        int orderId
        date orderDate
        string status
    }
    LINE-ITEM {
        int quantity
        float price
    }
```

### Complex Schema

```mermaid
erDiagram
    STUDENT ||--o{ ENROLLMENT : "enrolls in"
    COURSE ||--o{ ENROLLMENT : "offers"
    PROFESSOR ||--o{ COURSE : "teaches"
    DEPARTMENT ||--o{ PROFESSOR : "employs"
    DEPARTMENT ||--o{ COURSE : "owns"

    STUDENT {
        int studentId PK
        string firstName
        string lastName
        string email
        date enrollmentDate
    }
    COURSE {
        int courseId PK
        string title
        int credits
        string description
    }
    ENROLLMENT {
        int enrollmentId PK
        date enrollDate
        string grade
    }
    PROFESSOR {
        int professorId PK
        string name
        string department
    }
```
