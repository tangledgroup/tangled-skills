# Treemap Diagram

## Contents
- Basic Syntax
- Hierarchy via Indentation
- Styling (classDef)
- Configuration
- Limitations

## Overview

Treemaps display hierarchical data as nested rectangles, sized proportionally to values. Experimental — syntax may change.

```mermaid
treemap-beta
    "Products"
        "Electronics"
            "Phones": 50
            "Computers": 30
        "Clothing"
            "Men's": 40
```

## Basic Syntax

- **Section/parent nodes**: `"Name"` (no value)
- **Leaf nodes**: `"Name": value`
- **Hierarchy**: Indentation (spaces or tabs)
- **Styling**: `:::class` syntax

```mermaid
treemap-beta
    "Category A"
        "Item 1": 10
        "Item 2": 20
    "Category B"
        "Item 3": 15
```

## Hierarchy via Indentation

Any depth is supported:

```mermaid
treemap-beta
    "Root"
        "Level 1"
            "Level 2"
                "Leaf": 5
```

## Styling

Use `classDef` and `:::` operator:

```mermaid
treemap-beta
    "Section"
        "Item": 20:::highlight
        "Other": 10

classDef highlight fill:#f96,stroke:#333,stroke-width:2px;
```

## Configuration

```mermaid
---
config:
  treemap:
    minNodeSize: 10
    padding: 5
    borderRadius: 4
    ratiosOnly: false
---
treemap-beta
    "A"
        "A1": 10
```

## Limitations

- Beta feature — syntax may change
- No click events or interactivity
- Limited to rectangular layout
