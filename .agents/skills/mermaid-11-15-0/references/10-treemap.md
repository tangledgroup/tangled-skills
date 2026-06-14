# Treemaps

Hierarchical data displayed as nested rectangles. Rectangle size is proportional to value.

## Syntax

```
treemap-beta
    "Section 1"
        "Leaf 1.1": 12
        "Subsection 1.2"
            "Leaf 1.2.1": 5
            "Leaf 1.2.2": 7
    "Section 2"
        "Leaf 2.1": 20
```

## Node types

| Type | Syntax | Description |
| --- | --- | --- |
| Section (parent) | `"Name"` | Container node, no value |
| Leaf (value) | `"Name": value` | Terminal node with numeric value |

Hierarchy is defined by indentation (spaces or tabs).

## Styling

```
"Section 1.2":::highlight
    "Leaf": 12:::highlight
classDef highlight fill:red,color:blue,stroke:#FFD600;
```

Apply `:::className` to sections and leaves. Use `classDef` to define styles.
