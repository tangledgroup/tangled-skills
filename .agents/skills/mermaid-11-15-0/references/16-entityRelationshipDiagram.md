# Entity Relationship Diagrams

ER diagrams using crow's foot notation for database modeling.

## Relationships (crow's foot)

```
CUSTOMER ||--o{ ORDER : places
ORDER ||--|{ LINE-ITEM : contains
CUSTOMER }|..|{ DELIVERY-ADDRESS : uses
```

### Cardinality markers

| Marker | Meaning |
| --- | --- |
| `||` | Exactly one |
| `}|` | Zero or one |
| `}{` | Zero or many |
| `\|{` | One or many |
| `|O` | Zero or one (alt) |
| `o|` | Zero or one (alt) |
| `o{` | Zero or many (alt) |
| `{` | Many |

Line styles: `--` (solid), `..` (dashed).

## Entities with attributes

```
CUSTOMER {
    string name
    string custNumber
    int sector
}
ORDER {
    int orderNumber
    string deliveryAddress
}
```

Attributes are defined inside `{}` blocks. Type precedes name.

## Direction

```mermaid
erDiagram
    direction LR     %% LR, RL, TB, TD, BT
    CUSTOMER ||--o{ ORDER : places
```
